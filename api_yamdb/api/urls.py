from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import TokenObtainView, UserRegistrationView, UserViewSet, CategoryViewSet, GenreViewSet, TitleViewSet

# app_name = 'api'
v1_router = DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')

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

def validate(self, data):
    title = get_object_or_404(Title, pk=title_id)

    reviews = title.reviews.all()
    user = self.context['request'].user
    if reviews.filter(author=user).exists():
        raise serializers.ValidationError(
            'Вы уже оставляли отзыв на это произведение.'
        )
    
    return data
