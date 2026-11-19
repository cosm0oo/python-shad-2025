from abc import ABC, abstractmethod
import string
import typing as tp
from .base import TRow, TRowsGenerator


class Mapper(ABC):
    """Base class for mappers"""

    @abstractmethod
    def __call__(self, row: TRow) -> TRowsGenerator:
        pass


class DummyMapper(Mapper):
    """Yield exactly the row passed"""

    def __call__(self, row: TRow) -> TRowsGenerator:
        yield row


class FilterPunctuation(Mapper):
    """Remove punctuation from column"""

    def __init__(self, column: str) -> None:
        self._column = column

    def __call__(self, row: TRow) -> TRowsGenerator:
        result = row.copy()
        text = result[self._column]
        result[self._column] = text.translate(str.maketrans("", "", string.punctuation))
        yield result


class LowerCase(Mapper):
    """Convert column to lowercase"""

    def __init__(self, column: str) -> None:
        self._column = column

    def __call__(self, row: TRow) -> TRowsGenerator:
        result = row.copy()
        result[self._column] = result[self._column].lower()
        yield result


class Split(Mapper):
    """Split row into multiple rows by separator"""

    def __init__(self, column: str, separator: str | None = None) -> None:
        self._column = column
        self._separator = separator

    def __call__(self, row: TRow) -> TRowsGenerator:
        import re

        text = row[self._column]
        if self._separator is None:
            parts = re.split(r"\s+", text)
            for part in parts:
                yield {**row, self._column: part}
        else:
            start = 0
            sep_len = len(self._separator)
            while True:
                pos = text.find(self._separator, start)
                if pos == -1:
                    yield {**row, self._column: text[start:]}
                    break
                yield {**row, self._column: text[start:pos]}
                start = pos + sep_len


class Product(Mapper):
    """Calculate product of multiple columns"""

    def __init__(self, columns: tp.Sequence[str], result_column: str = "product") -> None:
        self._columns = columns
        self._result_column = result_column

    def __call__(self, row: TRow) -> TRowsGenerator:
        result = row.copy()
        product = 1
        for col in self._columns:
            product *= row[col]
        result[self._result_column] = product
        yield result


class Filter(Mapper):
    """Filter rows by condition"""

    def __init__(self, condition: tp.Callable[[TRow], bool]) -> None:
        self._condition = condition

    def __call__(self, row: TRow) -> TRowsGenerator:
        if self._condition(row):
            yield row


class Project(Mapper):
    """Keep only specified columns"""

    def __init__(self, columns: tp.Sequence[str]) -> None:
        self._columns = columns

    def __call__(self, row: TRow) -> TRowsGenerator:
        yield {col: row[col] for col in self._columns}
