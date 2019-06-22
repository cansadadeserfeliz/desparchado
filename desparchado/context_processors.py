from places.models import City


def cities(request):
    return {
        'global_cities':
        City.objects.filter(show_on_home=True).order_by('?').all()[:3]
    }
