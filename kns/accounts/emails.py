from django.conf import settings
from django.core.mail import send_mail


def send_password_change_email(user_email):
    subject = "Password Changed Successfully"

    message = (
        "Dear User,\n\n"
        "Your password has been successfully changed.\n\n"
        "If you did not make this change, please contact support immediately."
    )

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)
