import streamlit as st
from extract import extract_tables_from_pdf, classify_data, save_to_csv
from vectorize import vectorize_data
from store import store_in_pinecone
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="Devis Processing App")
st.header("Devis Processing App 📄")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Processing..."):
        # Save uploaded file to disk
        pdf_path = f"/tmp/{uploaded_file.name}"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if os.path.exists(pdf_path):
            tables = extract_tables_from_pdf(pdf_path)
            if tables:
                classified_data = classify_data(tables)
                if not classified_data.empty:
                    csv_path = f"/tmp/{uploaded_file.name}.csv"
                    save_to_csv(classified_data, csv_path)
                    vector_store = vectorize_data(csv_path)
                    store_in_pinecone(vector_store)
                    st.success("Processing complete and data stored in Pinecone!")
                else:
                    st.error("The extracted table is empty or has incorrect format.")
            else:
                st.error("No tables found in PDF.")
        else:
            st.error(f"File {pdf_path} does not exist")
