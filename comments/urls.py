from django.conf.urls import url
from django.contrib import admin
# from django.db import router

# Create a router and register our viewsets with it.
from django.urls import include
from rest_framework.routers import DefaultRouter

from comments.views import CommentViewSet

router = DefaultRouter()
# router.register(r'user', UserViewSet, 'user')
router.register(r'comment', CommentViewSet, 'comment')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
]
