import streamlit as st
import pandas as pd
from extract_2 import extract_data_from_pdf
import tempfile
import os

st.title("Extraction de données PDF")

uploaded_file = st.file_uploader("Télécharger un fichier PDF", type="pdf")

if uploaded_file is not None:
    # Sauvegarder le fichier téléchargé dans un fichier temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name
        st.write(f"Fichier temporaire sauvegardé à: {temp_file_path}")
    
    # Extraire les données du fichier PDF temporaire
    df = extract_data_from_pdf(temp_file_path)
    
    if df is not None:
        st.write("Données extraites du PDF:")
        st.write(df)
        df.to_csv("extracted_data.csv", index=False)
        st.write("Les données ont été enregistrées dans 'extracted_data.csv'.")
    else:
        st.write("Aucun tableau trouvé dans le PDF.")
    
    # Optionnel : supprimer le fichier temporaire après extraction des données
    os.remove(temp_file_path)
