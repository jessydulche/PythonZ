# Chat avec Zylon AI

Une interface de chat utilisant Streamlit pour interagir avec l'API PGPT.

## Prérequis

- Python 3.11 ou supérieur
- Un serveur PGPT en cours d'exécution

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

3. Créez un fichier `.env` à la racine du projet avec l'URL de votre API PGPT :
```
URL=http://localhost:8000
```

## Utilisation

1. Assurez-vous que votre serveur PGPT est en cours d'exécution

2. Lancez l'application Streamlit :
```bash
streamlit run streamlit_chat.py
```

3. Ouvrez votre navigateur à l'adresse indiquée (généralement http://localhost:8501)

## Fonctionnalités

- Interface de chat intuitive
- Historique des conversations
- Intégration avec l'API PGPT via le SDK officiel
- Gestion des erreurs et feedback utilisateur

## Structure du Projet

- `streamlit_chat.py` : Application principale
- `requirements.txt` : Dépendances Python
- `.env` : Configuration de l'API (à créer)

## Dépendances

- streamlit==1.32.0
- httpx>=0.26.0,<0.27.0
- python-dotenv==1.0.1
- pgpt_python==0.1.2

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur le dépôt. 