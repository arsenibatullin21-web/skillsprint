from django.contrib import admin

from study_groups.models import StudyGroup, GroupMembership, GroupPost, GroupResource


# Register your models here.

@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ['id','owner', 'name', 'visibility']
    prepopulated_fields = {'slug': ('name', )}

@admin.register(GroupMembership)
class GroupMembership(admin.ModelAdmin):
    list_display = ['id','group', 'user', 'joined_at']

@admin.register(GroupPost)
class GroupPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'group', 'author', 'title', 'content']

@admin.register(GroupResource)
class GroupResourceAdmin(admin.ModelAdmin):
    list_display = ['id', 'group', 'title', 'url', 'description']

