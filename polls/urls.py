# polls/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'polls'

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'polls', views.PollViewSet, basename='poll')

urlpatterns = [
    path('', include(router.urls)),
]
