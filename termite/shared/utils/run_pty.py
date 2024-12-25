# Standard library
import os
import pty
import sys
import errno
from select import select
from subprocess import Popen

# Local
try:
    from termite.shared.utils.python_exe import get_python_executable
except ImportError:
    from python_exe import get_python_executable


def run_pty(command: str):
    python_exe = get_python_executable()

    masters, slaves = zip(pty.openpty(), pty.openpty())
    with Popen(
        [python_exe, command],
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

    command = sys.argv[1]
    run_pty(command)
