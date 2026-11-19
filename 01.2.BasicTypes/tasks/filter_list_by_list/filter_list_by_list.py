def filter_list_by_list(lst_a: list[int] | range, lst_b: list[int] | range) -> list[int]:
    """
    Filter first sorted list by other sorted list
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: filtered sorted list
    """
    i = j = 0
    filtered_sorted_list = []
    while i < len(lst_a) and j < len(lst_b):
        if lst_a[i] < lst_b[j]:
            filtered_sorted_list.append(lst_a[i])
            i += 1
        elif lst_a[i] > lst_b[j]:
            j +=1
        else:
            i += 1
    filtered_sorted_list.extend(lst_a[i:])
    return filtered_sorted_list
