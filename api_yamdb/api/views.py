from django.shortcuts import get_object_or_404
from django_filters import rest_framework as django_filters
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (IsAdminOrReadOnly,
                             IsAdminOrReadOnlyWithRestrictedGet,
                             IsAdminOrSuperUser, IsAuthorOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, MyTokenObtainPairSerializer,
                             ReviewSerializer, TitleCreateUpdateSerializer,
                             TitleSerializer, UserRegistrationSerializer,
                             UsersSerializerForAdmin, UsersSerializerForUser)
from api.utils import generate_and_send_confirmation_code
from reviews.models import Category, Genre, MyUser, Review, Title


class UserRegistrationView(generics.CreateAPIView):
    """Для создания нового юзера и отправки кода подтверждения на почту."""

    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        username = request.data.get('username')
        user = MyUser.objects.filter(email=email, username=username).first()
        if user:
            # Если пользователь уже существует, отправляем повторный код
            return self.resend_confirmation_code(user)

        # Если пользователь не существует, создаём нового
        return self.register_new_user(request)

    def resend_confirmation_code(self, user):
        generate_and_send_confirmation_code(user)
        return Response(
            {'email': user.email, 'username': user.username},
            status=status.HTTP_200_OK
        )

    def register_new_user(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'email': user.email, 'username': user.username},
            status=status.HTTP_200_OK
        )


class TokenObtainView(generics.GenericAPIView):
    """Для генерации токена."""

    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        return Response(
            {'token': str(AccessToken.for_user(user))},
            status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ModelViewSet):
    """Для работы с пользователями."""

    queryset = MyUser.objects.all()
    permission_classes = (IsAdminOrSuperUser, IsAuthenticated)
    serializer_class = UsersSerializerForAdmin
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )

    @action(
        methods=(
            'GET',
            'PATCH',
        ),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me',
    )
    def get_user(self, request):
        serializer_class = (
            UsersSerializerForAdmin if request.user.role == 'admin'
            or request.user.is_superuser else UsersSerializerForUser
        )
        if request.method == 'PATCH':
            serializer = serializer_class(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = serializer_class(request.user)
        return Response(serializer.data)


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Класс для работы с категориями произведений."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnlyWithRestrictedGet,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    http_method_names = ('get', 'post', 'delete')


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Класс для работы с жанрами произведений."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnlyWithRestrictedGet,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    http_method_names = ('get', 'post', 'delete')


class TitleViewSet(viewsets.ModelViewSet):
    """Класс для работы с произведениями."""

    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )
    filter_backends = (django_filters.DjangoFilterBackend, SearchFilter)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleSerializer
        return TitleCreateUpdateSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Класс для работы с комментариями к отзывам."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination
    ordering = ('pub_date',)
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )

    def get_queryset(self):
        review_id = self.kwargs['review_id']
        review = get_object_or_404(Review, pk=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs['review_id']
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    """Класс для работы с отзывами на произведения."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination
    ordering = ('pub_date',)
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)
