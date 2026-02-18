from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='culture_index'),
    path('fait/<int:fait_id>/', views.detail_fait, name='culture_fait'),
    path('fait/<int:fait_id>/quiz/', views.quiz_culture, name='culture_quiz'),
]
