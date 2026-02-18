from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='quiz_index'),
    path('niveau/<slug:niveau>/', views.niveau, name='quiz_niveau'),
    path('niveau/<slug:niveau>/commencer/', views.commencer_quiz, name='quiz_commencer'),
    path('niveau/<slug:niveau>/quiz/', views.quiz, name='quiz_quiz'),
    path('resultat/', views.resultat, name='quiz_resultat'),
    path('historique/', views.historique, name='quiz_historique'),
]
