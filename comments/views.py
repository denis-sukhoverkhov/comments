from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from comments.models import Comment
from comments.serrializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    @action(detail=True, url_path='comment')
    def child_comments(self, request, pk=None):
        comment_list_qs = Comment.objects.filter(object_id=pk, content_type=ContentType.objects.get_for_model(Comment))

        ser = self.serializer_class(comment_list_qs, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)
