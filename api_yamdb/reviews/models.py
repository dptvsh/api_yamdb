from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    """Кастомная модель юзера, позволяет выбрать роль каждого пользователя"""
    email = models.EmailField('Почта', max_length=254, unique=True)
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=6,
        blank=True,
        null=True,
    )
    bio = models.TextField('Биография', blank=True, null=True, default='')
    role = models.CharField(
        'Роль',
        max_length=10,
        choices=[
            ('user', 'Пользователь'),
            ('moderator', 'Модератор'),
            ('admin', 'Админ')
        ],
        default='user',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
