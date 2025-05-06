# Chat avec Zylon AI

Une application de chat simple utilisant l'API Zylon AI avec une interface graphique Tkinter.

## Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

## Installation

1. Clonez ce dépôt :
```bash
git clone [URL_DU_REPO]
cd [NOM_DU_DOSSIER]
```

2. Créez un environnement virtuel (recommandé) :
```bash
python -m venv venv
```

3. Activez l'environnement virtuel :
- Windows :
```bash
venv\Scripts\activate
```
- Linux/Mac :
```bash
source venv/bin/activate
```

4. Installez les dépendances :
```bash
pip install -r requirements.txt
```

5. Créez un fichier `.env` à la racine du projet avec votre URL d'API :
```
URL=votre_url_api_ici
```

## Utilisation

1. Lancez l'application :
```bash
python main.py
```

2. Une fenêtre de chat s'ouvrira où vous pourrez :
   - Écrire votre message dans le champ de texte
   - Cliquer sur "Envoyer" ou appuyer sur Entrée pour envoyer votre message
   - Voir la conversation dans la zone de texte principale

## Structure du projet

- `main.py` : Application principale
- `requirements.txt` : Liste des dépendances
- `.env` : Configuration (non versionné)
- `.gitignore` : Fichiers à ignorer par Git

## Sécurité

- Le fichier `.env` n'est pas versionné pour protéger vos informations sensibles
- Assurez-vous de ne jamais partager votre fichier `.env` ou votre URL d'API

## Dépendances principales

- `httpx` : Pour les requêtes HTTP
- `python-dotenv` : Pour la gestion des variables d'environnement
- `tkinter` : Pour l'interface graphique (inclus dans Python) 