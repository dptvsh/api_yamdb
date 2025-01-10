from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, GenreViewSet, TitleViewSet,
                    CommentViewSet, ReviewViewSet)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register(r'titles/(?P<title_id>\d+?)/reviews',
                ReviewViewSet, basename='review')
router.register(r'titles/(?P<title_id>\d+?)/reviews/(?P<review_id>\d+?)/comments',
                CommentViewSet, basename='comment')
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include(router.urls)),
]
