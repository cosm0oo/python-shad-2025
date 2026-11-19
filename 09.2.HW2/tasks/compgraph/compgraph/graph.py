import typing as tp
from . import operations as ops
from .external_sort import ExternalSort


class Graph:
    """Computational graph implementation"""

    def __init__(self, operations: list[ops.Operation] | None = None) -> None:
        self._operations = operations or []

    @staticmethod
    def graph_from_iter(name: str) -> "Graph":
        """Construct graph that reads data from iterator factory

        :param name: name of kwarg to use as data source
        """
        return Graph([ops.ReadIterFactory(name)])

    @staticmethod
    def graph_from_file(filename: str, parser: tp.Callable[[str], ops.TRow]) -> "Graph":
        """Construct graph that reads data from file

        :param filename: filename to read from
        :param parser: parser from string to Row
        """
        return Graph([ops.Read(filename, parser)])

    def map(self, mapper: ops.Mapper) -> "Graph":
        """Extend graph with map operation

        :param mapper: mapper to use
        """
        return Graph(self._operations + [ops.Map(mapper)])

    def reduce(self, reducer: ops.Reducer, keys: tp.Sequence[str]) -> "Graph":
        """Extend graph with reduce operation

        :param reducer: reducer to use
        :param keys: keys for grouping
        """
        return Graph(self._operations + [ops.Reduce(reducer, keys)])

    def sort(self, keys: tp.Sequence[str]) -> "Graph":
        """Extend graph with sort operation

        :param keys: sorting keys
        """
        return Graph(self._operations + [ExternalSort(keys)])

    def join(self, joiner: ops.Joiner, join_graph: "Graph", keys: tp.Sequence[str]) -> "Graph":
        """Extend graph with join operation

        :param joiner: join strategy to use
        :param join_graph: other graph to join with
        :param keys: keys for grouping
        """

        class JoinOperation(ops.Operation):
            def __init__(self, joiner: ops.Joiner, keys: tp.Sequence[str], other_graph: "Graph") -> None:
                self._joiner = joiner
                self._keys = keys
                self._other_graph = other_graph

            def __call__(self, rows: ops.TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> ops.TRowsGenerator:
                other_rows = self._other_graph.run(**kwargs)
                yield from ops.Join(self._joiner, self._keys)(rows, other_rows)

        return Graph(self._operations + [JoinOperation(joiner, keys, join_graph)])

    def run(self, **kwargs: tp.Any) -> ops.TRowsIterable:
        """Execute the graph with given data sources

        :param kwargs: data sources as keyword arguments
        :return: iterable of result rows
        """
        result: ops.TRowsIterable = iter([])

        for operation in self._operations:
            result = operation(result, **kwargs)

        return result
