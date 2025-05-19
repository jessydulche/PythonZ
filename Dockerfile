# Utiliser une image Python officielle comme base
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code source
COPY . .

# Définir la variable d'environnement
ENV URL=""

# Exposer le port sur lequel Streamlit s'exécute
EXPOSE 8501

# Commande pour démarrer l'application
CMD ["streamlit", "run", "streamlit_chat.py", "--server.address", "0.0.0.0"] 