from dataclasses import dataclass
from typing import Literal


@dataclass
class Operation:
    type: Literal["insert", "delete"]
    position: int
    char: str
    timestamp: float
    origin: str  # "US" or "Sydney"

    def __repr__(self):
        return (
            f"Operation(type={self.type!r}, pos={self.position}, "
            f"char={self.char!r}, ts={self.timestamp}ms, origin={self.origin!r})"
        )
