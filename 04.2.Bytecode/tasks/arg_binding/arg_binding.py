from types import FunctionType
from typing import Any

CO_VARARGS = 4
CO_VARKEYWORDS = 8

ERR_TOO_MANY_POS_ARGS = 'Too many positional arguments'
ERR_TOO_MANY_KW_ARGS = 'Too many keyword arguments'
ERR_MULT_VALUES_FOR_ARG = 'Multiple values for arguments'
ERR_MISSING_POS_ARGS = 'Missing positional arguments'
ERR_MISSING_KWONLY_ARGS = 'Missing keyword-only arguments'
ERR_POSONLY_PASSED_AS_KW = 'Positional-only argument passed as keyword argument'


def bind_args(func: FunctionType, *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Bind values from `args` and `kwargs` to corresponding arguments of `func`

    :param func: function to be inspected
    :param args: positional arguments to be bound
    :param kwargs: keyword arguments to be bound
    :return: `dict[argument_name] = argument_value` if binding was successful,
             raise TypeError with one of `ERR_*` error descriptions otherwise
    """
    code = func.__code__
    varnames = code.co_varnames
    argcount = code.co_argcount
    posonlyargcount = code.co_posonlyargcount
    kwonlyargcount = code.co_kwonlyargcount
    flags = code.co_flags

    has_varargs = bool(flags & CO_VARARGS)
    has_varkwargs = bool(flags & CO_VARKEYWORDS)

    all_pos_names = list(varnames[:argcount])
    posonly_names = set(varnames[:posonlyargcount])

    idx = argcount
    kwonly_names = list(varnames[idx:idx + kwonlyargcount])
    idx += kwonlyargcount

    varargs_name = None
    if has_varargs:
        varargs_name = varnames[idx]
        idx += 1

    varkwargs_name = None
    if has_varkwargs:
        varkwargs_name = varnames[idx]

    defaults = func.__defaults__ or ()
    kwdefaults = func.__kwdefaults__ or {}

    result: dict[str, Any] = {}
    kwargs_used = set()

    for i, name in enumerate(all_pos_names):
        if i < len(args):
            result[name] = args[i]
            if name in kwargs:
                if name in posonly_names:
                    if not has_varkwargs:
                        raise TypeError(ERR_POSONLY_PASSED_AS_KW)
                else:
                    raise TypeError(ERR_MULT_VALUES_FOR_ARG)
        elif name in kwargs and name not in posonly_names:
            result[name] = kwargs[name]
            kwargs_used.add(name)

    if len(args) > argcount and not has_varargs:
        raise TypeError(ERR_TOO_MANY_POS_ARGS)

    for name in posonly_names:
        if name in kwargs and not has_varkwargs:
            raise TypeError(ERR_POSONLY_PASSED_AS_KW)

    defaults_offset = argcount - len(defaults)
    for i, name in enumerate(all_pos_names):
        if name not in result:
            default_idx = i - defaults_offset
            if default_idx >= 0:
                result[name] = defaults[default_idx]

    for name in all_pos_names:
        if name not in result:
            raise TypeError(ERR_MISSING_POS_ARGS)

    for name in kwonly_names:
        if name in kwargs:
            result[name] = kwargs[name]
            kwargs_used.add(name)
        elif name in kwdefaults:
            result[name] = kwdefaults[name]
        else:
            raise TypeError(ERR_MISSING_KWONLY_ARGS)

    extra_kwargs = {}
    for k, v in kwargs.items():
        if k not in kwargs_used:
            extra_kwargs[k] = v

    if extra_kwargs and not has_varkwargs:
        raise TypeError(ERR_TOO_MANY_KW_ARGS)

    if has_varargs:
        result[varargs_name] = args[argcount:]  # type: ignore

    if has_varkwargs:
        result[varkwargs_name] = extra_kwargs  # type: ignore

    return result
