import typing as tp


def convert_to_common_type(data: list[tp.Any]) -> list[tp.Any]:
    """
    Takes list of multiple types' elements and convert each element to common type according to given rules
    :param data: list of multiple types' elements
    :return: list with elements converted to common type
    """
    def is_empty(value: tp.Any) -> bool:
        return value is None or value == ""

    def get_value_type(value: tp.Any) -> type | None:
        if is_empty(value):
            return None
        return list if isinstance(value, (list, tuple)) else type(value)

    def get_common_type(types: set[type]) -> tp.Type[list | float | int | bool | str]:
        if not types:
            return str

        if bool in types and int in types:
            int_values = [value for value in data if not is_empty(value) and isinstance(value, int)]
            if all(v in (0, 1) for v in int_values):
                return bool

        if list in types:
            return list
        if float in types:
            return float
        if int in types:
            return int
        if bool in types:
            return bool
        return str

    converters = {
        list: lambda x: list(x) if isinstance(x, (list, tuple)) else [x] if not is_empty(x) else [],
        float: lambda x: float(x) if not is_empty(x) else 0.0,
        int: lambda x: int(x) if not is_empty(x) else 0,
        bool: lambda x: bool(x) if not is_empty(x) else False,
        str: lambda x: str(x) if x is not None and x != "" else "",
    }

    all_types = [get_value_type(value) for value in data]
    non_empty_types = {t for t in all_types if t is not None}
    common_type = get_common_type(non_empty_types)

    return [converters[common_type](value) for value in data]
