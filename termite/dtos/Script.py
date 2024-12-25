# Standard library
from typing import Optional
from dataclasses import dataclass


@dataclass
class Script:
    code: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    # snapshot: Optional[str] = None
    reflection: Optional[str] = None
