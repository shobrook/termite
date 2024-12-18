# Standard library
import re
from typing import Tuple

# Local
# from termite.run_llm import run_llm
# from termite.prompts import EVALUATE_PROMPT
# from termite.execute_script import Script

from run_llm import run_llm
from prompts import EVALUATE_PROMPT
from execute_script import Script


#########
# HELPERS
#########


def parse_evaluation(output: str) -> Tuple[bool, str]:
    # NOTE: Not using structured output since we might be using ollama

    is_optimal, feedback = False, output

    chunks = output.split("<is_optimal>")
    if len(chunks) == 1:
        return is_optimal, feedback

    is_optimal_str = chunks[1].split("</is_optimal>")[0].strip().lower()
    is_optimal = is_optimal_str.startswith(("yes", "y", "true", "correct", "optimal"))

    chunks = output.split("<feedback>")
    if len(chunks) == 1:
        return is_optimal, feedback

    feedback = chunks[1].split("</feedback>")[0].strip()

    return is_optimal, feedback


######
# MAIN
######


def evaluate_script(script: Script, requirements: str) -> Script:
    messages = [
        {
            "role": "user",
            "content": f"# Description\n\n{requirements}\n\n# Implementation\n\n{script.code}\n\n#####\n\nCritique this implementation. Determine whether it is optimally implemented and provide feedback if it is not.",
        }
    ]
    evaluation = run_llm(EVALUATE_PROMPT, messages)
    script.is_correct, script.reflection = parse_evaluation(evaluation)

    return script
