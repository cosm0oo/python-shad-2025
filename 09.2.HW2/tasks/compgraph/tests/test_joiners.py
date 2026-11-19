import pytest
from compgraph import operations as ops


def test_inner_joiner_basic() -> None:
    """Test InnerJoiner basic functionality"""
    joiner = ops.InnerJoiner()
    left = [{'id': 1, 'name': 'Alice'}]
    right = [{'id': 1, 'score': 100}]
    
    result = list(joiner(['id'], iter(left), iter(right)))
    assert result == [{'id': 1, 'name': 'Alice', 'score': 100}]


def test_inner_joiner_no_match() -> None:
    """Test InnerJoiner with no matching keys"""
    joiner = ops.InnerJoiner()
    left = [{'id': 1, 'name': 'Alice'}]
    right = [{'id': 2, 'score': 100}]
    
    result = list(joiner(['id'], iter(left), iter(right)))
    assert result == []


def test_inner_joiner_multiple_matches() -> None:
    """Test InnerJoiner with multiple matches"""
    joiner = ops.InnerJoiner()
    left = [{'id': 1, 'name': 'Alice'}, {'id': 1, 'name': 'Bob'}]
    right = [{'id': 1, 'score': 100}, {'id': 1, 'score': 200}]
    
    result = list(joiner(['id'], iter(left), iter(right)))
    assert len(result) == 4


def test_inner_joiner_empty_keys() -> None:
    """Test InnerJoiner with empty keys (cross join)"""
    joiner = ops.InnerJoiner()
    left = [{'name': 'A'}, {'name': 'B'}]
    right = [{'value': 1}, {'value': 2}]
    
    result = list(joiner([], iter(left), iter(right)))
    assert len(result) == 4


def test_inner_joiner_suffix() -> None:
    """Test InnerJoiner with custom suffixes"""
    joiner = ops.InnerJoiner(suffix_a='_left', suffix_b='_right')
    left = [{'id': 1, 'value': 10}]
    right = [{'id': 1, 'value': 20}]
    
    result = list(joiner(['id'], iter(left), iter(right)))
    assert result == [{'id': 1, 'value_left': 10, 'value_right': 20}]


def test_outer_joiner_basic() -> None:
    """Test OuterJoiner basic functionality"""
    joiner = ops.OuterJoiner()
    left = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
    right = [{'id': 1, 'score': 100}, {'id': 3, 'score': 200}]
    
    result = list(joiner(['id'], iter(left), iter(right)))
    assert len(result) == 3


def test_outer_joiner_all_match() -> None:
    """Test OuterJoiner when all keys match"""
    joiner = ops.OuterJoiner()
    left = [{'id': 1, 'x': 'a'}]
    right = [{'id': 1, 'y': 'b'}]
    
    result = list(joiner(['id'], iter(left), iter(right)))
    assert result == [{'id': 1, 'x': 'a', 'y': 'b'}]


def test_left_joiner_basic() -> None:
    """Test LeftJoiner basic functionality"""
    joiner = ops.LeftJoiner()
    left = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
    right = [{'id': 1, 'score': 100}]
    
    result = list(joiner(['id'], iter(left), iter(right)))
    assert len(result) == 2
    assert any(row.get('name') == 'Alice' and row.get('score') == 100 for row in result)
    assert any(row.get('name') == 'Bob' and row.get('score') is None for row in result)


def test_left_joiner_all_match() -> None:
    """Test LeftJoiner when all left rows match"""
    joiner = ops.LeftJoiner()
    left = [{'id': 1, 'x': 'a'}]
    right = [{'id': 1, 'y': 'b'}]
    
    result = list(joiner(['id'], iter(left), iter(right)))
    assert result == [{'id': 1, 'x': 'a', 'y': 'b'}]


def test_right_joiner_basic() -> None:
    """Test RightJoiner basic functionality"""
    joiner = ops.RightJoiner()
    left = [{'id': 1, 'name': 'Alice'}]
    right = [{'id': 1, 'score': 100}, {'id': 2, 'score': 200}]
    
    result = list(joiner(['id'], iter(left), iter(right)))
    assert len(result) == 2
    assert any(row.get('name') == 'Alice' and row.get('score') == 100 for row in result)
    assert any(row.get('name') is None and row.get('score') == 200 for row in result)


def test_right_joiner_all_match() -> None:
    """Test RightJoiner when all right rows match"""
    joiner = ops.RightJoiner()
    left = [{'id': 1, 'x': 'a'}]
    right = [{'id': 1, 'y': 'b'}]
    
    result = list(joiner(['id'], iter(left), iter(right)))
    assert result == [{'id': 1, 'x': 'a', 'y': 'b'}]


def test_joiner_multiple_keys() -> None:
    """Test joiner with multiple keys"""
    joiner = ops.InnerJoiner()
    left = [{'a': 1, 'b': 2, 'x': 'left'}]
    right = [{'a': 1, 'b': 2, 'y': 'right'}]
    
    result = list(joiner(['a', 'b'], iter(left), iter(right)))
    assert result == [{'a': 1, 'b': 2, 'x': 'left', 'y': 'right'}]

