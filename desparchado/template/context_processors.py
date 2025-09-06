from django.conf import settings


def constants(request):
    return {
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
        "ANALYTICS_ENABLED": settings.ANALYTICS_ENABLED,
    }
