# Standard library
import os
import re
import sys
import ast
import platform
import tempfile
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from subprocess import TimeoutExpired, DEVNULL, PIPE, run as run_cmd

# Local
# from termite.run_llm import run_llm
# from termite.prompts import LIBRARY, RESOLVE_IMPORT_PROMPT

from run_llm import run_llm
from prompts import LIBRARY, RESOLVE_IMPORT_PROMPT


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
        RESOLVE_IMPORT_PROMPT,
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


def execute_script_with_subprocess(script: Script, suppressed=True) -> Script:
    python_exe = get_python_executable()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
        temp_file.write(script.code)
        temp_file_path = temp_file.name

    try:
        result = run_cmd(
            [python_exe, temp_file_path],
            stdout=DEVNULL if suppressed else None,
            stderr=PIPE if suppressed else None,
            timeout=5 if suppressed else None,
        )
        script.error_message = result.stderr.decode() if result.stderr else ""
        script.has_errors = result.returncode != 0 and script.error_message.strip()
    except TimeoutExpired:
        script.has_errors = False

    # Delete the temporary file
    if suppressed:
        os.remove(temp_file_path)

    return script


######
# MAIN
######


def execute_script(script: Script, suppressed=True) -> Script:
    try:
        ast.parse(script.code)
    except SyntaxError as e:
        script.has_errors = True
        script.error_message = str(e)
        return script

    install_package(LIBRARY)

    retry = True
    while retry:  # Loop until imports are resolved
        script = execute_script_with_subprocess(script, suppressed)

        if not suppressed:
            return script

        retry = False
        if script.has_errors and script.error_message:
            match = re.search(
                r"ModuleNotFoundError: No module named '(\w+)'", script.error_message
            )
            if match:
                # TODO: Ask user if it's okay to install package to the venv
                module = match.group(1)
                package = get_package_name(module)
                if install_package(package):
                    retry = True

    return script
