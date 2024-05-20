import pinecone
import openai
from dotenv import load_dotenv
import os

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

def store_in_pinecone(data):
    vectors = []
    for i, record in enumerate(data):
        embedding = generate_embedding(record["designation"])
        vectors.append({'id': str(i), 'values': embedding, 'metadata': record})
    
    # Upserter les vecteurs dans Pinecone
    index.upsert(vectors=vectors)

if __name__ == "__main__":
    # Données à insérer
    data = [
        {"designation": "Curage complet et mise à nu des locaux", "unit": "M2", "quantity": 444.61, "unit_price": 48, "total_price": 21341},
        {"designation": "Total Bâtiment réhabilité", "unit": "U", "quantity": 2, "unit_price": 360, "total_price": 720}
    ]
    
    store_in_pinecone(data)
