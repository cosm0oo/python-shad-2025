def find_value(nums: list[int] | range, value: int) -> bool:
    """
    Find value in sorted sequence
    :param nums: sequence of integers. Could be empty
    :param value: integer to find
    :return: True if value exists, False otherwise
    """
    left = -1
    right = len(nums)
    while left < right - 1:
        mid = (left + right) // 2
        if nums[mid] == value:
            return True
        elif nums[mid] > value:
            right = mid
        else:
            left = mid
    return False
