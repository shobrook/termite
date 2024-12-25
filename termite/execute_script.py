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
try:
    from termite.run_llm import run_llm
    from termite.prompts import RESOLVE_IMPORTS
except ImportError as e:
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
    stdout: Optional[str] = None
    stderr: Optional[str] = None


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


def save_script_to_file(script: Script) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
        temp_file.write(script.code)
        temp_file_path = temp_file.name

    return temp_file_path


def strip_ansi_escape_sequences(data: str) -> str:
    ansi_escape = re.compile(
        r"""
        \x1B
        (?:
            [@-Z\\-_]
        |
            \[
            [0-?]*
            [ -/]*
            [@-~]
        |
            \]
            (?:
                [^\x07]*?
                \x07
            |
                [^\x1B]*?
                \x1B\\
            )
        |
            [PX^_]
            .*?
            \x1B\\
        )
        """,
        re.VERBOSE | re.DOTALL,
    )
    return ansi_escape.sub("", data)


def run_in_pseudo_terminal(script: Script, timeout: int = 5) -> Tuple[str, str]:
    python_exe = get_python_executable()
    tui_file = save_script_to_file(script)
    runner_file = os.path.join(os.path.dirname(__file__), "run_pt.py")

    stdout, stderr = "", ""
    try:
        result = run_cmd(
            [
                python_exe,
                runner_file,
                tui_file,
            ],
            stdout=DEVNULL,
            stderr=PIPE,
            text=True,
            timeout=timeout,
        )
        stdout = result.stdout if result.stdout else ""
        stderr = result.stderr if result.stderr else ""
    except TimeoutExpired as e:
        stdout, stderr = "", ""
    finally:
        os.remove(tui_file)

    stderr = strip_ansi_escape_sequences(stderr)
    return stdout.strip(), stderr.strip()


def run_in_subprocess(script: Script):
    python_exe = get_python_executable()
    script_file = save_script_to_file(script)
    run_cmd([python_exe, script_file])


######
# MAIN
######


def execute_script(script: Script, pseudo=True):
    if not pseudo:
        run_in_subprocess(script)
        return

    stdout, stderr = "", ""
    try:
        # Check for valid syntax before executing
        ast.parse(script.code)

        # Execute the script, resolving import errors if any
        retry = True
        while retry:
            stdout, stderr = run_in_pseudo_terminal(script)

            if not pseudo:
                return

            retry = False
            if stderr:
                match = re.search(
                    r"ModuleNotFoundError: No module named '(\w+)'",
                    stderr,
                )
                if match:
                    # TODO: Ask user if it's okay to install package to the venv
                    module = match.group(1)
                    package = get_package_name(module)
                    if install_package(package):
                        retry = True
    except SyntaxError as e:
        stderr = str(e)

    script.stdout = stdout
    script.stderr = stderr
