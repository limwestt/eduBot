from django.db import models
from django.contrib.auth.models import User


class TentativeQuiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tentatives_quiz')
    niveau = models.CharField(max_length=20, choices=[
        ('debutant', 'Débutant'),
        ('intermediaire', 'Intermédiaire'),
        ('avance', 'Avancé'),
    ])
    questions_repondus = models.IntegerField()
    bonnes_reponses = models.IntegerField()
    score_total = models.IntegerField()
    pourcentage = models.FloatField()
    temps_employe = models.IntegerField(default=0)
    date_tentative = models.DateTimeField(auto_now_add=True)

    @property
    def score(self):
        return f"{self.bonnes_reponses}/{self.questions_repondus}"

    class Meta:
        ordering = ['-date_tentative']

    def __str__(self):
        return f"{self.user.username} — {self.niveau} — {self.score}"
