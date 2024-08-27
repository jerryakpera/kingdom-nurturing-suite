from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path(
        "",
        views.index,
        name="index",
    ),
    path(
        "login/",
        views.login_view,
        name="login",
    ),
    path(
        "logout/",
        view=views.logout_view,
        name="logout",
    ),
    path(
        "change-password/",
        views.change_password,
        name="change_password",
    ),
    path(
        "set-password/<uidb64>/<token>/",
        views.set_password,
        name="set_password",
    ),
    path(
        "agree-to-terms/",
        views.agree_to_terms,
        name="agree_to_terms",
    ),
    path(
        "send-verification-email/<int:user_id>",
        views.verification_email,
        name="verification_email",
    ),
    path(
        "verify-email/<uidb64>/<token>/",
        views.verify_email,
        name="verify_email",
    ),
]
