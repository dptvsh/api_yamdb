import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg

from reviews.constants import (MAX_LENGTH_CONFIRMATION_CODE, MAX_LENGTH_EMAIL,
                               MAX_LENGTH_NAME, MAX_LENGTH_ROLE,
                               MAX_LENGTH_SLUG, MAX_LENGTH_USERNAME,
                               MAX_VALUE_SCORE, MIN_VALUE_SCORE)


class MyUser(AbstractUser):
    """Кастомная модель юзера, позволяет выбрать роль каждого пользователя."""

    email = models.EmailField(
        'Почта',
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=MAX_LENGTH_CONFIRMATION_CODE,
        blank=True,
        null=True,
    )
    bio = models.TextField('Биография', blank=True, null=True, default='')
    role = models.CharField(
        'Роль',
        max_length=MAX_LENGTH_ROLE,
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

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'


class BaseNameSlugModel(models.Model):
    """Базовая модель с полями name и slug для Category и Genre."""

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        max_length=MAX_LENGTH_SLUG,
        verbose_name='Уникальный идентификатор',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Category(BaseNameSlugModel):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseNameSlugModel):
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название произведения',
    )
    year = models.PositiveIntegerField(verbose_name='Год выпуска')
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def save(self, *args, **kwargs):
        year = int(self.year)
        if year > datetime.datetime.now().year:
            raise ValueError("Год выпуска не может быть больше текущего.")
        super().save(*args, **kwargs)

    @property
    def rating(self):
        average = self.reviews.aggregate(Avg('score'))['score__avg']
        return round(average) if average is not None else None

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        verbose_name='Произведение', related_name='reviews',
    )
    author = models.ForeignKey(
        MyUser, on_delete=models.CASCADE,
        verbose_name='Автор', related_name='reviews',
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления', auto_now_add=True,
    )
    score = models.PositiveIntegerField(verbose_name='Оценка')

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_review'),
        ]

    def save(self, *args, **kwargs):
        score = int(self.score)
        if not (MIN_VALUE_SCORE <= score <= MAX_VALUE_SCORE):
            raise ValueError(
                f'Введите целое число от {MIN_VALUE_SCORE}'
                'до {MAX_VALUE_SCORE}.'
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.author} о произведении "{self.title}"'


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        verbose_name='Отзыв', related_name='comments',
    )
    author = models.ForeignKey(
        MyUser, on_delete=models.CASCADE,
        verbose_name='Автор', related_name='comments',
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления', auto_now_add=True,
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий №{self.id} к отзыву "{self.review}"'
