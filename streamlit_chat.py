import streamlit as st
from dotenv import load_dotenv
import os
import tempfile
import httpx
import json
from datetime import datetime
import pandas as pd
import re
import numpy as np

# Chargement des variables d'environnement
load_dotenv()

# Configuration de l'API
API_URL = os.getenv("URL")
if not API_URL:
    st.error("L'URL de l'API n'est pas définie dans le fichier .env")
    st.stop()

# Configuration des timeouts et limites
UPLOAD_TIMEOUT = 1800  # 30 minutes pour les gros fichiers
MAX_RETRIES = 3
CHUNK_SIZE = 512 * 1024  # 512KB chunks pour plus de stabilité

headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

# Configuration de la page Streamlit
st.set_page_config(page_title="MonChatZylon", page_icon="🤖")
st.title("Chat avec Mistral Small 3")

# Ajout du mode debug
debug_mode = st.sidebar.checkbox("Mode Debug", value=False)

# Initialisation des variables de session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "upload_progress" not in st.session_state:
    st.session_state.upload_progress = {}

# Fonction pour lister les documents ingérés avec pagination et recherche
def list_ingested_documents(search_query=None, page=1, per_page=20):
    try:
        with httpx.Client(timeout=30.0) as client:
            params = {
                "collection": "chat_documents",
                "page": page,
                "per_page": per_page
            }
            if search_query:
                params["search"] = search_query
                
            response = client.get(
                f"{API_URL}/v1/ingest/list",
                params=params,
                headers={"accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la récupération des documents: {str(e)}")
        return None

# Fonction pour supprimer un document
def delete_document(artifact_name):
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_URL}/v1/delete",
                json={
                    "collection": "chat_documents",
                    "artifact": artifact_name
                },
                headers={"accept": "application/json"}
            )
            response.raise_for_status()
            return True
    except Exception as e:
        st.error(f"Erreur lors de la suppression du document: {str(e)}")
        return False


def upload_file_with_progress(file_path, file_name, progress_bar):
    try:
        file_size = os.path.getsize(file_path)
        uploaded_size = 0
        
        # Configuration spéciale pour les gros fichiers PDF
        is_large_pdf = file_name.lower().endswith('.pdf') and file_size > 50 * 1024 * 1024  # > 50MB
        
        with open(file_path, 'rb') as file:
            files = {'file': (file_name, file)}
            params = {
                'artifact': file_name,
                'collection': 'chat_documents'
            }
            
            # Configuration du client avec timeout adapté
            timeout = UPLOAD_TIMEOUT if is_large_pdf else 300  # 30 minutes pour gros PDF, 5 minutes pour autres
            client = httpx.Client(timeout=timeout)
            
            try:
                with client.stream(
                    "POST",
                    f"{API_URL}/v1/ingest/file",
                    headers={"accept": "application/json"},
                    files=files,
                    params=params
                ) as response:
                    response.raise_for_status()
                    
                    # Mise à jour de la barre de progression
                    for chunk in response.iter_bytes():
                        uploaded_size += len(chunk)
                        progress = min(1.0, uploaded_size / file_size)
                        progress_bar.progress(progress)
                    
                    return True
            except httpx.TimeoutException:
                if is_large_pdf:
                    st.warning(f"Le fichier {file_name} est très volumineux. Tentative avec un timeout plus long...")
                    # Nouvelle tentative avec un timeout encore plus long
                    with httpx.Client(timeout=3600) as retry_client:  # 1 heure
                        with retry_client.stream(
                            "POST",
                            f"{API_URL}/v1/ingest/file",
                            headers={"accept": "application/json"},
                            files=files,
                            params=params
                        ) as retry_response:
                            retry_response.raise_for_status()
                            return True
                raise
    except Exception as e:
        raise e
    finally:
        client.close()

# Fonction pour générer des embeddings
def generate_embeddings(text):
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_URL}/v1/embeddings",
                json={"input": text},
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la génération des embeddings: {str(e)}")
        return None

# Fonction pour filtrer les chunks par similarité
def filter_chunks_by_similarity(query_embedding, chunks, threshold=0.7):
    filtered_chunks = []
    for chunk in chunks:
        if "score" in chunk:
            if chunk["score"] > threshold:
                chunk["similarity_score"] = chunk["score"]
                filtered_chunks.append(chunk)
    return sorted(filtered_chunks, key=lambda x: x["similarity_score"], reverse=True)

# Fonction pour rechercher des chunks pertinents
def search_chunks(query, collection="chat_documents", limit=5):
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_URL}/v1/chunks",
                json={
                    "text": query,
                    "context_filter": {
                        "collection": collection
                    },
                    "limit": limit
                },
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la recherche des chunks: {str(e)}")
        return None

# Fonction pour ingérer du texte
def ingest_text(text, artifact_name):
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_URL}/v1/ingest/text",
                json={
                    "text": text,
                    "artifact": artifact_name,
                    "collection": "chat_documents"
                },
                headers=headers
            )
            response.raise_for_status()
            return True
    except Exception as e:
        st.error(f"Erreur lors de l'ingestion du texte: {str(e)}")
        return False

# Sidebar pour le téléchargement des fichiers
with st.sidebar:
    st.header("📁 Gestion des fichiers")
    
    # Bouton pour télécharger l'historique du chat
    if st.session_state.messages:
        chat_history = {
            "messages": st.session_state.messages,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }
        st.download_button(
            label="📥 Télécharger l'historique du chat",
            data=json.dumps(chat_history, ensure_ascii=False, indent=2),
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # Onglets pour choisir entre fichier et texte
    tab1, tab2 = st.tabs(["📄 Fichiers", "📝 Texte"])
    
    with tab1:
        st.subheader("Télécharger des fichiers")
        uploaded_files = st.file_uploader(
            "Choisissez un ou plusieurs fichiers",
            type=['pdf', 'txt', "docx"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            # Afficher un résumé des fichiers à uploader
            st.write("Fichiers sélectionnés :")
            for file in uploaded_files:
                size_mb = file.size / (1024 * 1024)
                st.write(f"- {file.name} ({size_mb:.1f} MB)")
            
            if st.button("Commencer l'upload", type="primary"):
                for uploaded_file in uploaded_files:
                    if uploaded_file.name not in st.session_state.uploaded_files:
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                tmp_file_path = tmp_file.name

                            progress_bar = st.progress(0)
                            file_size = os.path.getsize(tmp_file_path)
                            size_mb = file_size / (1024 * 1024)
                            st.write(f"Upload de {uploaded_file.name} en cours... ({size_mb:.1f} MB)")

                            if upload_file_with_progress(tmp_file_path, uploaded_file.name, progress_bar):
                                st.session_state.uploaded_files.append(uploaded_file.name)
                                st.success(f"Fichier {uploaded_file.name} téléchargé avec succès!")
                            else:
                                st.error(f"Échec du téléchargement de {uploaded_file.name}")

                        except Exception as e:
                            st.error(f"Erreur lors du téléchargement de {uploaded_file.name}: {str(e)}")
                        finally:
                            try:
                                if os.path.exists(tmp_file_path):
                                    os.unlink(tmp_file_path)
                            except Exception as e:
                                st.warning(f"Impossible de supprimer le fichier temporaire: {str(e)}")
                    else:
                        st.info(f"Le fichier {uploaded_file.name} a déjà été téléchargé dans cette session.")
        
        st.divider()
        
        # Affichage des documents existants
        documents = list_ingested_documents()
        if documents and "data" in documents:
            st.subheader("📚 Documents disponibles")
            for doc in documents["data"]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 {doc['artifact']}")
                with col2:
                    if st.button("🗑️", key=f"delete_{doc['artifact']}"):
                        if delete_document(doc['artifact']):
                            st.success(f"Document {doc['artifact']} supprimé avec succès!")
                            st.rerun()
        else:
            st.info("Aucun document disponible")

    with tab2:
        st.subheader("Ingérer du texte")
        text_input = st.text_area("Entrez votre texte ici", height=200)
        text_name = st.text_input("Nom du document")
        
        if st.button("Ingérer le texte", key="ingest_text"):
            if text_input and text_name:
                if ingest_text(text_input, text_name):
                    st.success(f"Texte '{text_name}' ingéré avec succès!")
                    st.rerun()
            else:
                st.warning("Veuillez entrer du texte et un nom de document")

# Affichage de l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            clean_content = re.sub(r'<citation.*?>.*?<\/citation>', '', message["content"], flags=re.DOTALL)
            st.markdown(clean_content)
        else:
            st.markdown(message["content"])

# Zone de saisie pour l'utilisateur
if prompt := st.chat_input("Entrez votre message ici..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Générer l'embedding de la requête
        query_embedding_response = generate_embeddings(prompt)
        if not query_embedding_response or "data" not in query_embedding_response:
            st.error("Impossible de générer l'embedding de la requête")
            st.stop()

        query_embedding = query_embedding_response["data"][0]["embedding"]

        # Rechercher les chunks pertinents
        chunks_response = search_chunks(prompt)
        if not chunks_response or "data" not in chunks_response:
            st.error("Impossible de récupérer les chunks")
            st.stop()

        # Filtrer les chunks par similarité
        filtered_chunks = filter_chunks_by_similarity(query_embedding, chunks_response["data"])
        
        # Construire le contexte à partir des chunks filtrés
        context = "\n".join([chunk["text"] for chunk in filtered_chunks[:3]])  # Prendre les 3 plus pertinents

        # Préparation de la requête avec contexte
        messages = [
            {
                "role": "system",
                "content": "Vous êtes un assistant spécialisé dans la rédaction de documents administratifs. Vos réponses doivent être précises, professionnelles et basées uniquement sur les informations fournies dans le contexte. Vous devez respecter le style et le format des documents existants."
            }
        ]
        
        # Ajouter l'historique des messages
        for message in st.session_state.messages:
            messages.append({
                "role": message["role"],
                "content": message["content"]
            })

        # Configuration du contexte
        data = {
            "messages": messages,
            "use_context": True,
            "context_filter": {
                "collection": "chat_documents"
            },
            "stream": True,
            "include_sources": True,
            "generate_citations": True,
            "use_default_prompt": False  # Désactivé car nous utilisons notre propre prompt système
        }

        # Création d'un conteneur pour le message de l'assistant
        assistant_message = st.chat_message("assistant")
        message_placeholder = assistant_message.empty()
        full_response = ""

        # Envoi de la requête avec streaming
        with httpx.Client(timeout=30.0) as client:
            with client.stream("POST", f"{API_URL}/v1/chat/completions", json=data, headers=headers) as response:
                response.raise_for_status()
                
                if debug_mode:
                    st.write("Réponse brute de l'API:")
                    debug_container = st.empty()
                    raw_response = ""
                
                for line in response.iter_lines():
                    if line:
                        try:
                            # La ligne est déjà en format string
                            if line.startswith('data: '):
                                json_data = json.loads(line[6:])
                                
                                if debug_mode:
                                    raw_response += f"\n{json.dumps(json_data, indent=2, ensure_ascii=False)}"
                                    debug_container.code(raw_response, language="json")
                                
                                # Gérer les différents types d'événements
                                if json_data.get('type') == 'content_block_delta':
                                    delta = json_data.get('delta', {})
                                    if delta.get('type') == 'text_delta':
                                        text = delta.get('text', '')
                                        full_response += text

                                    elif delta.get('type') == 'source_delta':
                                        sources = delta.get('sources', [])
                                        if sources:
                                            # Filtrer les sources avec un score > 0.70
                                            relevant_sources = [s for s in sources if s.get('score', 0) > 0.70]
                                            
                                            if relevant_sources:
                                                st.write("Sources pertinentes (score > 70%) :")
                                                # Trier les sources par score décroissant
                                                for source in sorted(relevant_sources, key=lambda x: x.get('score', 0), reverse=True):
                                                    with st.expander(f"📄 {source.get('document', {}).get('artifact', 'N/A')} (Score: {source.get('score', 0):.2f})"):
                                                        st.write(f"**Document:** {source.get('document', {}).get('artifact', 'N/A')}")
                                                        st.write(f"**Extrait:** {source.get('text', 'N/A')}")
                                                        st.write("---")
                                            else:
                                                st.info("Aucune source avec un score supérieur à 70% n'a été trouvée.")
                                
                        except json.JSONDecodeError as e:
                            continue
                        except Exception as e:
                            continue

        # Mise à jour finale du message
        if full_response:
            clean_response = re.sub(r'<citation.*?>.*?<\/citation>', '', full_response, flags=re.DOTALL)
            message_placeholder.markdown(clean_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        else:
            st.error("Aucune réponse n'a été reçue de l'API")

    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        # Afficher la réponse complète en cas d'erreur
        st.write("Réponse complète:", full_response if full_response else "Pas de réponse disponible")