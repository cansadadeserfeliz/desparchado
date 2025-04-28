import pytest

from ..utils import sanitize_html


@pytest.mark.parametrize('input,output', [
    ('Line 1\nLine2', 'Line 1\nLine2'),
])
def test_do_not_remove_linebreaks(input_html, output_html):
    assert sanitize_html(input_html) == output_html
