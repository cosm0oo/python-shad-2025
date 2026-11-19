import typing as tp
from pathlib import Path
import sys


def tail(filename: Path, lines_amount: int = 10, output: tp.IO[bytes] | None = None) -> None:
    """
    :param filename: file to read lines from (the file can be very large)
    :param lines_amount: number of lines to read
    :param output: stream to write requested amount of last lines from file
                   (if nothing specified stdout will be used)
    """
    if output is None:
        output = sys.stdout.buffer

    if lines_amount == 0:
        return

    with open(filename, 'rb') as f:
        f.seek(0, 2)
        file_size = f.tell()

        if file_size == 0:
            return

        chunk_size = 4096
        buffer = bytearray(chunk_size)
        position = file_size
        data = bytearray()

        while position > 0:
            read_size = min(chunk_size, position)
            position -= read_size
            f.seek(position)
            bytes_read = f.readinto(memoryview(buffer)[:read_size])

            chunk = memoryview(buffer)[:bytes_read]
            data[0:0] = chunk

            if data.count(b'\n') > lines_amount:
                break

        lines = data.split(b'\n')

        if lines and lines[-1] == b'':
            lines = lines[:-1]

        result_lines = lines[-lines_amount:]

        for line in result_lines:
            output.write(line + b'\n')
