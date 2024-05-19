import pandas as pd
import openai
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Clé API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Fonction pour vectoriser les données
def vectorize_data(file_path):
    # Lire les données depuis le fichier CSV
    data = pd.read_csv(file_path)
    
    # Combinez toutes les colonnes de chaque ligne en une seule chaîne
    data_combined = data.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    
    # Crée une liste pour stocker les vecteurs
    vectors = []

    # Utiliser l'API d'OpenAI pour obtenir les embeddings
    for text in data_combined:
        response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
        vectors.append(response['data'][0]['embedding'])
    
    return vectors
