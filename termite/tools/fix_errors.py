# Third party
from rich.progress import Progress

# Local

try:
    from termite.dtos import Script, Config
    from termite.shared import run_tui, call_llm, MAX_TOKENS
except ImportError:
    from dtos import Script, Config
    from shared import run_tui, call_llm, MAX_TOKENS


#########
# HELPERS
#########


PROMPT = """You are an expert Python programmer tasked with fixing a terminal user interface (TUI) implementation.
Your goal is to analyze, debug, and rewrite a broken Python script to make the TUI work without errors.

Before providing the fixed Python script, think through the debugging process using the following steps:

<debugging_process>
1. Analyze the provided Python script and the error message.
2. Identify the issues in the script that are causing the error.
3. Rewrite the script to fix the issues and make the TUI work without errors.
4. Ensure that the TUI continues to adhere to the original TUI design document.
5. Do NOT use any try/except blocks. All exceptions must ALWAYS be raised.
6. Continue using the {library} library. Do NOT use any other TUI libraries.
</debugging_process>

Respond with the complete, fixed Python script without any explanations or markdown formatting."""


def parse_code(output: str) -> str:
    chunks = output.split("```")

    if len(chunks) == 1:
        return output

    code = "```".join(chunks[1:-1]).strip()
    if code.split("\n")[0].lower().startswith("python"):
        code = "\n".join(code.split("\n")[1:])

    return code


######
# MAIN
######


def fix_errors(
    script: Script, design: str, incr_p_bar: callable, config: Config
) -> Script:
    num_retries = 0
    curr_script = script
    while num_retries < config.fix_iters:
        run_tui(curr_script)

        if not curr_script.stderr:
            return curr_script

        messages = [
            {"role": "user", "content": design},
            {"role": "assistant", "content": curr_script.code},
            {
                "role": "user",
                "content": f"<error>\n{curr_script.stderr}\n</error>\n\nFix the error above. Remember: do NOT suppress exceptions.",
            },
        ]
        output = call_llm(
            system=PROMPT.format(library="urwid"),
            messages=messages,
            stream=True,
            prediction={"type": "content", "content": curr_script.code},
        )
        code = ""
        for token in output:
            code += token
            incr_p_bar()
        code = parse_code(code)
        curr_script = Script(code=code)

        num_retries += 1

    return curr_script


# TODO: Use self-consistency
