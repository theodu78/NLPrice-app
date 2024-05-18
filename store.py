import pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone as LangchainPinecone
from dotenv import load_dotenv
import os

load_dotenv()

def store_in_pinecone(index_name, vectors):
    # Initialiser les embeddings OpenAI
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    # Utiliser l'index existant
    pinecone_index = LangchainPinecone.from_existing_index(
        index_name=index_name,
        embedding=embeddings
    )
    
    # Upserter les vecteurs dans Pinecone
    pinecone_index.upsert(vectors)

if __name__ == "__main__":
    from vectorize import vectorize_data

    csv_path = "path/to/output.csv"
    index_name = vectorize_data(csv_path)
    store_in_pinecone(index_name)
