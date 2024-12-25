# Standard library
import time
import argparse
from pathlib import Path

# Third party
from rich.console import Console
from rich.live import Live

# Local
# from termite.termite import termite
# from termite.execute_script import Script, execute_script

from termite import termite
from execute_script import Script, execute_script

console = Console(log_time=False, log_path=False)
print = console.print
input = console.input


#########
# HELPERS
#########


def print_banner():
    # print("[bold white]╔╦╗┌─┐┬─┐┌┬┐┬┌┬┐┌─┐")
    # print("[bold white] ║ ├┤ ├┬┘││││ │ ├┤")
    # print("[bold white] ╩ └─┘┴└─┴ ┴┴ ┴ └─┘")
    print("[white]▗▄▄▄▖▗▄▄▄▖▗▄▄▖ ▗▖  ▗▖▗▄▄▄▖▗▄▄▄▖▗▄▄▄▖")
    print("[white]  █  ▐▌   ▐▌ ▐▌▐▛▚▞▜▌  █    █  ▐▌   ")
    print("[white]  █  ▐▛▀▀▘▐▛▀▚▖▐▌  ▐▌  █    █  ▐▛▀▀▘")
    print("[white]  █  ▐▙▄▄▖▐▌ ▐▌▐▌  ▐▌▗▄█▄▖  █  ▐▙▄▄▖")
    print("[bold white]\ntermite v1.0.0")
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
    args = parser.parse_args()

    prompt = get_prompt(args)
    if not prompt or not prompt.strip():
        print("[red]Please provide a non-empty prompt.[/red]")
        return

    tui = termite(prompt)
    save_to_library(prompt, tui)

    # Animate the ellipsis in the message
    with Live(console=console, refresh_per_second=4) as live:
        for i in range(8):
            dots = "." * (i % 4)
            live.update(f"[magenta]Opening your TUI{dots}[/magenta]")
            time.sleep(0.5)

        if tui.stderr:
            live.update("")
            print("[red]\nFailed to open TUI.[/red]")
            return

    execute_script(tui, pseudo=False)


if __name__ == "__main__":
    main()
