"""
====================================================
Supplier Quality Intelligence Module
ABLBL Sourcing Intelligence Platform
====================================================
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.header import render_header
from utils.theme import load_css
from data.quality_service import get_quality_data
from utils.formatters import fmt_price, fmt_pct, fmt_int


def render_supplier_quality(selected_vendor):
    """
    Renders the Supplier Quality Intelligence dashboard structure.
    """
    load_css()

    quality_df = get_quality_data()
    
    render_header(
        page_title="📊 Supplier Quality Intelligence",
        page_description="Enterprise Supplier Performance & Quality Assessment"
    )

    supplier = quality_df[
        quality_df["Vendor Name"].astype(str).str.strip().str.upper()
        ==
        str(selected_vendor).strip().upper()
    ]

    if supplier.empty:
        st.warning("No quality data found for the selected supplier.")
        return

    # Check if a specific brand row was selected from Benchmarking table
    sel_brand = st.session_state.get("selected_quality_brand")
    if sel_brand and "Associated Brand" in supplier.columns:
        brand_match = supplier[supplier["Associated Brand"].astype(str).str.strip().str.upper() == str(sel_brand).strip().upper()]
        if not brand_match.empty:
            row = brand_match.iloc[0]
        else:
            row = supplier.iloc[0]
    else:
        row = supplier.iloc[0]

    # Dynamic Top Metadata Header
    eval_period = str(row.get("Evaluation Period", "2025-2026")).strip()
    assoc_brand = str(row.get("Associated Brand", "ABLBL")).strip()
    vendor_cat = str(row.get("Vendor Category", "Fabric")).strip()
    score = float(row.get("Vendor Rating Total Score", 0))
    rank = int(row.get("Current Overall Rank", 999))
    total_vendors = len(quality_df)

    if score >= 80 or rank <= 10:
        status_badge = f"🟢 Approved Strategic Vendor (Rank #{rank})"
    elif score >= 70 or rank <= 30:
        status_badge = f"🟡 Approved with Review (Rank #{rank})"
    else:
        status_badge = f"🔴 Corrective Action Required (Rank #{rank})"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Selected Vendor", selected_vendor)
    col2.metric("Brand Program", f"{assoc_brand} ({vendor_cat})")
    col3.metric("Evaluation Period", eval_period if eval_period != "nan" else "2025-2026")
    col4.metric("Overall Status", status_badge)
    st.divider()

    # --- Quality Performance Overview ---
    st.subheader("Quality Performance Overview")

    q_cols = st.columns(6)

    # Correct Metric Formatting
    vpqi_raw = float(row.get("VPQI", 0))
    vpqi_pct = vpqi_raw * 100 if vpqi_raw <= 1.0 else vpqi_raw
    q_cols[0].metric("VPQI (Process Quality)", f"{vpqi_pct:.1f}%")

    ppmh_raw = float(row.get("PPMH", 0))
    ppmh_pct = ppmh_raw * 100 if ppmh_raw <= 1.0 else ppmh_raw
    q_cols[1].metric("PPMH (Customer Happiness)", f"{ppmh_pct:.1f}%")

    otif_raw = float(row.get("OTIF", 0))
    otif_pct = otif_raw * 100 if otif_raw <= 1.0 else otif_raw
    q_cols[2].metric("OTIF (Delivery Adherence)", f"{otif_pct:.1f}%")

    dpmo_raw = row.get("DPMO", None)
    if pd.notnull(dpmo_raw) and str(dpmo_raw).strip() != "" and str(dpmo_raw).strip() != "0":
        dpmo_str = fmt_int(dpmo_raw)
    else:
        dpmo_str = "Low Defect Count"
    q_cols[3].metric("DPMO (Defect Rate)", dpmo_str)

    q_cols[4].metric("Vendor Score", f"{score:.1f} / 100")
    q_cols[5].metric("Current Rank", f"Rank #{rank} of {total_vendors}")

    # --- Supplier Benchmarking ---
    raw_cats = sorted([str(c).strip() for c in quality_df["Vendor Category"].dropna().unique() if str(c).strip() not in ["nan", ""]])
    cat_filter_list = ["All Categories"] + raw_cats

    raw_brands = sorted([str(b).strip() for b in quality_df["Associated Brand"].dropna().unique() if str(b).strip() not in ["nan", ""]])
    brand_filter_list = ["All Brands"] + raw_brands

    col_bench_title, col_cat_filter, col_brand_filter = st.columns([2.0, 1.2, 1.2])
    with col_cat_filter:
        selected_cat = st.selectbox(
            "🔍 Fabric Category:",
            cat_filter_list,
            key="bench_cat_filter"
        )
    with col_brand_filter:
        selected_brand_f = st.selectbox(
            "🏷️ Brand Program:",
            brand_filter_list,
            key="bench_brand_filter"
        )
    with col_bench_title:
        st.subheader("Supplier Benchmarking")
        caption_bits = []
        if selected_cat != "All Categories": caption_bits.append(f"**{selected_cat}**")
        if selected_brand_f != "All Brands": caption_bits.append(f"**{selected_brand_f} Brand**")
        if caption_bits:
            st.caption("Filtered for " + " & ".join(caption_bits))

    benchmark_cols = [
        "Vendor Name", "Vendor Category", "Associated Brand", "VPQI", "PPMH", "OTIF", "DPMO",
        "Vendor Rating Total Score", "Current Overall Rank", "Vendor Performance Rating"
    ]
    available_cols = [c for c in benchmark_cols if c in quality_df.columns]
    bench_df = quality_df[available_cols].copy()

    rename_mapping = {
        "Vendor Name": "Supplier",
        "Vendor Category": "Category",
        "Associated Brand": "Brand",
        "Vendor Rating Total Score": "Vendor Score",
        "Current Overall Rank": "Current Rank",
        "Vendor Performance Rating": "Performance"
    }
    bench_df = bench_df.rename(columns=rename_mapping)

    # Filter bench_df by selected Category & Brand
    if selected_cat != "All Categories":
        bench_df = bench_df[bench_df["Category"].astype(str).str.strip().str.upper() == str(selected_cat).strip().upper()]
    if selected_brand_f != "All Brands":
        bench_df = bench_df[bench_df["Brand"].astype(str).str.strip().str.upper() == str(selected_brand_f).strip().upper()]

    # Reorder columns as specified
    column_order = ["Supplier", "Category", "Brand", "VPQI", "PPMH", "OTIF", "DPMO", "Vendor Score", "Current Rank", "Performance"]
    existing_cols = [c for c in column_order if c in bench_df.columns]
    bench_df = bench_df[existing_cols]

    # ==========================================================
    # Format Benchmarking Display
    # ==========================================================

    display_df = bench_df.copy()

    # VPQI → Percentage
    if "VPQI" in display_df.columns:
        display_df["VPQI"] = display_df["VPQI"].apply(lambda x: f"{(float(x)*100 if float(x)<=1.0 else float(x)):.1f}%" if pd.notnull(x) else "—")

    # PPMH → Percentage
    if "PPMH" in display_df.columns:
        display_df["PPMH"] = display_df["PPMH"].apply(lambda x: f"{(float(x)*100 if float(x)<=1.0 else float(x)):.1f}%" if pd.notnull(x) else "—")

    # OTIF → Percentage
    if "OTIF" in display_df.columns:
        display_df["OTIF"] = display_df["OTIF"].apply(lambda x: f"{(float(x)*100 if float(x)<=1.0 else float(x)):.1f}%" if pd.notnull(x) else "—")

    # DPMO → Whole Number / Text
    if "DPMO" in display_df.columns:
        display_df["DPMO"] = display_df["DPMO"].apply(lambda x: fmt_int(x) if (pd.notnull(x) and str(x).strip() not in ['', '0', 'nan']) else "Low Defect Count")

    # Vendor Score → 1 decimal
    if "Vendor Score" in display_df.columns:
        display_df["Vendor Score"] = display_df["Vendor Score"].apply(lambda x: fmt_price(x, 1))

    if "Current Rank" in display_df.columns:
        display_df = display_df.sort_values(
            by="Current Rank",
            ascending=True
        ).reset_index(drop=True)

    benchmarking_event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )

    if benchmarking_event.selection.rows:
        selected_index = benchmarking_event.selection.rows[0]
        selected_supplier = display_df.iloc[selected_index]["Supplier"]
        selected_brand_val = display_df.iloc[selected_index]["Brand"]

        if (st.session_state.get("selected_vendor") != selected_supplier or 
            st.session_state.get("selected_quality_brand") != selected_brand_val):
            st.session_state["selected_vendor"] = selected_supplier
            st.session_state["selected_quality_brand"] = selected_brand_val
            st.rerun()

    st.divider()

    # --- Quality KPI Analysis ---
    st.subheader("Quality KPI Analysis")

    kpi_data = [
        {"KPI": "VPQI (Vendor Process Quality Index)", "Current Value": row.get("VPQI"), "Rating": row.get("VPQI Rating", "Not Evaluated")},
        {"KPI": "PPMH (Post Purchase Mission Happiness)", "Current Value": row.get("PPMH"), "Rating": row.get("PPMH Rating", "Not Evaluated")},
        {"KPI": "OTIF (On Time In Full)", "Current Value": row.get("OTIF"), "Rating": row.get("OTIF Rating", "Not Evaluated")},
        {"KPI": "DPMO (Defects Per Million Opp.)", "Current Value": row.get("DPMO"), "Rating": "Not Evaluated"},
        {"KPI": "Sample Service & Lab-Dip", "Current Value": row.get("Sample Service Score"), "Rating": row.get("Sample Service Rating", "Not Evaluated")},
        {"KPI": "Vendor Total Score", "Current Value": row.get("Vendor Rating Total Score"), "Rating": row.get("Vendor Performance Rating", "Not Evaluated")}
    ]

    def get_insight(r_item):
        kpi = r_item["KPI"]
        val_raw = pd.to_numeric(r_item.get("Current Value"), errors="coerce")
        
        if "VPQI" in kpi:
            v_pct = val_raw * 100 if (pd.notnull(val_raw) and val_raw <= 1.0) else (val_raw if pd.notnull(val_raw) else 0)
            if v_pct >= 98: return "Supplier demonstrates excellent manufacturing process capability with highly consistent fabric output."
            if v_pct >= 95: return "Supplier maintains stable manufacturing quality with minor improvement opportunities."
            if v_pct >= 90: return "Manufacturing process quality requires closer monitoring to maintain sourcing standards."
            return "Supplier process quality is below acceptable sourcing expectations."
            
        elif "PPMH" in kpi:
            p_pct = val_raw * 100 if (pd.notnull(val_raw) and val_raw <= 1.0) else (val_raw if pd.notnull(val_raw) else 0)
            if p_pct >= 70: return "High end-consumer & store post-purchase garment satisfaction index."
            if p_pct >= 50: return "Moderate post-purchase customer satisfaction; monitor garment wash fastness & finish durability."
            return "Low post-purchase customer satisfaction index; requires technical review on fabric performance."
            
        elif "OTIF" in kpi:
            o_pct = val_raw * 100 if (pd.notnull(val_raw) and val_raw <= 1.0) else (val_raw if pd.notnull(val_raw) else 0)
            if o_pct >= 95: return "Supplier consistently delivers fabric on schedule, supporting factory garment production timelines."
            if o_pct >= 90: return "Delivery reliability is dependable with occasional minor delays."
            return "Frequent delivery delays present garment factory line-stoppage risk."
            
        elif "DPMO" in kpi:
            if pd.notnull(val_raw) and val_raw > 0:
                if val_raw < 25: return "Raw fabric inspection defect rate remains exceptionally low."
                if val_raw <= 100: return "Audit defect frequency remains within acceptable operational limits."
                return "Elevated fabric defect frequency requires process improvement."
            return "Low audit defect count during raw fabric inspection."
            
        elif "Sample Service" in kpi:
            if pd.notnull(val_raw) and val_raw >= 12: return "Fast lab-dip color approval and rapid sample yardage development turnaround (<7 days)."
            return "Standard sampling turnaround time."
            
        elif "Vendor Total Score" in kpi:
            if val_raw >= 85: return "Ranked among ABLBL's highest-performing strategic fabric partners."
            if val_raw >= 75: return "Supplier consistently meets enterprise sourcing quality & commercial expectations."
            return "Supplier overall performance requires active management review."
            
        return "Standard performance level."

    def get_procurement_action(r_item):
        kpi = r_item["KPI"]
        val_raw = pd.to_numeric(r_item.get("Current Value"), errors="coerce")
        
        if "VPQI" in kpi:
            v_pct = val_raw * 100 if (pd.notnull(val_raw) and val_raw <= 1.0) else (val_raw if pd.notnull(val_raw) else 0)
            if v_pct >= 95: return "Approved for core high-volume Shirting & Bottomwear production."
            return "Increase incoming fabric inspection frequency."
            
        elif "PPMH" in kpi:
            p_pct = val_raw * 100 if (pd.notnull(val_raw) and val_raw <= 1.0) else (val_raw if pd.notnull(val_raw) else 0)
            if p_pct >= 60: return "Maintain current fabric sourcing specification."
            return "Collaborate with mill technical team on fabric finish & wash durability."
            
        elif "OTIF" in kpi:
            o_pct = val_raw * 100 if (pd.notnull(val_raw) and val_raw <= 1.0) else (val_raw if pd.notnull(val_raw) else 0)
            if o_pct >= 95: return "Preferred supplier for time-critical seasonal collection drops."
            return "Monitor logistics dispatch schedules closely."
            
        elif "DPMO" in kpi:
            return "Continue routine 4-point system fabric inspection."
            
        elif "Sample Service" in kpi:
            return "Preferred vendor for new product development & rapid sampling."
            
        elif "Vendor Total Score" in kpi:
            if val_raw >= 80: return "Allocate priority sourcing volume for 2025-2026 programs."
            return "Review sourcing allocation during quarterly performance audit."
            
        return "Standard procurement action."

    kpi_df = pd.DataFrame(kpi_data)
    kpi_df["Current Value"] = kpi_df["Current Value"].astype(object)
    kpi_df["Executive Insight"] = kpi_df.apply(get_insight, axis=1)
    kpi_df["Procurement Action"] = kpi_df.apply(get_procurement_action, axis=1)

    # Format values for display table
    for idx, row_data in kpi_df.iterrows():
        val_tmp = pd.to_numeric(row_data["Current Value"], errors="coerce")
        kpi_name = row_data["KPI"]
        if ("VPQI" in kpi_name or "PPMH" in kpi_name or "OTIF" in kpi_name) and pd.notnull(val_tmp):
            pct_val = val_tmp * 100 if val_tmp <= 1.0 else val_tmp
            kpi_df.at[idx, "Current Value"] = f"{pct_val:.1f}%"
        elif "DPMO" in kpi_name:
            if pd.notnull(val_tmp) and val_tmp > 0:
                kpi_df.at[idx, "Current Value"] = fmt_int(val_tmp)
            else:
                kpi_df.at[idx, "Current Value"] = "Low Defect Count"
        elif "Vendor Total Score" in kpi_name and pd.notnull(val_tmp):
            kpi_df.at[idx, "Current Value"] = f"{val_tmp:.1f} / 100"
        elif "Sample Service" in kpi_name and pd.notnull(val_tmp):
            kpi_df.at[idx, "Current Value"] = f"{val_tmp:.0f} / 15"

    st.dataframe(
        kpi_df[['KPI', 'Current Value', 'Rating', 'Executive Insight', 'Procurement Action']],
        use_container_width=True,
        hide_index=True
    )
    st.divider()

    # Dynamic Sourcing Intelligence Classification Logic
    score_val = float(row.get("Vendor Rating Total Score", 0))
    rank_val = int(row.get("Current Overall Rank", 999))
    perf_val = str(row.get("Vendor Performance Rating", "Good")).strip()
    vpqi_r = str(row.get("VPQI Rating", "Good")).strip()
    otif_r = str(row.get("OTIF Rating", "Good")).strip()
    ppmh_r = str(row.get("PPMH Rating", "Good")).strip()

    if score_val >= 80 or rank_val <= 10 or perf_val in ["Excellent", "Very Good"]:
        assessment = "🟢 Preferred Strategic Partner"
    elif score_val >= 70 or rank_val <= 30 or perf_val == "Good":
        assessment = "🟡 Approved Vendor (Periodic Review)"
    else:
        assessment = "🔴 Corrective Action Required (SCAR)"

    st.subheader("🧠 Sourcing Intelligence")

    with st.container(border=True):
        st.markdown(f"### {assessment}")

        st.write("#### Business Summary")
        summary_text = (
            f"**{selected_vendor}** ranks **#{rank_val} overall out of {total_vendors} fabric suppliers** "
            f"in the 2025-2026 Quality Master evaluation with an overall score of **{score_val:.1f} / 100** ({perf_val}). "
            f"The supplier demonstrates strong manufacturing process quality ({vpqi_pct:.1f}% VPQI) "
            f"and dependable delivery reliability ({otif_pct:.1f}% OTIF) for ABLBL brands ({assoc_brand})."
        )
        st.write(summary_text)

        col_str, col_foc = st.columns(2)
        with col_str:
            st.write("#### Key Strengths")
            if vpqi_pct >= 90:
                st.markdown(f"✔ **Strong Process Quality Index (VPQI: {vpqi_pct:.1f}%)**")
            if otif_pct >= 90:
                st.markdown(f"✔ **Dependable Delivery Performance (OTIF: {otif_pct:.1f}%)**")
            sample_sc = float(row.get("Sample Service Score", 0))
            if sample_sc >= 10:
                st.markdown(f"✔ **Top-Tier Sampling Service & Lab-Dip Turnaround ({sample_sc:.0f}/15)**")
            if float(row.get("CC Score", 0)) >= 8:
                st.markdown("✔ **Zero Major Customer Complaint Escalations**")

        with col_foc:
            st.write("#### Focus Areas for Enhancement")
            if ppmh_pct < 70:
                st.markdown(f"⚠️ **Post Purchase Mission Happiness (PPMH: {ppmh_pct:.1f}%)**: Collaborate with mill to enhance fabric finish & post-wash durability.")
            if otif_pct < 95:
                st.markdown(f"⚠️ **Delivery Adherence (OTIF: {otif_pct:.1f}%)**: Monitor production dispatch schedules for time-critical orders.")
            if vpqi_pct < 95:
                st.markdown(f"⚠️ **Process Quality (VPQI: {vpqi_pct:.1f}%)**: Conduct periodic mill audits to maintain consistent quality pass rate.")

        st.write("#### Recommended Sourcing Action")
        if assessment == "🟢 Preferred Strategic Partner":
            st.success(f"**Prioritize Sourcing Allocation:** Maintain primary supplier status for 2025-2026 {assoc_brand} fabric programs while partnering on finish enhancements.")
        elif assessment == "🟡 Approved Vendor (Periodic Review)":
            st.warning(f"**Approved with Monitoring:** Continue sourcing while reviewing quarterly quality adherence for {assoc_brand}.")
        else:
            st.error(f"**Issue Corrective Action Request (SCAR):** Review supplier performance and implement quality improvements before expanding allocation.")

    # Smart Conditional Alternate Supplier Recommendation
    # Show alternate recommendation ONLY if currently selected vendor is lower-ranked (rank_val > 20 or score_val < 80)
    if rank_val > 20 or score_val < 80:
        st.divider()
        st.subheader("🏆 Recommended Alternate Fabric Supplier")
        
        # Find category leader in the SAME fabric category as the selected vendor
        v_cat_clean = str(row.get("Vendor Category", "Fabric")).strip()
        same_cat_df = quality_df[quality_df["Vendor Category"].astype(str).str.strip().str.upper() == v_cat_clean.upper()]
        
        if not same_cat_df.empty:
            top_supplier_row = same_cat_df.sort_values(by="Current Overall Rank", ascending=True).iloc[0]
        else:
            top_supplier_row = quality_df.sort_values(by="Current Overall Rank", ascending=True).iloc[0]

        top_vpqi = float(top_supplier_row.get("VPQI", 0))
        top_vpqi_pct = top_vpqi * 100 if top_vpqi <= 1.0 else top_vpqi
        top_otif = float(top_supplier_row.get("OTIF", 0))
        top_otif_pct = top_otif * 100 if top_otif <= 1.0 else top_otif
        top_score = float(top_supplier_row.get("Vendor Rating Total Score", 0))
        top_rank = int(top_supplier_row.get("Current Overall Rank", 1))
        top_name = str(top_supplier_row.get("Vendor Name", "Category Leader"))

        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Category Leader ({v_cat_clean}):** {top_name}")
                st.write(f"**Performance Rating:** {top_supplier_row.get('Vendor Performance Rating', 'Excellent')}")
            with col2:
                st.write(f"**Category Score:** {top_score:.1f} / 100")
                st.write(f"**Global Rank:** Rank #{top_rank}")

            st.write("#### Why Consider this Alternate Mill")
            st.markdown(f"• **Category Benchmark Leader:** Ranked **#{top_rank}** overall in **{v_cat_clean}** fabric evaluation.")
            st.markdown(f"• **High Quality & Delivery Reliability:** Demonstrates **{top_vpqi_pct:.1f}% VPQI** process quality and **{top_otif_pct:.1f}% OTIF** on-time delivery.")
            st.markdown(f"• **Dual-Sourcing Recommendation:** Ideal strategic partner to reallocate volume or dual-source if {selected_vendor} faces capacity or delivery delays.")

    st.divider()
    