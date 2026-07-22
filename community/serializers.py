from rest_framework import serializers

from community.models import Comment, Reaction, Bookmark
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

class PostCreateUpdateDestroySerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField('name', read_only=True)
    class Meta:
        model = GroupPost
        fields = ['id', 'group','title', 'content', 'updated_at', 'created_at']
        read_only_fields = ['id', 'updated_at', 'created_at']

class ReplySerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'context', 'created_at', 'updated_at']

class CommentListSerializer(serializers.ModelSerializer):
    post = serializers.StringRelatedField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    is_parent = serializers.SerializerMethodField(read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    class Meta:
        model = Comment
        fields = ['id','post', 'author', 'is_parent' ,'parent', 'context', 'updated_at', 'created_at', 'replies']

    def get_is_parent(self, obj):
        if obj.parent == None:
            return True
        return False

class CommentCreateSerializer(serializers.ModelSerializer):
    post = serializers.StringRelatedField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Comment
        fields = ['id','post', 'author','context', 'parent', 'updated_at', 'created_at']
        read_only_fields = ['updated_at', 'created_at', 'id']

    def validate_parent(self, value):
        post = self.context['post']

        if value and value.post != post :
            raise serializers.ValidationError('Parent and the comment post are not the same.')
        return value

class CommentUpdateDestroySerializer(serializers.ModelSerializer):
    post = serializers.StringRelatedField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id','post', 'author','context', 'parent', 'updated_at', 'created_at']
        read_only_fields = ['updated_at', 'created_at', 'id', 'parent']


class ReactionListSerializer(serializers.ModelSerializer):
    post = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    id = serializers.ReadOnlyField()
    class Meta:
        model = Reaction
        fields = ['id','post', 'user', 'type', 'updated_at', 'created_at']

class ReactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reaction
        fields = ['type']

class BookmarksListSerializer(serializers.ModelSerializer):
    post = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Bookmark
        fields = ['id','post', 'user', 'created_at']

