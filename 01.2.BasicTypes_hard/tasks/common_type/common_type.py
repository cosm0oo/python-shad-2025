def get_common_type(type1: type, type2: type) -> type:
    """
    Calculate common type according to rule, that it must have the most adequate interpretation after conversion.
    Look in tests for adequacy calibration.
    :param type1: one of [bool, int, float, complex, list, range, tuple, str] types
    :param type2: one of [bool, int, float, complex, list, range, tuple, str] types
    :return: the most concrete common type, which can be used to convert both input values
    """
    rules = {
        (bool, int): int,
        (bool, float): float,
        (bool, complex): complex,
        (int, float): float,
        (int, complex): complex,
        (float, complex): complex,
        (range, tuple): tuple,
        (range, list): list,
        (tuple, list): list,
        (range, range): tuple,
        (list, int): str,
    }
    if (type1, type2) in rules:
        return rules[(type1, type2)]
    if (type2, type1) in rules:
        return rules[(type2, type1)]
    if type1 == type2:
        return type1
    return str
