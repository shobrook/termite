try:
    from termite.shared.run_tui import run_tui
    from termite.shared.call_llm import call_llm, MAX_TOKENS
except ImportError:
    from shared.run_tui import run_tui
    from shared.call_llm import call_llm, MAX_TOKENS
