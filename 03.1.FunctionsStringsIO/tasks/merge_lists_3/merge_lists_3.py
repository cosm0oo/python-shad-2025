import typing as tp
import heapq


def merge(input_streams: tp.Sequence[tp.IO[bytes]], output_stream: tp.IO[bytes]) -> None:
    """
    Merge input_streams in output_stream
    :param input_streams: list of input streams. Contains byte-strings separated by "\n". Nonempty stream ends with "\n"
    :param output_stream: output stream. Contains byte-strings separated by "\n". Nonempty stream ends with "\n"
    :return: None
    """
    heap: list[tuple[int, int]] = []

    for i, stream in enumerate(input_streams):
        line = stream.readline()
        if line:
            num = int(line.strip())
            heapq.heappush(heap, (num, i))

    while heap:
        num, stream_idx = heapq.heappop(heap)
        output_stream.write(f"{num}\n".encode())

        line = input_streams[stream_idx].readline()
        if line:
            next_num = int(line.strip())
            heapq.heappush(heap, (next_num, stream_idx))
