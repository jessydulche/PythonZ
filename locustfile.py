from locust import HttpUser, task, between
import json
import random
import os
from dotenv import load_dotenv
import time

# Chargement des variables d'environnement
load_dotenv()

# Récupération de l'URL de l'API
API_URL = os.getenv("URL")
if not API_URL: 
    raise ValueError("L'URL de l'API n'est pas définie dans le fichier .env")

class ChatUser(HttpUser):
    host = os.getenv("URL")
    wait_time = between(1, 3)  # Temps d'attente entre les requêtes
    total_tokens = 0  # Variable pour suivre le nombre total de tokens
    start_time = time.time()  # Temps de début pour le calcul des tokens par seconde
    first_token_time = None  # Temps pour le premier token
    last_token_time = None  # Temps du dernier token
    
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
            catch_response=True,
            stream=True  # Activez le streaming
        ) as response:
            if response.status_code == 200:
                try:
                    for line in response.iter_lines():
                        if line:
                            # Traitez chaque ligne comme un événement
                            line_data = line.decode('utf-8')
                            if line_data.startswith('data: '):
                                json_data = json.loads(line_data[6:])  # Ignorez le préfixe 'data: '
                                # Traitez les données JSON ici
                                if 'usage' in json_data:
                                    input_tokens = json_data['usage'].get('input_tokens', 0)
                                    output_tokens = json_data['usage'].get('output_tokens', 0)
                                    self.total_tokens += (input_tokens + output_tokens)

                                    # Enregistrez le temps du premier token
                                    if self.first_token_time is None:
                                        self.first_token_time = time.time()

                                    # Enregistrez le temps du dernier token
                                    self.last_token_time = time.time()

                                    self.log_tokens_per_second()
                                # Vous pouvez également gérer d'autres types d'événements ici
                    response.success()
                except json.JSONDecodeError:
                    response.failure(f"Erreur de décodage JSON : {response.text}")
            else:
                response.failure(f"Échec avec le code {response.status_code}. Contenu : {response.text}")
    
    def log_tokens_per_second(self):
        """Affiche le nombre de tokens par seconde et d'autres métriques"""
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            tokens_per_second = self.total_tokens / elapsed_time
            print(f"Tokens par seconde : {tokens_per_second:.2f}")

            # Calculer le temps pour le premier token
            if self.first_token_time:
                ttft = self.first_token_time - self.start_time
                print(f"Temps pour le premier token (TTFT) : {ttft:.2f} secondes")

            # Calculer la latence entre les tokens
            if self.last_token_time and self.first_token_time:
                itl = self.last_token_time - self.first_token_time
                print(f"Latence entre les tokens (ITL) : {itl:.2f} secondes")

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