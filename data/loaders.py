"""
=========================================================
Data Loaders
ABLBL Sourcing Intelligence Platform
=========================================================
"""

from pathlib import Path
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# Data Folder
# ---------------------------------------------------------

DATA_FOLDER = Path(__file__).parent / "raw"


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Common cleaning steps for all master dataframes:
    1. Remove empty rows
    2. Clean column names (strip whitespace, replace newlines)
    3. Make duplicate columns unique
    4. Reset index
    """
    # Remove completely empty rows
    df = df.dropna(how="all")

    # Clean Column Names
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\n", " ", regex=False)
    )

    # Make Duplicate Columns Unique
    new_columns = []
    seen = {}

    for col in df.columns:
        if col not in seen:
            seen[col] = 0
            new_columns.append(col)
        else:
            seen[col] += 1
            new_columns.append(f"{col}_{seen[col]}")

    df.columns = new_columns

    # Reset Index
    df.reset_index(drop=True, inplace=True)
    
    return df


# ---------------------------------------------------------
# Loaders
# ---------------------------------------------------------

@st.cache_data
def load_vendor_master():
    """Loads Vendor Master data directly from Vendor_Master_ver1.xlsx (100% Cleaned Dataset)."""
    file_path = DATA_FOLDER / "Vendor_Master_ver1.xlsx"
    if not file_path.exists():
        matches = list(DATA_FOLDER.glob("*ver1*.xlsx")) + list(DATA_FOLDER.glob("*Vendor_Master*.xlsx"))
        if matches:
            file_path = matches[0]

    try:
        xl = pd.ExcelFile(file_path)
        sheet_name = "Data" if "Data" in xl.sheet_names else xl.sheet_names[0]
        df = pd.read_excel(xl, sheet_name=sheet_name)
        df = _clean_dataframe(df)
        
        # Ensure Construction Density and Construction Standardized alias to Const if missing
        if "Const" in df.columns:
            if "Construction Density" not in df.columns:
                df["Construction Density"] = df["Const"]
            if "Construction Standardized" not in df.columns:
                df["Construction Standardized"] = df["Const"]
                
        return df
    except Exception as e:
        st.error(f"Error loading Vendor Master: {e}")
        return pd.DataFrame()

@st.cache_data
def load_fibre_master():
    file_path = DATA_FOLDER / "Fibre_Master.xlsx"
    try:
        df = pd.read_excel(file_path)
        return _clean_dataframe(df)
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_yarn_master():
    file_path = DATA_FOLDER / "Yarn_Intelligence_Master.xlsx"
    try:
        df = pd.read_excel(file_path, sheet_name="Yarn_Master")
        return _clean_dataframe(df)
    except Exception as e:
        st.error(f"Error loading Yarn Master: {e}")
        return pd.DataFrame()
        
@st.cache_data
def load_quality_master():
    file_path = DATA_FOLDER / "Quality_Master.xlsx"

    try:
        df = pd.read_excel(file_path, sheet_name="Quality_Master")
        return _clean_dataframe(df)

    except Exception as e:
        st.error(f"Error loading Quality Master: {e}")
        return pd.DataFrame()

@st.cache_data
def load_commercial_vendor_master():
    """Loads the Quality specs- SS27.xlsx sheet with Technical and Commercial data."""
    file_path = DATA_FOLDER / "Quality specs- SS27.xlsx"
    if not file_path.exists():
        # Fallback search if filename has slight variation
        matches = list(DATA_FOLDER.glob("*Quality*specs*ss27*.xlsx")) + list(DATA_FOLDER.glob("*Quality*specs*.xlsx"))
        if matches:
            file_path = matches[0]

    try:
        xl = pd.ExcelFile(file_path)
        # Find sheet name flexibly (handling trailing spaces)
        target_sheet = None
        for sheet in xl.sheet_names:
            if "technical and commercial" in sheet.strip().lower():
                target_sheet = sheet
                break
        if not target_sheet:
            target_sheet = xl.sheet_names[0]
            
        df = pd.read_excel(xl, sheet_name=target_sheet)
        return _clean_dataframe(df)
    except Exception as e:
        st.error(f"Error loading Quality specs - SS27: {e}")
        return pd.DataFrame()