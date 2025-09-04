import pytest

from ..utils import sanitize_html


@pytest.mark.parametrize(
    "input_html,output_html",
    [
        ("Line 1\nLine 2", "Line 1\nLine 2"),
        ("Line 1\r\nLine 2", "Line 1\r\nLine 2"),
        ("Line 1<br>Line 2", "Line 1<br>Line 2"),
        ("Line 1<p>Line 2</p>", "Line 1<p>Line 2</p>"),
        ("Line 1    Line 2", "Line 1    Line 2"),
        ("Line 1\n\nLine 2", "Line 1\n\nLine 2"),
        ("Line 1 \nLine 2", "Line 1 \nLine 2"),
        ("Line 1\n Line 2", "Line 1\n Line 2"),
        ('<p class="red">Line</p>', "<p>Line</p>"),
    ],
)
def test_do_not_remove_linebreaks(input_html, output_html):
    assert sanitize_html(input_html) == output_html
