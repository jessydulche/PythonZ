# Chatbot Zylon AI avec Streamlit

Une interface de chat moderne et interactive utilisant Streamlit pour communiquer avec l'API Zylon AI.

## 🚀 Fonctionnalités

- Interface utilisateur moderne et responsive
- Historique des conversations
- Support du formatage Markdown
- Gestion des erreurs et des timeouts
- Interface intuitive de type chat

## 📋 Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

## 🔧 Installation

1. Clonez ce dépôt :
```bash
git clone [URL_DU_REPO]
cd [NOM_DU_DOSSIER]
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Créez un fichier `.env` à la racine du projet et ajoutez votre URL d'API :
```
URL=votre_url_api_ici
```

## 🎮 Utilisation

Pour lancer l'application :

```bash
streamlit run streamlit_chat.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut.

## 📦 Dépendances

- streamlit==1.32.0
- httpx==0.27.0
- python-dotenv==1.0.1

## 🔍 Structure du Projet

```
.
├── streamlit_chat.py    # Application principale
├── requirements.txt     # Dépendances du projet
├── .env                # Variables d'environnement
└── README.md          # Documentation
```

## ⚠️ Notes

- Assurez-vous d'avoir une connexion Internet active pour communiquer avec l'API
- Le fichier `.env` ne doit pas être partagé ou commité dans le dépôt
- Les timeouts sont configurés à 30 secondes par défaut

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request. 