import streamlit as st
import pandas as pd
from extract_2 import extract_data_from_pdf
from normalize_data import normalize_data
from store_2 import store_data_in_db
import tempfile
import os

st.title("Extraction, Normalisation et Stockage de données PDF")

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
        
        if normalized_data is not None:
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
            

            # Sauvegarder le fichier normalisé CSV dans un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv_file:
                temp_csv_file.write(csv)
                temp_csv_file_path = temp_csv_file.name
            
            # Bouton pour envoyer les données vers la base de données
            if st.button("Envoyer les Données vers la Base de Données"):
                with st.spinner("Envoi en cours..."):
                    store_data_in_db(temp_csv_file_path)
                    st.success("Données envoyées vers la base de données avec succès!")
                    
                    # Optionnel : supprimer le fichier temporaire CSV après envoi des données
                    os.remove(temp_csv_file_path)
            
            # Optionnel : supprimer le fichier temporaire PDF après extraction des données
            os.remove(temp_file_path)
        else:
            st.write("La normalisation des données a échoué.")
    else:
        st.write("Aucun tableau trouvé dans le PDF.")
