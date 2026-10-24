"""
=========================================================
ABLBL SOURCING INTELLIGENCE PLATFORM
Application Entry Point
=========================================================
"""

# -------------------------------------------------------
# Imports
# -------------------------------------------------------

import sys
from pathlib import Path

# Ensure root directory is in sys.path for cloud deployment
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from config import (
    APP_NAME,
    PAGE_ICON,
    LAYOUT,
    SIDEBAR_STATE,
)

from utils.sidebar import render_sidebar

from views.home import render_home
from views.vendor_directory import render_vendor_directory
from views.vendor_360 import render_vendor_360
from views.vendor_commercial_directory import render_vendor_commercial_directory
from views.vendor_commercial_360 import render_vendor_commercial_360
from views.supplier_quality import render_supplier_quality
from views.fibre_market import render_fibre_market
from views.yarn_market import render_yarn_market

# -------------------------------------------------------
# Page Configuration
# -------------------------------------------------------

st.set_page_config(
    page_title=APP_NAME,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE,
)

# -------------------------------------------------------
# Load Global CSS
# -------------------------------------------------------

css_file = Path("assets/styles/main.css")

if css_file.exists():
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True,
        )

# -------------------------------------------------------
# Session State Initialization
# -------------------------------------------------------

if "page" not in st.session_state:
    st.session_state["page"] = "🏠 Home"

# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------

render_sidebar()

# -------------------------------------------------------
# Page Routing
# -------------------------------------------------------

if st.session_state["page"] == "🏠 Home":
    render_home()

elif st.session_state["page"] == "📁 Vendor Capability Search":
    render_vendor_directory()

elif st.session_state["page"] == "🏢 Vendor 360":
    if "selected_vendor" in st.session_state:
        render_vendor_360(st.session_state["selected_vendor"])
    else:
        st.info("Please select a vendor from the Capability Search to view 360 details.")

elif st.session_state["page"] == "💼 Commercial & Technical Search":
    render_vendor_commercial_directory()

elif st.session_state["page"] == "🏢 Vendor 360 (Tech + Comm)":
    render_vendor_commercial_360()

elif st.session_state["page"] == "📊 Supplier Quality Intelligence":
    if "selected_vendor" in st.session_state:
        render_supplier_quality(st.session_state["selected_vendor"])
    else:
        st.info("Please select a vendor from Vendor Capability Search.")

elif st.session_state["page"] == "📈 Fibre Market Intelligence":
    render_fibre_market()

elif st.session_state["page"] == "🧶 Yarn Market Intelligence":
    render_yarn_market()