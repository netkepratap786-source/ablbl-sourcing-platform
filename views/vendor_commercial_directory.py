"""
====================================================
Commercial & Technical Capability Search
ABLBL Sourcing Intelligence Platform
====================================================
"""

import streamlit as st
from utils.header import render_header
from utils.theme import load_css
from data.loaders import load_commercial_vendor_master
from data.commercial_vendor_service import (
    unique_commercial_values,
    filter_commercial_vendor_data
)

def render_vendor_commercial_directory():
    """
    Commercial & Technical Vendor Capability Search Page
    """
    load_css()

    render_header(
        page_title="💼 Commercial & Technical Capability Search",
        page_description="Filter fabric technical specifications and review commercial terms (NLC, Price, MOQ, Lead Time)."
    )

    st.info(
        "💡 **Page Purpose:** SS27 Seasonal Commercial & Technical Sourcing Search. "
        "Filter suppliers by SS27 season fabric quotes, MOQ, lead times, and landed costs (NLC) to support strategic seasonal buying decisions."
    )

    vendor_df = load_commercial_vendor_master()
    
    if vendor_df.empty:
        st.error("❌ Quality Specs - SS27 Master Data could not be loaded.")
        return

    st.markdown("Select technical fabric specifications to identify capable vendors along with their commercial metrics.")

    # --------------------------------------------
    # Technical Search Filters
    # --------------------------------------------
    st.markdown("### Technical Search Filters")
    
    filter_order = [
        "Fabric Composition", "Count", "ERP Construction Density", 
        "Construction", "Weave", "Finish", "Dye Type", "Pattern"
    ]
    
    # Render filters in two rows of 4 columns
    r1 = st.columns(4)
    r2 = st.columns(4)
    cols = r1 + r2
    
    current_selections = {}
    for i, f_name in enumerate(filter_order):
        options = unique_commercial_values(vendor_df, f_name, current_filters=current_selections)
        val = cols[i].selectbox(f_name, options, key=f"comm_filter_{f_name}")
        current_selections[f_name] = val

    # Search Bar
    search = st.text_input("🔍 Search Vendors, Fabric Codes or Products", key="comm_search_input")

    # Filter Data
    filtered_df = filter_commercial_vendor_data(
        composition=current_selections.get("Fabric Composition", "All"),
        count=current_selections.get("Count", "All"),
        construction_density=current_selections.get("ERP Construction Density", "All"),
        construction_standardized=current_selections.get("Construction", "All"),
        weave=current_selections.get("Weave", "All"),
        finish=current_selections.get("Finish", "All"),
        dye_type=current_selections.get("Dye Type", "All"),
        pattern=current_selections.get("Pattern", "All"),
        search=search
    )

    # Active Filters Display
    active = {k: v for k, v in current_selections.items() if v != "All"}
    if search: active["Search"] = search
    
    if active:
        st.markdown("**Active Filters:** " + ", ".join([f"*{k}: {v}*" for k, v in active.items()]))

    # --------------------------------------------
    # Results Table
    # --------------------------------------------
    st.markdown("### 📋 Matching Vendors & Commercial Specs")
    
    if not filtered_df.empty:
        # Reset index for selection stability
        filtered_df = filtered_df.reset_index(drop=True)

        # KPI Metrics
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Matching Vendors", filtered_df["Vendor Name"].nunique() if "Vendor Name" in filtered_df.columns else 0)
        k2.metric("Matching Fabrics", len(filtered_df))
        k3.metric("Origins / Countries", filtered_df["Origin"].nunique() if "Origin" in filtered_df.columns else 0)
        k4.metric("Product Categories", filtered_df["Product"].nunique() if "Product" in filtered_df.columns else 0)

        # Display Columns including Commercial Specs
        desired_cols = [
            "Vendor Name", "Fabric code", "Product", "Origin",
            "Fabric Composition", "Count", "ERP Construction Density", "Weave", "Finish", "Dye Type",
            "Ex mill price / M", "Ex mill price / Kg", "NLC/meter", "NLC/Kg", "MOQ", "MCQ", "Ex mill lead time"
        ]
        
        final_cols = [c for c in desired_cols if c in filtered_df.columns]
        
        selected_row = st.dataframe(
            filtered_df[final_cols],
            use_container_width=True,
            selection_mode="single-row",
            on_select="rerun"
        )

        if selected_row.selection.rows:
            idx = selected_row.selection.rows[0]
            selected_vendor_data = filtered_df.iloc[idx]
            
            if st.button("🔍 View Vendor 360 (Tech + Comm)", type="primary"):
                st.session_state["selected_commercial_vendor"] = selected_vendor_data.get("Vendor Name", "N/A")
                st.session_state["selected_commercial_fabric_code"] = selected_vendor_data.get("Fabric code", "N/A")
                st.session_state["selected_commercial_row"] = selected_vendor_data.to_dict()
                st.session_state["page"] = "🏢 Vendor 360 (Tech + Comm)"
                st.rerun()
    else:
        st.warning("No vendors found matching your technical criteria.")
