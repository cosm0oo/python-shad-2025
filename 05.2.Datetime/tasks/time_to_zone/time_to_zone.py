from datetime import datetime
from zoneinfo import ZoneInfo

DEFAULT_TZ_NAME = "Europe/Moscow"


def now() -> datetime:
    """Return now in default timezone"""
    return datetime.now(tz=ZoneInfo(DEFAULT_TZ_NAME))


def strftime(dt: datetime, fmt: str) -> str:
    """Return dt converted to string according to format in default timezone"""
    dt_msk = _to_moscow(dt)
    return dt_msk.strftime(fmt)


def strptime(dt_str: str, fmt: str) -> datetime:
    """Return dt parsed from string according to format in default timezone"""
    parsed = datetime.strptime(dt_str, fmt)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ZoneInfo(DEFAULT_TZ_NAME))
    return parsed.astimezone(ZoneInfo(DEFAULT_TZ_NAME))


def diff(first_dt: datetime, second_dt: datetime) -> int:
    """Return seconds between two datetimes rounded down to closest int"""
    first = _to_moscow(first_dt)
    second = _to_moscow(second_dt)
    return int((second - first).total_seconds())


def timestamp(dt: datetime) -> int:
    """Return timestamp for given datetime rounded down to closest int"""
    aware = _to_moscow(dt)
    return int(aware.timestamp())


def from_timestamp(ts: float) -> datetime:
    """Return datetime from given timestamp"""
    return datetime.fromtimestamp(ts, tz=ZoneInfo(DEFAULT_TZ_NAME))


def _to_moscow(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo(DEFAULT_TZ_NAME))
    return dt.astimezone(ZoneInfo(DEFAULT_TZ_NAME))
