import streamlit as st
import httpx
import json
from dotenv import load_dotenv
import os

# Chargement des variables d'environnement
load_dotenv()

# Configuration de l'API
API_URL = os.getenv("URL")
if not API_URL:
    st.error("L'URL de l'API n'est pas définie dans le fichier .env")
    st.stop()

headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

# Configuration de la page Streamlit
st.set_page_config(page_title="Chat avec Zylon AI", page_icon="🤖")
st.title("Chat avec Zylon AI")

# Initialisation de l'historique des messages dans la session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie pour l'utilisateur
if prompt := st.chat_input("Entrez votre message ici..."):
    # Ajout du message de l'utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Préparation de la requête
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        # Envoi de la requête
        with httpx.Client(timeout=30.0) as client:
            response = client.post(API_URL, headers=headers, json=data)
            response.raise_for_status()
            
            # Traitement de la réponse
            result = response.json()
            
            if "content" in result and isinstance(result["content"], list) and len(result["content"]) > 0:
                # Extraire le texte de la première entrée de content
                text_content = result["content"][0]["text"]
                # Ajout de la réponse à l'historique
                st.session_state.messages.append({"role": "assistant", "content": text_content})
                with st.chat_message("assistant"):
                    st.markdown(text_content)
            else:
                st.error(f"Format de réponse inattendu. Réponse reçue: {json.dumps(result, indent=2)}")

    except httpx.TimeoutException:
        st.error("La requête a pris trop de temps. Veuillez réessayer.")
    except Exception as e:
        st.error(f"Erreur: {str(e)}") 