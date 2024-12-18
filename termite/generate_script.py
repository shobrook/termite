# Standard library
from typing import Optional

# Local
# from termite.run_llm import run_llm
# from termite.evaluate_script import Script
# from termite.prompts import REQUIREMENTS_PROMPT, GENERATE_SCRIPT_PROMPT

from run_llm import run_llm
from evaluate_script import Script
from prompts import REQUIREMENTS_PROMPT, GENERATE_SCRIPT_PROMPT


#########
# HELPERS
#########


def get_evaluation_str(script: Script) -> str:
    evaluation_str = ""
    if script.has_errors:
        if script.error_message and script.error_message.strip():
            evaluation_str = f"Error:\n{script.error_message}\n\n#####\n\nFix this error and try again."
        else:
            evaluation_str = "Error:\nThis script has an unknown error.\n\nTry again."
    elif not script.is_correct:
        evaluation_str = f"Failed to meet requirements. Feedback:\n{script.reflection}\n\n#####\n\nFix these issues and try again."

    return evaluation_str


# TODO: Check first for ```python before splitting by ```
def parse_code(output: str) -> str:
    chunks = output.split("```")

    if len(chunks) == 1:
        return output

    script = "```".join(chunks[1:-1]).strip()
    if script.split("\n")[0].lower().startswith("python"):
        script = "\n".join(script.split("\n")[1:])

    return script


######
# MAIN
######


def generate_requirements(prompt: str) -> str:
    """
    Turns the prompt into a fleshed out requirements document for a TUI.
    """

    messages = [{"role": "user", "content": prompt}]
    requirements = run_llm(REQUIREMENTS_PROMPT, messages)
    design = f"<request>{prompt}</request>\n\n<requirements>\n{requirements}\n</requirements>"
    return design


def generate_script(requirements: str, last_script: Optional[Script] = None) -> Script:
    messages = [{"role": "user", "content": requirements}]
    if last_script:
        messages.append({"role": "assistant", "content": last_script.code})
        messages.append({"role": "user", "content": get_evaluation_str(last_script)})

    code = run_llm(GENERATE_SCRIPT_PROMPT, messages)
    code = parse_code(code)

    return Script(code=code)
