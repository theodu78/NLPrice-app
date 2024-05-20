import pinecone
import openai
import pandas as pd
from dotenv import load_dotenv
import os
import sys
from datetime import datetime

# Charger les clés API depuis le fichier .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = "nlprice"

# Initialiser OpenAI
openai.api_key = OPENAI_API_KEY

# Initialiser Pinecone
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=PINECONE_API_KEY)

# Vérifier si l'index existe, sinon le créer
if INDEX_NAME not in pc.list_indexes().names():
    print(f"Creating index {INDEX_NAME}...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

# Connecter à l'index existant
index = pc.Index(INDEX_NAME)

def generate_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

def store_in_pinecone(file_path):
    try:
        data = pd.read_csv(file_path)
        vectors = []
        for i, record in data.iterrows():
            embedding = generate_embedding(record["designation"])
            unique_id = f"{datetime.now().timestamp()}_{i}"
            vectors.append({'id': unique_id, 'values': embedding, 'metadata': record.to_dict()})
        
        # Upserter les vecteurs dans Pinecone
        print("Upserting vectors into Pinecone...")
        index.upsert(vectors=vectors)
        print("Vectors upserted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Prendre le chemin du fichier CSV en argument
    if len(sys.argv) < 2:
        print("Usage: python store.py <path_to_csv>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    print(f"Storing data from {csv_path} into Pinecone...")
    store_in_pinecone(csv_path)
