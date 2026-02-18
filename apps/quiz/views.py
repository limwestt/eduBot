import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Categorie, Question, TentativeQuiz
from apps.accounts.models import UserProfile

NIVEAUX_CONFIG = {
    'debutant': {'label': 'Débutant', 'nb_questions': 10, 'points_par_reponse': 10, 'seuil_promotion': 80},
    'intermediaire': {'label': 'Intermédiaire', 'nb_questions': 10, 'points_par_reponse': 20, 'seuil_promotion': 80},
    'avance': {'label': 'Avancé', 'nb_questions': 10, 'points_par_reponse': 30, 'seuil_promotion': 80},
}


@login_required
def index(request):
    profile = UserProfile.objects.get(user=request.user)
    stats_niveaux = []
    for niveau_key, config in NIVEAUX_CONFIG.items():
        tentatives = TentativeQuiz.objects.filter(
            user=request.user,
            categorie__niveau=niveau_key
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
    context = {
        'profile': profile,
        'stats_niveaux': stats_niveaux,
    }
    return render(request, 'quiz/index.html', context)


@login_required
def niveau(request, niveau):
    if niveau not in NIVEAUX_CONFIG:
        messages.error(request, "Niveau invalide.")
        return redirect('quiz_index')
    config = NIVEAUX_CONFIG[niveau]
    categories = Categorie.objects.filter(niveau=niveau)
    tentatives = TentativeQuiz.objects.filter(
        user=request.user,
        categorie__niveau=niveau
    ).order_by('-date_tentative')[:5]
    context = {
        'niveau': niveau,
        'config': config,
        'categories': categories,
        'tentatives': tentatives,
    }
    return render(request, 'quiz/niveau.html', context)


@login_required
def commencer_quiz(request, niveau):
    if niveau not in NIVEAUX_CONFIG:
        return redirect('quiz_index')
    config = NIVEAUX_CONFIG[niveau]
    categories = Categorie.objects.filter(niveau=niveau)
    if not categories.exists():
        messages.error(request, "Aucune catégorie disponible pour ce niveau.")
        return redirect('quiz_index')
    categorie = random.choice(list(categories))
    questions = list(Question.objects.filter(categorie=categorie))
    if len(questions) < config['nb_questions']:
        questions_selectionnees = questions
    else:
        questions_selectionnees = random.sample(questions, config['nb_questions'])
    request.session['quiz_niveau'] = niveau
    request.session['quiz_categorie_id'] = categorie.id
    request.session['quiz_questions_ids'] = [q.id for q in questions_selectionnees]
    return redirect('quiz_quiz', niveau=niveau)


@login_required
def quiz(request, niveau):
    if niveau not in NIVEAUX_CONFIG:
        return redirect('quiz_index')
    questions_ids = request.session.get('quiz_questions_ids', [])
    categorie_id = request.session.get('quiz_categorie_id')
    if not questions_ids or not categorie_id:
        messages.error(request, "Session expirée. Recommence le quiz.")
        return redirect('quiz_niveau', niveau=niveau)
    categorie = get_object_or_404(Categorie, id=categorie_id)
    questions = list(Question.objects.filter(id__in=questions_ids))
    questions.sort(key=lambda q: questions_ids.index(q.id))
    if request.method == 'POST':
        config = NIVEAUX_CONFIG[niveau]
        bonnes_reponses = 0
        score_total = 0
        resultats = []
        for question in questions:
            reponse_user = request.POST.get(f'question_{question.id}', '').upper()
            correct = reponse_user == question.bonne_reponse.upper()
            if correct:
                bonnes_reponses += 1
                score_total += question.points
            resultats.append({
                'question': question,
                'reponse_user': reponse_user,
                'correct': correct,
            })
        total_questions = len(questions)
        pourcentage = round((bonnes_reponses / total_questions) * 100, 1) if total_questions > 0 else 0
        temps = int(request.POST.get('temps_employe', 0))
        tentative = TentativeQuiz.objects.create(
            user=request.user,
            categorie=categorie,
            questions_repondus=total_questions,
            bonnes_reponses=bonnes_reponses,
            score_total=score_total,
            pourcentage=pourcentage,
            temps_employe=temps,
        )
        profile = UserProfile.objects.get(user=request.user)
        profile.score_total += score_total
        profile.dernier_score = pourcentage

        # Mise à jour automatique du niveau
        if pourcentage >= config['seuil_promotion']:
            if niveau == 'debutant':
                profile.niveau = 'intermediate'
            elif niveau == 'intermediaire':
                profile.niveau = 'advanced'
        profile.save()

        request.session.pop('quiz_questions_ids', None)
        request.session.pop('quiz_categorie_id', None)
        request.session.pop('quiz_niveau', None)

        request.session['quiz_resultats'] = {
            'categorie_nom': categorie.nom,
            'niveau': niveau,
            'bonnes_reponses': bonnes_reponses,
            'total_questions': total_questions,
            'score_total': score_total,
            'pourcentage': pourcentage,
            'temps': temps,
            'promotion': pourcentage >= config['seuil_promotion'],
        }
        return redirect('quiz_resultat')

    context = {
        'categorie': categorie,
        'questions': questions,
        'niveau': niveau,
        'config': NIVEAUX_CONFIG[niveau],
        'total': len(questions),
    }
    return render(request, 'quiz/quiz.html', context)


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
    ).select_related('categorie').order_by('-date_tentative')
    total_tentatives = tentatives.count()
    moyenne_globale = 0
    if total_tentatives > 0:
        moyenne_globale = round(
            sum(t.pourcentage for t in tentatives) / total_tentatives, 1
        )
    context = {
        'tentatives': tentatives,
        'total_tentatives': total_tentatives,
        'moyenne_globale': moyenne_globale,
    }
    return render(request, 'quiz/historique.html', context)
