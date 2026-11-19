import pytest
from compgraph import operations as ops


def test_dummy_mapper() -> None:
    """Test DummyMapper"""
    mapper = ops.DummyMapper()
    result = list(mapper({'a': 1, 'b': 2}))
    assert result == [{'a': 1, 'b': 2}]


def test_filter_punctuation() -> None:
    """Test FilterPunctuation mapper"""
    mapper = ops.FilterPunctuation('text')
    result = list(mapper({'text': 'Hello, World!'}))
    assert result == [{'text': 'Hello World'}]


def test_filter_punctuation_all_punctuation() -> None:
    """Test FilterPunctuation with all punctuation"""
    mapper = ops.FilterPunctuation('text')
    result = list(mapper({'text': '!@#$%^&*()'}))
    assert result == [{'text': ''}]


def test_lowercase() -> None:
    """Test LowerCase mapper"""
    mapper = ops.LowerCase('text')
    result = list(mapper({'text': 'HELLO World'}))
    assert result == [{'text': 'hello world'}]


def test_split_default() -> None:
    """Test Split mapper with default separator"""
    mapper = ops.Split('text')
    result = list(mapper({'id': 1, 'text': 'hello world test'}))
    assert sorted(result, key=lambda x: x['text']) == [
        {'id': 1, 'text': 'hello'},
        {'id': 1, 'text': 'test'},
        {'id': 1, 'text': 'world'}
    ]


def test_split_custom_separator() -> None:
    """Test Split mapper with custom separator"""
    mapper = ops.Split('text', ',')
    result = list(mapper({'text': 'a,b,c'}))
    assert sorted(result, key=lambda x: x['text']) == [
        {'text': 'a'},
        {'text': 'b'},
        {'text': 'c'}
    ]


def test_split_empty_strings() -> None:
    """Test Split mapper filters empty strings"""
    mapper = ops.Split('text')
    result = list(mapper({'text': 'a  b'}))
    assert sorted(result, key=lambda x: x['text']) == [
        {'text': 'a'},
        {'text': 'b'}
    ]


def test_product() -> None:
    """Test Product mapper"""
    mapper = ops.Product(['a', 'b'], 'result')
    result = list(mapper({'a': 3, 'b': 4}))
    assert result == [{'a': 3, 'b': 4, 'result': 12}]


def test_product_multiple_columns() -> None:
    """Test Product mapper with multiple columns"""
    mapper = ops.Product(['a', 'b', 'c'], 'product')
    result = list(mapper({'a': 2, 'b': 3, 'c': 4}))
    assert result == [{'a': 2, 'b': 3, 'c': 4, 'product': 24}]


def test_filter_true() -> None:
    """Test Filter mapper with true condition"""
    mapper = ops.Filter(lambda row: row['value'] > 5)
    result = list(mapper({'value': 10}))
    assert result == [{'value': 10}]


def test_filter_false() -> None:
    """Test Filter mapper with false condition"""
    mapper = ops.Filter(lambda row: row['value'] > 5)
    result = list(mapper({'value': 3}))
    assert result == []


def test_project() -> None:
    """Test Project mapper"""
    mapper = ops.Project(['a', 'b'])
    result = list(mapper({'a': 1, 'b': 2, 'c': 3}))
    assert result == [{'a': 1, 'b': 2}]


def test_project_single_column() -> None:
    """Test Project mapper with single column"""
    mapper = ops.Project(['name'])
    result = list(mapper({'name': 'test', 'id': 1, 'value': 100}))
    assert result == [{'name': 'test'}]

