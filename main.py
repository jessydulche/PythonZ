import tkinter as tk
from tkinter import scrolledtext
import httpx
import json

# Configuration de l'API
API_URL = "https://3de0f3c3-b58e-40c8-a5dc-72e2bd3be1a6.pub.instances.scw.cloud/gpt/v1/chat/completions"
headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

def envoyer_question():
    question = entree.get()
    if question.strip():
        sortie.insert(tk.END, f"Vous: {question}\n")
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
                        "content": question
                    }
                ]
            }
           
            # Envoi de la requête avec un timeout plus long
            with httpx.Client(timeout=30.0) as client:
                response = client.post(API_URL, headers=headers, json=data)
                print(f"Status Code: {response.status_code}")
                print(f"Response Text: {response.text}")
               
                response.raise_for_status()
               
                # Traitement de la réponse
                result = response.json()
                print(f"Parsed JSON: {json.dumps(result, indent=2)}")
               
                if "content" in result and isinstance(result["content"], list) and len(result["content"]) > 0:
                    # Extraire le texte de la première entrée de content
                    text_content = result["content"][0]["text"]
                    sortie.insert(tk.END, f"Assistant: {text_content}\n\n")
                else:
                    sortie.insert(tk.END, f"Erreur: Format de réponse inattendu. Réponse reçue: {json.dumps(result, indent=2)}\n\n")
        except httpx.TimeoutException:
            sortie.insert(tk.END, "Erreur: La requête a pris trop de temps. Veuillez réessayer.\n\n")
        except Exception as e:
            sortie.insert(tk.END, f"Erreur: {str(e)}\n\n")
        entree.delete(0, tk.END)

fenetre = tk.Tk()
fenetre.title("Chat avec Zylon AI")

sortie = scrolledtext.ScrolledText(fenetre, wrap=tk.WORD, width=80, height=20)
sortie.pack(padx=10, pady=10)

entree = tk.Entry(fenetre, width=70)
entree.pack(side=tk.LEFT, padx=10, pady=10)

bouton_envoyer = tk.Button(fenetre, text="Envoyer", command=envoyer_question)
bouton_envoyer.pack(side=tk.RIGHT, padx=10)

fenetre.mainloop()