from django.contrib import admin
from .models import Categorie, Question, TentativeQuiz


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['texte', 'choix_a', 'choix_b', 'choix_c', 'choix_d', 'bonne_reponse', 'points']


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'niveau', 'description', 'ordre']
    list_filter = ['niveau']
    inlines = [QuestionInline]
    ordering = ['ordre']


@admin.register(TentativeQuiz)
class TentativeQuizAdmin(admin.ModelAdmin):
    list_display = ['user', 'categorie', 'score', 'pourcentage', 'date_tentative']
    list_filter = ['categorie', 'date_tentative']
    search_fields = ['user__username']
