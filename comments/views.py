from rest_framework import viewsets

from comments.models import Comment
from comments.serrializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
