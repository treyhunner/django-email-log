from django.conf.urls import url

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url("admin/", admin.site.urls),
]
