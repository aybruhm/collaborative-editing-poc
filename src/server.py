from copy import deepcopy
from dataclasses import dataclass, field

from src.types import Operation


def apply_operation(doc: str, op: Operation) -> str:
    if op.type == "insert":
        return doc[: op.position] + op.char + doc[op.position :]
    if op.type == "delete":
        return doc[: op.position] + doc[op.position + 1 :]
    raise ValueError(f"Unknown op type: {op.type}")


@dataclass
class OTServer:
    doc_id: str
    content: str
    history: list[Operation] = field(default_factory=list)

    def apply(self, op: Operation) -> str:
        """
        Transform the incoming op against all ops that arrived
        concurrently (i.e. ops the client hadn't seen yet),
        then apply it to the document.
        """
        concurrent_ops = [
            h
            for h in self.history
            if h.timestamp >= op.timestamp and h.origin != op.origin
        ]

        transformed_op = deepcopy(op)
        for concurrent in concurrent_ops:
            print(
                f"  [OT server]  Transforming {op.origin} op against {concurrent.origin} op "
                f"(pos {transformed_op.position} → ",
                end="",
            )
            transformed_op = transform(concurrent, transformed_op)
            print(f"{transformed_op.position})")

        old = self.content
        self.content = apply_operation(self.content, transformed_op)
        self.history.append(op)

        print(f"  [{op.origin:7}]  Applied    | '{old}' → '{self.content}'")
        return self.content


def transform(op1: Operation, op2: Operation) -> Operation:
    """
    Transform op2 against op1 so that op2 can be applied
    AFTER op1 and still produce the correct result.

    Only handles insert vs insert for clarity.
    A production OT implementation also handles delete vs insert,
    delete vs delete, and multi-character ops.
    """
    transformed = deepcopy(op2)

    if op1.type == "insert" and op2.type == "insert":
        if op1.position <= op2.position:
            # op1 inserted before (or at) op2's position — shift op2 right
            transformed.position += len(op1.char)

        # if op1 inserted after op2's position, no adjustment needed

    elif op1.type == "delete" and op2.type == "insert":
        if op1.position < op2.position:
            # op1 deleted a char before op2's position — shift op2 left
            transformed.position -= 1

    return transformed
