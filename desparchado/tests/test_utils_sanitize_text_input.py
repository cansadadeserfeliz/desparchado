import pytest

from ..utils import sanitize_text_input


def test_nul_byte_is_removed():
    assert sanitize_text_input("hello\x00world") == "helloworld"


@pytest.mark.parametrize("safe_char", ["\t", "\n", "\r"])
def test_safe_whitespace_is_preserved(safe_char):
    assert sanitize_text_input(safe_char) == safe_char


def test_only_control_chars_returns_empty_string():
    assert sanitize_text_input("\x00\x01\x02\x03\x1f") == ""
