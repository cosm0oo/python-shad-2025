from dataclasses import dataclass, field, InitVar
from abc import ABC, abstractmethod

DISCOUNT_PERCENTS = 15


@dataclass(frozen=True, order=True)
class Item:
    item_id: int = field(compare=False)
    title: str
    cost: int

    def __post_init__(self):
        assert self.title != ""
        assert self.cost > 0


# You may set `# type: ignore` on this class
# It is [a really old issue](https://github.com/python/mypy/issues/5374)
# But seems to be solved
@dataclass
class Position(ABC):
    item: Item

    @property
    @abstractmethod
    def cost(self) -> float:
        ...


@dataclass
class CountedPosition(Position):
    count: int = 1

    @property
    def cost(self) -> float:
        return self.item.cost * self.count


@dataclass
class WeightedPosition(Position):
    weight: float = 1.0

    @property
    def cost(self) -> float:
        return self.item.cost * self.weight


@dataclass
class Order:
    order_id: int
    positions: list[Position] = field(default_factory=list)
    have_promo: InitVar[bool] = False
    cost: int = field(init=False)

    def __post_init__(self, have_promo: bool):
        total = sum(position.cost for position in self.positions)
        if have_promo:
            total = total * (100 - DISCOUNT_PERCENTS) / 100
        self.cost = int(total)

