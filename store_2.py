import sqlite3
import pandas as pd

def store_data_in_db(csv_file_path):
    """
    Stocke les données normalisées d'un fichier CSV dans une base de données SQLite.
    
    Args:
    - csv_file_path (str): Chemin vers le fichier CSV contenant les données normalisées.
    """
    # Lire le CSV dans un DataFrame
    dataframe = pd.read_csv(csv_file_path)
    
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
