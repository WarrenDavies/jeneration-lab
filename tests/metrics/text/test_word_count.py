import pytest
from jenerationlab.metrics.text.word_count import WordCount

@pytest.mark.parametrize("text,expected_count", [
        ("hello world", 2),
        ("", 0),
        ("   ", 0),
        ("single", 1),
        ("  hello  world  ", 2),
        ("hello, world!", 2),
        ("hello-world", 2),
        ("hello_world", 1), 
        ("hello...world", 2),
        ("don't stop", 2),
        ("New York City", 3),
        ("  hello   world  with   extra   spaces  ", 5),        
        ("\t\n", 0),
        ("café au lait", 3),
        ("123 456", 2),
        ("hello@world.com", 3),
        ("hello...world...", 2),
        ("...hello...world...", 2),
])
def test_word_count(text, expected_count):
    word_counter = WordCount()
    actual_count = word_counter.calculate(text)
    assert actual_count == expected_count
