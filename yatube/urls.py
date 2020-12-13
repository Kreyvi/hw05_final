import debug_toolbar # noqa
from django.conf import settings
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
    path(
        'about-author/',
        views.flatpage,
        {'url': '/about-author/'},
        name='about',
    ),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name='spec'),
    path('', include('posts.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('404/', handler404),
    path('500/', handler500),
]

if settings.DEBUG:

    urlpatterns += path('__debug__/', include(debug_toolbar.urls)),

    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT,)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT,)


handler404 = 'posts.views.page_not_found' # noqa
handler500 = 'posts.views.server_error' # noqa
