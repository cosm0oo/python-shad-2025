from abc import abstractmethod, ABC
import typing as tp
from itertools import groupby
import heapq
import string
import re

TRow = dict[str, tp.Any]
TRowsIterable = tp.Iterable[TRow]
TRowsGenerator = tp.Generator[TRow, None, None]


class Operation(ABC):
    @abstractmethod
    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        pass


class Read(Operation):
    def __init__(self, filename: str, parser: tp.Callable[[str], TRow]) -> None:
        self._filename = filename
        self._parser = parser

    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        with open(self._filename) as f:
            for line in f:
                yield self._parser(line)


class ReadIterFactory(Operation):
    def __init__(self, name: str) -> None:
        self._name = name

    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        for row in kwargs[self._name]():
            yield row


# Operations


class Mapper(ABC):
    """Base class for mappers"""

    @abstractmethod
    def __call__(self, row: TRow) -> TRowsGenerator:
        """
        :param row: one table row
        """
        pass


class Map(Operation):
    def __init__(self, mapper: Mapper) -> None:
        self._mapper = mapper

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        for row in rows:
            yield from self._mapper(row)


class Reducer(ABC):
    """Base class for reducers"""

    @abstractmethod
    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        """
        :param rows: table rows
        """
        pass


class Reduce(Operation):
    def __init__(self, reducer: Reducer, keys: tp.Sequence[str]) -> None:
        self._reducer = reducer
        self._keys = keys

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        for group_key_value, group_rows in groupby(rows, lambda row: tuple(row[key] for key in self._keys)):
            yield from self._reducer(tuple(self._keys), group_rows)


class Joiner(ABC):
    """Base class for joiners"""

    def __init__(self, suffix_a: str = "_1", suffix_b: str = "_2") -> None:
        self._a_suffix = suffix_a
        self._b_suffix = suffix_b

    @abstractmethod
    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        """
        :param keys: join keys
        :param rows_a: left table rows
        :param rows_b: right table rows
        """
        pass


class Join(Operation):
    def __init__(self, joiner: Joiner, keys: tp.Sequence[str]):
        self._keys = keys
        self._joiner = joiner

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        def key_func(row: TRow) -> tuple[tp.Any, ...]:
            return tuple(row[key] for key in self._keys)

        rows_a_grouped = groupby(rows, key_func)
        rows_b_grouped = groupby(args[0], key_func)

        iter_a = iter(rows_a_grouped)
        iter_b = iter(rows_b_grouped)

        try:
            key_a, group_a = next(iter_a)
        except StopIteration:
            key_a, group_a = None, iter([])

        try:
            key_b, group_b = next(iter_b)
        except StopIteration:
            key_b, group_b = None, iter([])

        while key_a is not None or key_b is not None:
            if key_a is None:
                yield from self._joiner(self._keys, iter([]), group_b)
                try:
                    key_b, group_b = next(iter_b)
                except StopIteration:
                    key_b = None
            elif key_b is None:
                yield from self._joiner(self._keys, group_a, iter([]))
                try:
                    key_a, group_a = next(iter_a)
                except StopIteration:
                    key_a = None
            elif key_a == key_b:
                yield from self._joiner(self._keys, group_a, group_b)
                try:
                    key_a, group_a = next(iter_a)
                except StopIteration:
                    key_a = None
                try:
                    key_b, group_b = next(iter_b)
                except StopIteration:
                    key_b = None
            elif key_a < key_b:
                yield from self._joiner(self._keys, group_a, iter([]))
                try:
                    key_a, group_a = next(iter_a)
                except StopIteration:
                    key_a = None
            else:
                yield from self._joiner(self._keys, iter([]), group_b)
                try:
                    key_b, group_b = next(iter_b)
                except StopIteration:
                    key_b = None


# Dummy operators


class DummyMapper(Mapper):
    """Yield exactly the row passed"""

    def __call__(self, row: TRow) -> TRowsGenerator:
        yield row


class FirstReducer(Reducer):
    """Yield only first row from passed ones"""

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        for row in rows:
            yield row
            break


# Mappers


class FilterPunctuation(Mapper):
    """Left only non-punctuation symbols"""

    def __init__(self, column: str):
        """
        :param column: name of column to process
        """
        self._column = column

    def __call__(self, row: TRow) -> TRowsGenerator:
        new_row = row.copy()
        new_row[self._column] = "".join(c for c in row[self._column] if c not in string.punctuation)
        yield new_row


class LowerCase(Mapper):
    """Replace column value with value in lower case"""

    def __init__(self, column: str):
        """
        :param column: name of column to process
        """
        self._column = column

    def __call__(self, row: TRow) -> TRowsGenerator:
        new_row = row.copy()
        new_row[self._column] = row[self._column].lower()
        yield new_row


class Split(Mapper):
    """Split row on multiple rows by separator"""

    def __init__(self, column: str, separator: str | None = None) -> None:
        """
        :param column: name of column to split
        :param separator: string to separate by
        """
        self._column = column
        self._separator = separator

    def __call__(self, row: TRow) -> TRowsGenerator:
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
    """Calculates product of multiple columns"""

    def __init__(self, columns: tp.Sequence[str], result_column: str = "product") -> None:
        """
        :param columns: column names to product
        :param result_column: column name to save product in
        """
        self._columns = columns
        self._result_column = result_column

    def __call__(self, row: TRow) -> TRowsGenerator:
        new_row = row.copy()
        result = 1
        for col in self._columns:
            result *= row[col]
        new_row[self._result_column] = result
        yield new_row


class Filter(Mapper):
    """Remove records that don't satisfy some condition"""

    def __init__(self, condition: tp.Callable[[TRow], bool]) -> None:
        """
        :param condition: if condition is not true - remove record
        """
        self._condition = condition

    def __call__(self, row: TRow) -> TRowsGenerator:
        if self._condition(row):
            yield row


class Project(Mapper):
    """Leave only mentioned columns"""

    def __init__(self, columns: tp.Sequence[str]) -> None:
        """
        :param columns: names of columns
        """
        self._columns = columns

    def __call__(self, row: TRow) -> TRowsGenerator:
        yield {col: row[col] for col in self._columns}


# Reducers


class TopN(Reducer):
    """Calculate top N by value"""

    def __init__(self, column: str, n: int) -> None:
        """
        :param column: column name to get top by
        :param n: number of top values to extract
        """
        self._column_max = column
        self._n = n

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        heap: list[tuple[tp.Any, int, TRow]] = []
        for idx, row in enumerate(rows):
            if len(heap) < self._n:
                heapq.heappush(heap, (row[self._column_max], idx, row))
            else:
                heapq.heappushpop(heap, (row[self._column_max], idx, row))
        for _, _, row in sorted(heap, reverse=True):
            yield row


class TermFrequency(Reducer):
    """Calculate frequency of values in column"""

    def __init__(self, words_column: str, result_column: str = "tf") -> None:
        """
        :param words_column: name for column with words
        :param result_column: name for result column
        """
        self._words_column = words_column
        self._result_column = result_column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        freq_map: dict[tp.Any, int] = {}
        group_key_values: dict[str, tp.Any] = {}
        total = 0
        for row in rows:
            if not group_key_values:
                group_key_values = {key: row[key] for key in group_key}
            word = row[self._words_column]
            freq_map[word] = freq_map.get(word, 0) + 1
            total += 1
        for word, count in freq_map.items():
            result_row = group_key_values.copy()
            result_row[self._words_column] = word
            result_row[self._result_column] = count / total
            yield result_row


class Count(Reducer):
    """
    Count records by key
    Example for group_key=('a',) and column='d'
        {'a': 1, 'b': 5, 'c': 2}
        {'a': 1, 'b': 6, 'c': 1}
        =>
        {'a': 1, 'd': 2}
    """

    def __init__(self, column: str) -> None:
        """
        :param column: name for result column
        """
        self._column = column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        count = 0
        group_key_values: dict[str, tp.Any] = {}
        for row in rows:
            if not group_key_values:
                group_key_values = {key: row[key] for key in group_key}
            count += 1
        if count > 0:
            result_row = group_key_values.copy()
            result_row[self._column] = count
            yield result_row


class Sum(Reducer):
    """
    Sum values aggregated by key
    Example for key=('a',) and column='b'
        {'a': 1, 'b': 2, 'c': 4}
        {'a': 1, 'b': 3, 'c': 5}
        =>
        {'a': 1, 'b': 5}
    """

    def __init__(self, column: str) -> None:
        """
        :param column: name for sum column
        """
        self._column = column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        total = 0
        group_key_values: dict[str, tp.Any] = {}
        for row in rows:
            if not group_key_values:
                group_key_values = {key: row[key] for key in group_key}
            total += row[self._column]
        if group_key_values:
            result_row = group_key_values.copy()
            result_row[self._column] = total
            yield result_row


# Joiners


class InnerJoiner(Joiner):
    """Join with inner strategy"""

    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        list_b = list(rows_b)
        if not list_b:
            return

        keys_set = set(keys)
        cols_b_set = set(list_b[0].keys())

        cols_a_unique: tuple[str, ...] = ()
        cols_b_unique: tuple[str, ...] = ()
        cols_conflicting: tuple[str, ...] = ()
        initialized = False

        for row_a in rows_a:
            if not initialized:
                cols_a_set = set(row_a.keys())
                cols_a_unique = tuple(col for col in row_a.keys() if col not in keys_set and col not in cols_b_set)
                cols_b_unique = tuple(col for col in list_b[0].keys() if col not in keys_set and col not in cols_a_set)
                cols_conflicting = tuple(col for col in row_a.keys() if col not in keys_set and col in cols_b_set)
                initialized = True

            for row_b in list_b:
                result_row = {key: row_a[key] for key in keys}
                for col in cols_a_unique:
                    result_row[col] = row_a[col]
                for col in cols_b_unique:
                    result_row[col] = row_b[col]
                for col in cols_conflicting:
                    result_row[col + self._a_suffix] = row_a[col]
                    result_row[col + self._b_suffix] = row_b[col]
                yield result_row


class OuterJoiner(Joiner):
    """Join with outer strategy"""

    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        list_a = list(rows_a)
        list_b = list(rows_b)

        if list_a and list_b:
            keys_set = set(keys)
            cols_a_set = set(list_a[0].keys())
            cols_b_set = set(list_b[0].keys())

            cols_a_unique = tuple(col for col in list_a[0].keys() if col not in keys_set and col not in cols_b_set)
            cols_b_unique = tuple(col for col in list_b[0].keys() if col not in keys_set and col not in cols_a_set)
            cols_conflicting = tuple(col for col in list_a[0].keys() if col not in keys_set and col in cols_b_set)

            for row_a in list_a:
                for row_b in list_b:
                    result_row = {key: row_a[key] for key in keys}
                    for col in cols_a_unique:
                        result_row[col] = row_a[col]
                    for col in cols_b_unique:
                        result_row[col] = row_b[col]
                    for col in cols_conflicting:
                        result_row[col + self._a_suffix] = row_a[col]
                        result_row[col + self._b_suffix] = row_b[col]
                    yield result_row
        elif list_a:
            for row_a in list_a:
                yield dict(row_a)
        elif list_b:
            for row_b in list_b:
                yield dict(row_b)


class LeftJoiner(Joiner):
    """Join with left strategy"""

    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        list_b = list(rows_b)

        if list_b:
            keys_set = set(keys)
            cols_b_set = set(list_b[0].keys())

            cols_a_unique: tuple[str, ...] = ()
            cols_b_unique: tuple[str, ...] = ()
            cols_conflicting: tuple[str, ...] = ()
            initialized = False

            for row_a in rows_a:
                if not initialized:
                    cols_a_set = set(row_a.keys())
                    cols_a_unique = tuple(col for col in row_a.keys() if col not in keys_set and col not in cols_b_set)
                    cols_b_unique = tuple(
                        col for col in list_b[0].keys() if col not in keys_set and col not in cols_a_set
                    )
                    cols_conflicting = tuple(col for col in row_a.keys() if col not in keys_set and col in cols_b_set)
                    initialized = True

                for row_b in list_b:
                    result_row = {key: row_a[key] for key in keys}
                    for col in cols_a_unique:
                        result_row[col] = row_a[col]
                    for col in cols_b_unique:
                        result_row[col] = row_b[col]
                    for col in cols_conflicting:
                        result_row[col + self._a_suffix] = row_a[col]
                        result_row[col + self._b_suffix] = row_b[col]
                    yield result_row
        else:
            for row_a in rows_a:
                yield dict(row_a)


class RightJoiner(Joiner):
    """Join with right strategy"""

    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        list_a = list(rows_a)

        if list_a:
            keys_set = set(keys)
            cols_a_set = set(list_a[0].keys())

            cols_a_unique: tuple[str, ...] = ()
            cols_b_unique: tuple[str, ...] = ()
            cols_conflicting: tuple[str, ...] = ()
            initialized = False

            for row_b in rows_b:
                if not initialized:
                    cols_b_set = set(row_b.keys())
                    cols_a_unique = tuple(
                        col for col in list_a[0].keys() if col not in keys_set and col not in cols_b_set
                    )
                    cols_b_unique = tuple(col for col in row_b.keys() if col not in keys_set and col not in cols_a_set)
                    cols_conflicting = tuple(
                        col for col in list_a[0].keys() if col not in keys_set and col in cols_b_set
                    )
                    initialized = True

                for row_a in list_a:
                    result_row = {key: row_a[key] for key in keys}
                    for col in cols_a_unique:
                        result_row[col] = row_a[col]
                    for col in cols_b_unique:
                        result_row[col] = row_b[col]
                    for col in cols_conflicting:
                        result_row[col + self._a_suffix] = row_a[col]
                        result_row[col + self._b_suffix] = row_b[col]
                    yield result_row
        else:
            for row_b in rows_b:
                yield dict(row_b)
