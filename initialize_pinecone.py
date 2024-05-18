import os
from dotenv import load_dotenv, find_dotenv
from pinecone import Pinecone, ServerlessSpec

# Charger les variables d'environnement
dotenv_path = find_dotenv()
if dotenv_path == "":
    print("Aucun fichier .env trouvé")
else:
    print(f"Fichier .env trouvé à : {dotenv_path}")
    load_dotenv(dotenv_path)

# Initialiser Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))

# Nom de l'index
index_name = "nlprice"

# Créer l'index si nécessaire
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name, 
        dimension=1536, 
        metric="cosine", 
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

print(f"L'index '{index_name}' a été initialisé.")
