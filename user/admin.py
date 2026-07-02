from django.contrib import admin
from user.models import User, Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id' ,'username', 'email']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'location']


