"""
Helper functions for loading and encoding local images for rich UI presentation.
"""

import base64
from pathlib import Path
import streamlit as st

IMAGE_DIR = Path(__file__).parent.parent / "assets" / "images"

@st.cache_data
def get_image_base64(filename: str) -> str:
    img_path = IMAGE_DIR / filename
    if img_path.exists():
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            ext = img_path.suffix.lstrip(".").lower()
            if ext == "jpg":
                ext = "jpeg"
            return f"data:image/{ext};base64,{encoded}"
    return ""
