import string


def caesar_encrypt(message: str, n: int) -> str:
    """Encrypt message using caesar cipher

    :param message: message to encrypt
    :param n: shift
    :return: encrypted message
    """
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase

    n %= 26
    shifted_lower = lower[n:] + lower[:n]
    shifted_upper = upper[n:] + upper[:n]

    trans_table = str.maketrans(lower + upper, shifted_lower + shifted_upper)

    return message.translate(trans_table)
