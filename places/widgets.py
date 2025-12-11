from mapwidgets import GoogleMapPointFieldWidget


class GoogleMapPointFieldFixedWidget(GoogleMapPointFieldWidget):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["name"] = name
        context["id"] = name

        return context
