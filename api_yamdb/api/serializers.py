import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from reviews.models import Category, Comment, Genre, MyUser, Review, Title


class BaseUsersSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для работы с пользователем."""

    class Meta:
        model = MyUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Имя 'me' недопустимо.")
        pattern = r'^[\w.@+-]+\Z'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Некорректное имя пользователя.")
        return value


class UserRegistrationSerializer(BaseUsersSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta:
        model = MyUser
        fields = ('username', 'email')

    def create(self, validated_data):
        user = MyUser(**validated_data)
        user.save()
        return user


class MyTokenObtainPairSerializer(serializers.Serializer):
    """Сериализатор для обработки системы получения токена."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        if not username or not confirmation_code:
            raise serializers.ValidationError(
                'Обязательные поля не могут быть пустыми.'
            )

        user = MyUser.objects.filter(username=username).first()

        if user is None:
            raise NotFound('Пользователь не найден.')

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError('Неверный код подтверждения.')

        return data


class UsersSerializerForAdmin(BaseUsersSerializer):
    """Сериализатор для работы админа с пользователем."""


class UsersSerializerForUser(BaseUsersSerializer):
    """Сериализатор для работы со своей учетной записью любому пользователю."""

    def update(self, instance, validated_data):
        # Здесь убираем 'role', чтобы не обновлять его
        validated_data.pop('role', None)
        return super().update(instance, validated_data)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для работы с категориями произведений."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с жанрами произведений."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с произведениями."""

    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления произведений."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с отзывами на произведения."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.SlugRelatedField(
        slug_field='name', read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'author', 'title', 'pub_date', 'text', 'score')
        read_only_fields = ('title',)

    def validate_score(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError(
                'Введите целое число от 1 до 10.'
            )
        return value

    def validate(self, data):
        title_id = self.context['view'].kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)
        user = self.context['request'].user
        if (title.reviews.filter(author=user).exists()
                and self.context['request'].method == 'POST'):
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с комментариями к отзывам."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'review', 'pub_date', 'text')
        read_only_fields = ('review',)
