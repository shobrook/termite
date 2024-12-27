# Standard library
from typing import Optional

# Third party
from rich.progress import Progress

# Local
try:
    from termite.dtos import Script, Config
    from termite.shared import call_llm, MAX_TOKENS
except ImportError:
    from dtos import Script, Config
    from shared import call_llm, MAX_TOKENS


#########
# HELPERS
#########


PROGRESS_LIMIT = MAX_TOKENS // 15
PROMPT = """You are an expert Python programmer tasked with building a terminal user interface (TUI).
You will be given a design document that describes the TUI and its requirements. Your job is to implement the TUI using the {library} library.

You MUST follow these rules at all times:
- Use ONLY the {library} library to build the TUI. Do NOT use any other TUI libraries.
- You may use common Python packages, but only if absolutely necessary. E.g. numpy, redis, beautifulsoup4, etc.
- Do NOT use any try/except blocks. All exceptions must ALWAYS be raised. 
- Ensure the TUI takes up the full width (and ideally height) of the terminal window.
- Implement the design and functionality in the given TUI description.
- Double-check your code for potential bugs or unexpected behaviors.

Output your response in this format:

<thoughts>
Your step-by-step implementation plan goes here...
</thoughts>

<code>
import {library}

# TUI implementation code goes here
# ...

if __name__ == "__main__":
    main()
</code>

Remember, your code must be bug-free and adhere precisely to the given TUI design without any unexpected behavior."""


def parse_code(output: str) -> str:
    def _parse_tags() -> Optional[str]:
        chunks = output.split("<code>")

        if len(chunks) == 1:
            return None

        code = chunks[1].split("</code>")[0].strip()
        return code

    def _parse_delimiters() -> Optional[str]:
        chunks = output.split("```")

        if len(chunks) == 1:
            return None

        code = "```".join(chunks[1:-1]).strip()
        if code.split("\n")[0].lower().startswith("python"):
            code = "\n".join(code.split("\n")[1:])

        return code

    if code := _parse_tags():
        return code

    if code := _parse_delimiters():
        return code

    return output


######
# MAIN
######


def build_tui(design: str, p_bar: Progress, config: Config) -> Script:
    task = p_bar.add_task("build", total=PROGRESS_LIMIT)

    output = call_llm(
        system=PROMPT.format(library=config.library),
        messages=[{"role": "user", "content": design}],
        stream=True,
    )
    code = ""
    for token in output:
        code += token
        p_bar.update(task, advance=1)
    code = parse_code(code)
    script = Script(code=code)

    p_bar.update(task, completed=PROGRESS_LIMIT)
    return script
