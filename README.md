# Chat avec Assistant IA

Une interface de chat moderne utilisant Streamlit pour interagir avec un assistant IA spécialisé en immobilier.

## Prérequis

- Python 3.11 ou supérieur

## Installation

1. Clonez ce dépôt :
```bash
git clone [URL_DU_REPO]
cd [NOM_DU_DOSSIER]
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

1. Lancez l'application Streamlit :
```bash
streamlit run streamlit_chat.py
```

2. Ouvrez votre navigateur à l'adresse indiquée (généralement http://localhost:8501)

## Tests de Charge avec Locust

Le projet inclut des tests de charge utilisant Locust pour simuler le comportement des utilisateurs.

### Installation de Locust

```bash
pip install locust
```

### Configuration

1. Créez un fichier `.env` à la racine du projet :
```
URL=http://localhost:8000
```

### Exécution des Tests

1. Lancez les tests de charge :
```bash
locust -f locustfile.py
```

2. Ouvrez votre navigateur à l'adresse http://localhost:8089

3. Configurez le nombre d'utilisateurs et le taux de spawn

### Métriques Surveillées

- Temps de réponse
- Tokens par seconde
- Temps pour le premier token (TTFT)
- Latence entre les tokens (ITL)
- Taux de réussite des requêtes

### Scénarios de Test

- Simulation d'envoi de messages de chat
- Consultation de la liste des documents
- Temps d'attente aléatoire entre les requêtes (45-180 secondes)

## Fonctionnalités

- Interface de chat intuitive et moderne
- Gestion complète des documents (PDF, TXT, DOCX)
- Historique des conversations
- Assistant IA spécialisé en immobilier
- Gestion des erreurs et feedback utilisateur
- Interface utilisateur responsive
- Système de recherche et filtrage des documents
- Upload de fichiers avec barre de progression
- Gestion de la pagination des documents

## Structure du Projet

- `streamlit_chat.py` : Application principale
- `requirements.txt` : Dépendances Python

## Dépendances

- streamlit==1.32.0
- httpx>=0.26.0,<0.27.0
- python-dotenv==1.0.1
- pandas>=2.0.0
- tqdm>=4.65.0

## Fonctionnalités Détaillées

### Gestion des Documents
- Upload de fichiers multiples (PDF, TXT, DOCX)
- Barre de progression pour les uploads
- Gestion des fichiers volumineux
- Interface de recherche et filtrage
- Suppression de documents
- Pagination des résultats

### Interface de Chat
- Assistant IA spécialisé en immobilier
- Historique des conversations
- Streaming des réponses en temps réel
- Interface utilisateur intuitive

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur le dépôt.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails. 