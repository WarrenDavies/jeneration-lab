import pytest

from jenerationlab.benchmarking.checks import functions


@pytest.mark.parametrize("params, output, expected_result", [
    ({"expected": 5}, 5, {"actual": 5, "expected": 5, "score": 1}),
    ({"expected": 5}, 3, {"actual": 3, "expected": 5, "score": 0}),
    ({"expected": "hello"}, "hello", {"actual": "hello", "expected": "hello", "score": 1}),
    ({"expected": "hello"}, "world", {"actual": "world", "expected": "hello", "score": 0}),
])
def test_is_exact(params, output, expected_result):
    assert functions.is_exact(params, output) == expected_result


@pytest.mark.parametrize("params, output, expected_result", [
    ({"expected": {"key": "value"}}, '{"key": "value"}', {"actual": '{"key": "value"}', "expected": {"key": "value"}, "score": 1}),
    ({"expected": {"key": "value"}}, '{"key": "value}', {"actual": '{"key": "value}', "expected": {"key": "value"}, "score": 0}),
    ({"expected": {"key": "value"}}, 'invalid_json', {"actual": 'invalid_json', "expected": {"key": "value"}, "score": 0}),
    ({"expected": [1, 2, 3]}, '[1, 2, 3]', {"actual": '[1, 2, 3]', "expected": [1, 2, 3], "score": 1}),
    ({"expected": [1, 2, 3]}, '(1, 2, 3)', {"actual": '(1, 2, 3)', "expected": [1, 2, 3], "score": 0}),
])
def test_is_correct_json(params, output, expected_result):
    assert functions.is_correct_json(params, output) == expected_result


@pytest.mark.parametrize("params, output, expected_result", [
    ({"expected": "3"}, "line1\nline2\nline3", {"actual": "3", "expected": "3", "score": 1}),
    ({"expected": "2"}, "line1\n\nline2", {"actual": "2", "expected": "2", "score": 1}),
    ({"expected": "1"}, "   line1   ", {"actual": "1", "expected": "1", "score": 1}),
    ({"expected": "0"}, "", {"actual": "0", "expected": "0", "score": 1}),
    ({"expected": "2"}, "line1\nline2\nline3", {"actual": "3", "expected": "2", "score": 0}),
    ({"expected": "1"}, "\n\nline1\n", {"actual": "1", "expected": "1", "score": 1}),
])
def test_count_lines(params, output, expected_result):
    assert functions.count_lines(params, output) == expected_result


@pytest.mark.parametrize("params, output, expected_result", [
    ({"substring": "hello", "expected": True}, "hello world", {"actual": "True", "expected": True, "score": 1}),
    ({"substring": "hello", "expected": False}, "world", {"actual": "False", "expected": False, "score": 1}),
    ({"substring": "hello", "expected": True}, "goodbye", {"actual": "False", "expected": True, "score": 0}),
    ({"substring": "", "expected": True}, "hello", {"actual": "True", "expected": True, "score": 1}),
    ({"substring": "hello", "expected": True}, "", {"actual": "False", "expected": True, "score": 0}),
    ({"substring": "HELLO", "expected": True}, "hello", {"actual": "False", "expected": True, "score": 0}),
])
def test_contains(params, output, expected_result):
    assert functions.contains(params, output) == expected_result


@pytest.mark.parametrize("params, output, expected_result", [
    ({"substring": "hello", "expected": True}, "hello world", {"actual": "True", "expected": True, "score": 1}),
    ({"substring": "hello", "expected": False}, "world", {"actual": "False", "expected": False, "score": 1}),
    ({"substring": "hello", "expected": True}, "helloworld", {"actual": "False", "expected": True, "score": 0}),
    ({"substring": "hello", "expected": True}, "hello!", {"actual": "True", "expected": True, "score": 1}),
    ({"substring": "", "expected": True}, "hello", {"actual": "True", "expected": True, "score": 1}),
    ({"substring": "hello", "expected": True}, "hello world", {"actual": "True", "expected": True, "score": 1}),
    ({"substring": "hello", "expected": "true"}, "hello world", {"actual": "True", "expected": "true", "score": 1}),
])
def test_contains_word(params, output, expected_result):
    assert functions.contains_word(params, output) == expected_result