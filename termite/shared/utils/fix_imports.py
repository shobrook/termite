# Standard library
import re
from subprocess import run as run_cmd


# Local
try:
    from termite.shared.call_llm import call_llm
    from termite.shared.utils.python_exe import get_python_executable
except ImportError:
    from shared.call_llm import call_llm
    from shared.utils.python_exe import get_python_executable


#########
# HELPERS
#########


PROMPT = """You are an expert Python programmer. 
Your job is to respond with the name of the package on PyPI that corresponds to the given import statement.

You MUST follow these rules at all times:
- Respond with only the name of the package on PyPI and nothing else.
- If you are unsure, respond with the original import name.
- Your output should be a single word (the package name).

## Examples

Input: \"import numpy\"
Output: \"numpy\"

Input: \"import sklearn\"
Output: \"scikit-learn\"

Input: \"import yaml\"
Output: \"PyYAML\""""


def get_package_name(module: str) -> str:
    return call_llm(
        PROMPT,
        [{"role": "user", "content": f"import {module}"}],
        model="gpt-4o-mini",  # TODO: oai_model="gpt-4o-mini", anthropic_model="..."
        temperature=0.1,
    )


def install_package(package: str) -> bool:
    python_executable = get_python_executable()
    result = run_cmd(
        [python_executable, "-m", "pip", "install", package],
        capture_output=True,
        check=True,
    )
    return result.returncode == 0


######
# MAIN
######


def fix_any_import_errors(stderr: str) -> bool:
    match = re.search(
        r"ModuleNotFoundError: No module named '(\w+)'",
        stderr,
    )
    if not match:
        return False

    # TODO: Ask user if it's okay to install package to the venv
    module = match.group(1)
    package = get_package_name(module)
    return install_package(package)
