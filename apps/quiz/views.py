import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TentativeQuiz
from .ai_service import generer_questions
from apps.accounts.models import UserProfile

NIVEAUX_CONFIG = {
    'debutant':       {'label': 'Débutant',       'nb_questions': 10, 'points_par_reponse': 10, 'seuil_promotion': 80},
    'intermediaire':  {'label': 'Intermédiaire',   'nb_questions': 10, 'points_par_reponse': 20, 'seuil_promotion': 80},
    'avance':         {'label': 'Avancé',           'nb_questions': 10, 'points_par_reponse': 30, 'seuil_promotion': 80},
}


@login_required
def index(request):
    profile = UserProfile.objects.get(user=request.user)
    stats_niveaux = []
    for niveau_key, config in NIVEAUX_CONFIG.items():
        tentatives = TentativeQuiz.objects.filter(
            user=request.user,
            niveau=niveau_key
        )
        meilleur = tentatives.order_by('-pourcentage').first()
        stats_niveaux.append({
            'niveau': niveau_key,
            'label': config['label'],
            'nb_tentatives': tentatives.count(),
            'meilleur': meilleur,
            'points_par_reponse': config['points_par_reponse'],
            'nb_questions': config['nb_questions'],
        })
    return render(request, 'quiz/index.html', {
        'profile': profile,
        'stats_niveaux': stats_niveaux,
    })


@login_required
def niveau(request, niveau):
    if niveau not in NIVEAUX_CONFIG:
        return redirect('quiz_index')
    tentatives = TentativeQuiz.objects.filter(
        user=request.user,
        niveau=niveau
    ).order_by('-date_tentative')[:5]
    return render(request, 'quiz/niveau.html', {
        'niveau': niveau,
        'config': NIVEAUX_CONFIG[niveau],
        'tentatives': tentatives,
    })


@login_required
def commencer_quiz(request, niveau):
    if niveau not in NIVEAUX_CONFIG:
        return redirect('quiz_index')

    config = NIVEAUX_CONFIG[niveau]

    # Génération ai
    questions = generer_questions(niveau, config['nb_questions'])

    if not questions:
        messages.error(request, "Impossible de générer les questions. Réessaie dans quelques secondes.")
        return redirect('quiz_niveau', niveau=niveau)

    # Stocker en session
    request.session['quiz_niveau'] = niveau
    request.session['quiz_questions'] = questions

    return redirect('quiz_quiz', niveau=niveau)


@login_required
def quiz(request, niveau):
    if niveau not in NIVEAUX_CONFIG:
        return redirect('quiz_index')

    questions = request.session.get('quiz_questions', [])
    if not questions:
        messages.error(request, "Session expirée. Recommence le quiz.")
        return redirect('quiz_niveau', niveau=niveau)

    if request.method == 'POST':
        config = NIVEAUX_CONFIG[niveau]
        bonnes_reponses = 0
        score_total = 0
        resultats = []

        for i, question in enumerate(questions):
            reponse_user = request.POST.get(f'question_{i}', '').upper()
            correct = reponse_user == question['bonne_reponse'].upper()
            if correct:
                bonnes_reponses += 1
                score_total += config['points_par_reponse']
            resultats.append({
                'texte': question['texte'],
                'choix_a': question['choix_a'],
                'choix_b': question['choix_b'],
                'choix_c': question['choix_c'],
                'choix_d': question['choix_d'],
                'bonne_reponse': question['bonne_reponse'],
                'explication': question.get('explication', ''),
                'reponse_user': reponse_user,
                'correct': correct,
            })

        total_questions = len(questions)
        pourcentage = round((bonnes_reponses / total_questions) * 100, 1) if total_questions > 0 else 0
        temps = int(request.POST.get('temps_employe', 0))

        TentativeQuiz.objects.create(
            user=request.user,
            niveau=niveau,
            questions_repondus=total_questions,
            bonnes_reponses=bonnes_reponses,
            score_total=score_total,
            pourcentage=pourcentage,
            temps_employe=temps,
        )

        # Mise à jour profil
        profile = UserProfile.objects.get(user=request.user)
        profile.score_total += score_total
        profile.dernier_score = pourcentage
        if pourcentage >= config['seuil_promotion']:
            if niveau == 'debutant':
                profile.niveau = 'intermediate'
            elif niveau == 'intermediaire':
                profile.niveau = 'advanced'
        profile.save()

        request.session.pop('quiz_questions', None)
        request.session.pop('quiz_niveau', None)

        request.session['quiz_resultats'] = {
            'niveau': niveau,
            'label': config['label'],
            'bonnes_reponses': bonnes_reponses,
            'total_questions': total_questions,
            'score_total': score_total,
            'pourcentage': pourcentage,
            'temps': temps,
            'promotion': pourcentage >= config['seuil_promotion'],
            'resultats': resultats,
        }
        return redirect('quiz_resultat')

    return render(request, 'quiz/quiz.html', {
        'questions': questions,
        'niveau': niveau,
        'config': NIVEAUX_CONFIG[niveau],
        'total': len(questions),
    })


@login_required
def resultat(request):
    data = request.session.get('quiz_resultats')
    if not data:
        return redirect('quiz_index')
    return render(request, 'quiz/resultat.html', {'data': data})


@login_required
def historique(request):
    tentatives = TentativeQuiz.objects.filter(
        user=request.user
    ).order_by('-date_tentative')
    total = tentatives.count()
    moyenne = round(sum(t.pourcentage for t in tentatives) / total, 1) if total > 0 else 0
    return render(request, 'quiz/historique.html', {
        'tentatives': tentatives,
        'total_tentatives': total,
        'moyenne_globale': moyenne,
    })
