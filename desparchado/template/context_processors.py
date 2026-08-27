from django.conf import settings


def constants(request):
    return {
        "ANALYTICS_ENABLED": settings.ANALYTICS_ENABLED,
        "CARTO_API_KEY": settings.CARTO_API_KEY,
    }
