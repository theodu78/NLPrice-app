import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import logging
import sqlite3

# Configurer la journalisation
logging.basicConfig(level=logging.INFO)

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = "nlprice"

# Initialiser Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Fonction pour vider la base de données Pinecone
def clear_pinecone_index(index_name):
    try:
        if index_name in pc.list_indexes().names():
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            total_vector_count = stats['total_vector_count']
            if total_vector_count > 0:
                index.delete(deleteAll=True)
                logging.info(f"Pinecone index '{index_name}' has been cleared.")
            else:
                logging.info(f"Pinecone index '{index_name}' is already empty.")
        else:
            logging.info(f"Pinecone index '{index_name}' does not exist.")
    except Exception as e:
        logging.error(f"An error occurred while clearing the Pinecone index: {e}")

# Fonction pour vider la base de données SQLite
def clear_sqlite_database(db_path='data.db'):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Suppression de toutes les données de la table
        cursor.execute('DELETE FROM data')
        conn.commit()
        conn.close()
        logging.info("All SQLite tables have been cleared.")
    except Exception as e:
        logging.error(f"An error occurred while clearing the SQLite database: {e}")

# Exemples d'utilisation
if __name__ == "__main__":
    clear_pinecone_index(INDEX_NAME)
    clear_sqlite_database()
