# Standard library
from dataclasses import dataclass


@dataclass
class Config:
    library: str = "urwid"
    should_refine: bool = False
    refine_iters: int = 1
    fix_iters: int = 10
