from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.TrackViewSet, basename='tracks')

urlpatterns = [
    path('history/', views.user_track_history, name='user_track_history'),
    path('', include(router.urls)),
]