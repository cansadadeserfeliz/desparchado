from urllib.parse import urlparse

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def format_currency(value):
    """
    E.g. 543921.9354 becomes $543,921.94
    """
    try:
        value = float(value)
        return '${:,.0f}'.format(value)
    except (ValueError, TypeError):
        return value


@register.simple_tag
def google_analytics_code():
    """Render the code needed for google analytics only when DEBUG is false
    """
    if settings.DEBUG:
        return mark_safe("""<script>function ga() {}</script>""")

    return mark_safe("""
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

  ga('create', '%s', 'auto');
  ga('send', 'pageview');

</script>
    """ % settings.GOOGLE_ANALYTICS_CODE)


@register.filter()
def shorten_url(value):
    """
    E.g. 543921.9354 becomes $543,921.94
    """
    parsed_uri = urlparse(value)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return domain
