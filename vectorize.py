import pinecone
from langchain.vectorstores import LangchainPinecone
import pandas as pd
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Obtenir l'API key de Pinecone et initialiser le client
api_key = os.getenv("PINECONE_API_KEY")
pinecone.init(api_key=api_key, environment="us-east-1")

# Initialiser le client Pinecone
pc_client = pinecone.Client(api_key=api_key)

def vectorize_data(csv_path):
    # Lire les données depuis le fichier CSV
    df = pd.read_csv(csv_path)

    # Préparer les textes à vectoriser
    texts = df['Article'].tolist()

    # Vérifier si l'index existe
    index_name = "nlprice"
    if index_name not in pc_client.list_indexes():
        raise ValueError(f"Index '{index_name}' does not exist.")

    # Créer ou utiliser un index existant
    vector_store = LangchainPinecone.from_texts(
        texts,
        index_name=index_name,
        api_key=api_key
    )
    return vector_store
