import typing as tp

T = tp.TypeVar("T", int, float)
Number = int | float


class Pair(tp.Generic[T]):
    def __init__(self, a: T, b: T) -> None:
        self._a: Number = a
        self._b: Number = b

    def sum(self) -> Number:
        return self._a + self._b

    def first(self) -> Number:
        return self._a

    def second(self) -> Number:
        return self._b

    def __iadd__(self, pair: "Pair[T]") -> "Pair[T]":
        self._a += pair._a
        self._b += pair._b
        return self
