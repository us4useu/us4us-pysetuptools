import subprocess
from typing import Tuple, Union


def run_cmd(cmd: str, return_code: bool = False,
            cwd: str = None) -> Union[str, Tuple[str, str, int]]:
    """
    Runs the given command and returns its output.

    :param cmd: command to run, split by whitespaces
    :param return_code: when true, returns the ``(stdout, stderr, returncode)``
      tuple instead of raising an exception on a non-zero exit code
    :param cwd: working directory in which the command should be run,
      ``None`` means the current working directory
    :return: command's stdout (stripped), or the
      ``(stdout, stderr, returncode)`` tuple when ``return_code`` is true
    :raises RuntimeError: when the command exited with a non-zero code and
      ``return_code`` is false
    """
    argv = cmd.strip().split(" ")
    result = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd,
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    if return_code:
        return stdout, stderr, result.returncode
    if result.returncode != 0:
        raise RuntimeError(
            f"The process {argv} exited with code {result.returncode}, "
            f"stdout: '{stdout}', stderr: '{stderr}'")
    return stdout
