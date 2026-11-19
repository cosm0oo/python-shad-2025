import sys
import traceback
from contextlib import contextmanager
from typing import Iterator, TextIO, Type


@contextmanager
def supresser(*types_: Type[BaseException]) -> Iterator[None]:
    try:
        yield
    except BaseException:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if not isinstance(exc_value, types_):
            raise


@contextmanager
def retyper(type_from: Type[BaseException], type_to: Type[BaseException]) -> Iterator[None]:
    try:
        yield
    except type_from as e:
        new_exc = type_to(*e.args)
        raise new_exc.with_traceback(e.__traceback__)


@contextmanager
def dumper(stream: TextIO | None = None) -> Iterator[None]:
    try:
        yield
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        message = ''.join(traceback.format_exception_only(exc_type, exc_value))
        output_stream = stream if stream is not None else sys.stderr
        output_stream.write(message)
        raise
