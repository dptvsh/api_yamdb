from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

from reviews.models import MAX_LENGTH_CONFIRMATION_CODE


def generate_and_send_confirmation_code(user):
    confirmation_code = get_random_string(length=MAX_LENGTH_CONFIRMATION_CODE)
    user.confirmation_code = confirmation_code
    user.save()

    send_mail(
        subject='Код подтверждения',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return confirmation_code
