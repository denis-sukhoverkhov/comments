from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from rest_framework import generics, permissions, authentication, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from .libs.misc import dict_fetchall

from comments.models import Comment, Post
from comments.serrializers import CommentSerializer, HistoryCommentSerializer


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


class RecursivelyCommentList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        entity_name = request.query_params.get('entity', Comment.__name__.lower())
        object_id = request.query_params.get('object_id', None)
        if object_id is None:
            raise serializers.ValidationError('missing parameter: object_id')
        app_label = 'auth' if entity_name == User.__name__.lower() else 'comments'
        content_type = ContentType.objects.get(app_label=app_label, model=entity_name)
        comment_content_type = ContentType.objects.get_for_model(Comment)

        if entity_name == Comment.__name__.lower():
            condition1 = f't1.id = {object_id}'
            condition2 = f'WHERE id != {object_id}'
        elif entity_name in (Post.__name__.lower(), User.__name__.lower()):
            condition1 = f't1.object_id = {object_id} and t1.content_type_id={content_type.id}'
            condition2 = ''
        else:
            raise serializers.ValidationError(f'wrong entity name: {entity_name}')

        raw_sql = f"""with recursive rec(id, body, user_id, created, object_id, content_type_id, level)
as
(
  select t1.id, t1.body, t1.user_id, t1.created, t1.object_id, t1.content_type_id, 1 as level
  from comments_comment as t1
  where {condition1}
  union all
  select t2.id, t2.body, t2.user_id, t2.created, t2.object_id, t2.content_type_id, rec.level + 1 AS level
  from comments_comment as t2, rec where t2.object_id = rec.id AND t2.content_type_id = {comment_content_type.id}
)
select * from rec
{condition2}
ORDER BY level, object_id
        """
        with connection.cursor() as cursor:
            cursor.execute(raw_sql)
            res = dict_fetchall(cursor)
        return Response(res)


class UserHistoryCommentList(generics.ListAPIView):
    serializer_class = HistoryCommentSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        # slug = self.kwargs.get('slug', None)
        pk = self.kwargs.get('pk', None)
        return Comment.objects.filter(user=pk)
