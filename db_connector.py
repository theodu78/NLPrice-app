import pinecone
import sqlalchemy
from sqlalchemy.orm import sessionmaker

# Configuration de Pinecone
pinecone.init(api_key="YOUR_PINECONE_API_KEY")
index = pinecone.Index("construction-prices")

# Configuration de SQLAlchemy
DATABASE_URL = "sqlite:///construction.db"
engine = sqlalchemy.create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def query_pinecone(query):
    # Convertir la requête en vecteur et chercher dans Pinecone
    vector = pinecone.vectorize(query)
    result = index.query(vector=vector, top_k=10)
    return result

def query_sql(query):
    session = SessionLocal()
    # Rechercher dans la base de données SQL
    result = session.execute(f"SELECT * FROM prices WHERE item LIKE '%{query}%'")
    return result.fetchall()
