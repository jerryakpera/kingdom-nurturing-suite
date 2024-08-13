from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", include("admin_honeypot.urls")),
    path("control-panel/", admin.site.urls),
    path("accounts/", include("kns.accounts.urls")),
]

admin.site.site_title = "KNS Admin Portal"
admin.site.index_title = "Welcome to KNS Admin Portal"
admin.site.site_header = "Kingdom Nurturing Suite Admin"
