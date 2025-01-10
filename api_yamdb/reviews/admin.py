from django.contrib import admin

from .models import Category, Genre, Title, Comment, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'category', 'rating')
    search_fields = ('name', 'description')
    list_filter = ('year', 'category')
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'text', 'pub_date', 'score')
    search_fields = ('title', 'author', 'text')
    list_filter = ('title', 'author', 'score')
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'author', 'text', 'pub_date')
    search_fields = ('review', 'author', 'text')
    list_filter = ('review', 'author')
    empty_value_display = '-пусто-'
