import typing as tp
import math
import heapq
from . import Graph, operations


def word_count_graph(input_stream_name: str, text_column: str = "text", count_column: str = "count") -> Graph:
    """Constructs graph which counts words in text_column of all rows passed

    :param input_stream_name: name of input stream
    :param text_column: name of column with text
    :param count_column: name of column for count result
    """
    return (
        Graph.graph_from_iter(input_stream_name)
        .map(operations.FilterPunctuation(text_column))
        .map(operations.LowerCase(text_column))
        .map(operations.Split(text_column))
        .sort([text_column])
        .reduce(operations.Count(count_column), [text_column])
        .sort([count_column, text_column])
    )


class IdfMapper(operations.Mapper):
    """Calculate IDF from document count and total count"""

    def __init__(self, result_column: str = "idf") -> None:
        self._result_column = result_column

    def __call__(self, row: operations.TRow) -> operations.TRowsGenerator:
        result = row.copy()
        result[self._result_column] = math.log(row["total_docs"] / row["docs_with_word"])
        yield result


class TfIdfMapper(operations.Mapper):
    """Calculate TF-IDF from TF and IDF"""

    def __init__(self, result_column: str = "tf_idf") -> None:
        self._result_column = result_column

    def __call__(self, row: operations.TRow) -> operations.TRowsGenerator:
        result = row.copy()
        result[self._result_column] = row["tf"] * row["idf"]
        yield result


class TopNByColumn(operations.Reducer):
    """Get top N rows by column value"""

    def __init__(self, column: str, n: int, doc_column: str = "doc_id") -> None:
        self._column = column
        self._n = n
        self._doc_column = doc_column

    def __call__(self, group_key: tuple[str, ...], rows: operations.TRowsIterable) -> operations.TRowsGenerator:
        heap: list[tuple[tp.Any, int, operations.TRow]] = []
        for idx, row in enumerate(rows):
            if len(heap) < self._n:
                heapq.heappush(heap, (row[self._column], idx, row))
            else:
                heapq.heappushpop(heap, (row[self._column], idx, row))
        for _, _, row in sorted(heap, reverse=True):
            yield row


def inverted_index_graph(
    input_stream_name: str, doc_column: str = "doc_id", text_column: str = "text", result_column: str = "tf_idf"
) -> Graph:
    """Constructs graph which calculates tf-idf for every word/document pair

    :param input_stream_name: name of input stream
    :param doc_column: name of column with document id
    :param text_column: name of column with text
    :param result_column: name of column for tf-idf result
    """

    docs_count = Graph.graph_from_iter(input_stream_name).reduce(operations.Count("total_docs"), [])

    idf_graph = (
        Graph.graph_from_iter(input_stream_name)
        .map(operations.FilterPunctuation(text_column))
        .map(operations.LowerCase(text_column))
        .map(operations.Split(text_column))
        .sort([doc_column, text_column])
        .reduce(operations.FirstReducer(), [doc_column, text_column])
        .sort([text_column])
        .reduce(operations.Count("docs_with_word"), [text_column])
        .join(operations.InnerJoiner(), docs_count, [])
        .map(IdfMapper("idf"))
        .map(operations.Project(["text", "idf"]))
    )

    tf_graph = (
        Graph.graph_from_iter(input_stream_name)
        .map(operations.FilterPunctuation(text_column))
        .map(operations.LowerCase(text_column))
        .map(operations.Split(text_column))
        .sort([doc_column, text_column])
        .reduce(operations.TermFrequency(text_column, "tf"), [doc_column])
    )

    return (
        tf_graph.sort([text_column])
        .join(operations.InnerJoiner(), idf_graph, [text_column])
        .map(TfIdfMapper(result_column))
        .map(operations.Project([doc_column, text_column, result_column]))
        .sort([text_column, result_column])
        .reduce(TopNByColumn(result_column, 3, doc_column), [text_column])
        .sort([doc_column, text_column])
    )


class PmiMapper(operations.Mapper):
    """Calculate PMI"""

    def __init__(self, result_column: str = "pmi") -> None:
        self._result_column = result_column

    def __call__(self, row: operations.TRow) -> operations.TRowsGenerator:
        result = row.copy()
        result[self._result_column] = math.log(row["doc_freq"] / row["total_freq"])
        yield result


def pmi_graph(
    input_stream_name: str, doc_column: str = "doc_id", text_column: str = "text", result_column: str = "pmi"
) -> Graph:
    """Constructs graph which gives for every document the top 10 words ranked by PMI

    :param input_stream_name: name of input stream
    :param doc_column: name of column with document id
    :param text_column: name of column with text
    :param result_column: name of column for pmi result
    """

    total_words_per_doc = (
        Graph.graph_from_iter(input_stream_name)
        .map(operations.FilterPunctuation(text_column))
        .map(operations.LowerCase(text_column))
        .map(operations.Split(text_column))
        .map(operations.Filter(lambda row: len(row[text_column]) > 4))
        .sort([doc_column, text_column])
        .reduce(operations.Count("count"), [doc_column, text_column])
        .map(operations.Filter(lambda row: row["count"] >= 2))
        .sort([doc_column])
        .reduce(operations.Sum("count"), [doc_column])
    )

    word_counts_all = (
        Graph.graph_from_iter(input_stream_name)
        .map(operations.FilterPunctuation(text_column))
        .map(operations.LowerCase(text_column))
        .map(operations.Split(text_column))
        .map(operations.Filter(lambda row: len(row[text_column]) > 4))
        .sort([doc_column, text_column])
        .reduce(operations.Count("count"), [doc_column, text_column])
        .map(operations.Filter(lambda row: row["count"] >= 2))
        .sort([text_column])
        .reduce(operations.Sum("count"), [text_column])
    )

    total_words_all = (
        Graph.graph_from_iter(input_stream_name)
        .map(operations.FilterPunctuation(text_column))
        .map(operations.LowerCase(text_column))
        .map(operations.Split(text_column))
        .map(operations.Filter(lambda row: len(row[text_column]) > 4))
        .sort([doc_column, text_column])
        .reduce(operations.Count("count"), [doc_column, text_column])
        .map(operations.Filter(lambda row: row["count"] >= 2))
        .reduce(operations.Sum("count"), [])
    )

    class CalculatePmi(operations.Mapper):
        def __init__(self, result_column: str = "pmi") -> None:
            self._result_column = result_column

        def __call__(self, row: operations.TRow) -> operations.TRowsGenerator:
            result = row.copy()
            word_count_in_doc = row["count_1"]
            doc_total_words = row["count_2"]
            word_count_all = row["count"]
            total_words = row["count_total"]

            tf = word_count_in_doc / doc_total_words
            freq_in_all = word_count_all / total_words

            result[self._result_column] = math.log(tf / freq_in_all)
            yield result

    pmi_calc = (
        Graph.graph_from_iter(input_stream_name)
        .map(operations.FilterPunctuation(text_column))
        .map(operations.LowerCase(text_column))
        .map(operations.Split(text_column))
        .map(operations.Filter(lambda row: len(row[text_column]) > 4))
        .sort([doc_column, text_column])
        .reduce(operations.Count("count"), [doc_column, text_column])
        .map(operations.Filter(lambda row: row["count"] >= 2))
        .sort([doc_column])
        .join(operations.InnerJoiner(), total_words_per_doc, [doc_column])
        .sort([text_column])
        .join(operations.InnerJoiner(), word_counts_all, [text_column])
        .join(operations.InnerJoiner(suffix_a="", suffix_b="_total"), total_words_all, [])
        .map(CalculatePmi(result_column))
        .map(operations.Project([doc_column, text_column, result_column]))
    )

    return pmi_calc.sort([doc_column]).reduce(TopNByColumn(result_column, 10, doc_column), [doc_column])


class HaversineDistance(operations.Mapper):
    """Calculate distance using Haversine formula"""

    def __init__(self, start_column: str = "start", end_column: str = "end", result_column: str = "length") -> None:
        self._start_column = start_column
        self._end_column = end_column
        self._result_column = result_column

    def __call__(self, row: operations.TRow) -> operations.TRowsGenerator:
        result = row.copy()
        start = row[self._start_column]
        end = row[self._end_column]

        lon1, lat1 = math.radians(start[0]), math.radians(start[1])
        lon2, lat2 = math.radians(end[0]), math.radians(end[1])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        result[self._result_column] = c * 6373
        yield result


class ParseDateTime(operations.Mapper):
    """Parse datetime and extract weekday and hour"""

    def __init__(
        self, time_column: str = "enter_time", weekday_column: str = "weekday", hour_column: str = "hour"
    ) -> None:
        self._time_column = time_column
        self._weekday_column = weekday_column
        self._hour_column = hour_column

    def __call__(self, row: operations.TRow) -> operations.TRowsGenerator:
        from datetime import datetime

        result = row.copy()

        time_str = row[self._time_column]
        try:
            dt = datetime.strptime(time_str, "%Y%m%dT%H%M%S.%f")
        except ValueError:
            dt = datetime.strptime(time_str, "%Y%m%dT%H%M%S")

        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        result[self._weekday_column] = weekdays[dt.weekday()]
        result[self._hour_column] = dt.hour
        yield result


class CalculateSpeed(operations.Mapper):
    """Calculate speed from distance and time"""

    def __init__(
        self,
        enter_time_column: str = "enter_time",
        leave_time_column: str = "leave_time",
        length_column: str = "length",
        speed_column: str = "speed",
    ) -> None:
        self._enter_time_column = enter_time_column
        self._leave_time_column = leave_time_column
        self._length_column = length_column
        self._speed_column = speed_column

    def __call__(self, row: operations.TRow) -> operations.TRowsGenerator:
        from datetime import datetime

        result = row.copy()

        enter_time_str = row[self._enter_time_column]
        leave_time_str = row[self._leave_time_column]

        try:
            enter_time = datetime.strptime(enter_time_str, "%Y%m%dT%H%M%S.%f")
        except ValueError:
            enter_time = datetime.strptime(enter_time_str, "%Y%m%dT%H%M%S")

        try:
            leave_time = datetime.strptime(leave_time_str, "%Y%m%dT%H%M%S.%f")
        except ValueError:
            leave_time = datetime.strptime(leave_time_str, "%Y%m%dT%H%M%S")

        time_diff = (leave_time - enter_time).total_seconds() / 3600

        if time_diff > 0:
            result[self._speed_column] = row[self._length_column] / time_diff
        else:
            result[self._speed_column] = 0

        yield result


class AverageSpeed(operations.Reducer):
    """Calculate average speed"""

    def __init__(self, speed_column: str = "speed") -> None:
        self._speed_column = speed_column

    def __call__(self, group_key: tuple[str, ...], rows: operations.TRowsIterable) -> operations.TRowsGenerator:
        rows_list = list(rows)
        if rows_list:
            result = {key: rows_list[0][key] for key in group_key}
            result[self._speed_column] = sum(row[self._speed_column] for row in rows_list) / len(rows_list)
            yield result


def yandex_maps_graph(
    input_stream_name_time: str,
    input_stream_name_length: str,
    enter_time_column: str = "enter_time",
    leave_time_column: str = "leave_time",
    edge_id_column: str = "edge_id",
    start_coord_column: str = "start",
    end_coord_column: str = "end",
    weekday_result_column: str = "weekday",
    hour_result_column: str = "hour",
    speed_result_column: str = "speed",
) -> Graph:
    """Constructs graph which measures average speed in km/h depending on the weekday and hour

    :param input_stream_name_time: name of stream with time data
    :param input_stream_name_length: name of stream with length data
    :param enter_time_column: name of column with enter time
    :param leave_time_column: name of column with leave time
    :param edge_id_column: name of column with edge id
    :param start_coord_column: name of column with start coordinates
    :param end_coord_column: name of column with end coordinates
    :param weekday_result_column: name of column for weekday result
    :param hour_result_column: name of column for hour result
    :param speed_result_column: name of column for speed result
    """

    lengths = (
        Graph.graph_from_iter(input_stream_name_length)
        .map(HaversineDistance(start_coord_column, end_coord_column, "length"))
        .map(operations.Project([edge_id_column, "length"]))
        .sort([edge_id_column])
    )

    times = (
        Graph.graph_from_iter(input_stream_name_time)
        .map(ParseDateTime(enter_time_column, weekday_result_column, hour_result_column))
        .sort([edge_id_column])
        .join(operations.InnerJoiner(), lengths, [edge_id_column])
        .map(CalculateSpeed(enter_time_column, leave_time_column, "length", speed_result_column))
        .map(operations.Project([weekday_result_column, hour_result_column, speed_result_column]))
    )

    return times.sort([weekday_result_column, hour_result_column]).reduce(
        AverageSpeed(speed_result_column), [weekday_result_column, hour_result_column]
    )
