import typing as tp
from itertools import groupby
from .base import Operation, TRowsIterable, TRowsGenerator, TRow
from .mappers import Mapper
from .reducers import Reducer
from .joiners import Joiner


class Map(Operation):
    """Apply mapper to each row"""

    def __init__(self, mapper: Mapper) -> None:
        self._mapper = mapper

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        for row in rows:
            yield from self._mapper(row)


class Reduce(Operation):
    """Apply reducer to grouped rows"""

    def __init__(self, reducer: Reducer, keys: tp.Sequence[str]) -> None:
        self._reducer = reducer
        self._keys = tuple(keys)

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        def key_func(row: TRow) -> tuple[tp.Any, ...]:
            return tuple(row[key] for key in self._keys)

        for key, group in groupby(rows, key=key_func):
            yield from self._reducer(self._keys, group)


class Join(Operation):
    """Join two streams of rows"""

    def __init__(self, joiner: Joiner, keys: tp.Sequence[str]) -> None:
        self._keys = keys
        self._joiner = joiner

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        if not args:
            return

        if not self._keys:
            yield from self._joiner(self._keys, rows, args[0])
            return

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
