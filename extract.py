import tabula
import pandas as pd
import os
import json

def extract_tables_from_pdf(pdf_path):
    try:
        # Try extracting tables using lattice method
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, lattice=True)
        # If no tables found, try using stream method
        if not tables:
            tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, stream=True)
        return tables
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        return []
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return []

def classify_data(tables):
    if not tables:
        return pd.DataFrame()
    
    # Combine all tables into one DataFrame
    df = pd.concat(tables, ignore_index=True)
    
    # Expected columns
    expected_columns = ["Article", "Prix Unitaire", "Quantités", "Total"]
    
    # Ensure we only have four columns
    if len(df.columns) >= len(expected_columns):
        df = df.iloc[:, :len(expected_columns)]
        df.columns = expected_columns
    else:
        print(f"Column length mismatch. Expected {len(expected_columns)}, got {len(df.columns)}. Using default column names.")
    
    return df

def save_to_csv(df, output_path):
    df.to_csv(output_path, index=False)

if __name__ == "__main__":
    pdf_path = "path/to/your/pdf"
    output_path = "path/to/output.csv"
    if os.path.exists(pdf_path):
        tables = extract_tables_from_pdf(pdf_path)
        classified_data = classify_data(tables)
        save_to_csv(classified_data, output_path)
    else:
        print(f"File {pdf_path} does not exist")
