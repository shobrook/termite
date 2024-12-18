# Standard library
import os
import re
import sys
import ast
import platform
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
from subprocess import TimeoutExpired, DEVNULL, PIPE, run as run_cmd

# Local
# from termite.run_llm import run_llm
# from termite.prompts import RESOLVE_IMPORTS

from run_llm import run_llm
from prompts import RESOLVE_IMPORTS


#########
# HELPERS
#########


@dataclass
class Script:
    code: str
    is_correct: bool = False
    reflection: Optional[str] = None
    has_errors: Optional[bool] = None
    error_message: Optional[str] = None


def get_python_executable() -> str:
    venv_dir = Path.home() / ".termite"
    if platform.system() == "Windows":
        executable = venv_dir / "Scripts" / "python"
    else:
        executable = venv_dir / "bin" / "python"

    if not venv_dir.exists():
        run_cmd(
            [sys.executable, "-m", "venv", str(venv_dir)],
            stdout=DEVNULL,
            stderr=DEVNULL,
            check=True,
        )

    return str(executable)


def get_package_name(module: str) -> str:
    return run_llm(
        RESOLVE_IMPORTS,
        [{"role": "user", "content": f"import {module}"}],
        model="gpt-4o-mini",
        temperature=0.1,
    )


def install_package(package: str) -> bool:
    if package in ["curses"]:  # Standard library
        return True

    python_executable = get_python_executable()
    result = run_cmd(
        [python_executable, "-m", "pip", "install", package],
        capture_output=True,
        check=True,
    )
    return result.returncode == 0


def execute_script_with_subprocess(script: Script, suppressed=True) -> Tuple[bool, str]:
    python_exe = get_python_executable()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
        temp_file.write(script.code)
        temp_file_path = temp_file.name

    has_errors = False
    error_message = ""

    try:
        result = run_cmd(
            [python_exe, temp_file_path],
            stdout=DEVNULL if suppressed else None,
            stderr=PIPE if suppressed else None,
            timeout=5 if suppressed else None,
        )
        error_message = result.stderr.decode() if result.stderr else ""
        has_errors = (
            result.returncode != 0 and error_message.strip()
        )  # NOTE: Kinda dumb..
    except TimeoutExpired:
        pass
    finally:
        # Delete the temporary file
        if suppressed:
            os.remove(temp_file_path)

    return has_errors, error_message


######
# MAIN
######


def execute_script(script: Script, suppressed=True):
    has_errors = False
    error_message = ""

    try:
        # Check for valid syntax before executing
        ast.parse(script.code)

        # Execute the script, resolving import errors if any
        retry = True
        while retry:
            has_errors, error_message = execute_script_with_subprocess(
                script, suppressed
            )

            if not suppressed:
                return

            retry = False
            if has_errors and error_message:
                match = re.search(
                    r"ModuleNotFoundError: No module named '(\w+)'",
                    error_message,
                )
                if match:
                    # TODO: Ask user if it's okay to install package to the venv
                    module = match.group(1)
                    package = get_package_name(module)
                    if install_package(package):
                        retry = True
    except SyntaxError as e:
        has_errors = True
        error_message = str(e)

    script.has_errors = has_errors
    script.error_message = error_message
