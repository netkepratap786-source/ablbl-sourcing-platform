"""
=========================================================
Commercial Vendor Service Layer
ABLBL Sourcing Intelligence Platform
=========================================================
"""

import re
import pandas as pd
from data.loaders import load_commercial_vendor_master

def natural_sort_key(s):
    """
    Helper function for natural alphanumeric sorting (small to big).
    E.g., 5D < 10L < 20D < 100D, 2/16 < 2/38 < 2/80.
    """
    return [(0, int(t)) if t.isdigit() else (1, t.lower()) for t in re.split(r'(\d+)', str(s))]

def get_commercial_vendor_data():
    """Returns the cleaned commercial vendor dataframe."""
    df = load_commercial_vendor_master()
    return df if df is not None else pd.DataFrame()

def unique_commercial_values(df, column, current_filters=None):
    """
    Returns sorted unique values for a column, optionally filtered by previous selection context.
    """
    if df.empty:
        return ["All"]
    
    # Match column flexibly
    target_col = column if column in df.columns else None
    if not target_col:
        matches = [c for c in df.columns if c.strip().lower() == column.strip().lower()]
        if matches:
            target_col = matches[0]
        else:
            return ["All"]
    
    # Apply existing filters to narrow down values for cascading
    filtered_df = df.copy()
    if current_filters:
        for col, val in current_filters.items():
            if val != "All":
                c_match = col if col in filtered_df.columns else ([c for c in filtered_df.columns if c.strip().lower() == col.strip().lower()] or [None])[0]
                if c_match and c_match in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[c_match] == val]
    
    values = filtered_df[target_col].dropna().astype(str).str.strip()
    values = values[(values != "") & (values.str.lower() != "nan") & (values.str.lower() != "none")]
    return ["All"] + sorted(values.unique().tolist(), key=natural_sort_key)

def filter_commercial_vendor_data(
    composition="All",
    count="All",
    construction_density="All",
    construction_standardized="All",
    weave="All",
    finish="All",
    dye_type="All",
    pattern="All",
    season="All",
    product="All",
    origin="All",
    search=""
):
    """
    Filters the commercial vendor dataframe based on technical & commercial specifications.
    """
    df = get_commercial_vendor_data().copy()
    if df.empty:
        return df

    # Map filter keys to actual dataframe columns flexibly
    col_mapping = {
        "Fabric Composition": composition,
        "Count": count,
        "ERP Construction Density": construction_density,
        "Construction": construction_standardized,
        "Weave": weave,
        "Finish": finish,
        "Dye Type": dye_type,
        "Pattern": pattern,
        "Season": season,
        "Product": product,
        "Origin": origin
    }

    for target_col, val in col_mapping.items():
        if val != "All":
            # Match column flexibly
            c_match = target_col if target_col in df.columns else ([c for c in df.columns if c.strip().lower() == target_col.strip().lower()] or [None])[0]
            if c_match and c_match in df.columns:
                df = df[df[c_match].astype(str).str.strip() == str(val).strip()]

    # Global text search across common vendor/product columns
    if search and search.strip():
        search_term = search.lower()
        search_cols = [c for c in ["Vendor Name", "Fabric code", "Product", "Subbrand", "Country of Origin"] if c in df.columns]
        if search_cols:
            mask = df[search_cols].apply(lambda x: x.astype(str).str.lower().str.contains(search_term, na=False)).any(axis=1)
            df = df[mask]

    return df
