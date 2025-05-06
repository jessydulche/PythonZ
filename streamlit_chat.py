import streamlit as st
from dotenv import load_dotenv
import os
import tempfile
import contextlib

# Chargement des variables d'environnement
load_dotenv()

# Configuration de l'API
API_URL = os.getenv("URL")
if not API_URL:
    st.error("L'URL de l'API n'est pas définie dans le fichier .env")
    st.stop()

# Configuration de la page Streamlit
st.set_page_config(page_title="Chat avec Assistant IA", page_icon="🤖")
st.title("Chat avec Assistant IA")

# Initialisation des variables de session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# Sidebar pour le téléchargement des fichiers
with st.sidebar:
    st.header("📁 Gestion des fichiers")
    uploaded_file = st.file_uploader("Téléchargez un fichier", type=['txt', 'pdf', 'docx', 'md'])
    
    if uploaded_file is not None:
        try:
            # Créer un fichier temporaire avec un contexte
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Préparer les données pour l'ingestion
            with open(tmp_file_path, 'rb') as file:
                files = {'file': (uploaded_file.name, file)}
                params = {
                    'artifact': uploaded_file.name,
                    'collection': 'chat_documents'
                }
                
                # Envoyer le fichier à l'API
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(
                        f"{API_URL}/v1/ingest/file",
                        headers={"accept": "application/json"},
                        files=files,
                        params=params
                    )
                    response.raise_for_status()
                    
                    # Ajouter le fichier à la liste des fichiers téléchargés
                    st.session_state.uploaded_files.append(uploaded_file.name)
                    st.success(f"Fichier {uploaded_file.name} téléchargé avec succès!")
                
        except Exception as e:
            st.error(f"Erreur lors du téléchargement du fichier: {str(e)}")
        finally:
            # Nettoyer le fichier temporaire de manière sécurisée
            try:
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
            except Exception as e:
                st.warning(f"Impossible de supprimer le fichier temporaire: {str(e)}")
    
    # Afficher la liste des fichiers téléchargés
    if st.session_state.uploaded_files:
        st.subheader("Fichiers téléchargés:")
        for file in st.session_state.uploaded_files:
            st.write(f"📄 {file}")

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
        # Préparation de la requête avec contexte si des fichiers sont présents
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Use the provided context to answer questions accurately."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "use_context": len(st.session_state.uploaded_files) > 0,
            "context_filter": {
                "collection": "chat_documents"
            } if st.session_state.uploaded_files else None
        }

        # Envoi de la requête
        with httpx.Client(timeout=30.0) as client:
            response = client.post(f"{API_URL}/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            
            # Traitement de la réponse
            result = response.json()
            
            # Extraction du texte de la réponse
            if "content" in result and isinstance(result["content"], list):
                # Chercher le bloc de type "text" dans la réponse
                text_content = None
                for content_block in result["content"]:
                    if content_block.get("type") == "text":
                        text_content = content_block.get("text")
                        break
                
                if text_content:
                    # Ajout de la réponse à l'historique
                    st.session_state.messages.append({"role": "assistant", "content": text_content})
                    with st.chat_message("assistant"):
                        st.markdown(text_content)
                else:
                    st.error("Aucun contenu textuel trouvé dans la réponse")
            else:
                st.error(f"Format de réponse inattendu. Réponse reçue: {json.dumps(result, indent=2)}")

    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        # Afficher la réponse complète en cas d'erreur
        st.write("Réponse complète:", result if 'result' in locals() else "Pas de réponse disponible")