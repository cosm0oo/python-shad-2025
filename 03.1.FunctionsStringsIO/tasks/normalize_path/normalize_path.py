def normalize_path(path: str) -> str:
    """
    :param path: unix path to normalize
    :return: normalized path
    """
    is_absolute = path.startswith('/')
    parts = path.split('/')
    stack = []

    for part in parts:
        if part == '' or part == '.':
            continue
        elif part == '..':
            if stack and stack[-1] != '..':
                stack.pop()
            elif not is_absolute:
                stack.append('..')
        else:
            stack.append(part)

    result = '/'.join(stack)

    if is_absolute:
        return '/' + result

    return result if result else '.'
