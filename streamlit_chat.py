import streamlit as st
from dotenv import load_dotenv
import os
from pgpt_python.client import PrivateGPTApi

# Chargement des variables d'environnement
load_dotenv()

# Configuration de l'API
API_URL = os.getenv("URL")
if not API_URL:
    st.error("L'URL de l'API n'est pas définie dans le fichier .env")
    st.stop()

# Configuration de la page Streamlit
st.set_page_config(page_title="Chat avec Zylon AI", page_icon="🤖")
st.title("Chat avec Zylon AI")

# Affichage de l'URL de l'API (pour le débogage)
st.sidebar.write(f"URL de l'API: {API_URL}")

# Initialisation du client PGPT
try:
    client = PrivateGPTApi(base_url=API_URL)
    st.sidebar.success("Client initialisé")
except Exception as e:
    st.error(f"Erreur lors de l'initialisation du client: {str(e)}")
    st.stop()

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
        # Envoi de la requête via le SDK
        st.sidebar.write("Envoi de la requête...")
        response = client.contextual_completions.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Traitement de la réponse
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            # Ajout de la réponse à l'historique
            assistant_response = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
        else:
            st.error("Format de réponse inattendu")
            st.write("Réponse reçue:", response)

    except Exception as e:
        st.error(f"Erreur lors de l'envoi de la requête: {str(e)}")
        st.write("Détails de l'erreur:", str(e))
        st.sidebar.error("Échec de la requête") 