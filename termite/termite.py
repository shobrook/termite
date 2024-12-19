# Third party
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

# Local
# from termite.run_llm import MAX_TOKENS
# from termite.generate_script import generate_script
# from termite.evaluate_script import Script, evaluate_script
# from termite.execute_script import execute_script

from run_llm import MAX_TOKENS
from generate_script import generate_script
from evaluate_script import Script, evaluate_script
from execute_script import execute_script

console = Console(log_time=False, log_path=False)
print = console.print


#########
# HELPERS
#########


def get_progress_bar() -> Progress:
    return Progress(
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TimeElapsedColumn(),
        transient=False,
    )


def generate_requirements(prompt: str) -> str:
    # TODO: Implement
    console.log("[bold green]Designing the TUI")
    with get_progress_bar() as p_bar:
        task = p_bar.add_task("requirements", total=MAX_TOKENS // 10)
        p_bar.update(task, completed=MAX_TOKENS // 10)

    return prompt


def generate_mvp(prompt: str) -> Script:
    console.log("[bold green]Building an initial version")
    with get_progress_bar() as p_bar:
        task = p_bar.add_task("initial", total=MAX_TOKENS // 10)
        update_p_bar = lambda: p_bar.update(task, advance=1)

        script = generate_script(prompt, update_p_bar=update_p_bar)

        p_bar.update(task, completed=MAX_TOKENS // 10)

    return script


# TODO: Include the refine history in the messages
def refine_script(script: Script, prompt: str, max_iters: int = 3) -> Script:
    if not max_iters:
        return script

    console.log("[bold green]Refining implementation")
    with get_progress_bar() as p_bar:
        task = p_bar.add_task("refine", total=max_iters)

        num_iters = 0
        curr_script = script
        while num_iters < max_iters and not curr_script.is_correct:
            evaluate_script(curr_script, prompt)

            if curr_script.is_correct:
                p_bar.update(task, completed=max_iters)
                return curr_script

            curr_script = generate_script(prompt, curr_script)
            p_bar.update(task, advance=1)
            num_iters += 1

        return curr_script


# TODO: Include the fix history in the messages
def fix_script(script: Script, prompt: str, max_retries: int = 10) -> Script:
    if not max_retries:
        return script

    console.log("[bold green]Fixing bugs")
    with get_progress_bar() as p_bar:
        task = p_bar.add_task("fix", total=max_retries)

        num_retries = 0
        curr_script = script
        while num_retries < max_retries:
            execute_script(curr_script)

            if not curr_script.has_errors:
                p_bar.update(task, completed=max_retries)
                return curr_script

            curr_script = generate_script(prompt, curr_script, predictive=True)
            p_bar.update(task, advance=1)
            num_retries += 1

        return curr_script


######
# MAIN
######


def termite(prompt: str) -> Script:
    """
    1. Generate requirements for the TUI.
    2. Generate an implementation plan (pseudocode).
    3. Generate a first draft of the script in Python, using urwid.
    4. (Optional) Iteratively refine the code using self-reflection.
    5. Iteratively fix runtime errors.
    """

    requirements = generate_requirements(prompt)
    # plan = generate_pseudocode(requirements)
    script = generate_mvp(requirements)
    script = refine_script(script, requirements)
    script = fix_script(script, requirements)

    return script
