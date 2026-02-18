import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST
from groq import Groq
from django.conf import settings
from .models import ConversationMessage

SYSTEM_PROMPT = """Tu es EduBot, un assistant IA intelligent et polyvalent.
Tu peux répondre à toutes sortes de questions : sciences, technologie, histoire, mathématiques, programmation, langues, culture générale, et bien plus encore.
Tu réponds toujours en français, de manière claire, précise et pédagogique.
Tu utilises des exemples concrets pour faciliter la compréhension.
Tu es enthousiaste et bienveillant avec tous les utilisateurs.
Tes réponses sont bien structurées avec des titres et des listes quand c'est pertinent."""


@login_required
def index(request):
    messages = ConversationMessage.objects.filter(user=request.user).order_by('created_at')
    return render(request, 'chat/index.html', {'messages': messages})


@login_required
@require_POST
def envoyer_message(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except Exception:
        return JsonResponse({'error': 'Message invalide'}, status=400)

    if not user_message:
        return JsonResponse({'error': 'Message vide'}, status=400)

    # Sauvegarde message utilisateur
    ConversationMessage.objects.create(
        user=request.user,
        role='user',
        content=user_message
    )

    # Historique pour Groq (max 20 derniers messages)
    historique = ConversationMessage.objects.filter(
        user=request.user
    ).order_by('-created_at')[:20]

    messages_groq = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in reversed(list(historique)):
        messages_groq.append({"role": msg.role, "content": msg.content})

    # Streaming
    def generate():
        client = Groq(api_key=settings.GROQ_API_KEY)
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_groq,
                temperature=0.7,
                max_tokens=1024,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    # Envoie chaque morceau en SSE
                    yield f"data: {json.dumps({'chunk': delta})}\n\n"

            # Sauvegarde la réponse complète en base
            ConversationMessage.objects.create(
                user=request.user,
                role='assistant',
                content=full_response
            )
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingHttpResponse(
        generate(),
        content_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )


@login_required
@require_POST
def effacer_historique(request):
    ConversationMessage.objects.filter(user=request.user).delete()
    return JsonResponse({'status': 'ok'})
