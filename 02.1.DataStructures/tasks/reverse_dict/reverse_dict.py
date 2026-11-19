import typing as tp


def revert(dct: tp.Mapping[str, str]) -> dict[str, list[str]]:
    """
    :param dct: dictionary to revert in format {key: value}
    :return: reverted dictionary {value: [key1, key2, key3]}
    """
    result = {}
    for key, value in dct.items():
        if value not in result:
            result[value] = []
        result[value].append(key)
    return result
