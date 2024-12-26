# Standard library
from typing import Optional

# Third party
from rich.progress import Progress

# Local
try:
    from termite.dtos import Script, Config
    from termite.shared import call_llm, MAX_TOKENS
    from termite.tools.fix_errors import fix_errors
except ImportError:
    from dtos import Script, Config
    from shared import call_llm, MAX_TOKENS
    from tools.fix_errors import fix_errors


#########
# HELPERS
#########


# """
# 1. Nothing is painted to the terminal.
# 2. Errors are thrown on user input.
# 3. Design specifications are not met: content OR styling.
# 4. Refresh loop doesn't exist or is failing.
# """

PROMPT = """You are an expert Python programmer tasked with improving a terminal user interface (TUI).
Your job is to identify issues with a given TUI implementation and rewrite it to address those issues.

You MUST follow these rules at all times:
- You will receive a design document for the TUI and the Python script that implements it.
- Identify issues with the TUI, such as:
  - Failure to meet the design requirements.
  - Incorrect behavior or output.
  - Unhandled user input.
  - Missing features or components.
  - Usability problems (bad UX, e.g. missing labels, unclear instructions).
  - Suppressed exceptions.
- Rewrite the implementation to address the identified issues and improve the TUI.
- Do NOT focus on code quality or readability. This task is solely about improving the TUI to meet the design requirements.
- Continue using the {library} library. Do NOT use any other TUI libraries.
- You MUST return the full Python script for the TUI, not just the changes.

Output your response in this format:

<thoughts>
The top issues you identified and how you place to address them...
</thoughts>

<code>
Your full Python script for the improved TUI (ONLY code, and with no markdown formatting)...
</code>"""


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

        # TODO: Do not join all chunks back together –– just get the first chunk after the delimiter
        code = "```".join(chunks[1:-1]).strip()
        if code.split("\n")[0].lower().startswith("python"):
            code = "\n".join(code.split("\n")[1:])

        return code

    if code := _parse_tags():
        return code

    if code := _parse_delimiters():
        return code

    return output


def improve_tui(
    script: Script, design: str, incr_p_bar: callable, config: Config
) -> Script:
    messages = [
        # {
        #     "role": "user",
        #     "content": f"<tui_design>\n{design}\n</tui_design>\n\n<code>\n{script.code}\n</code>",
        # },
        {"role": "user", "content": design},
        {"role": "assistant", "content": script.code},
        {
            "role": "user",
            "content": "Reflect on your implementation and make a better one.",
        },
    ]
    output = call_llm(
        system=PROMPT.format(library=config.library),
        messages=messages,
        stream=True,
    )
    code = ""
    for token in output:
        code += token
        incr_p_bar()
    code = parse_code(code)

    return Script(code=code)


######
# MAIN
######


# TODO: Include the refine history in the messages
def refine(script: Script, design: str, p_bar: Progress, config: Config) -> Script:
    progress_limit = config.refine_iters * (
        (MAX_TOKENS // 12) + (config.fix_iters * (MAX_TOKENS // 12))
    )
    task = p_bar.add_task("refine", total=progress_limit)

    num_iters = 0
    curr_script = script
    while num_iters < config.refine_iters:
        incr_p_bar = lambda: p_bar.update(task, advance=1)
        curr_script = improve_tui(curr_script, design, incr_p_bar, config)
        curr_script = fix_errors(curr_script, design, incr_p_bar, config)

        num_iters += 1

    p_bar.update(task, completed=progress_limit)
    return curr_script