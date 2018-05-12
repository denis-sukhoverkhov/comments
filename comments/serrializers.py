from django.contrib.auth.models import User
from rest_framework import serializers

from comments.models import Comment, Post, CommentHistory


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'body', 'user', 'created', 'content_type', 'object_id')


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('id', 'title', 'body')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class HistoryCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'body', 'user', 'created')


class CommentHistoryUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommentHistory
        fields = ('id', 'comment', 'body', 'author', 'created', 'is_deleted')
