from django.contrib import admin
from .models import TentativeQuiz


@admin.register(TentativeQuiz)
class TentativeQuizAdmin(admin.ModelAdmin):
    list_display = ['user', 'niveau', 'score', 'pourcentage', 'temps_employe', 'date_tentative']
    list_filter = ['niveau', 'date_tentative']
    search_fields = ['user__username']
    readonly_fields = ['date_tentative']
