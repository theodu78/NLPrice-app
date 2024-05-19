import sqlite3
import pandas as pd

def store_data_in_db(file_path, db_path='data.db'):
    # Lire les données depuis le fichier CSV
    data = pd.read_csv(file_path)

    # Connexion à la base de données SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Créer une table si elle n'existe pas déjà
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            designation TEXT,
            unit TEXT,
            quantity REAL,
            unit_price REAL,
            total_price REAL
        )
    ''')

    # Insérer les données dans la table
    data.to_sql('articles', conn, if_exists='replace', index=False)

    # Fermer la connexion
    conn.commit()
    conn.close()
