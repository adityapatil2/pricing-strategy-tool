import pandas as pd
import os

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def read_file(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    if ext == 'csv':
        df = pd.read_csv(filepath)
    elif ext == 'xlsx':
        df = pd.read_excel(filepath)
    return df

def clean_data(df):
    # Remove duplicate rows
    df = df.drop_duplicates()
    
    # Remove rows with missing values
    df = df.dropna()
    
    # Make column names lowercase and remove spaces
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    return df

def validate_columns(df, required_columns):
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        return False, f"Missing columns: {', '.join(missing)}"
    return True, "OK"