import streamlit as st
import openai
import sqlite3
import pinecone
from dotenv import load_dotenv
import os
import logging

# Configurer le logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les clés API et les informations de connexion à partir d'un fichier de configuration
load_dotenv()

# Configurer l'API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configurer Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = "nlprice"

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

# Fonction pour interroger la base de données SQL
def query_db(question):
    logger.info(f"Interrogation de la base de données SQL avec la question: {question}")
    conn = sqlite3.connect('data.db')  # Mettre à jour le chemin de la base de données
    cursor = conn.cursor()
    
    # Exécuter une requête SQL basée sur la question
    cursor.execute("SELECT designation, unit, unit_price FROM articles WHERE designation LIKE ?", ('%' + question + '%',))
    results = cursor.fetchall()
    
    conn.close()
    logger.info(f"Résultats de la base de données SQL: {results}")
    return results

# Fonction pour interroger Pinecone
def query_pinecone(question, top_k=1):
    logger.info(f"Interrogation de Pinecone avec la question: {question}")
    embedding = openai.Embedding.create(input=question, model="text-embedding-ada-002")['data'][0]['embedding']
    results = index.query(vector=embedding, top_k=top_k, include_values=False, include_metadata=True)
    logger.info(f"Résultats de Pinecone: {results['matches']}")
    return results['matches']

# Interface utilisateur Streamlit
st.title("Rechercher un Prix")

example_question = "prix d'un éclairage de chantier ?"
question = st.text_input("Posez votre question ici :", placeholder=example_question)

st.write("Nombre de résultats :")
top_k = st.slider("", min_value=1, max_value=50, value=1)

if st.button("Envoyer"):
    if question:
        # Interroger la base de données SQL
        results_db = query_db(question)
        
        # Interroger Pinecone
        results_pinecone = query_pinecone(question, top_k=top_k)
        
        if results_db:
            st.write("Voici les résultats de la base de données SQL :")
            for designation, unit, unit_price in results_db:
                st.write(f"Article : {designation} = {unit_price} €/ {unit}")
        else:
            st.write("Aucun résultat trouvé dans la base de données SQL.")
            logger.info("Aucun résultat trouvé dans la base de données SQL.")

        if results_pinecone:
            st.write("Voici les résultats de Pinecone :")
            for match in results_pinecone:
                metadata = match['metadata']
                st.write(f"Article : {metadata['designation']} = {metadata['unit_price']} €/ {metadata['unit']}")
        else:
            st.write("Aucun résultat trouvé dans Pinecone.")
            logger.info("Aucun résultat trouvé dans Pinecone.")
    else:
        st.write("Veuillez poser une question.")
        logger.info("Aucune question posée.")
