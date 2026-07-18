from rest_framework import serializers

from study_groups.models import GroupPost


class PostListDetailSerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField('name', read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)
    reactions_count = serializers.SerializerMethodField(read_only=True)
    bookmarks_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GroupPost
        fields = ['id','group', 'author', 'title', 'content', 'comments_count', 'reactions_count', 'bookmarks_count','created_at', 'updated_at']

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_reactions_count(self, obj):
        return obj.reactions.count()

    def get_bookmarks_count(self, obj):
        return obj.bookmarks.count()
