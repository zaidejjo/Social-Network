from django.contrib import admin
from .models import User, Post, Follow

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')


# Register your models here.

admin.site.register(Post)
admin.site.register(Follow)
