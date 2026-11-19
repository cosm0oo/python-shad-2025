import typing as tp
import pytest
from compgraph import Graph, operations as ops


def test_graph_from_iter() -> None:
    """Test graph creation from iterator"""
    graph = Graph.graph_from_iter('data')
    result = list(graph.run(data=lambda: iter([{'a': 1}, {'a': 2}])))
    assert result == [{'a': 1}, {'a': 2}]


def test_graph_from_file(tmp_path: tp.Any) -> None:
    """Test graph creation from file"""
    import json
    test_file = tmp_path / "test.txt"
    test_file.write_text('{"a": 1}\n{"a": 2}\n')
    
    graph = Graph.graph_from_file(str(test_file), json.loads)
    result = list(graph.run())
    assert result == [{'a': 1}, {'a': 2}]


def test_graph_map() -> None:
    """Test graph map operation"""
    graph = Graph.graph_from_iter('data').map(ops.DummyMapper())
    result = list(graph.run(data=lambda: iter([{'a': 1}])))
    assert result == [{'a': 1}]


def test_graph_reduce() -> None:
    """Test graph reduce operation"""
    graph = Graph.graph_from_iter('data').reduce(ops.Count('count'), ['a'])
    result = list(graph.run(data=lambda: iter([{'a': 1}, {'a': 1}, {'a': 2}])))
    assert sorted(result, key=lambda x: x['a']) == [{'a': 1, 'count': 2}, {'a': 2, 'count': 1}]


def test_graph_sort() -> None:
    """Test graph sort operation"""
    graph = Graph.graph_from_iter('data').sort(['a'])
    result = list(graph.run(data=lambda: iter([{'a': 3}, {'a': 1}, {'a': 2}])))
    assert result == [{'a': 1}, {'a': 2}, {'a': 3}]


def test_graph_join() -> None:
    """Test graph join operation"""
    left = Graph.graph_from_iter('left')
    right = Graph.graph_from_iter('right')
    
    graph = left.join(ops.InnerJoiner(), right, ['id'])
    
    result = list(graph.run(
        left=lambda: iter([{'id': 1, 'name': 'a'}]),
        right=lambda: iter([{'id': 1, 'value': 10}])
    ))
    
    assert result == [{'id': 1, 'name': 'a', 'value': 10}]


def test_graph_multiple_runs() -> None:
    """Test that graph can be run multiple times with different data"""
    graph = Graph.graph_from_iter('data').map(ops.LowerCase('text'))
    
    result1 = list(graph.run(data=lambda: iter([{'text': 'HELLO'}])))
    assert result1 == [{'text': 'hello'}]
    
    result2 = list(graph.run(data=lambda: iter([{'text': 'WORLD'}])))
    assert result2 == [{'text': 'world'}]
    
    result3 = list(graph.run(data=lambda: iter([{'text': 'TEST'}])))
    assert result3 == [{'text': 'test'}]


def test_graph_complex_pipeline() -> None:
    """Test complex graph pipeline"""
    graph = Graph.graph_from_iter('data') \
        .map(ops.FilterPunctuation('text')) \
        .map(ops.LowerCase('text')) \
        .map(ops.Split('text')) \
        .sort(['text']) \
        .reduce(ops.Count('count'), ['text'])
    
    data = [
        {'text': 'Hello, World!'},
        {'text': 'Hello Python'}
    ]
    
    result = list(graph.run(data=lambda: iter(data)))
    result_sorted = sorted(result, key=lambda x: x['text'])
    
    assert result_sorted == [
        {'text': 'hello', 'count': 2},
        {'text': 'python', 'count': 1},
        {'text': 'world', 'count': 1}
    ]


def test_graph_sequential_runs_independence() -> None:
    """Test that sequential runs don't affect each other"""
    graph = Graph.graph_from_iter('data') \
        .map(ops.LowerCase('text'))
    
    data1 = [{'text': 'HELLO'}]
    result1 = list(graph.run(data=lambda: iter(data1)))
    assert result1 == [{'text': 'hello'}]
    
    data2 = [{'text': 'WORLD'}]
    result2 = list(graph.run(data=lambda: iter(data2)))
    assert result2 == [{'text': 'world'}]
    
    result3 = list(graph.run(data=lambda: iter(data1)))
    assert result3 == [{'text': 'hello'}]


def test_graph_empty_input() -> None:
    """Test graph with empty input"""
    graph = Graph.graph_from_iter('data').map(ops.DummyMapper())
    result = list(graph.run(data=lambda: iter([])))
    assert result == []


def test_graph_chained_operations() -> None:
    """Test multiple chained operations"""
    graph = Graph.graph_from_iter('data') \
        .map(ops.Product(['a', 'b'], 'product')) \
        .map(ops.Filter(lambda row: row['product'] > 10)) \
        .map(ops.Project(['product']))
    
    data = [
        {'a': 2, 'b': 3},
        {'a': 5, 'b': 4},
        {'a': 1, 'b': 8}
    ]
    
    result = list(graph.run(data=lambda: iter(data)))
    assert sorted(result, key=lambda x: x['product']) == [{'product': 20}]

