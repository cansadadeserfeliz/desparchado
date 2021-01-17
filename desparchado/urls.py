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
from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from django.contrib.auth import logout
from django.contrib.sitemaps.views import sitemap

from .views import HomeView, AtomSiteEventsFeed, \
    SocialNetworksRssSiteEventsFeed
from .sitemap import sitemaps


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path(
        'about/',
        TemplateView.as_view(template_name='desparchado/about.html'),
        name='about'
    ),

    path(
        'about-markdown/',
        TemplateView.as_view(template_name='desparchado/markdown.html'),
        name='markdown',
    ),

    path(
        'terms-and-conditions/',
        TemplateView.as_view(
            template_name='desparchado/terms_and_conditions.html',
        ),
        name='terms_and_conditions'
    ),
    path(
        '404/',
        TemplateView.as_view(template_name='404.html'),
        name='page_404'
    ),
    path(
        '500/',
        TemplateView.as_view(template_name='500.html'),
        name='page_500'
    ),
    path('rss/', SocialNetworksRssSiteEventsFeed(), name='rss'),
    path(
        'rss/social-networks/',
        SocialNetworksRssSiteEventsFeed(),
        name='rss_social_networks',
    ),
    path('atom/', AtomSiteEventsFeed(), name='atom'),

    path('events/', include('events.urls', namespace='events')),
    path('places/', include('places.urls', namespace='places')),
    path('users/', include('users.urls', namespace='users')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('games/', include('games.urls', namespace='games')),
    path('specials/', include('specials.urls', namespace='specials')),
    path('news/', include('news.urls', namespace='news')),
    path('books/', include('books.urls', namespace='books')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),

    path('i18n/', include('django.conf.urls.i18n')),

    path('logout/', logout, name='logout'),

    path('', include('social_django.urls', namespace='social')),

    path('grappelli/', include('grappelli.urls')),  # grappelli URLS
    path('admin/', admin.site.urls),
    path('markdownx/', include('markdownx.urls')),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
