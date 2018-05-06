import csv
import xml
import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.http import StreamingHttpResponse
from rest_framework import generics, permissions, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from comments.models import Comment, Post
from comments.serrializers import CommentSerializer, HistoryCommentSerializer
from .libs.misc import dict_fetchall


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

        raw_sql = (
            f"""with recursive rec(id, body, user_id, created, object_id, content_type_id, level)
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
            """)
        with connection.cursor() as cursor:
            cursor.execute(raw_sql)
            res = dict_fetchall(cursor)
        return Response(res)


class UserHistoryCommentList(generics.ListAPIView):
    serializer_class = HistoryCommentSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        return Comment.objects.filter(user=pk)


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def echo_xml(item):
    template = \
        f"""<comment>
  <id>{item.id}</id>
  <user>{item.user.username}</user>
  <body>{item.body}</body>
  <created>{item.created}</created>
</comment>
"""
    return template


def gen_xml(qs):
    for idx, item in enumerate(qs):
        if idx == 0:
            yield '<comments>\n' + echo_xml(item)
        else:
            yield echo_xml(item)
    else:
        yield '</comments>'


def streaming_csv_view(request, pk, format_export):
    date_start = request.GET.get('date_start', None)
    date_end = request.GET.get('date_end', None)
    comment_qs = Comment.objects.filter(user_id=pk)
    if date_start:
        date_start = datetime.datetime.strptime(date_start, '%d.%m.%Y')
        comment_qs.filter(created__gte=date_start)
    if date_end:
        date_end = datetime.datetime.strptime(date_end, '%d.%m.%Y')
        date_end = date_end.replace(hour=23, minute=59, second=59)
        comment_qs.filter(created__lte=date_end)

    if format_export == 'xml':
        response = StreamingHttpResponse(gen_xml(comment_qs), content_type='application/xml')
        response[
            'Content-Disposition'] = f'attachment; filename="export_comments_user_{pk}_{datetime.datetime.now()}.xml"'
    elif format_export == 'csv':
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse((writer.writerow((idx,
                                                           obj.id,
                                                           obj.body,
                                                           obj.user.username,
                                                           obj.created)) for idx, obj in enumerate(comment_qs)),
                                         content_type="text/csv")
        response[
            'Content-Disposition'] = f'attachment; filename="export_comments_user_{pk}_{datetime.datetime.now()}.csv"'
    else:
        raise Exception(f'Wrong format of export: {format_export}')

    return response
