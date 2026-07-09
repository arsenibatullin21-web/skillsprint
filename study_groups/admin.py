from django.contrib import admin

from study_groups.models import StudyGroup, GroupMembership


# Register your models here.

@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ['owner', 'name', 'visibility']
    prepopulated_fields = {'slug': ('name', )}

@admin.register(GroupMembership)
class GroupMembership(admin.ModelAdmin):
    list_display = ['group', 'user', 'joined_at']

