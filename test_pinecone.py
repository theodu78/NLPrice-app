import os
from dotenv import load_dotenv
import pinecone

# Charger les variables d'environnement
print("Chargement des variables d'environnement...")
load_dotenv()
print("Variables d'environnement chargées.")

# Initialiser Pinecone
print("Initialisation de Pinecone...")
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
print("Pinecone initialisé.")

# Liste des index existants pour vérifier la connexion
print("Liste des index existants :")
print(pinecone.list_indexes())
