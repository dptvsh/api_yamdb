from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import TokenObtainView, UserRegistrationView, UserViewSet

app_name = 'api'
v1_router = DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path(
        'v1/auth/signup/',
        UserRegistrationView.as_view(),
        name='user-signup'
    ),
    path(
        'v1/auth/token/',
        TokenObtainView.as_view(),
        name='user-token'
    ),
    path('v1/', include(v1_router.urls)),
]
