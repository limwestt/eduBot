from django.contrib import admin
from .models import FaitCulturel, QuestionCulture, ScoreCulture


class QuestionInline(admin.TabularInline):
    model = QuestionCulture
    extra = 3
    max_num = 3


@admin.register(FaitCulturel)
class FaitCulturelAdmin(admin.ModelAdmin):
    list_display = ['titre', 'actif', 'date_ajout']
    list_editable = ['actif']
    inlines = [QuestionInline]
    search_fields = ['titre', 'contenu']


@admin.register(ScoreCulture)
class ScoreCultureAdmin(admin.ModelAdmin):
    list_display = ['user', 'fait', 'score', 'total_questions', 'date_tentative']
    list_filter = ['user', 'fait']
