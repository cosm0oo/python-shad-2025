import functools
from collections import OrderedDict
from collections.abc import Callable
from typing import Any, TypeVar

Function = TypeVar('Function', bound=Callable[..., Any])


def cache(max_size: int) -> Callable[[Function], Function]:
    """
    Returns decorator, which stores result of function
    for `max_size` most recent function arguments.
    :param max_size: max amount of unique arguments to store values for
    :return: decorator, which wraps any function passed
    """

    def decorator(func: Function) -> Function:
        cache_dict: OrderedDict[Any, Any] = OrderedDict()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, tuple(sorted(kwargs.items())))

            if key in cache_dict:
                cache_dict.move_to_end(key)
                return cache_dict[key]

            result = func(*args, **kwargs)
            cache_dict[key] = result

            if len(cache_dict) > max_size:
                cache_dict.popitem(last=False)

            return result

        return wrapper  # type: ignore

    return decorator  # type: ignore
