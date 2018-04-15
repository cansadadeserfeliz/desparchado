"""desparchado URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap

from .views import HomeView
from .sitemap import sitemaps


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='desparchado/about.html'), name='about'),

    url(
        r'^markdown/$',
        TemplateView.as_view(template_name='desparchado/markdown.html'),
        name='markdown',
    ),

    url(r'^events/', include('events.urls', namespace='events')),
    url(r'^places/', include('places.urls', namespace='places')),
    url(r'^users/', include('users.urls', namespace='users')),
    url(r'^dashboard/', include('dashboard.urls', namespace='dashboard')),

    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^logout/$', auth_views.logout, name='logout'),

    url('', include('social_django.urls', namespace='social')),

    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),  # admin site

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
