# Third party
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

# Local
try:
    from termite.prompts import GENERATE_DESIGN
    from termite.run_llm import MAX_TOKENS, run_llm
    from termite.generate_script import GenerateScriptAction, generate_script
    from termite.evaluate_script import Script, evaluate_script
    from termite.execute_script import execute_script
except ImportError:
    from prompts import GENERATE_DESIGN
    from run_llm import MAX_TOKENS, run_llm
    from generate_script import GenerateScriptAction, generate_script
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


def generate_design(prompt: str) -> str:
    console.log("[bold green]Designing the TUI")
    with get_progress_bar() as p_bar:
        task = p_bar.add_task("requirements", total=MAX_TOKENS // 12)

        messages = [{"role": "user", "content": prompt}]
        output = run_llm(GENERATE_DESIGN, messages, stream=True)

        design = ""
        for token in output:
            design += token
            p_bar.update(task, advance=1)
        p_bar.update(task, completed=MAX_TOKENS // 12)

        design = f"# Design Document\n\n<user_request>\n{prompt}\n</user_request>\n\n<details>\n{design}\n</details>"
        return design


def generate_tui(plan: str) -> Script:
    console.log("[bold green]Building the TUI")
    with get_progress_bar() as p_bar:
        task = p_bar.add_task("initial", total=MAX_TOKENS // 12)
        update_p_bar = lambda: p_bar.update(task, advance=1)

        script = generate_script(plan, update_p_bar=update_p_bar)

        p_bar.update(task, completed=MAX_TOKENS // 12)

    return script


# TODO: Include the fix history in the messages
def fix_bugs(script: Script, plan: str, max_retries: int = 10) -> Script:
    if not max_retries:
        return script

    console.log("[bold green]Fixing bugs")
    with get_progress_bar() as p_bar:
        task = p_bar.add_task("fix", total=max_retries)

        num_retries = 0
        curr_script = script
        while num_retries < max_retries:
            execute_script(curr_script)

            if not curr_script.stderr:
                p_bar.update(task, completed=max_retries)
                return curr_script

            curr_script = generate_script(
                plan,
                action=GenerateScriptAction.FIX,
                last_script=curr_script,
            )
            p_bar.update(task, advance=1)
            num_retries += 1

        return curr_script


# TODO: Include the refine history in the messages
def refine_tui(script: Script, plan: str, max_iters: int = 3) -> Script:
    if not max_iters:
        return script

    console.log("[bold green]Adding finishing touches")
    with get_progress_bar() as p_bar:
        task = p_bar.add_task("refine", total=max_iters)

        num_iters = 0
        curr_script = script
        while num_iters < max_iters and not curr_script.is_correct:
            evaluate_script(curr_script, plan)

            if curr_script.is_correct:
                p_bar.update(task, completed=max_iters)
                return curr_script

            curr_script = generate_script(
                plan, action=GenerateScriptAction.REFINE, last_script=curr_script
            )
            p_bar.update(task, advance=1)
            num_iters += 1

        return curr_script


######
# MAIN
######


def termite(prompt: str) -> Script:
    """
    1. Generate a design document.
    2. Implement the TUI.
    3. Fix any bugs.
    4. (Optional) Refine the TUI.
    """

    design = generate_design(prompt)
    script = generate_tui(design)
    script = fix_bugs(script, design)
    # script = refine_tui(script, plan)

    return script
