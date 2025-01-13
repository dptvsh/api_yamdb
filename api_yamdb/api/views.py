from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters import rest_framework as django_filters
from rest_framework.filters import SearchFilter
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.permissions import (IsAdminOrReadOnly, IsAdminOrSuperUser,
                             IsAuthorOrReadOnly,
                             IsAdminOrReadOnlyWithRestrictedGet)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, MyTokenObtainPairSerializer,
                             ReviewSerializer, TitleCreateUpdateSerializer,
                             TitleSerializer, UserRegistrationSerializer,
                             UsersSerializerForAdmin, UsersSerializerForUser)
from reviews.models import Category, Genre, MyUser, Review, Title


class UserRegistrationView(generics.CreateAPIView):
    """Для создания нового юзера и отправки кода подтверждения на почту"""
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        username = request.data.get('username')
        user = MyUser.objects.filter(email=email, username=username).first()
        if user:
            # Если пользователь уже существует, отправляем повторный код
            return self.resend_confirmation_code(user)

        # Если пользователь не существует, создаем нового
        return self.register_new_user(request)

    def resend_confirmation_code(self, user):
        self.generate_send_confirmation_code(user)
        return Response(
            {'message': 'Код подтверждения отправлен повторно.'},
            status=200
        )

    def register_new_user(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Генерация и отправка нового кода подтверждения
        self.generate_send_confirmation_code(user)
        return Response(serializer.data, status=200)

    def generate_send_confirmation_code(self, user):
        confirmation_code = get_random_string(length=6)
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


class TokenObtainView(generics.GenericAPIView):
    """Для генерации токена"""
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            MyUser, username=serializer.validated_data.get('username')
        )

        return Response(
            {'token': str(AccessToken.for_user(user))},
            status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ModelViewSet):
    """Для работы с пользователями"""
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


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnlyWithRestrictedGet]
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'
    filter_backends = [SearchFilter]
    search_fields = ['name']
    http_method_names = ['get', 'post', 'delete']

    def retrieve(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnlyWithRestrictedGet]
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'
    filter_backends = [SearchFilter]
    search_fields = ['name']
    http_method_names = ['get', 'post', 'delete']

    def retrieve(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class TitleFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(
        field_name='genre__slug', lookup_expr='exact'
    )
    category = django_filters.CharFilter(
        field_name='category__slug', lookup_expr='exact'
    )
    year = django_filters.NumberFilter(field_name='year', lookup_expr='exact')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().distinct()
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [django_filters.DjangoFilterBackend, SearchFilter]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleSerializer
        return TitleCreateUpdateSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination
    ordering = ('pub_date',)
    http_method_names = [
        'get', 'head', 'options', 'post', 'patch', 'delete'
    ]

    def get_queryset(self):
        review_id = self.kwargs['review_id']
        review = get_object_or_404(Review, pk=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs['review_id']
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination
    ordering = ('pub_date',)
    http_method_names = [
        'get', 'head', 'options', 'post', 'patch', 'delete'
    ]

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)
