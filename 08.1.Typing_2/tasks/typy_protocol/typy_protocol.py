import typing as tp
from typing import Protocol


T = tp.TypeVar("T", covariant=True)


class Gettable(Protocol[T]):
    def __getitem__(self, item: int) -> T: ...

    def __len__(self) -> int: ...


def get(container: Gettable[T], index: int) -> T:
    return container[index]
