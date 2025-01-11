from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import MyUser

from api.permissions import IsAdminOrSuperUser
from api.serializers import (MyTokenObtainPairSerializer,
                             UserRegistrationSerializer,
                             UsersSerializerForAdmin, UsersSerializerForUser)


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
    filter_backends = (filters.SearchFilter,)
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
