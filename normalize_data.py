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
    prompt = f"""
    Tu es un assistant qui aide à structurer les données des devis. Les devis contiennent des informations sur les articles, les unités, les quantités, les prix unitaires et les prix totaux. 

    Les données normalisées doivent respecter le format suivant :
    designation, unit, quantity, unit_price, total_price

    Quelques règles à suivre :
    1. Ne pas prendre en compte les prix mentionnés TTC.
    2. Ignore les lignes qui ne contiennent que des titres, sous-titres, ou lignes vides.
    3. Ignore les lignes qui ne contiennent pas de prix.
    4. Ignore les lignes qui ne contiennent pas d'article.
    5. Ignore une ligne qui te parait vague, hors sujet, ou qui ne comportes pas de prix.
    6. Convertis tous les prix dans un format numérique standard sans symbole de devise (par exemple, 1234.56 au lieu de 1 234,56 €).
    7. Ignore les caractères non pertinents comme les espaces ou les symboles de devise.
    8. Assure-toi que les lignes de données contiennent des articles et des prix cohérents.
    9. Les nombres doivent être bien séparés des unités et des virgules pour éviter toute confusion.
    10. Encapsule entre guillemets les éléments qui contiennent des guillemets dans les article
    11. Assure-toi que chaque ligne est bien encapsulée et qu'il n'y a pas de retour à la ligne dans les champs, pour ne pas polluler la structure du CSV.

    Voici les données brutes à normaliser :
    {data}

    Les données normalisées doivent être sous forme de colonnes séparées par des virgules : designation, unit, quantity, unit_price, total_price. Les données doivent être formatées en CSV sans texte supplémentaire.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es un assistant qui aide à structurer les données des devis."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.0,  # Température abaissée pour des réponses plus prévisibles
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
    # Remplacer toutes les virgules par des points dans le DataFrame
    extracted_data = extracted_data.applymap(lambda x: str(x).replace(',', '.') if isinstance(x, str) else x)
    
    # Convertir les données extraites en texte brut
    data_text = extracted_data.to_csv(index=False)
    
    # Debug: Afficher les données brutes avant de les envoyer à l'agent
    print("Données brutes extraites:")
    print(data_text)
    
    # Appeler l'agent OpenAI pour normaliser les données
    normalized_text = call_openai_agent(data_text)
    
    # Debug: Afficher le texte normalisé renvoyé par OpenAI
    print("Texte normalisé renvoyé par l'API OpenAI:")
    print(normalized_text)
    
    # Nettoyer le texte normalisé
    cleaned_text, skipped_lines = clean_text(normalized_text)
    
    # Afficher les lignes non retenues
    print("Lignes non retenues:")
    for line in skipped_lines:
        print(line)
    
    # Convertir le texte nettoyé en DataFrame
    try:
        normalized_data = pd.read_csv(StringIO(cleaned_text))
        return normalized_data
    except pd.errors.ParserError as e:
        print(f"Erreur de parsing: {e}")
        return None

def clean_text(text):
    """
    Nettoie le texte renvoyé par OpenAI pour s'assurer qu'il est au format CSV attendu.
    
    Args:
    - text (str): Texte renvoyé par OpenAI.
    
    Returns:
    - str: Texte nettoyé prêt à être converti en DataFrame.
    - list: Liste des lignes non retenues.
    """
    lines = text.strip().split("\n")
    csv_lines = []
    skipped_lines = []
    
    for line in lines:
        if line and not line.startswith("```") and not line.startswith("Note:"):
            if ',' in line:  # S'assurer que la ligne contient des virgules
                csv_lines.append(line)
            else:
                skipped_lines.append(line)
    
    if not csv_lines:
        raise ValueError("Le format du texte renvoyé par OpenAI n'est pas correct.")
    
    return "\n".join(csv_lines), skipped_lines

