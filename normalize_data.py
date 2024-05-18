import openai
import pandas as pd
import os
from dotenv import load_dotenv
from io import StringIO

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_openai_agent(data):
    """
    Appelle l'API OpenAI pour normaliser les données.
    
    Args:
    - data (str): Données brutes extraites du devis en texte.
    
    Returns:
    - str: Données structurées sous forme de texte.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Utiliser "gpt-4" ou un autre modèle de chat approprié
        messages=[
            {"role": "system", "content": "Tu es un assistant qui aide à structurer les données des devis."},
            {"role": "user", "content": f"Normalise les données suivantes pour qu'elles respectent le format standard. Voici les données brutes:\n{data}\n\nLes données normalisées doivent être sous la forme de colonnes séparées par des virgules: designation,unit,quantity,unit_price,total_price. Ignore les lignes qui ne sont pas complètement remplies et les lignes où à la fois le total_price et le unit_price sont nuls. Les données doivent être formatées en CSV sans texte supplémentaire."}
        ],
        max_tokens=500,
        temperature=0.5,
    )
    return response['choices'][0]['message']['content']

def normalize_data(extracted_data):
    """
    Normalise les données extraites pour garantir une structure uniforme.
    
    Args:
    - extracted_data (pd.DataFrame): Données brutes extraites sous forme de DataFrame.
    
    Returns:
    - pd.DataFrame: Données normalisées sous forme de DataFrame.
    """
    # Convertir les données extraites en texte brut
    data_text = extracted_data.to_string(index=False)
    
    # Appeler l'agent OpenAI pour normaliser les données
    normalized_text = call_openai_agent(data_text)
    
    # Debug : Afficher le texte normalisé
    print("Texte normalisé renvoyé par l'API OpenAI:")
    print(normalized_text)
    
    # Convertir le texte normalisé en DataFrame
    try:
        normalized_data = pd.read_csv(StringIO(normalized_text))
        
        # Supprimer les lignes où toutes les valeurs ne sont pas remplies
        normalized_data.dropna(inplace=True)
        
        # Supprimer les lignes où total_price et unit_price sont tous deux nuls
        normalized_data = normalized_data[~((normalized_data['total_price'] == 0) & (normalized_data['unit_price'] == 0))]
        
        return normalized_data
    except pd.errors.ParserError as e:
        print(f"Erreur de parsing: {e}")
        return None
