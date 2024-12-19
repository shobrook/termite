# Standard library
from typing import Optional

# Third party
from rich.progress import Progress

# Local
# from termite.run_llm import run_llm
# from termite.evaluate_script import Script
# from termite.prompts import GENERATE_SCRIPT, REFINE_SCRIPT

from run_llm import run_llm
from evaluate_script import Script
from prompts import GENERATE_SCRIPT, REFINE_SCRIPT


#########
# HELPERS
#########


def get_evaluation_str(script: Script) -> str:
    # We handle two "types" of evaluations: compiler errors and self-reflections

    evaluation_str = ""
    if script.has_errors:
        if script.error_message and script.error_message.strip():
            evaluation_str = f"Script is throwing an error:\n{script.error_message}\n\n#####\n\nFix the error. Remember: you CANNOT suppress exceptions."
        else:
            evaluation_str = "Script is throwing an error. Identify and fix it. Remember: you CANNOT suppress exceptions."
    elif not script.is_correct:
        evaluation_str = script.reflection

    return evaluation_str


def parse_code(output: str) -> str:
    def _parse_tags() -> Optional[str]:
        chunks = output.split("<code>")

        if len(chunks) == 1:
            return None

        code = chunks[1].split("</code>")[0].strip()
        return code

    def _parse_delimiters() -> Optional[str]:
        # TODO: Split by ```python before splitting by ```
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


######
# MAIN
######


def generate_script(
    prompt: str,
    last_script: Optional[Script] = None,
    predictive: bool = False,
    update_p_bar: Optional[callable] = None,
) -> Script:
    messages = [{"role": "user", "content": prompt}]
    if last_script:
        messages = [
            {
                "role": "user",
                "content": f"Build a TUI that satisfies the following request:\n{prompt}",
            },
            {
                "role": "assistant",
                "content": last_script.code,
            },
            {"role": "user", "content": get_evaluation_str(last_script)},
        ]

    llm_args = {
        "system": REFINE_SCRIPT if last_script else GENERATE_SCRIPT,
        "messages": messages,
        "prediction": (
            {"type": "content", "content": last_script.code} if predictive else None
        ),
        "stream": True if update_p_bar else False,
    }

    output = run_llm(**llm_args)
    code = ""
    if update_p_bar:
        for token in output:
            code += token
            update_p_bar()
    else:
        code = output
    code = parse_code(code)
    script = Script(code=code)

    return script
