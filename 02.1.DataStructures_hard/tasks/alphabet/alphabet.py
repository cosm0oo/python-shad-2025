import enum


class Status(enum.Enum):
    NEW = 0
    EXTRACTED = 1
    FINISHED = 2


def extract_alphabet(
        graph: dict[str, set[str]]
        ) -> list[str]:
    """
    Extract alphabet from graph
    :param graph: graph with partial order
    :return: alphabet
    """
    result = []
    status: dict[str, Status] = {node: Status.NEW for node in graph}

    for node in graph:
        if status[node] == Status.NEW:
            stack = [(node, False)]
            while stack:
                current, processed = stack.pop()
                if processed:
                    result.append(current)
                    status[current] = Status.FINISHED
                else:
                    if status[current] == Status.NEW:
                        status[current] = Status.EXTRACTED
                        stack.append((current, True))
                        for neighbour in graph[current]:
                            if status[neighbour] == Status.NEW:
                                stack.append((neighbour, False))

    return result[::-1]


def build_graph(
        words: list[str]
        ) -> dict[str, set[str]]:
    """
    Build graph from ordered words. Graph should contain all letters from words
    :param words: ordered words
    :return: graph
    """
    graph: dict[str, set[str]] = {}

    for word in words:
        for char in word:
            if char not in graph:
                graph[char] = set()

    for i in range(len(words) - 1):
        word1, word2 = words[i], words[i + 1]
        for char1, char2 in zip(word1, word2):
            if char1 != char2:
                graph[char1].add(char2)
                break

    return graph


#########################
# Don't change this code
#########################

def get_alphabet(
        words: list[str]
        ) -> list[str]:
    """
    Extract alphabet from sorted words
    :param words: sorted words
    :return: alphabet
    """
    graph = build_graph(words)
    return extract_alphabet(graph)

#########################
