# Standard library
import os
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
    print("[bold white]\ntermite v1.0.5")
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


def get_tool_name(prompt: str, args: argparse.Namespace) -> str:
    timestamp = time.strftime("%Y-%m-%d-%H%M%S")
    default_name = f"{timestamp}_{prompt[:25].replace(' ', '_')}"

    print("[cyan]What would you like to name your tool?[/cyan]")
    print(f"[bright_black]Default: '{default_name}'[/bright_black]")
    tool_name = input("[cyan]>[/cyan] ").strip()

    # If the user didn't provide a name, just use a timestamp + prompt
    if len(tool_name) == 0:
        tool_name = default_name

    return tool_name


def get_library_home() -> Path:
    config_home = os.getenv("XDG_CONFIG_HOME", None)
    if config_home:
        library_dir = Path(config_home) / "termite"
    else:
        library_dir = Path.home() / ".termite"

    library_dir.mkdir(parents=True, exist_ok=True)

    return library_dir


def save_to_library(tui: Script, tool_name: str) -> Script:
    library_dir = get_library_home()
    file_path = library_dir / f"{tool_name}.py"

    with open(file_path, "w") as file:
        file.write(tui.code)

    print(f"[bright_black]\nDone! Code saved to: {file_path}[/bright_black]")


def load_script(name: str) -> Script:
    library_dir = get_library_home()
    file_path = library_dir / f"{name}.py"

    if not file_path.exists():
        print(f"[red]Error: No tool found with name '{name}'.[/red]")
        raise SystemExit

    return Script(code=file_path.read_text())


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
    parser.add_argument(
        "--run-tool",
        type=str,
        default=None,
        help="Run a previously generated TUI. Use --name when creating a TUI to name it.",
    )
    args = parser.parse_args()
    config = Config(
        library=args.library,
        should_refine=args.refine,
        refine_iters=args.refine_iters,
        fix_iters=args.fix_iters,
    )

    if args.run_tool is not None:
        tui = load_script(args.run_tool)
        print_loader(tui)
        run_tui(tui, pseudo=False)
        return

    prompt = get_prompt(args)
    if not prompt or not prompt.strip():
        print("[red]Please provide a non-empty prompt.[/red]")
        return

    tui = termite(prompt, config)
    tool_name = get_tool_name(prompt, args)
    save_to_library(tui, tool_name)
    print_loader(tui)

    if not tui.stderr:
        run_tui(tui, pseudo=False)


if __name__ == "__main__":
    main()
