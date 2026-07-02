from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.models import User, Profile


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['id' ,'username', 'email']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'location']


