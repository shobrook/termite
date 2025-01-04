import os
import pty
import sys
import errno
from select import select, error as SelectError
from subprocess import Popen, TimeoutExpired

try:
    from termite.shared.utils.python_exe import get_python_executable
except ImportError:
    from python_exe import get_python_executable


def run_pty(command: str):
    python_exe = get_python_executable()
    masters, slaves = zip(pty.openpty(), pty.openpty())
    proc = Popen(
        [python_exe, command],
        stdin=slaves[0],
        stdout=slaves[0],
        stderr=slaves[1],
    )

    try:
        for fd in slaves:
            os.close(fd)

        readable = {
            masters[0]: sys.stdout.buffer,
            masters[1]: sys.stderr.buffer,
        }

        # Keep reading until EOF from both stdout/stderr or the process ends
        while True:
            if not readable:
                break

            try:
                rlist, _, _ = select(readable, [], [])
            except SelectError:
                break

            for fd in rlist:
                try:
                    data = os.read(fd, 1024)
                except OSError as e:
                    if e.errno != errno.EIO:
                        raise
                    del readable[fd]
                else:
                    if not data:
                        del readable[fd]
                    else:
                        readable[fd].write(data)
                        readable[fd].flush()

    finally:
        # Once we've finished reading or an error occurred, close the child process.
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except TimeoutExpired:
                proc.kill()

        for fd in masters:
            try:
                os.close(fd)
            except OSError:
                pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    command = sys.argv[1]
    run_pty(command)
