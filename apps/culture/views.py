import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import FaitCulturel, QuestionCulture, ScoreCulture
from apps.accounts.models import UserProfile


@login_required
def index(request):
    faits = FaitCulturel.objects.filter(actif=True)
    faits_avec_score = []

    for fait in faits:
        dernier_score = ScoreCulture.objects.filter(
            user=request.user, fait=fait
        ).first()
        faits_avec_score.append({
            'fait': fait,
            'dernier_score': dernier_score,
            'deja_fait': dernier_score is not None,
        })

    total_points = sum(
        s.score for s in ScoreCulture.objects.filter(user=request.user)
    )

    context = {
        'faits_avec_score': faits_avec_score,
        'total_faits': faits.count(),
        'total_points': total_points,
    }
    return render(request, 'culture/index.html', context)


@login_required
def detail_fait(request, fait_id):
    fait = get_object_or_404(FaitCulturel, id=fait_id, actif=True)
    dernier_score = ScoreCulture.objects.filter(
        user=request.user, fait=fait
    ).first()
    return render(request, 'culture/fait.html', {
        'fait': fait,
        'dernier_score': dernier_score,
    })


@login_required
def quiz_culture(request, fait_id):
    fait = get_object_or_404(FaitCulturel, id=fait_id, actif=True)
    questions = list(fait.questions.all())

    if len(questions) < 3:
        messages.error(request, "Ce fait n'a pas encore 3 questions configurées.")
        return redirect('culture_index')

    questions = random.sample(questions, 3)

    if request.method == 'POST':
        score = 0
        resultats = []

        for question in questions:
            reponse_user = request.POST.get(f'question_{question.id}', '')
            correct = reponse_user.upper() == question.bonne_reponse.upper()
            if correct:
                score += 1
            resultats.append({
                'question': question,
                'reponse_user': reponse_user.upper(),
                'correct': correct,
            })

        # Sauvegarder le score
        ScoreCulture.objects.create(
            user=request.user,
            fait=fait,
            score=score,
            total_questions=3,
        )

        # Mettre à jour UserProfile
        profile = UserProfile.objects.get(user=request.user)
        points_gagnes = score * 10
        profile.score_total += points_gagnes
        profile.dernier_score = score
        profile.save()

        return render(request, 'culture/resultat.html', {
            'fait': fait,
            'score': score,
            'total': 3,
            'points_gagnes': points_gagnes,
            'resultats': resultats,
        })

    return render(request, 'culture/quiz.html', {
        'fait': fait,
        'questions': questions,
    })
