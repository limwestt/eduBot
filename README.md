# EduBot — Plateforme E-learning IA

EduBot est une plateforme d'apprentissage moderne propulsée par l'IA (Groq).
Elle permet de créer des quiz personnalisés, d'analyser des documents PDF
et de poser des questions à un assistant IA en temps réel.

---

## Fonctionnalités

| Module | Description |
|---|---|
| Quiz IA | Thème libre + 3 niveaux de difficulté — 5 questions générées par Groq |
| Documents | Upload PDF — l'IA génère un quiz à partir du contenu |
| Chat IA | Réponses en streaming temps réel avec rendu Markdown |
| Dashboard | Statistiques, graphiques Chart.js, streak, classement |
| Culture | 50 faits + 150 questions, quiz 3 niveaux |
| Authentification | Inscription, connexion, profil, historique |

---

## Stack technique

| Couche | Technologie |
|---|---|
| Backend | Django 5.1 + Python 3.13 |
| IA | Groq API (Llama3-8B) + PyPDF2 |
| Frontend | Tailwind CSS + Chart.js |
| Base de données | SQLite (dev) / PostgreSQL (prod) |
| Déploiement | Railway |

---

## Installation locale

### Prérequis

- Python 3.13+
- Une clé API Groq ([console.groq.com](https://console.groq.com))

### Étapes

 Clone le repo :
   ```bash
   git clone https://github.com/limwest/edubot.git
   cd edubot
Installe les dépendances :

bash
pip install -r requirements.txt
Configure les variables d'environnement :

bash
cp .env.example .env
Remplis .env :

text
SECRET_KEY=ton-secret-key
GROQ_API_KEY=ta-cle-groq
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
Applique les migrations :

bash
python manage.py migrate
Crée un superutilisateur :

bash
python manage.py createsuperuser
Lance le serveur :

bash
python manage.py runserver
Accède à l'application : http://127.0.0.1:8000
