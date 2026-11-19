def problem01() -> dict[int, str]:
    return {
        5: "Операция + не поддерживается для None и int",
        7: "dict.get возвращает int | None, что не совместимо с типом int"
    }


def problem02() -> dict[int, str]:
    return {
        5: "Операция += не поддерживается для разных типов элементов списка",
        6: "set[int] не совместим с типами элементов списка int | list[int] | str"
    }


def problem03() -> dict[int, str]:
    return {
        9: "set[float] не совместим с set[int]",
        13: "set[bool] не совместим с set[int]"
    }


def problem04() -> dict[int, str]:
    return {
        9: "set[float] не совместим с AbstractSet[int]"
    }


def problem05() -> dict[int, str]:
    return {
        11: "Возвращаемый тип A не совместим с объявленным типом B"
    }


def problem06() -> dict[int, str]:
    return {
        12: "B.VAR переопределяет A.VAR с типом S вместо T - тип read-write атрибутов нельзя менять",
        15: "C.VAR переопределяет B.VAR с типом T вместо S - тип read-write атрибутов нельзя менять"
    }


def problem07() -> dict[int, str]:
    return {
        25: "(A) -> A не совместим с (A) -> B - возвращаемый тип должен быть подтипом",
        27: "(B) -> A не совместим с (A) -> B - аргумент должен быть супертипом, возврат подтипом",
        28: "(B) -> B не совместим с (A) -> B - аргумент должен быть супертипом"
    }


def problem08() -> dict[int, str]:
    return {
        6: "Iterable[str] не совместим с Sized - Iterable не имеет __len__",
        18: "A не совместим с Iterable[str] - отсутствует __iter__",
        24: "B не совместим с Iterable[str] - __iter__ возвращает Iterator[int]"
    }


def problem09() -> dict[int, str]:
    return {
        32: "Операция in не поддерживается для Fooable - отсутствует __contains__",
        34: "list не совместим с Fooable - отсутствует метод foo",
        37: "C не совместим с Fooable - отсутствует __len__",
        38: "Функция не совместима с Fooable - функция не является экземпляром класса"
    }
