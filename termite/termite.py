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
    from termite.shared import MAX_TOKENS
    from termite.dtos import Script, Config
    from termite.tools import design_tui, build_tui, fix_errors, refine
except ImportError:
    from shared import MAX_TOKENS
    from dtos import Script, Config
    from tools import design_tui, build_tui, fix_errors, refine

console = Console(log_time=False, log_path=False)


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


def _design_tui(prompt: str, config: Config) -> str:
    console.log("[bold green]Designing the TUI")
    with get_progress_bar() as p_bar:
        design = design_tui(prompt, p_bar, config)
        return design


def _build_tui(design: str, config: Config) -> Script:
    console.log("[bold green]Building the TUI")
    with get_progress_bar() as p_bar:
        script = build_tui(design, p_bar, config)
        return script


def _fix_errors(script: Script, design: str, config: Config) -> Script:
    console.log("[bold green]Fixing bugs")
    with get_progress_bar() as p_bar:
        # TODO: Use count_tokens(script.code) instead of MAX_TOKENS // 15
        progress_limit = config.fix_iters * (MAX_TOKENS // 15)
        task = p_bar.add_task("fix", total=progress_limit)
        incr_p_bar = lambda: p_bar.update(task, advance=1)
        script = fix_errors(script, design, incr_p_bar, config)
        p_bar.update(task, completed=progress_limit)

        return script


def _refine(script: Script, design: str, config: Config) -> Script:
    if not config.should_refine:
        return script

    console.log("[bold green]Finishing touches")
    with get_progress_bar() as p_bar:
        script = refine(script, design, p_bar, config)
        return script


######
# MAIN
######


def termite(prompt: str, config: Config) -> Script:
    """
    1. Generate a design document.
    2. Implement the TUI.
    3. Fix any bugs.
    4. (Optional) Refine the TUI.
    """

    design = _design_tui(prompt, config)
    script = _build_tui(design, config)
    script = _fix_errors(script, design, config)
    script = _refine(script, design, config)

    return script
