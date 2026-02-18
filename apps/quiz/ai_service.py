import json
import re
from groq import Groq
from django.conf import settings

NIVEAUX_PROMPTS = {
    'debutant': {
        'label': 'débutant',
        'sujet': 'trading, bourse, e-commerce et finance personnelle pour débutants',
        'difficulte': 'très simples, vocabulaire basique, concepts fondamentaux',
    },
    'intermediaire': {
        'label': 'intermédiaire',
        'sujet': 'analyse technique, indicateurs boursiers, stratégies e-commerce',
        'difficulte': 'modérées, nécessitent des connaissances de base',
    },
    'avance': {
        'label': 'avancé',
        'sujet': 'options, dérivés, analyse fondamentale avancée, gestion du risque',
        'difficulte': 'difficiles, nécessitent une expertise solide',
    },
}


def generer_questions(niveau, nb_questions=10):
    config = NIVEAUX_PROMPTS.get(niveau)
    if not config:
        return None

    prompt = f"""Tu es un expert en {config['sujet']}.

Génère exactement {nb_questions} questions de quiz de niveau {config['label']} sur : {config['sujet']}.
Les questions doivent être {config['difficulte']}.

RÈGLES :
- 4 choix (A, B, C, D) par question
- Une seule bonne réponse
- Questions VARIÉES et DIFFÉRENTES à chaque génération
- Inclure une explication courte

Réponds UNIQUEMENT avec un JSON valide, sans texte avant ou après :
{{
  "questions": [
    {{
      "texte": "La question ?",
      "choix_a": "Choix A",
      "choix_b": "Choix B",
      "choix_c": "Choix C",
      "choix_d": "Choix D",
      "bonne_reponse": "A",
      "explication": "Explication courte"
    }}
  ]
}}"""

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,
            max_tokens=4096,
        )

        raw = response.choices[0].message.content.strip()
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        raw = raw.strip()

        data = json.loads(raw)
        questions = data.get('questions', [])

        questions_valides = []
        for q in questions:
            if all(k in q for k in ['texte', 'choix_a', 'choix_b', 'choix_c', 'choix_d', 'bonne_reponse']):
                questions_valides.append(q)

        return questions_valides[:nb_questions]

    except Exception as e:
        print(f"Erreur Groq : {e}")
        return None
