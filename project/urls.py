from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path("tinymce/", include("tinymce.urls")),
    path("", include("kns.core.urls")),
    path("admin/", include("admin_honeypot.urls")),
    path("control-panel/", admin.site.urls),
    path("accounts/", include("kns.accounts.urls")),
    path("profiles/", include("kns.profiles.urls")),
    path("groups/", include("kns.groups.urls")),
    path("skills/", include("kns.skills.urls")),
    # Password reset urls
    path(
        "reset_password/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/pages/authentication/reset_password.html"
        ),
        name="reset_password",
    ),
    path(
        "reset_password_sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/pages/authentication/reset_password_sent.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/pages/authentication/reset.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset_password_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/pages/authentication/reset_password_complete.html"
        ),
        name="password_reset_complete",
    ),
]

handler404 = "kns.core.views.error_404"

if settings.DEBUG:
    # If in production
    from django.conf.urls.static import static

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )

admin.site.site_title = "KNS Admin Portal"
admin.site.index_title = "Welcome to KNS Admin Portal"
admin.site.site_header = "Kingdom Nurturing Suite Admin"
