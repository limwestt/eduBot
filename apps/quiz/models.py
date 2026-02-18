from django.db import models
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    niveau = models.CharField(
        max_length=20,
        choices=[('debutant', 'Débutant'), ('intermediaire', 'Intermédiaire'), ('avance', 'Avancé')]
    )
    description = models.CharField(max_length=200, blank=True)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Catégories"
        ordering = ['ordre']

    def __str__(self):
        return f"{self.nom} ({self.get_niveau_display()})"


class Question(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='questions')
    texte = models.TextField()
    choix_a = models.CharField(max_length=300)
    choix_b = models.CharField(max_length=300)
    choix_c = models.CharField(max_length=300)
    choix_d = models.CharField(max_length=300)
    bonne_reponse = models.CharField(max_length=1, choices=[('A','A'), ('B','B'), ('C','C'), ('D','D')])
    explication = models.TextField(blank=True)
    points = models.IntegerField(default=10)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return f"{self.categorie} — {self.texte[:60]}"


class TentativeQuiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tentatives_quiz')
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    questions_repondus = models.IntegerField()
    bonnes_reponses = models.IntegerField()
    score_total = models.IntegerField()
    pourcentage = models.FloatField()
    temps_employe = models.IntegerField(default=0)  # secondes
    date_tentative = models.DateTimeField(auto_now_add=True)

    @property
    def score(self):
        return f"{self.bonnes_reponses}/{self.questions_repondus}"

    class Meta:
        ordering = ['-date_tentative']

    def __str__(self):
        return f"{self.user.username} — {self.categorie} — {self.score}"
