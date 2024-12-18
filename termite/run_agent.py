# Standard library
from typing import List, Optional

# Local
# from termite.generate_script import generate_design, generate_script
# from termite.evaluate_script import Script, evaluate_script, execute_script

from generate_script import generate_requirements, generate_script
from evaluate_script import Script, evaluate_script
from execute_script import execute_script

MAX_ITERS = 3
MAX_RETRIES = 5


#########
# HELPERS
#########


def refine_script(script: Script, requirements: str) -> Script:
    num_iters = 0
    curr_script = script
    while num_iters < MAX_ITERS and not curr_script.is_correct:
        curr_script = evaluate_script(curr_script, requirements)

        if curr_script.is_correct:
            print("Script is self-evaluated as correct!")
            return curr_script

        print(f"Evaluated script. Issues found:\n{curr_script.reflection}\n")

        curr_script = generate_script(requirements, curr_script)
        num_iters += 1

        print(f"Refined script:\n{curr_script.code}\n\n")

    return curr_script


# TODO: Should the same generate_script function be used here? Or should there
# be separate prompts for fixing bugs?
# TODO: Bug – sometimes has_errors == True but stderr is empty
def fix_script(script: Script, requirements: str) -> Script:
    num_retries = 0
    curr_script = script
    while num_retries < MAX_RETRIES:
        curr_script = execute_script(curr_script)

        if not curr_script.has_errors:
            print("Script has no errors!")
            return curr_script

        print(f"Executed script. Error found:\n{curr_script.error_message}\n")

        curr_script = generate_script(requirements, curr_script)
        num_retries += 1

        print(f"Fixed script:\n{curr_script.code}\n\n")

    return curr_script


def get_best_script(versions: List[Script]) -> Optional[Script]:
    for script in reversed(versions):
        if script.has_errors:
            continue

        return script

    return None


######
# MAIN
######


def run_agent(prompt: str) -> Script:
    requirements = generate_requirements(prompt)

    print(f"REQUIREMENTS:\n{requirements}\n\n")

    script = generate_script(requirements)
    script = refine_script(script, requirements)
    script = fix_script(script, requirements)

    return script


# Iteratively refine the script until the LLM marks it as correct.
# THEN iteratively fix errors in the script until the compiler marks it as correct.
