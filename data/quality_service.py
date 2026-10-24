
# =========================================================
# Quality Service Layer
# ABLBL Sourcing Intelligence Platform
# =========================================================

import pandas as pd

from data.loaders import load_quality_master

def get_quality_data():
    """Returns the raw quality master dataframe."""
    df = load_quality_master()
    return df if df is not None else pd.DataFrame()
