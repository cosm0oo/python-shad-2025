import sys
import math
from typing import Any

PROMPT = '>>> '


def run_calc(context: dict[str, Any] | None = None) -> None:
    """Run interactive calculator session in specified namespace"""
    if context is None:
        context = {}

    namespace = {'__builtins__': {}}
    namespace.update(context)

    while True:
        sys.stdout.write(PROMPT)
        sys.stdout.flush()
        line = sys.stdin.readline()

        if line == '':
            print()
            break

        result = eval(line, namespace)
        print(result)


if __name__ == '__main__':
    context = {'math': math}
    run_calc(context)
