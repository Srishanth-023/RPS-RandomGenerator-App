# game/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Example: http://127.0.0.1:8000/
    path('', views.home_view, name='home'),

    # URL for form submission
    path('start/', views.start_game_view, name='start_game'),

    # Example: http://127.0.0.1:8000/game/Player1/
    path('game/<str:username>/', views.index, name='game_page'),

    # The endpoint for the frontend to send image data
    path('analyze/', views.analyze_frame, name='analyze_frame'),
]