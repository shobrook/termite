try:
    from termite.shared.utils.fix_imports import fix_any_import_errors
    from termite.shared.utils.python_exe import get_python_executable
except ImportError:
    from shared.utils.fix_imports import fix_any_import_errors
    from shared.utils.python_exe import get_python_executable
