# Standard library
from typing import List, Optional

# Local
# from termite.generate_script import generate_script
# from termite.evaluate_script import Script, evaluate_script
# from termite.execute_script import execute_script

from generate_script import generate_script
from evaluate_script import Script, evaluate_script
from execute_script import execute_script

MAX_ITERS = 3
MAX_RETRIES = 10


#########
# HELPERS
#########


# TODO: Include the refine history in the messages
def refine_script(script: Script, prompt: str) -> Script:
    print(f"Initial script:\n{script.code}\n\n")

    num_iters = 0
    curr_script = script
    while num_iters < MAX_ITERS and not curr_script.is_correct:
        evaluate_script(curr_script, prompt)

        if curr_script.is_correct:
            print("Script is self-evaluated as correct!")
            return curr_script

        print(f"Evaluated script. Issues found:\n{curr_script.reflection}\n")

        curr_script = generate_script(prompt, curr_script)
        num_iters += 1

        print(f"Refined script:\n{curr_script.code}\n\n")

    return curr_script


# TODO: Include the fix history in the messages
# TODO: Use predictive outputs to speed this up
def fix_script(script: Script, prompt: str) -> Script:
    num_retries = 0
    curr_script = script
    while num_retries < MAX_RETRIES:
        execute_script(curr_script)

        if not curr_script.has_errors:
            print("Script has no errors!")
            return curr_script

        print(f"Executed script. Error found:\n{curr_script.error_message}\n")

        curr_script = generate_script(prompt, curr_script)
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


def run_pipeline(prompt: str) -> Script:
    script = generate_script(prompt)
    script = refine_script(script, prompt)
    script = fix_script(script, prompt)

    return script
