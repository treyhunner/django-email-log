from django import VERSION
from django.contrib import admin

if VERSION[0] < 2:
    from django.conf.urls import url, include
else:
    from django.urls import path

admin.autodiscover()

if VERSION[0] < 2:
    urlpatterns = [
        url(r'^admin/', include(admin.site.urls), name='admin'),
    ]
else:
    urlpatterns = [
        path('admin/', admin.site.urls),
    ]
