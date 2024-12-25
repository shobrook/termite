# Standard library
from typing import Tuple

# Local
# from termite.run_llm import run_llm
# from termite.execute_script import Script
# from termite.prompts import EVALUATE_SCRIPT

from run_llm import run_llm
from execute_script import Script
from prompts import EVALUATE_SCRIPT


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


def evaluate_script(script: Script, prompt: str):
    messages = [
        {
            "role": "user",
            "content": f"<request>{prompt}</request>\n\n<code>\n{script.code}\n</code>",
        },
    ]
    evaluation = run_llm(EVALUATE_SCRIPT, messages)
    script.is_correct, script.reflection = parse_evaluation(evaluation)


"""
1. Nothing is painted to the terminal.
2. Errors are thrown on user input.
3. Design specifications are not met: content OR styling.
4. Refresh loop doesn't exist or is failing.
"""
