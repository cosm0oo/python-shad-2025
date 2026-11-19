from abc import ABC, abstractmethod
import typing as tp
from collections import Counter
import heapq
from .base import TRow, TRowsIterable, TRowsGenerator


class Reducer(ABC):
    """Base class for reducers"""

    @abstractmethod
    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        pass


class FirstReducer(Reducer):
    """Yield only first row"""

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        for row in rows:
            yield row
            break


class TopN(Reducer):
    """Get top N rows by column value"""

    def __init__(self, column: str, n: int) -> None:
        self._column = column
        self._n = n

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        heap: list[tuple[tp.Any, int, TRow]] = []
        for idx, row in enumerate(rows):
            if len(heap) < self._n:
                heapq.heappush(heap, (row[self._column], idx, row))
            else:
                heapq.heappushpop(heap, (row[self._column], idx, row))
        for _, _, row in sorted(heap, reverse=True):
            yield row


class TermFrequency(Reducer):
    """Calculate term frequency for each word"""

    def __init__(self, words_column: str, result_column: str = "tf") -> None:
        self._words_column = words_column
        self._result_column = result_column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        word_counts: Counter[tp.Any] = Counter()
        group_key_values: dict[str, tp.Any] = {}

        for row in rows:
            if not group_key_values:
                group_key_values = {key: row[key] for key in group_key}
            word_counts[row[self._words_column]] += 1

        if word_counts:
            total = sum(word_counts.values())
            for word, count in word_counts.items():
                result = group_key_values.copy()
                result[self._words_column] = word
                result[self._result_column] = count / total
                yield result


class Count(Reducer):
    """Count rows by group key"""

    def __init__(self, column: str) -> None:
        self._column = column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        count = 0
        group_key_values: dict[str, tp.Any] = {}
        for row in rows:
            if not group_key_values:
                group_key_values = {key: row[key] for key in group_key}
            count += 1
        if count > 0:
            result_row = group_key_values.copy() if group_key_values else {}
            result_row[self._column] = count
            yield result_row


class Sum(Reducer):
    """Sum column values by group key"""

    def __init__(self, column: str) -> None:
        self._column = column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        total = 0
        group_key_values: dict[str, tp.Any] = {}
        has_rows = False
        for row in rows:
            has_rows = True
            if not group_key_values:
                group_key_values = {key: row[key] for key in group_key}
            total += row[self._column]
        if has_rows:
            result_row = group_key_values.copy()
            result_row[self._column] = total
            yield result_row
