from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet, TokenObtainView,
                       UserRegistrationView, UserViewSet)

# app_name = 'api'
v1_router = DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)

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