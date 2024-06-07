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
    Tu es un assistant qui aide à structurer les données des devis. Tu dois repérer et extraire des devis les articles, les unités et les prix unitaires. 

    Ton objectif est de structurer les données vers un format csv. Ainsi les données normalisées doivent respecter le format suivant :
    designation, unit, unit_price,

    Quelques règles à suivre :
    1. Ignore les colonnes total_price et quantity
    2. Ignore les lignes qui contiennent de titres, sous-titres, ou lignes vides.
    3. Ignore les lignes qui ne contiennent pas d'article.
    4. Ignore les lignes dont le unit_price est nul.
    5. Ignore les lignes qui te paraissent vagues, hors sujet ou incertaines.
    6. Convertis tous les prix dans un format numérique standard sans symbole de devise (par exemple, 1234.56 au lieu de 1 234,56 €).
    7. Ignore les caractères non pertinents comme les espaces ou les symboles de devise.
    8. Assure-toi que les lignes de données contiennent des articles et des prix cohérents.
    9. Assure-toi que chaque ligne est bien encapsulée et qu'il n'y a pas de retour à la ligne dans les champs, pour ne pas polluer la structure du CSV.
    10. Si un unit est manquant essaye de le deviner ou bien ajoute "?".
    11. Pour que les données de sortie au format csv restent pure, tu ne dois pas ajouter de rapport, ni de note ou de commentaires après le tableau. 
    12. Pour identifier facilement le tableau CSV dans la réponse, ajoute un caret (^) au début et à la fin du tableau CSV. Le résultat final doit être encadré par des carets (^) comme indiqué ci-dessous :

    ^
    "designation","unit","unit_price"
    "article_1","unit_1","unit_price_1"
    "article_2","unit_2","unit_price_2"
    ...
    ^

    Voici les données brutes à normaliser :
    {data}

    IMPORTANT : interdiction d'ajouter du text en fin. Les données normalisées doivent être sous forme de colonnes séparées par des virgules : designation, unit, unit_price.
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

def extract_csv_from_response(response):
    """
    Extrait le contenu CSV encadré par des carets (^) dans la réponse.
    
    Args:
    - response (str): Texte renvoyé par OpenAI.
    
    Returns:
    - str: Contenu CSV extrait.
    """
    start = response.find('^') + 1
    end = response.rfind('^')
    if start == 0 or end == -1:
        raise ValueError("Le format du texte renvoyé par OpenAI n'est pas correct.")
    return response[start:end].strip()

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
    
    # Extraire le contenu CSV entre les carets (^)
    csv_content = extract_csv_from_response(normalized_text)
    
    # Convertir le texte CSV extrait en DataFrame
    try:
        normalized_data = pd.read_csv(StringIO(csv_content))
        
        # Debug: Afficher le DataFrame avant conversion des types
        print("DataFrame normalisé avant conversion des types:")
        print(normalized_data)
        print(normalized_data.dtypes)
        
        # Vérifier et remplacer les valeurs NaN
        normalized_data = normalized_data.fillna('')

        # Debug: Afficher le DataFrame après remplacement des NaN
        print("DataFrame après remplacement des NaN:")
        print(normalized_data)
        print(normalized_data.dtypes)

        # Convertir les colonnes en types numériques si possible
        normalized_data['unit_price'] = pd.to_numeric(normalized_data['unit_price'], errors='coerce')
        
        # Debug: Afficher le DataFrame après conversion des types
        print("DataFrame après conversion des types:")
        print(normalized_data)
        print(normalized_data.dtypes)
        
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
        if line and not line.startswith("```"):
            if ',' in line:  # S'assurer que la ligne contient des virgules
                csv_lines.append(line)
            else:
                skipped_lines.append(line)
    
    if not csv_lines:
        raise ValueError("Le format du texte renvoyé par OpenAI n'est pas correct.")
    
    return "\n".join(csv_lines), skipped_lines

def store_data_in_pinecone(dataframe):
    """
    Envoie les données normalisées à Pinecone.
    
    Args:
    - dataframe (pd.DataFrame): Données normalisées sous forme de DataFrame.
    """
    # Convertir le DataFrame en dictionnaire
    data_dict = dataframe.to_dict(orient='records')
    
    # Envoyer les données à Pinecone
    for record in data_dict:
        # Vérifier que toutes les valeurs nécessaires sont présentes et correctes
        if not all(k in record and record[k] != '' for k in ('designation', 'unit', 'unit_price')):
            print(f"Enregistrement invalide: {record}")
            continue

        # Créer un vecteur pour chaque enregistrement
        vector = {
            'id': f"{record['designation']}_{record['unit']}",
            'values': [record['unit_price']],
            'metadata': record
        }

        # Insérer le vecteur dans Pinecone
        try:
            # Code d'insertion dans Pinecone
            pass
        except Exception as e:
            print(f"Erreur lors de l'insertion dans Pinecone: {e}")

def store_data_in_db(dataframe):
    """
    Envoie les données normalisées à une base de données SQL.
    
    Args:
    - dataframe (pd.DataFrame): Données normalisées sous forme de DataFrame.
    """
    import sqlite3
    
    # Connexion à la base de données (SQLite pour cet exemple)
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Créer une table si elle n'existe pas déjà
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS data (
        designation TEXT,
        unit TEXT,
        unit_price REAL
    )
    ''')
    
    # Insérer les données dans la base de données
    for index, row in dataframe.iterrows():
        insert_query = 'INSERT INTO data (designation, unit, unit_price) VALUES (?, ?, ?)'
        values = (row['designation'], row['unit'], row['unit_price'])
        cursor.execute(insert_query, values)
    
    # Valider les changements et fermer la connexion
    conn.commit()
    conn.close()
    
    print("Données insérées avec succès dans la base de données.")
