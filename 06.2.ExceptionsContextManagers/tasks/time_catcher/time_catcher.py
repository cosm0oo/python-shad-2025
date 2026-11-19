import time
import contextlib


class TimeoutException(Exception):
    pass


class SoftTimeoutException(TimeoutException):
    pass


class HardTimeoutException(TimeoutException):
    pass


class TimeCatcher(contextlib.ContextDecorator):
    def __init__(self, soft_timeout=None, hard_timeout=None):
        if soft_timeout is not None and soft_timeout <= 0:
            raise AssertionError
        if hard_timeout is not None and hard_timeout <= 0:
            raise AssertionError
        if soft_timeout is not None and hard_timeout is not None:
            if soft_timeout > hard_timeout:
                raise AssertionError

        self.soft_timeout = soft_timeout
        self.hard_timeout = hard_timeout
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time

        if self.hard_timeout is not None and elapsed > self.hard_timeout:
            raise HardTimeoutException

        if self.soft_timeout is not None and elapsed > self.soft_timeout:
            raise SoftTimeoutException

        return False

    def __float__(self):
        if self.end_time is not None:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def __str__(self):
        elapsed = float(self)
        return f"Time consumed: {elapsed:.4f}"
