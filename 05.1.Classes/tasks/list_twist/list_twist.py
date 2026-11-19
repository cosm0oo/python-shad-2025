from collections import UserList
import typing as tp


class ListTwist(UserList[tp.Any]):
    """
    List-like class with additional attributes:
        * reversed, R - return reversed list
        * first, F - insert or retrieve first element;
                     Undefined for empty list
        * last, L -  insert or retrieve last element;
                     Undefined for empty list
        * size, S -  set or retrieve size of list;
                     If size less than list length - truncate to size;
                     If size greater than list length - pad with Nones
    """

    def __getattr__(self, name: str):
        if name in ("reversed", "R"):
            return list(reversed(self.data))
        if name in ("first", "F"):
            return self.data[0]
        if name in ("last", "L"):
            return self.data[-1]
        if name in ("size", "S"):
            return len(self.data)

    def __setattr__(self, name: str, value: tp.Any) -> None:
        if name in ("first", "F"):
            self.data[0] = value
            return
        if name in ("last", "L"):
            self.data[-1] = value
            return
        if name in ("size", "S"):
            current = len(self.data)
            if value < current:
                del self.data[value:]
            elif value > current:
                self.data.extend([None] * (value - current))
            return
        super().__setattr__(name, value)
