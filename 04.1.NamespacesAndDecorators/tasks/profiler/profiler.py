import functools
from datetime import datetime


def profiler(func):  # type: ignore
    """
    Returns profiling decorator, which counts calls of function
    and measure last function execution time.
    Results are stored as function attributes: `calls`, `last_time_taken`
    :param func: function to decorate
    :return: decorator, which wraps any function passed
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore
        wrapper._depth = getattr(wrapper, '_depth', 0)

        if wrapper._depth == 0:
            wrapper.calls = 0
            start_time = datetime.now()

        wrapper._depth += 1
        wrapper.calls += 1

        result = func(*args, **kwargs)

        wrapper._depth -= 1
        if wrapper._depth == 0:
            wrapper.last_time_taken = (datetime.now() - start_time).total_seconds()

        return result

    return wrapper
