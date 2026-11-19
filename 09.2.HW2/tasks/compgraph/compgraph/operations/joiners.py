from abc import ABC, abstractmethod
import typing as tp
from .base import TRowsIterable, TRowsGenerator


class Joiner(ABC):
    """Base class for joiners"""

    def __init__(self, suffix_a: str = "_1", suffix_b: str = "_2") -> None:
        self._a_suffix = suffix_a
        self._b_suffix = suffix_b

    @abstractmethod
    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        pass


class InnerJoiner(Joiner):
    """Inner join strategy"""

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
                if not keys or all(row_a.get(key) == row_b.get(key) for key in keys):
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
    """Full outer join strategy"""

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

            if not keys:
                for row_a in list_a:
                    for row_b in list_b:
                        result_row = {}
                        for col in cols_a_unique:
                            result_row[col] = row_a[col]
                        for col in cols_b_unique:
                            result_row[col] = row_b[col]
                        for col in cols_conflicting:
                            result_row[col + self._a_suffix] = row_a[col]
                            result_row[col + self._b_suffix] = row_b[col]
                        yield result_row
            else:
                matched_a = set()
                matched_b = set()

                for i, row_a in enumerate(list_a):
                    for j, row_b in enumerate(list_b):
                        if all(row_a.get(key) == row_b.get(key) for key in keys):
                            matched_a.add(i)
                            matched_b.add(j)
                            result_row = {key: row_a[key] for key in keys}
                            for col in cols_a_unique:
                                result_row[col] = row_a[col]
                            for col in cols_b_unique:
                                result_row[col] = row_b[col]
                            for col in cols_conflicting:
                                result_row[col + self._a_suffix] = row_a[col]
                                result_row[col + self._b_suffix] = row_b[col]
                            yield result_row

                for i, row_a in enumerate(list_a):
                    if i not in matched_a:
                        yield dict(row_a)

                for j, row_b in enumerate(list_b):
                    if j not in matched_b:
                        yield dict(row_b)
        elif list_a:
            for row_a in list_a:
                yield dict(row_a)
        elif list_b:
            for row_b in list_b:
                yield dict(row_b)


class LeftJoiner(Joiner):
    """Left join strategy"""

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

                matched = False
                for row_b in list_b:
                    if all(row_a.get(key) == row_b.get(key) for key in keys):
                        matched = True
                        result_row = {key: row_a[key] for key in keys}
                        for col in cols_a_unique:
                            result_row[col] = row_a[col]
                        for col in cols_b_unique:
                            result_row[col] = row_b[col]
                        for col in cols_conflicting:
                            result_row[col + self._a_suffix] = row_a[col]
                            result_row[col + self._b_suffix] = row_b[col]
                        yield result_row

                if not matched:
                    yield dict(row_a)
        else:
            for row_a in rows_a:
                yield dict(row_a)


class RightJoiner(Joiner):
    """Right join strategy"""

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

                matched = False
                for row_a in list_a:
                    if all(row_a.get(key) == row_b.get(key) for key in keys):
                        matched = True
                        result_row = {key: row_a[key] for key in keys}
                        for col in cols_a_unique:
                            result_row[col] = row_a[col]
                        for col in cols_b_unique:
                            result_row[col] = row_b[col]
                        for col in cols_conflicting:
                            result_row[col + self._a_suffix] = row_a[col]
                            result_row[col + self._b_suffix] = row_b[col]
                        yield result_row

                if not matched:
                    yield dict(row_b)
        else:
            for row_b in rows_b:
                yield dict(row_b)
