import datetime
import enum
import typing as tp  # noqa


class GranularityEnum(enum.Enum):
    """
    Enum for describing granularity
    """

    DAY = datetime.timedelta(days=1)
    TWELVE_HOURS = datetime.timedelta(hours=12)
    HOUR = datetime.timedelta(hours=1)
    THIRTY_MIN = datetime.timedelta(minutes=30)
    FIVE_MIN = datetime.timedelta(minutes=5)


def truncate_to_granularity(dt: datetime.datetime, gtd: GranularityEnum) -> datetime.datetime:
    """
    :param dt: datetime to truncate
    :param gtd: granularity
    :return: resulted datetime
    """

    delta = gtd.value
    if delta >= datetime.timedelta(days=1):
        return datetime.datetime(dt.year, dt.month, dt.day)
    if delta == datetime.timedelta(hours=12):
        hour = 0 if dt.hour < 12 else 12
        return datetime.datetime(dt.year, dt.month, dt.day, hour)
    if delta == datetime.timedelta(hours=1):
        return datetime.datetime(dt.year, dt.month, dt.day, dt.hour)
    if delta == datetime.timedelta(minutes=30):
        minute = 0 if dt.minute < 30 else 30
        return datetime.datetime(dt.year, dt.month, dt.day, dt.hour, minute)
    if delta == datetime.timedelta(minutes=5):
        minute = (dt.minute // 5) * 5
        return datetime.datetime(dt.year, dt.month, dt.day, dt.hour, minute)
    return dt


class DtRange:
    def __init__(
            self,
            before: int,
            after: int,
            shift: int,
            gtd: GranularityEnum
    ) -> None:
        """
        :param before: number of datetimes should take before `given datetime`
        :param after: number of datetimes should take after `given datetime`
        :param shift: shift of `given datetime`
        :param gtd: granularity
        """

        self._before = before
        self._after = after
        self._shift = shift
        self._gtd = gtd

    def __call__(self, dt: datetime.datetime) -> list[datetime.datetime]:
        """
        :param dt: given datetime
        :return: list of datetimes in range
        """

        base = truncate_to_granularity(dt, self._gtd) + self._shift * self._gtd.value
        result = []
        start = base - self._before * self._gtd.value
        for i in range(self._before + self._after + 1):
            result.append(start + i * self._gtd.value)
        return result


def get_interval(
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        gtd: GranularityEnum
) -> list[datetime.datetime]:
    """
    :param start_time: start of interval
    :param end_time: end of interval
    :param gtd: granularity
    :return: list of datetimes according to granularity
    """

    start = truncate_to_granularity(start_time, gtd)
    if start < start_time:
        start = start + gtd.value
    result: list[datetime.datetime] = []
    current = start
    while current <= end_time:
        result.append(current)
        current = current + gtd.value
    return result
