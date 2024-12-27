# Third party
from rich.progress import Progress

# Local
try:
    from termite.dtos import Config
    from termite.shared import call_llm, MAX_TOKENS
except ImportError:
    from dtos import Config
    from shared import call_llm, MAX_TOKENS


#########
# HELPERS
#########


PROGRESS_LIMIT = MAX_TOKENS // 15
PROMPT = """You are an expert in designing terminal user interfaces (TUIs). Your task is to write a design document for a TUI that satisfies the user's request.

Your design will be implemented by a junior developer using the {library} library, so it's crucial to keep it SIMPLE and EASY TO UNDERSTAND.

Before providing your final design, think through the process using the following steps:

<design_process>
1. Analyze the user's request and identify key requirements. List these requirements explicitly.
2. List the main components of the TUI.
3. Determine the layout for these components.
4. Consider a simple color scheme and aesthetic elements.
5. List the necessary user inputs and how they should be handled.
6. Decide if a refresh loop is needed and how information should be updated.
7. Plan a clear exit mechanism.
8. Identify any input requirements needed to run the TUI (e.g., connection strings, file paths).
9. Brainstorm potential challenges or edge cases in the implementation.
10. Remember that all data must be properly labeled for the user (e.g. column headers in a table, etc.).
</design_process>

After your analysis, output your TUI design document using the following guidelines:

<guidelines>
1. Use bullet points as much as possible.
2. Ensure each point is clear and easy for a junior developer to implement.
3. Cover all the elements you considered in your design process.
4. Keep your design simple and avoid overcomplicating any aspect.
5. Output ONLY the design document, nothing more. NO title is needed.
</guidelines>

Here's an example of how your output should be structured (use your own content based on the user's request):

<example>
• Layout: Single-screen interface with header, main content area, and footer
• Components:
  - Header: Display title and current status
  - Main content: Show [specific information]
  - Footer: List available commands
• Color scheme: Use default terminal colors for simplicity
• User inputs:
  - 'q' to quit
  - 'r' to refresh data
• Refresh: Update main content every 5 seconds
• Exit: Press 'q' to exit the program
• Input requirements: Require [specific input] on startup
</example>

Remember, your design should satisfy the user's request while maintaining EXTREME simplicity and ease of implementation."""
# TODO: Make a better <example>


######
# MAIN
######


def design_tui(prompt: str, p_bar: Progress, config: Config) -> str:
    task = p_bar.add_task("design", total=PROGRESS_LIMIT)

    messages = [{"role": "user", "content": prompt}]
    output = call_llm(PROMPT.format(library=config.library), messages, stream=True)

    design = ""
    for token in output:
        design += token
        p_bar.update(task, advance=1)

    design = f"# Design Document\n\n<user_request>\n{prompt}\n</user_request>\n\n<details>\n{design}\n</details>"
    p_bar.update(task, completed=PROGRESS_LIMIT)

    return design
