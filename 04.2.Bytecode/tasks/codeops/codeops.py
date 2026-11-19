import dis
import types
from collections import defaultdict


def count_operations(source_code: types.CodeType) -> dict[str, int]:
    """Count byte code operations in given source code.

    :param source_code: the bytecode operation names to be extracted from
    :return: operation counts
    """
    counts: dict[str, int] = defaultdict(int)

    for instruction in dis.get_instructions(source_code):
        counts[instruction.opname] += 1

        if isinstance(instruction.argval, types.CodeType):
            nested_counts = count_operations(instruction.argval)
            for opname, count in nested_counts.items():
                counts[opname] += count

    return dict(counts)
