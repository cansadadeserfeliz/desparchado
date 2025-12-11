from mapwidgets import GoogleMapPointFieldWidget


class GoogleMapPointFieldFixedWidget(GoogleMapPointFieldWidget):
    """This fix was added due to braking changes in Django 6.0:
    the widget fails to display with a JS crash.

    See https://github.com/erdem/django-map-widgets/issues/163
    """

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["name"] = name
        context["id"] = name

        return context
