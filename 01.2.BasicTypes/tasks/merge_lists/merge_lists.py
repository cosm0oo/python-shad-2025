def merge_iterative(lst_a: list[int], lst_b: list[int]) -> list[int]:
    """
    Merge two sorted lists in one sorted list
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: merged sorted list
    """
    i = j = 0
    merged_sorted_list = []
    while i < len(lst_a) and j < len(lst_b):
        if lst_a[i] <= lst_b[j]:
            merged_sorted_list.append(lst_a[i])
            i += 1
        else:
            merged_sorted_list.append(lst_b[j])
            j += 1
    merged_sorted_list.extend(lst_a[i:])
    merged_sorted_list.extend(lst_b[j:])
    return merged_sorted_list


def merge_sorted(lst_a: list[int], lst_b: list[int]) -> list[int]:
    """
    Merge two sorted lists in one sorted list using `sorted`
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: merged sorted list
    """
    return sorted(lst_a + lst_b)
