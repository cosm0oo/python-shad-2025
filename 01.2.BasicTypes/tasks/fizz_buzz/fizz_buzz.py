def get_fizz_buzz(n: int) -> list[int | str]:
    """
    If value divided by 3 - "Fizz",
       value divided by 5 - "Buzz",
       value divided by 15 - "FizzBuzz",
    else - value.
    :param n: size of sequence
    :return: list of values.
    """
    res_list = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            res_list.append("FizzBuzz")
        elif i % 3 == 0:
            res_list.append("Fizz")
        elif i % 5 == 0:
            res_list.append("Buzz")
        else:
            res_list.append(i)
    return res_list
