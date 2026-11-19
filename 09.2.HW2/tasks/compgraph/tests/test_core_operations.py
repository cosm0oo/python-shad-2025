import typing as tp
import pytest
from compgraph import operations as ops


def test_map_operation() -> None:
    """Test Map operation"""
    mapper = ops.DummyMapper()
    map_op = ops.Map(mapper)
    
    data = [{'a': 1}, {'a': 2}]
    result = list(map_op(iter(data)))
    assert result == data


def test_map_with_split() -> None:
    """Test Map operation with Split mapper"""
    mapper = ops.Split('text')
    map_op = ops.Map(mapper)
    
    data = [{'text': 'hello world'}]
    result = list(map_op(iter(data)))
    assert len(result) == 2


def test_reduce_operation() -> None:
    """Test Reduce operation"""
    reducer = ops.Count('count')
    reduce_op = ops.Reduce(reducer, ['key'])
    
    data = [{'key': 'a'}, {'key': 'a'}, {'key': 'b'}]
    result = list(reduce_op(iter(data)))
    result_sorted = sorted(result, key=lambda x: x['key'])
    
    assert result_sorted == [{'key': 'a', 'count': 2}, {'key': 'b', 'count': 1}]


def test_reduce_no_keys() -> None:
    """Test Reduce operation with no keys"""
    reducer = ops.Count('total')
    reduce_op = ops.Reduce(reducer, [])
    
    data = [{'x': 1}, {'x': 2}, {'x': 3}]
    result = list(reduce_op(iter(data)))
    assert result == [{'total': 3}]


def test_join_operation() -> None:
    """Test Join operation"""
    joiner = ops.InnerJoiner()
    join_op = ops.Join(joiner, ['id'])
    
    left = [{'id': 1, 'name': 'test'}]
    right = [{'id': 1, 'value': 100}]
    
    result = list(join_op(iter(left), iter(right)))
    assert result == [{'id': 1, 'name': 'test', 'value': 100}]


def test_read_iter_factory() -> None:
    """Test ReadIterFactory operation"""
    op = ops.ReadIterFactory('data')
    
    data = [{'a': 1}, {'a': 2}]
    result = list(op(data=lambda: iter(data)))
    assert result == data


def test_read_operation(tmp_path: tp.Any) -> None:
    """Test Read operation"""
    import json
    import typing as tp
    
    test_file = tmp_path / "test.txt"
    test_file.write_text('{"a": 1}\n{"a": 2}\n')
    
    op = ops.Read(str(test_file), json.loads)
    result = list(op())
    assert result == [{'a': 1}, {'a': 2}]

