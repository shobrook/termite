# Standard library
import sys
import platform
from pathlib import Path
from subprocess import DEVNULL, run as run_cmd


######
# MAIN
######


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
