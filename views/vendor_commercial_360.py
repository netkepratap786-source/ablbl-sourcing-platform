"""
====================================================
Vendor 360 (Commercial & Technical) View
ABLBL Sourcing Intelligence Platform
====================================================
"""

import streamlit as st
import pandas as pd
from utils.header import render_header
from utils.theme import load_css
from data.loaders import load_commercial_vendor_master

def render_vendor_commercial_360(vendor_name=None, fabric_code=None):
    """
    Vendor 360 (Tech + Comm) Dashboard Page matching 4-section executive layout
    """
    load_css()

    # Render Header
    render_header(
        page_title=f"🏢 {vendor_name if vendor_name else 'Vendor'} — Commercial & Technical 360",
        page_description="SS27 Seasonal Supplier Commercial Intelligence & Technical Evaluation"
    )

    st.info(
        "💡 **Page Purpose:** SS27 Commercial & Technical 360 Evaluation. "
        "Review specific fabric technical specs alongside SS27 commercial terms (Quoted Price, NLC, MOQ, Lead Time) and automated sourcing decision support."
    )

    df = load_commercial_vendor_master()
    if df.empty:
        st.error("❌ Quality Specs - SS27 Master Data unavailable.")
        return

    # Check for selected vendor and fabric code from session state
    if not vendor_name and "selected_commercial_vendor" in st.session_state:
        vendor_name = st.session_state["selected_commercial_vendor"]
    if not fabric_code and "selected_commercial_fabric_code" in st.session_state:
        fabric_code = st.session_state["selected_commercial_fabric_code"]

    if not vendor_name:
        st.info("Please select a vendor from the Commercial & Technical Search page.")
        if st.button("⬅️ Back to Search"):
            st.session_state["page"] = "💼 Commercial & Technical Search"
            st.rerun()
        return

    # Filter vendor data
    vendor_mask = df["Vendor Name"].astype(str).str.strip().str.lower() == str(vendor_name).strip().lower()
    vendor_df = df[vendor_mask]

    if vendor_df.empty:
        st.warning(f"No records found for vendor '{vendor_name}'.")
        return

    # Specific fabric record if selected
    fabric_row = None
    if fabric_code and "Fabric code" in vendor_df.columns:
        fab_match = vendor_df[vendor_df["Fabric code"].astype(str).str.strip() == str(fabric_code).strip()]
        if not fab_match.empty:
            fabric_row = fab_match.iloc[0]

    if fabric_row is None:
        fabric_row = vendor_df.iloc[0]

    # --- Top Navigation Actions ---
    col_back, col_space, col_act1 = st.columns([1.5, 4, 2])
    with col_back:
        if st.button("⬅️ Back to Search"):
            st.session_state["page"] = "💼 Commercial & Technical Search"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------
    # 1. Vendor Identity
    # --------------------------------------------------
    st.subheader("1. Vendor Identity")
    
    i1, i2, i3, i4 = st.columns(4)
    i1.metric("Vendor Name", str(vendor_name))
    i2.metric("Vendor Code", str(fabric_row.get("Vendor Code", fabric_row.get("Subbrand", "1208915"))))
    i3.metric("Mill / Category", str(fabric_row.get("Product", "N/A")))
    i4.metric("Fabric Code", str(fabric_row.get("Fabric code", "N/A")))

    i5, i6, i7, i8 = st.columns(4)
    i5.metric("Origin", str(fabric_row.get("Origin", "N/A")))
    i6.metric("Mill Category / Country", str(fabric_row.get("Country of Origin", fabric_row.get("Origin", "Domestic"))))
    i7.metric("Currency", "INR" if str(fabric_row.get("Origin", "")).lower() == "domestic" else "USD")
    i8.metric("Subbrand", str(fabric_row.get("Subbrand", "N/A")))

    st.markdown("---")

    # Helper for vertical downward table inside expander
    def render_vertical_list(val_list, column_title, height=180):
        if val_list:
            df_vals = pd.DataFrame(sorted(val_list), columns=[column_title])
            st.dataframe(df_vals, use_container_width=True, hide_index=True, height=height)
        else:
            st.caption("No items available")

    # --------------------------------------------------
    # 2. Business Capability
    # --------------------------------------------------
    st.subheader("2. Business Capability")
    
    b1, b2 = st.columns(2)
    with b1:
        prod_vals = vendor_df['Product'].dropna().unique().astype(str).tolist() if 'Product' in vendor_df.columns else []
        with st.expander(f"📦 Product Categories ({len(prod_vals)})", expanded=True):
            render_vertical_list(prod_vals, "Product Category", height=160)
            
        sub_vals = vendor_df['Subbrand'].dropna().unique().astype(str).tolist() if 'Subbrand' in vendor_df.columns else []
        with st.expander(f"🏷️ Subbrands / Lines ({len(sub_vals)})", expanded=False):
            render_vertical_list(sub_vals, "Subbrand", height=160)
    
    with b2:
        season_vals = vendor_df['Season'].dropna().unique().astype(str).tolist() if 'Season' in vendor_df.columns else ["SS27"]
        with st.expander(f"🗓️ Seasons Supported ({len(season_vals)})", expanded=False):
            render_vertical_list(season_vals, "Season", height=160)
            
        orig_vals = vendor_df['Origin'].dropna().unique().astype(str).tolist() if 'Origin' in vendor_df.columns else []
        with st.expander(f"🌍 Origins Supported ({len(orig_vals)})", expanded=False):
            render_vertical_list(orig_vals, "Origin", height=160)

    st.markdown("---")

    # --------------------------------------------------
    # 3. Manufacturing Capability Matrix
    # --------------------------------------------------
    st.subheader("3. Manufacturing Capability Matrix")
    
    m1, m2, m3 = st.columns(3)
    
    def get_unique_list(col_name):
        if col_name in vendor_df.columns:
            vals = vendor_df[col_name].dropna().unique().astype(str)
            vals = [v.strip() for v in vals if v.strip() and v.lower() != "nan"]
            return sorted(list(set(vals)))
        return []

    with m1:
        comp_list = get_unique_list("Fabric Composition")
        with st.expander(f"🧬 Composition ({len(comp_list)})", expanded=True):
            render_vertical_list(comp_list, "Composition", height=180)
            
        weave_list = get_unique_list("Weave")
        with st.expander(f"🧶 Weave ({len(weave_list)})", expanded=False):
            render_vertical_list(weave_list, "Weave", height=180)
            
        pattern_list = get_unique_list("Pattern")
        with st.expander(f"🎨 Pattern ({len(pattern_list)})", expanded=False):
            render_vertical_list(pattern_list, "Pattern", height=180)

    with m2:
        count_list = get_unique_list("Count")
        with st.expander(f"🧵 Count ({len(count_list)})", expanded=True):
            render_vertical_list(count_list, "Count", height=180)
            
        finish_list = get_unique_list("Finish")
        with st.expander(f"✨ Finish ({len(finish_list)})", expanded=False):
            render_vertical_list(finish_list, "Finish", height=180)
            
        width_list = get_unique_list("Width")
        with st.expander(f"📏 Width ({len(width_list)})", expanded=False):
            render_vertical_list(width_list, "Width", height=180)

    with m3:
        const_list = get_unique_list("ERP Construction Density")
        with st.expander(f"📐 Construction Density ({len(const_list)})", expanded=True):
            render_vertical_list(const_list, "Construction Density", height=180)
            
        dye_list = get_unique_list("Dye Type")
        with st.expander(f"🎨 Dye Type ({len(dye_list)})", expanded=False):
            render_vertical_list(dye_list, "Dye Type", height=180)

    st.markdown("---")

    # --------------------------------------------------
    # 4. Commercial Snapshot
    # --------------------------------------------------
    st.subheader("4. Commercial Snapshot")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    
    moq_val = fabric_row.get("MOQ", "N/A")
    c1.metric("MOQ", f"{moq_val}" if pd.notnull(moq_val) else "N/A")
    
    mcq_val = fabric_row.get("MCQ", "N/A")
    c2.metric("MCQ", f"{mcq_val}" if pd.notnull(mcq_val) else "N/A")
    
    lead_time_val = fabric_row.get("Ex mill lead time", fabric_row.get("Lead time", "N/A"))
    c3.metric("Ex-Mill Lead Time", f"{lead_time_val}" if pd.notnull(lead_time_val) else "N/A")
    
    nlc_meter = fabric_row.get("NLC/meter", fabric_row.get("NLC/Kg", "N/A"))
    uom = fabric_row.get("UOM", "M")
    c4.metric(f"NLC / {uom}", f"{nlc_meter}" if pd.notnull(nlc_meter) else "N/A")
    
    ex_mill = fabric_row.get("Ex mill price / M", fabric_row.get("Ex mill price / Kg", "N/A"))
    c5.metric(f"Ex-Mill Price / {uom}", f"{ex_mill}" if pd.notnull(ex_mill) else "N/A")

    st.markdown("---")

    # --------------------------------------------------
    # 5. SS27 Sourcing Decision Engine
    # --------------------------------------------------
    st.subheader("5. 🤖 SS27 Sourcing Decision Engine")
    st.markdown("Automated commercial decision indicators computed from SS27 quotations & specs.")

    # 1. SS27 NLC Competitiveness
    cur_nlc = pd.to_numeric(fabric_row.get("NLC/meter", fabric_row.get("NLC/Kg")), errors="coerce")
    cur_comp = fabric_row.get("Fabric Composition", "")
    
    comp_matches = df[df["Fabric Composition"].astype(str).str.strip() == str(cur_comp).strip()] if cur_comp else df
    avg_cat_nlc = pd.to_numeric(comp_matches["NLC/meter"], errors="coerce").dropna().mean()
    
    if pd.notnull(cur_nlc) and pd.notnull(avg_cat_nlc) and avg_cat_nlc > 0:
        diff = ((cur_nlc - avg_cat_nlc) / avg_cat_nlc) * 100
        if diff < -3:
            comm_cost_rating = f"🟢 Best-in-Class ({abs(diff):.1f}% below SS27 avg)"
            comm_status = "cheaper"
        elif diff > 3:
            comm_cost_rating = f"🔴 Premium (+{diff:.1f}% vs SS27 avg)"
            comm_status = "premium"
        else:
            comm_cost_rating = f"🟡 Market Competitive (±{abs(diff):.1f}%)"
            comm_status = "aligned"
    else:
        comm_cost_rating = "🟡 Market Competitive"
        comm_status = "aligned"

    # 2. Order Commitment Risk (MOQ)
    import re
    moq_str = str(fabric_row.get("MOQ", ""))
    moq_nums = re.findall(r'\d+', moq_str)
    moq_val_num = int(moq_nums[0]) if moq_nums else 0
    
    if moq_val_num > 0 and moq_val_num <= 1000:
        moq_rating = f"🟢 High Flexibility ({moq_val_num}m MOQ)"
    elif moq_val_num > 5000:
        moq_rating = f"🔴 High Commitment ({moq_val_num}m MOQ)"
    elif moq_val_num > 0:
        moq_rating = f"🟡 Standard Volume ({moq_val_num}m MOQ)"
    else:
        moq_rating = "🟡 Standard Commercial MOQ"

    # 3. Delivery Lead Time Agility
    lead_str = str(fabric_row.get("Ex mill lead time", fabric_row.get("Lead time", "")))
    lead_nums = re.findall(r'\d+', lead_str)
    lead_days = int(lead_nums[0]) if lead_nums else 60
    
    if lead_days <= 45:
        lead_rating = f"🟢 Fast Track ({lead_days} Days)"
    elif lead_days <= 75:
        lead_rating = f"🟡 Standard Agility ({lead_days} Days)"
    else:
        lead_rating = f"🔴 Extended Lead Time ({lead_days} Days)"

    # 4. SS27 Commercial Score / Classification
    if comm_status == "cheaper" and lead_days <= 60:
        commercial_tier = "⭐ SS27 Preferred Partner"
    elif comm_status == "premium":
        commercial_tier = "⚠️ Renegotiation Priority"
    else:
        commercial_tier = "🔹 Core SS27 Supplier"

    # Render Metric Cards with Simplified Business Titles
    cd1, cd2, cd3, cd4 = st.columns(4)
    cd1.metric("SS27 Cost vs Category Benchmark", comm_cost_rating)
    cd2.metric("Min Order Quantity (MOQ) Risk", moq_rating)
    cd3.metric("Production Lead Time", lead_rating)
    cd4.metric("SS27 Strategic Sourcing Action", commercial_tier)

    # 5. Dynamic Advice Banner
    if comm_status == "premium":
        st.warning(
            f"💡 **SS27 Sourcing Advice:** {vendor_name}'s quoted NLC (₹{cur_nlc}) is {diff:.1f}% above the SS27 market average for {cur_comp}. "
            "Consider negotiating on basic price or batch upcharge before finalizing PO placement."
        )
    elif comm_status == "cheaper":
        st.success(
            f"💡 **SS27 Sourcing Advice:** {vendor_name} offers superior commercial terms ({abs(diff):.1f}% lower NLC than SS27 category average). "
            "Highly recommended for primary SS27 order allocation."
        )
    else:
        st.info(
            f"💡 **SS27 Sourcing Advice:** {vendor_name} provides standard, market-aligned commercial pricing and lead times for SS27. "
            "Suitable for balanced allocation."
        )
