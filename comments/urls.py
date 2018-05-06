from django.conf.urls import url
from django.contrib import admin

from comments.views import CommentList, CommentCreate

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/comment/(?P<slug>[a-z_]+)/(?P<pk>[0-9]+)/$', CommentList.as_view(), name='comment'),
    url(r'^api/comment/$', CommentCreate.as_view(), name='create-comment'),
]
