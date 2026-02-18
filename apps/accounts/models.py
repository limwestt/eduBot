from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    NIVEAUX = [
        ('beginner', 'Débutant'),
        ('intermediate', 'Intermédiaire'),
        ('advanced', 'Avancé'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    niveau = models.CharField(max_length=20, choices=NIVEAUX, default='beginner')
    score_total = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    date_inscription = models.DateTimeField(default=timezone.now)
    dernier_score = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_niveau_display()} ({self.score_total} pts)"
