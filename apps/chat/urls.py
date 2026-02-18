from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='chat_index'),
    path('envoyer/', views.envoyer_message, name='chat_envoyer'),
    path('effacer/', views.effacer_historique, name='chat_effacer'),
]
