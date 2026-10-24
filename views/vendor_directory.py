"""
====================================================
Vendor Capability Search
ABLBL Sourcing Intelligence Platform
====================================================
"""

import streamlit as st
from utils.header import render_header
from utils.theme import load_css
from data.loaders import load_vendor_master
from data.vendor_service import (
    unique_values,
    filter_vendor_data
)

def render_vendor_directory():
    """
    Vendor Capability Search Page
    """
    load_css()

    render_header(
        page_title="🔍 Vendor Capability Search",
        page_description="Find vendors capable of manufacturing your required fabric."
    )

    st.info(
        "💡 **Page Purpose:** Technical Supplier Capability & Specification Search. "
        "Filter vendors by technical fabric specifications (Composition, Count, Weave, Finish, Dye Type) to discover matching suppliers, then drill down into Vendor 360 intelligence."
    )

    vendor_df = load_vendor_master()
    
    if vendor_df.empty:
        st.error("❌ Vendor Master could not be loaded.")
        return

    st.markdown("Select the required fabric specifications to identify capable vendors.")

    # --------------------------------------------
    # Technical Search Filters
    # --------------------------------------------
    st.markdown("### Technical Search Filters")
    
    # Determine dynamic column names if present
    comp_filter_col = "ERP Standard Composition" if "ERP Standard Composition" in vendor_df.columns else "Composition"
    count_filter_col = "ERP Count Capability" if "ERP Count Capability" in vendor_df.columns else "Count"

    # Define Filter Order for Cascading (Replaced Composition & Count with ERP versions)
    filter_order = [
        comp_filter_col, count_filter_col, "Construction Density", 
        "Construction Standardized", "Weave", "Finish", "Dye Type", "Season"
    ]
    
    # Render filters in two rows
    r1 = st.columns(4)
    r2 = st.columns(4)
    cols = r1 + r2
    
    current_selections = {}
    for i, f_name in enumerate(filter_order):
        options = unique_values(vendor_df, f_name, current_filters=current_selections)
        
        # Selectbox directly drives the state
        val = cols[i].selectbox(f_name, options, key=f"filter_{f_name}")
        current_selections[f_name] = val

    # Search Bar
    search = st.text_input("🔍 Search Vendors or Products")

    # Filter Data
    filtered_df = filter_vendor_data(
        composition=current_selections.get("ERP Standard Composition", current_selections.get("Composition", "All")),
        count=current_selections.get("Count", "All"),
        count_capability=current_selections.get("ERP Count Capability", "All"),
        construction_density=current_selections.get("Construction Density", "All"),
        construction_standardized=current_selections.get("Construction Standardized", "All"),
        weave=current_selections.get("Weave", "All"),
        finish=current_selections.get("Finish", "All"),
        dye_type=current_selections.get("Dye Type", "All"),
        season=current_selections.get("Season", "All"),
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
    st.markdown("### 📋 Matching Vendors")
    
    if not filtered_df.empty:
        # Remove duplicates based on capability columns
        cap_cols = ["Vendor Name", comp_filter_col, count_filter_col, "Construction Density", 
                    "Construction Standardized", "Weave", "Finish", "Dye Type", "Season"]
        subset_cols = [c for c in cap_cols if c in filtered_df.columns]
        if subset_cols:
            filtered_df = filtered_df.drop_duplicates(subset=subset_cols)

        # Reset index for selection stability
        filtered_df = filtered_df.reset_index(drop=True)

        # KPI Metrics
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Matching Vendors", filtered_df["Vendor Name"].nunique() if "Vendor Name" in filtered_df.columns else 0)
        k2.metric("Matching Fabrics", len(filtered_df))
        k3.metric("Countries Represented", filtered_df["Country"].nunique() if "Country" in filtered_df.columns else 0)
        k4.metric("Key Mills", filtered_df["Mills"].nunique() if "Mills" in filtered_df.columns else 0)

        display_cols = [
            "Vendor Name", "Vendor Code", "Mills", "Product", 
            comp_filter_col, count_filter_col, "Construction Density", "Construction Standardized",
            "Country", "Origin (Imp/Dom)", "Mill Category", "Season"
        ]
        
        final_cols = [c for c in display_cols if c in filtered_df.columns]
        
        selected_row = st.dataframe(
            filtered_df[final_cols],
            use_container_width=True,
            selection_mode="single-row",
            on_select="rerun"
        )

        if selected_row.selection.rows:
            idx = selected_row.selection.rows[0]
            selected_vendor_data = filtered_df.iloc[idx]
            
            if st.button("🔍 View Vendor 360", type="primary"):
                st.session_state["selected_vendor"] = selected_vendor_data["Vendor Name"]
                st.session_state["selected_vendor_code"] = selected_vendor_data["Vendor Code"]
                
                # Determine correct fabric code column name
                fab_col = "Fab Code" if "Fab Code" in selected_vendor_data else "Fabric Code"
                st.session_state["selected_fabric_code"] = selected_vendor_data.get(fab_col, "N/A")
                
                st.session_state["selected_filters"] = active
                st.session_state["page"] = "🏢 Vendor 360"
                st.rerun()
    else:
        st.warning("No vendors found matching your criteria.")
