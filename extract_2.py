import camelot
import pandas as pd
import ctypes
import os

# Spécifier manuellement le chemin d'accès à Ghostscript
os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"
libgs = ctypes.CDLL("/opt/homebrew/lib/libgs.dylib")  # Utilise le chemin trouvé

def extract_data_from_pdf(pdf_path):
    # Utilisation de camelot pour extraire les tableaux des PDF en mode 'stream'
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream', strip_text='\n', split_text=True, edge_tol=500, row_tol=10, column_tol=10)
    
    if tables:
        print(f"{len(tables)} tables found")
        for i, table in enumerate(tables):
            print(f"Table {i} shape: {table.df.shape}")
            print(table.df)
        # Concaténer toutes les tables extraites en une seule
        df = pd.concat([table.df for table in tables])
        return df
    else:
        print("Aucun tableau trouvé dans le PDF.")
        return None
