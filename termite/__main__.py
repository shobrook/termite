# Standard library
import time
import argparse
from pathlib import Path

# Third party
from rich.live import Live
from rich.console import Console

# Local
try:
    from termite.shared import run_tui
    from termite.termite import termite
    from termite.dtos import Script, Config
except ImportError:
    from shared import run_tui
    from termite import termite
    from dtos import Script, Config

console = Console(log_time=False, log_path=False)
print = console.print
input = console.input


#########
# HELPERS
#########


def print_banner():
    # print("[white]╔╦╗┌─┐┬─┐┌┬┐┬┌┬┐┌─┐")
    # print("[white] ║ ├┤ ├┬┘││││ │ ├┤")
    # print("[white] ╩ └─┘┴└─┴ ┴┴ ┴ └─┘")
    print("[white]▗▄▄▄▖▗▄▄▄▖▗▄▄▖ ▗▖  ▗▖▗▄▄▄▖▗▄▄▄▖▗▄▄▄▖")
    print("[white]  █  ▐▌   ▐▌ ▐▌▐▛▚▞▜▌  █    █  ▐▌   ")
    print("[white]  █  ▐▛▀▀▘▐▛▀▚▖▐▌  ▐▌  █    █  ▐▛▀▀▘")
    print("[white]  █  ▐▙▄▄▖▐▌ ▐▌▐▌  ▐▌▗▄█▄▖  █  ▐▙▄▄▖")
    print("[bold white]\ntermite v1.0.1")
    print("What do you want to make? (Ctrl-C to exit)")


def get_prompt(args: argparse.Namespace) -> str:
    prompt = ""
    if len(args.prompt) > 0:
        prompt = " ".join(args.prompt)
    else:
        print_banner()
        prompt = input("[magenta]>[/magenta] ")
        print("")

    return prompt


def save_to_library(prompt: str, tui: Script):
    library_dir = Path.home() / ".termite"
    if not library_dir.exists():
        library_dir.mkdir(parents=True)

    timestamp = time.strftime("%Y-%m-%d-%H%M%S")
    file_name = f"{timestamp}_{prompt[:25].replace(" ", "_")}.py"
    file_path = library_dir / file_name

    with open(file_path, "w") as file:
        file.write(tui.code)

    print(f"[bright_black]\nDone! Code saved to: {file_path}[/bright_black]")


def print_loader(tui: Script):
    with Live(console=console, refresh_per_second=4) as live:
        for i in range(8):
            dots = "." * (i % 4)
            live.update(f"[magenta]Opening your TUI{dots}[/magenta]")
            time.sleep(0.5)

        if tui.stderr:
            live.update("")
            print("[red]\nFailed to open TUI.[/red]")
            return


######
# MAIN
######


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generative UI in your terminal. Describe a TUI and Termite will generate one for you."
        )
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Description of the TUI you want to generate.",
    )
    parser.add_argument(
        "--library",
        type=str,
        required=False,
        default="urwid",
        help="The library to use for implementing the TUI (urwid, rich, curses, textual).",
    )
    parser.add_argument(
        "--refine",
        action="store_true",
        help="Get better results (slower, more LLM calls) by adding a refinement loop.",
    )
    parser.add_argument(
        "--refine-iters",
        required=False,
        type=int,
        default=1,
        help="Number of refinement iterations to perform.",
    )
    parser.add_argument(
        "--fix-iters",
        type=int,
        required=False,
        default=10,
        help="Max. # of iterations to fix errors.",
    )
    args = parser.parse_args()
    config = Config(
        library=args.library,
        should_refine=args.refine,
        refine_iters=args.refine_iters,
        fix_iters=args.fix_iters,
    )

    prompt = get_prompt(args)
    if not prompt or not prompt.strip():
        print("[red]Please provide a non-empty prompt.[/red]")
        return

    tui = termite(prompt, config)
    save_to_library(prompt, tui)
    print_loader(tui)

    if not tui.stderr:
        run_tui(tui, pseudo=False)


if __name__ == "__main__":
    main()
