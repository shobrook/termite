# Third party
from rich.progress import Progress

# Local
try:
    from termite.dtos import Script, Config
    from termite.shared import call_llm, MAX_TOKENS
except ImportError:
    from dtos import Script, Config
    from shared import call_llm, MAX_TOKENS


"""
1. Nothing is painted to the terminal.
2. Errors are thrown on user input.
3. Design specifications are not met: content OR styling.
4. Refresh loop doesn't exist or is failing.
"""

EVALUATE_SCRIPT = """You are an expert code reviewer evaluating a terminal user interface (TUI).
Your job is to identify issues with a given TUI implementation based on the user's request.

You MUST follow these rules at all times:
- You will receive the user's request for the TUI and the Python script that implements it.
- Evaluate whether the TUI satisfies the user's request.
- Identify issues with the TUI, such as:
  - Incorrect behavior or output.
  - Poor design choices.
  - Missing features or components.
  - Usability problems.
  - Suppressed exceptions.
- Use bullet points to keep your feedback concise and clear.
- Do NOT focus on code quality or readability. This task is solely about whether the TUI satisfies the user's request.

Pay special attention to these rules:
- Keep your feedback short. Do NOT identify more than a few key issues or suggestions.
- Prioritize the most critical issues that prevent the TUI from satisfying the user's request. Leave out the minor issues.
- If you see ANY try/except blocks, suggest removing them. Exceptions are not allowed to be caught AT ALL.

Output your response in this format:
<feedback>
The issues with the TUI and suggestions for improvement go here...
</feedback>

<is_optimal>
Yes or No (Does the TUI implementation optimally satisfy the user's request?) goes here...
</is_optimal>"""

REFINE_SCRIPT = """You are an expert Python programmer tasked with improving a terminal user interface (TUI).
Your job is to use the user's feedback to improve a given TUI implementation.

You MUST follow these rules at all times:
- You will receive a description of the TUI, the current implementation in Python, and feedback on that implementation.
- Rewrite the implementation to address the feedback and make improvements.
- Ensure that the improved TUI still satisfies the user's requirements given in the design document.

<important>
- Do NOT use any try/except blocks. All exceptions must ALWAYS be raised. 
- You MUST return the full Python script for the TUI, not just the changes.
</important>

Response ONLY with code, and with no markdown formatting."""


def refine(script: Script, design: str, p_bar: Progress, config: Config) -> Script:
    task = p_bar.add_task("refine", total=config.refine_iters * (MAX_TOKENS // 12))

    num_iters = 0
    curr_script = script
    while num_iters < config.refine_iters:
        pass


# TODO: Include the refine history in the messages
# TODO: After each iteration, fix the bugs
# TODO: Then do it again until max_iters is hit
