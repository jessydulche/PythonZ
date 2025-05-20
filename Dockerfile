# Utiliser une image Python officielle comme base
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier uniquement les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Définir la variable d'environnement
ENV URL=""

# Exposer le port sur lequel Streamlit s'exécute
EXPOSE 8501

# La commande de démarrage sera définie dans docker-compose.yml 