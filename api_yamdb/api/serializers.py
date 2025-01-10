from rest_framework import serializers
from reviews.models import Title, Category, Genre, Comment, Review


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


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'author', 'title', 'pub_date', 'text', 'score')
        read_only_fields = ('title',)
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title'),
                message='Вы уже оставляли отзыв на это произведение.'
            )
        ]

    def validate_score(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError(
                'Введите целое число от 1 до 10.'
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'review', 'pub_date', 'text')
        read_only_fields = ('review',)
