import pytest
from pytest import approx
from compgraph import operations as ops


def test_first_reducer() -> None:
    """Test FirstReducer"""
    reducer = ops.FirstReducer()
    data = [{'a': 1, 'b': 2}, {'a': 1, 'b': 3}]
    result = list(reducer(('a',), iter(data)))
    assert result == [{'a': 1, 'b': 2}]


def test_first_reducer_single_row() -> None:
    """Test FirstReducer with single row"""
    reducer = ops.FirstReducer()
    data = [{'a': 1}]
    result = list(reducer(('a',), iter(data)))
    assert result == [{'a': 1}]


def test_topn_basic() -> None:
    """Test TopN reducer"""
    reducer = ops.TopN('score', 2)
    data = [
        {'id': 1, 'score': 10},
        {'id': 2, 'score': 30},
        {'id': 3, 'score': 20}
    ]
    result = list(reducer(tuple(), iter(data)))
    assert sorted(result, key=lambda x: x['id']) == [
        {'id': 2, 'score': 30},
        {'id': 3, 'score': 20}
    ]


def test_topn_less_than_n() -> None:
    """Test TopN with less rows than N"""
    reducer = ops.TopN('value', 5)
    data = [{'value': 1}, {'value': 2}]
    result = list(reducer(tuple(), iter(data)))
    assert len(result) == 2


def test_term_frequency() -> None:
    """Test TermFrequency reducer"""
    reducer = ops.TermFrequency('word', 'tf')
    data = [
        {'doc_id': 1, 'word': 'hello'},
        {'doc_id': 1, 'word': 'world'},
        {'doc_id': 1, 'word': 'hello'}
    ]
    result = list(reducer(('doc_id',), iter(data)))
    result_sorted = sorted(result, key=lambda x: x['word'])
    
    assert len(result_sorted) == 2
    assert result_sorted[0]['word'] == 'hello'
    assert result_sorted[0]['tf'] == approx(2/3, abs=0.01)
    assert result_sorted[1]['word'] == 'world'
    assert result_sorted[1]['tf'] == approx(1/3, abs=0.01)


def test_term_frequency_equal() -> None:
    """Test TermFrequency with equal frequencies"""
    reducer = ops.TermFrequency('word', 'tf')
    data = [
        {'doc_id': 1, 'word': 'a'},
        {'doc_id': 1, 'word': 'b'}
    ]
    result = list(reducer(('doc_id',), iter(data)))
    
    for row in result:
        assert row['tf'] == approx(0.5)


def test_count() -> None:
    """Test Count reducer"""
    reducer = ops.Count('count')
    data = [
        {'word': 'hello'},
        {'word': 'hello'},
        {'word': 'hello'}
    ]
    result = list(reducer(('word',), iter(data)))
    assert result == [{'word': 'hello', 'count': 3}]


def test_count_single() -> None:
    """Test Count reducer with single row"""
    reducer = ops.Count('n')
    data = [{'key': 'value'}]
    result = list(reducer(('key',), iter(data)))
    assert result == [{'key': 'value', 'n': 1}]


def test_count_empty() -> None:
    """Test Count reducer with empty data"""
    reducer = ops.Count('count')
    data: list[ops.TRow] = []
    result = list(reducer(('key',), iter(data)))
    assert result == []


def test_sum() -> None:
    """Test Sum reducer"""
    reducer = ops.Sum('value')
    data = [
        {'group': 'a', 'value': 10},
        {'group': 'a', 'value': 20},
        {'group': 'a', 'value': 30}
    ]
    result = list(reducer(('group',), iter(data)))
    assert result == [{'group': 'a', 'value': 60}]


def test_sum_single() -> None:
    """Test Sum reducer with single value"""
    reducer = ops.Sum('x')
    data = [{'key': 1, 'x': 42}]
    result = list(reducer(('key',), iter(data)))
    assert result == [{'key': 1, 'x': 42}]


def test_sum_floats() -> None:
    """Test Sum reducer with float values"""
    reducer = ops.Sum('value')
    data = [
        {'id': 1, 'value': 1.5},
        {'id': 1, 'value': 2.5}
    ]
    result = list(reducer(('id',), iter(data)))
    assert result[0]['value'] == approx(4.0)

