import streamlit as st
import pandas as pd
from extract_2 import extract_data_from_pdf
from normalize_data import normalize_data
import tempfile
import os

st.title("Extraction et Normalisation de données PDF")

uploaded_file = st.file_uploader("Télécharger un fichier PDF", type="pdf")

if uploaded_file is not None:
    # Sauvegarder le fichier téléchargé dans un fichier temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name
        st.write(f"Fichier temporaire sauvegardé à: {temp_file_path}")
    
    # Extraire les données du fichier PDF temporaire
    extracted_data = extract_data_from_pdf(temp_file_path)
    
    if extracted_data is not None:
        st.write("Données extraites du PDF:")
        st.write(extracted_data)
        
        # Normaliser les données extraites
        normalized_data = normalize_data(extracted_data)
        
        st.write("Données normalisées:")
        st.write(normalized_data)
        
        # Convertir le DataFrame normalisé en CSV
        csv = normalized_data.to_csv(index=False).encode('utf-8')
        
        # Télécharger le fichier CSV
        st.download_button(
            label="Télécharger les données normalisées en CSV",
            data=csv,
            file_name='normalized_data.csv',
            mime='text/csv',
        )
        
        # Optionnel : supprimer le fichier temporaire après extraction des données
        os.remove(temp_file_path)
    else:
        st.write("Aucun tableau trouvé dans le PDF.")
