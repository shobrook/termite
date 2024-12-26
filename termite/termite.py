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
    from termite.dtos import Script, Config
    from termite.tools import design_tui, build_tui, fix_errors, refine
except ImportError:
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

    console.log("[bold green]Designing the TUI")
    with get_progress_bar() as p_bar:
        design = design_tui(prompt, p_bar, config)

    console.log("[bold green]Building the TUI")
    with get_progress_bar() as p_bar:
        script = build_tui(design, p_bar, config)

    console.log("[bold green]Fixing bugs")
    with get_progress_bar() as p_bar:
        script = fix_errors(script, design, p_bar, config)

    # if refine:
    #     console.log("[bold green]Adding finishing touches")
    #     with get_progress_bar() as p_bar:
    #         script = refine(script, design, p_bar)

    return script


# TODO: Try capturing TUI screen as an image
# TODO: Allow for a config file
