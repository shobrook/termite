# Standard library
from typing import Optional
from enum import Enum

# Local
try:
    from termite.run_llm import run_llm
    from termite.evaluate_script import Script
    from termite.prompts import GENERATE_SCRIPT, FIX_SCRIPT, REFINE_SCRIPT
except ImportError:
    from run_llm import run_llm
    from evaluate_script import Script
    from prompts import GENERATE_SCRIPT, FIX_SCRIPT, REFINE_SCRIPT


#########
# HELPERS
#########


class GenerateScriptAction(str, Enum):
    CREATE = "CREATE"
    FIX = "FIX"
    REFINE = "REFINE"


def get_evaluation_str(script: Script) -> str:
    # We handle two "types" of evaluations: compiler errors and self-reflections

    evaluation_str = ""
    if script.stderr:
        evaluation_str = f"Script is throwing an error:\n{script.stderr}\n\n#####\n\nFix the error. Remember: you CANNOT suppress exceptions."
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
    action: GenerateScriptAction = GenerateScriptAction.CREATE,
    last_script: Optional[Script] = None,
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

    system = GENERATE_SCRIPT
    if action == GenerateScriptAction.REFINE:
        system = REFINE_SCRIPT
    elif action == GenerateScriptAction.FIX:
        system = FIX_SCRIPT

    llm_args = {
        "system": system,
        "messages": messages,
        "prediction": (
            {"type": "content", "content": last_script.code}
            if action == GenerateScriptAction.FIX
            else None
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


# TODO: Self-consitency for generating fixes
