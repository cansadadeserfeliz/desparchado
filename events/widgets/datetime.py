from django import forms


class DateTimeWidget(forms.DateTimeInput):
    """Custom datetime widget that delegates picker UI to a JS component.

    Renders a plain text input wrapped in a ``div.datetime-widget`` container.
    The JS component mounts onto the wrapper and provides the date/time
    picker UI. Django reads the submitted value using the ``'%Y-%m-%d %H:%M'``
    format.
    """

    template_name = "events/widgets/datetime/datetime.html"
    input_type = "text"

    def __init__(self, attrs: dict | None = None) -> None:
        super().__init__(attrs=attrs, format="%Y-%m-%d %H:%M")

    @property
    def media(self) -> forms.Media:
        return forms.Media(
            css={"all": ["events/css/datetime_widget.css"]},
            js=["events/js/datetime_widget.js"],
        )
