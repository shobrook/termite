# Standard library
import os
import re
import ast
import time
import tempfile
from typing import Tuple
from subprocess import TimeoutExpired, DEVNULL, PIPE, run as run_cmd


# Local
try:
    from termite.dtos import Script
    from termite.shared.utils import fix_any_import_errors, get_python_executable
except ImportError as e:
    from dtos import Script
    from shared.utils import fix_any_import_errors, get_python_executable


#########
# HELPERS
#########


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
    runner_file = os.path.join(os.path.dirname(__file__), "utils", "run_pty.py")

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
        time.sleep(3)
        stdout = result.stdout if result.stdout else ""
        stderr = result.stderr if result.stderr else ""
    except TimeoutExpired:
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


def run_tui(script: Script, pseudo=True):
    if not pseudo:
        run_in_subprocess(script)
        return

    stdout, stderr = "", ""
    try:
        # Check for valid syntax before executing
        ast.parse(script.code)

        # Execute the script, iteratively fixing any import errors
        retry = True
        while retry:
            stdout, stderr = run_in_pseudo_terminal(script)
            try:
                retry = fix_any_import_errors(stderr)
            except ImportError as e:
                retry = False
                stderr = str(e)
    except SyntaxError as e:
        stderr = str(e)

    script.stdout = stdout
    script.stderr = stderr


# TODO: The PTY process is not being killed
