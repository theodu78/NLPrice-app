import openai
from dotenv import load_dotenv
import os
from db_connector import query_sql, query_pinecone

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ChatAgent:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
    
    def get_response(self, user_input):
        # Utilisation de l'API OpenAI pour obtenir une réponse NLP
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"User: {user_input}\nAI:",
            max_tokens=150
        )
        answer = response.choices[0].text.strip()
        
        # Rechercher dans Pinecone et SQL
        pinecone_results = query_pinecone(user_input)
        sql_results = query_sql(user_input)
        
        # Fusionner et formater les résultats
        results = self.merge_results(pinecone_results, sql_results)
        
        return answer + "\n" + "\n".join(results)
    
    def merge_results(self, pinecone_results, sql_results):
        # Fusionner et classer les résultats des deux bases de données
        merged_results = pinecone_results + sql_results
        sorted_results = sorted(merged_results, key=lambda x: x['score'], reverse=True)
        formatted_results = [f"{res['item']}: {res['price']}" for res in sorted_results]
        return formatted_results
