from django.db import models
from django.contrib.auth.models import User


class FaitCulturel(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    source = models.CharField(max_length=200, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Fait culturel"
        verbose_name_plural = "Faits culturels"
        ordering = ['-date_ajout']

    def __str__(self):
        return self.titre


class QuestionCulture(models.Model):
    fait = models.ForeignKey(FaitCulturel, on_delete=models.CASCADE, related_name='questions')
    texte = models.TextField()
    choix_a = models.CharField(max_length=300)
    choix_b = models.CharField(max_length=300)
    choix_c = models.CharField(max_length=300)
    choix_d = models.CharField(max_length=300)
    bonne_reponse = models.CharField(
        max_length=1,
        choices=[('A','A'),('B','B'),('C','C'),('D','D')]
    )
    explication = models.TextField(blank=True)

    def __str__(self):
        return f"{self.fait.titre} — {self.texte[:60]}"


class ScoreCulture(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores_culture')
    fait = models.ForeignKey(FaitCulturel, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=3)
    date_tentative = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_tentative']

    def __str__(self):
        return f"{self.user.username} — {self.fait.titre} — {self.score}/{self.total_questions}"
