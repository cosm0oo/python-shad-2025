import heapq
from collections import defaultdict


def normalize(
        text: str
        ) -> str:
    """
    Removes punctuation and digits and convert to lower case
    :param text: text to normalize
    :return: normalized query
    """
    return ''.join(char if char.isalpha() or char.isspace() else '' for char in text.lower())


def get_words(
        query: str
        ) -> list[str]:
    """
    Split by words and leave only words with letters greater than 3
    :param query: query to split
    :return: filtered and split query by words
    """
    return [word for word in query.split() if len(word) > 3]


def build_index(
        banners: list[str]
        ) -> dict[str, list[int]]:
    """
    Create index from words to banners ids with preserving order and without repetitions
    :param banners: list of banners for indexation
    :return: mapping from word to banners ids
    """
    index: dict[str, list[int]] = defaultdict(list)

    for banner_id, banner in enumerate(banners):
        normalized = normalize(banner)
        words = get_words(normalized)
        seen = set()
        for word in words:
            if word not in seen:
                index[word].append(banner_id)
                seen.add(word)

    return dict(index)


def get_banner_indices_by_query(
        query: str,
        index: dict[str, list[int]]
        ) -> list[int]:
    """
    Extract banners indices from index, if all words from query contains in indexed banner
    :param query: query to find banners
    :param index: index to search banners
    :return: list of indices of suitable banners
    """
    normalized = normalize(query)
    words = get_words(normalized)

    if not words:
        return []

    lists = []
    for word in words:
        if word not in index:
            return []
        lists.append(index[word])

    if len(lists) == 1:
        return lists[0]

    heap: list[tuple[int, int, int]] = []
    for list_idx, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], list_idx, 0))

    result = []
    count = 1
    prev_value = None

    while heap:
        value, list_idx, elem_idx = heapq.heappop(heap)

        if value == prev_value:
            count += 1
        else:
            count = 1
            prev_value = value

        if count == len(lists):
            result.append(value)

        next_idx = elem_idx + 1
        if next_idx < len(lists[list_idx]):
            heapq.heappush(heap, (lists[list_idx][next_idx], list_idx, next_idx))

    return result


#########################
# Don't change this code
#########################

def get_banners(
        query: str,
        index: dict[str, list[int]],
        banners: list[str]
        ) -> list[str]:
    """
    Extract banners matched to queries
    :param query: query to match
    :param index: word-banner_ids index
    :param banners: list of banners
    :return: list of matched banners
    """
    indices = get_banner_indices_by_query(query, index)
    return [banners[i] for i in indices]

#########################
