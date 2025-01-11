import re

from rest_framework import serializers
from rest_framework.exceptions import NotFound
from reviews.models import MyUser, Title, Category, Genre


class BaseUsersSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для работы с пользователем"""

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
    """Сериализатор для обработки системы получения токена"""
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
    """Сериализатор для работы админа с пользователем"""


class UsersSerializerForUser(BaseUsersSerializer):
    """Сериализатор для работы со своей учетной записью любому пользователю"""

    def update(self, instance, validated_data):
        # Здесь убираем 'role', чтобы не обновлять его
        validated_data.pop('role', None)
        return super().update(instance, validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name', 'slug']


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = [
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        ]


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
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
        fields = ['name', 'year', 'description', 'genre', 'category']
