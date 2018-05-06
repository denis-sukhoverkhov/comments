from django.conf.urls import url
from django.contrib import admin

from comments.views import CommentList, CommentCreate, RecursivelyCommentList

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/comment/(?P<slug>[a-z_]+)/(?P<pk>[0-9]+)/$', CommentList.as_view(), name='top-level-comments'),
    url(r'^api/comment/$', CommentCreate.as_view(), name='create-comment'),
    url(r'^api/comment/tree/$', RecursivelyCommentList.as_view(), name='recursively-comments'),
]
