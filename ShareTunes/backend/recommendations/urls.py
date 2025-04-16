from django.urls import path
from . import views

urlpatterns = [
    # 推薦一覧取得（GET）
    path('', views.RecommendationViewSet.as_view({'get': 'list'}), name='recommendation-list'),
    # 個別の推薦詳細取得（GET）
    path('<int:pk>/', views.RecommendationViewSet.as_view({'get': 'retrieve'}), name='recommendation-detail'),
    # 新しい推薦生成（POST）
    path('generate/', views.generate_recommendation, name='generate_recommendation'),
]