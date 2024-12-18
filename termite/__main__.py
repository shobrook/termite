# Standard library
import argparse

# Local
# from termite.run_agent import run_agent
# from termite.execute_script import execute_script

from run_agent import run_agent
from execute_script import execute_script


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

    # TODO: Loading indicator
    tui = run_agent(" ".join(args.prompt))
    if tui.has_errors:
        print("ERROR: Could not generate a TUI.")
        return

    print("GOT A TUI, executing it now")
    execute_script(tui, suppressed=False)
    # TODO: Add option to save TUI to library


if __name__ == "__main__":
    main()
