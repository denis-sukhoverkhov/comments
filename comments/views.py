from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from comments.models import Comment
from comments.serrializers import CommentSerializer


class ResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CommentList(generics.ListAPIView):
    serializer_class = CommentSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        slug = self.kwargs.get('slug', None)
        pk = self.kwargs.get('pk', None)
        app_label = 'auth' if slug == 'user' else 'comments'
        content_type = ContentType.objects.get(app_label=app_label, model=slug)
        return Comment.objects.filter(object_id=pk, content_type=content_type.id)


class CommentCreate(generics.CreateAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
