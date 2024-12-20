# Standard library
import time
import argparse

# Third party
from rich.console import Console

# Local
# from termite.termite import termite
# from termite.execute_script import execute_script

from termite import termite
from execute_script import execute_script

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
        print("[red]Please provide a non-empty prompt.")
        return

    # TODO: Save TUI to user's local TUI library

    tui = termite(prompt)
    if tui.has_errors:  # TODO: For some reason this isn't always hit when it should be
        # TODO: Tell users how to access it if they want to debug
        print("[red]\nFailed to generate a TUI. Please try again.")
        return

    # "Finished! Your TUI is available in your local Termite library."
    # "Run your TUI? Y/n"
    # - Then clear the screen and run the TUI
    # - Also give the option to preview the code before running (show it in a TUI :^))

    print("[magenta]\nFinished! Starting up your TUI...")
    time.sleep(3)
    execute_script(tui, suppressed=False)


if __name__ == "__main__":
    main()
