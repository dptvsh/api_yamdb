from django.contrib import admin

from reviews.models import MyUser


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'bio', 'role')
    exclude = ('confirmation_code', 'password', 'groups')
