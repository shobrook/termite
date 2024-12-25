# Standard library
import os
import pty
import sys
import errno
import platform
from pathlib import Path
from select import select
from subprocess import Popen, DEVNULL, run as run_cmd


#########
# HELPERS
#########


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


######
# MAIN
######


def run_tui_virtually(tui_file: str):
    python_exe = get_python_executable()

    masters, slaves = zip(pty.openpty(), pty.openpty())
    with Popen(
        [python_exe, tui_file],
        stdin=slaves[0],
        stdout=slaves[0],
        stderr=slaves[1],
    ):
        for fd in slaves:
            os.close(fd)  # no input

        readable = {
            masters[0]: sys.stdout.buffer,
            masters[1]: sys.stderr.buffer,
        }
        while readable:
            for fd in select(readable, [], [])[0]:
                try:
                    data = os.read(fd, 1024)  # read available
                except OSError as e:
                    if e.errno != errno.EIO:
                        raise  # XXX cleanup
                    del readable[fd]  # EIO means EOF on some systems
                else:
                    if not data:  # EOF
                        del readable[fd]
                    else:
                        readable[fd].write(data)
                        readable[fd].flush()

    for fd in masters:
        os.close(fd)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    tui_file = sys.argv[1]
    run_tui_virtually(tui_file)
