import pytest

from ..utils import sanitize_html


@pytest.mark.parametrize(
    'input_html,output_html',
    [
        ('Line 1\nLine2', 'Line 1\nLine2'),
        ('Line 1\r\nLine2', 'Line 1\r\nLine2'),
        ('Line 1<br>Line2', 'Line 1<br>Line2'),
        ('Line 1<p>Line2</p>', 'Line 1<p>Line2</p>'),
        ('Line 1    Line2', 'Line 1    Line2'),
    ],
)
def test_do_not_remove_linebreaks(input_html, output_html):
    assert sanitize_html(input_html) == output_html
