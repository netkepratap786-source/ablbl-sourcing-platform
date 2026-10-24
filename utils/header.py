"""
=========================================================
ABLBL SOURCING INTELLIGENCE PLATFORM
Reusable Header Component
=========================================================
"""

# -------------------------------------------------------
# Imports
# -------------------------------------------------------

import streamlit as st


# -------------------------------------------------------
# Header Component
# -------------------------------------------------------

def render_header(page_title: str, page_description: str = ""):
    """
    Render a consistent page header across the application.

    Parameters
    ----------
    page_title : str
        Title displayed at the top of the page.

    page_description : str
        Optional short description shown below the title.
    """

    st.title(page_title)

    if page_description:
        st.caption(page_description)

    st.divider()