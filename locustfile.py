from locust import HttpUser, task, between
import json
import random
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Récupération de l'URL de l'API
API_URL = os.getenv("URL")
if not API_URL: 
    raise ValueError("L'URL de l'API n'est pas définie dans le fichier .env")

class ChatUser(HttpUser):
    host = os.getenv("URL")
    wait_time = between(1, 3)  # Temps d'attente entre les requêtes
    
    def on_start(self):
        """Initialisation de l'utilisateur"""
        if not self.host:
            raise ValueError("L'URL de l'API n'est pas définie.")
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        if not self.client:
            raise ValueError("Le client HTTP n'a pas été initialisé.")
        
    @task(3)
    def send_chat_message(self):
        """Simulation d'envoi de message"""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Bonjour, comment allez-vous?"
            }
        ]
        
        data = {
            "messages": messages,
            "use_context": True,
            "context_filter": {
                "collection": "chat_documents"
            },
            "stream": True
        }
        
        with self.client.post(
            "/v1/chat/completions",
            json=data,
            headers=self.headers,
            name="Chat Message",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Échec avec le code {response.status_code}")
    
    @task(1)
    def list_documents(self):
        """Simulation de liste des documents"""
        params = {
            "collection": "chat_documents",
            "page": 1,
            "per_page": 20
        }
        
        with self.client.get(
            "/v1/ingest/list",
            params=params,
            headers={"accept": "application/json"},
            name="List Documents",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Échec avec le code {response.status_code}") 