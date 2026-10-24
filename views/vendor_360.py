"""
====================================================
Vendor 360 - Enterprise Supplier Intelligence
ABLBL Sourcing Intelligence Platform
====================================================
"""

import streamlit as st
import pandas as pd
from utils.header import render_header
from utils.theme import load_css
from data.vendor_service import get_vendor_data
from utils.formatters import fmt_price, fmt_id
from utils.image_utils import get_image_base64

def get_unique_list(df, column):
    """Helper to get clean, sorted unique values for display."""
    if column not in df.columns:
        return []
    vals = df[column].dropna().astype(str).str.strip().unique()
    vals = [v for v in vals if v and v.lower() != 'nan']
    return sorted(vals)

def render_vendor_360(vendor_name):
    """
    Renders the detailed Vendor 360 intelligence dashboard.
    """
    load_css()
    
    # 1. Load Data
    df = get_vendor_data()
    
    # 2. Setup Selection Logic
    selected_vendor = st.session_state.get("selected_vendor", vendor_name)
    selected_fabric = st.session_state.get("selected_fabric_code")
    
    # vendor_info holds ALL rows for the supplier (for Capability sections)
    vendor_info = df[df["Vendor Name"] == selected_vendor]
    
    if vendor_info.empty:
        st.error(f"Vendor '{selected_vendor}' not found.")
        return

    # 3. Determine Fabric Column and filter for identity
    fab_col = "Fab Code" if "Fab Code" in df.columns else "Fabric Code"
    
    selected_vendor_row = pd.DataFrame()
    
    if selected_fabric:
        selected_vendor_row = vendor_info[
            vendor_info[fab_col] == selected_fabric
        ]
        
    if selected_vendor_row.empty:
        selected_vendor_row = vendor_info.iloc[[0]]
    
    # v contains the identity-specific data from the single selected row
    v = selected_vendor_row.iloc[0]

    # Render Header
    render_header(
        page_title=f"🏢 {selected_vendor}",
        page_description="Enterprise Supplier Intelligence Dashboard"
    )

    st.info(
        "💡 **Page Purpose:** Enterprise 360 Supplier Profile. "
        "Analyze vendor historical performance, track price movements for specific technical fabric specs across seasons, and evaluate strategic vendor tiering."
    )

    col_back, _ = st.columns([2.5, 5])
    with col_back:
        if st.button("⬅️ Back to Capability Search"):
            st.session_state["page"] = "📁 Vendor Capability Search"
            st.rerun()

    qa_col1, qa_col2 = st.columns(2)
    with qa_col1:
        if st.button("📊 View Supplier Quality Intelligence", use_container_width=True):
            st.session_state["selected_vendor"] = selected_vendor
            st.session_state["page"] = "📊 Supplier Quality Intelligence"
            st.rerun()
    with qa_col2:
        st.button("📈 Commercial Intelligence (Coming Soon)", disabled=True, use_container_width=True)
    st.divider()

    # --- SECTION 1: VENDOR IDENTITY & MATERIAL SPECIMEN ---
    st.subheader("1. Vendor Identity & Material Specimen")
    
    col_metrics, col_swatch = st.columns([3, 1.1])
    
    with col_metrics:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Vendor Name", v.get("Vendor Name", "N/A"))
        c2.metric("Vendor Code", fmt_id(v.get("Vendor Code", "N/A")))
        c3.metric("Mill", v.get("Mills", "N/A"))
        c4.metric("Fabric Code", v.get(fab_col, "N/A"))
        
        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Origin", v.get("Origin (Imp/Dom)", "N/A"))
        c6.metric("Mill Category", v.get("Mill Category", "N/A"))
        c7.metric("Currency", v.get("Currency", "N/A"))
        c8.metric("NLC", fmt_price(v.get("Actual NLC", 0)))

    with col_swatch:
        weave_str = str(v.get("Weave", "")).lower()
        comp_str = str(v.get("ERP Standard Composition", v.get("Composition", ""))).lower()
        
        if "twill" in weave_str:
            swatch_file = "swatch_twill.jpg"
            swatch_label = "2/1 Twill Weave"
        elif "oxford" in weave_str:
            swatch_file = "swatch_oxford.jpg"
            swatch_label = "Oxford Basketweave"
        elif "linen" in comp_str or "flax" in comp_str:
            swatch_file = "swatch_linen.jpg"
            swatch_label = "Pure Linen Slub"
        else:
            swatch_file = "swatch_oxford.jpg"
            swatch_label = "Fabric Weave Specimen"
            
        swatch_b64 = get_image_base64(swatch_file)
        if swatch_b64:
            st.markdown(
                f'''
                <div class="swatch-card" style="margin-top: 4px;">
                    <div class="swatch-img-container" style="height: 140px;">
                        <img src="{swatch_b64}" alt="{swatch_label}">
                        <span class="swatch-badge">Macro Zoom</span>
                    </div>
                    <div class="swatch-details" style="padding: 8px 12px;">
                        <div class="swatch-title" style="font-size: 0.85rem;">{swatch_label}</div>
                        <div class="swatch-subtitle" style="font-size: 0.72rem;">Hover to inspect weave structure</div>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
            
    st.divider()

    # Map capability fields to column names
    cap_fields = {
        "Brand": "Brand",
        "Product": "Product",
        "Category": "Category",
        "Season": "Season",
        "FY": "FY",
        "Composition": "ERP Standard Composition" if "ERP Standard Composition" in vendor_info.columns else "Composition",
        "Count": "ERP Count Capability" if "ERP Count Capability" in vendor_info.columns else "Count",
        "Const": "Construction Standardized" if "Construction Standardized" in vendor_info.columns else ("Const" if "Const" in vendor_info.columns else "Construction"),
        "Weave": "Weave",
        "Finish": "Finish",
        "Dye Type": "Dye Type",
        "Pattern": "Pattern",
        "Width": "Width",
        "Fiber": "Fiber"
    }

    # Build Cascading Filtered Dataframe
    cascading_df = vendor_info.copy()
    active_filters = {}
    
    for f_key, f_col in cap_fields.items():
        if f_col in vendor_info.columns:
            sel_val = st.session_state.get(f"cap_filter_{f_key}", "All")
            if sel_val != "All":
                active_filters[f_key] = sel_val
                cascading_df = cascading_df[
                    cascading_df[f_col].astype(str).str.strip() == str(sel_val).strip()
                ]

    # Active Filters & Reset Bar
    if active_filters:
        f_desc = " | ".join([f"**{k}**: `{v}`" for k, v in active_filters.items()])
        af_col1, af_col2 = st.columns([4, 1])
        with af_col1:
            st.info(f"⚡ **Active Capability Filter ({len(cascading_df)} of {len(vendor_info)} Line Items):** {f_desc}")
        with af_col2:
            if st.button("🔄 Clear Filters", use_container_width=True):
                for f_key in cap_fields.keys():
                    st.session_state[f"cap_filter_{f_key}"] = "All"
                st.rerun()

    # --- SECTION 2: BUSINESS CAPABILITY ---
    st.subheader("2. Business Capability")
    b_cols = ["Brand", "Product", "Category", "Season", "FY"]
    for i in range(0, len(b_cols), 2):
        row_cols = st.columns(2)
        for j in range(2):
            if i + j < len(b_cols):
                col_key = b_cols[i + j]
                col_name = cap_fields.get(col_key, col_key)
                
                # Options available across vendor
                vendor_options = get_unique_list(vendor_info, col_name)
                # Currently matching items after cascading filter
                filtered_options = get_unique_list(cascading_df, col_name)
                
                with row_cols[j]:
                    with st.expander(f"{col_key} ({len(filtered_options)})", expanded=False):
                        sel_idx = 0
                        current_sel = st.session_state.get(f"cap_filter_{col_key}", "All")
                        all_opts = ["All"] + vendor_options
                        if current_sel in all_opts:
                            sel_idx = all_opts.index(current_sel)
                            
                        st.selectbox(
                            f"Filter by {col_key}:",
                            all_opts,
                            index=sel_idx,
                            key=f"cap_filter_{col_key}"
                        )
                        
                        df_vals = pd.DataFrame(filtered_options, columns=[col_key])
                        st.dataframe(df_vals, use_container_width=True, hide_index=True, height=160)
    st.divider()

    # --- SECTION 3: MANUFACTURING CAPABILITY MATRIX ---
    st.subheader("3. Manufacturing Capability Matrix")
    m_cols = ["Composition", "Count", "Const", "Weave", "Finish", "Dye Type", "Pattern", "Width", "Fiber"]
    for i in range(0, len(m_cols), 3):
        row_cols = st.columns(3)
        for j in range(3):
            if i + j < len(m_cols):
                col_key = m_cols[i + j]
                display_name = "Construction" if col_key == "Const" else col_key
                col_name = cap_fields.get(col_key, col_key)
                
                # Options available across vendor
                vendor_options = get_unique_list(vendor_info, col_name)
                # Currently matching items after cascading filter
                filtered_options = get_unique_list(cascading_df, col_name)
                
                with row_cols[j]:
                    with st.expander(f"{display_name} ({len(filtered_options)})", expanded=False):
                        sel_idx = 0
                        current_sel = st.session_state.get(f"cap_filter_{col_key}", "All")
                        all_opts = ["All"] + vendor_options
                        if current_sel in all_opts:
                            sel_idx = all_opts.index(current_sel)
                            
                        st.selectbox(
                            f"Filter by {display_name}:",
                            all_opts,
                            index=sel_idx,
                            key=f"cap_filter_{col_key}"
                        )
                        
                        df_vals = pd.DataFrame(filtered_options, columns=[display_name])
                        st.dataframe(df_vals, use_container_width=True, hide_index=True, height=180)
    st.divider()

    # --- SECTION 4: HISTORICAL NLC & NEGOTIATION TREND ---
    st.subheader("4. 📈 Historical NLC & Negotiation Trend")
    st.markdown("Track this vendor's historical NLC movements across seasons for specific technical fabric specifications to support price negotiations.")

    # Step 1: Pre-filter vendor_info to ONLY rows with valid NLC price data (> 0)
    nlc_cols_to_check = [col for col in ["Actual NLC", "AW23 NLC", "SS24 NLC", "AW24 NLC", "SS25 NCL", "AW25 NLC", "SS26 NLC", "AW26 NLC"] if col in vendor_info.columns]
    
    def row_has_price(row):
        for c in nlc_cols_to_check:
            val = pd.to_numeric(row.get(c), errors="coerce")
            if pd.notnull(val) and val > 0:
                return True
        return False

    nlc_active_info = vendor_info[vendor_info.apply(row_has_price, axis=1)].copy()
    if nlc_active_info.empty:
        nlc_active_info = vendor_info.copy()

    comp_col_name = "ERP Standard Composition" if "ERP Standard Composition" in vendor_info.columns else "Composition"
    cnt_col_name = "ERP Count Capability" if "ERP Count Capability" in vendor_info.columns else "Count"
    weave_col_name = "Weave" if "Weave" in vendor_info.columns else None
    finish_col_name = "Finish" if "Finish" in vendor_info.columns else None
    orig_col_name = "Origin (Imp/Dom)" if "Origin (Imp/Dom)" in vendor_info.columns else "Origin"

    # Default values from selected fabric
    def_comp = v.get(comp_col_name, "All")
    def_cnt = v.get(cnt_col_name, "All")
    def_weave = v.get(weave_col_name, "All") if weave_col_name else "All"
    def_finish = v.get(finish_col_name, "All") if finish_col_name else "All"
    def_orig = v.get(orig_col_name, "All")

    t_col1, t_col2, t_col3, t_col4, t_col5 = st.columns(5)

    # 1. Composition Options (from NLC-active rows)
    comp_options = ["All"] + sorted([str(x).strip() for x in nlc_active_info[comp_col_name].dropna().unique() if str(x).strip() and str(x).lower() != "nan"])
    sel_comp = t_col1.selectbox("Composition", comp_options, index=comp_options.index(str(def_comp).strip()) if str(def_comp).strip() in comp_options else 0, key="trend_comp")

    # Cascading Filter Step A: Filter by Composition
    f_df = nlc_active_info.copy()
    if sel_comp != "All":
        f_df = f_df[f_df[comp_col_name].astype(str).str.strip() == sel_comp]

    # 2. Yarn Count Options (Cascaded from selected Composition)
    cnt_options = ["All"] + sorted([str(x).strip() for x in f_df[cnt_col_name].dropna().unique() if str(x).strip() and str(x).lower() != "nan"])
    sel_cnt = t_col2.selectbox("Yarn Count", cnt_options, index=cnt_options.index(str(def_cnt).strip()) if str(def_cnt).strip() in cnt_options else 0, key="trend_cnt")

    # Cascading Filter Step B: Filter by Yarn Count
    if sel_cnt != "All":
        f_df = f_df[f_df[cnt_col_name].astype(str).str.strip() == sel_cnt]

    # 3. Weave Options (Cascaded from Composition + Count)
    weave_options = ["All"] + sorted([str(x).strip() for x in f_df[weave_col_name].dropna().unique() if str(x).strip() and str(x).lower() != "nan"]) if weave_col_name else ["All"]
    sel_weave = t_col3.selectbox("Weave Spec", weave_options, index=weave_options.index(str(def_weave).strip()) if str(def_weave).strip() in weave_options else 0, key="trend_weave")

    # Cascading Filter Step C: Filter by Weave
    if weave_col_name and sel_weave != "All":
        f_df = f_df[f_df[weave_col_name].astype(str).str.strip() == sel_weave]

    # 4. Finish Options (Cascaded from Composition + Count + Weave)
    finish_options = ["All"] + sorted([str(x).strip() for x in f_df[finish_col_name].dropna().unique() if str(x).strip() and str(x).lower() != "nan"]) if finish_col_name else ["All"]
    sel_finish = t_col4.selectbox("Finish Spec", finish_options, index=finish_options.index(str(def_finish).strip()) if str(def_finish).strip() in finish_options else 0, key="trend_finish")

    # Cascading Filter Step D: Filter by Finish
    if finish_col_name and sel_finish != "All":
        f_df = f_df[f_df[finish_col_name].astype(str).str.strip() == sel_finish]

    # 5. Origin Options (Cascaded)
    orig_options = ["All"] + sorted([str(x).strip() for x in f_df[orig_col_name].dropna().unique() if str(x).strip() and str(x).lower() != "nan"])
    sel_orig = t_col5.selectbox("Origin", orig_options, index=orig_options.index(str(def_orig).strip()) if str(def_orig).strip() in orig_options else 0, key="trend_orig")

    if sel_orig != "All":
        f_df = f_df[f_df[orig_col_name].astype(str).str.strip() == sel_orig]

    trend_df = f_df.copy()

    # Extract Seasonal NLC Columns (AW23 NLC, SS24 NLC, AW24 NLC, SS25 NCL, AW25 NLC, SS26 NLC, AW26 NLC, Actual NLC)
    seasonal_nlc_cols = [
        ("AW23", "AW23 NLC"), ("SS24", "SS24 NLC"), ("AW24", "AW24 NLC"), 
        ("SS25", "SS25 NCL"), ("AW25", "AW25 NLC"), ("SS26", "SS26 NLC"), 
        ("AW26", "AW26 NLC")
    ]
    
    trend_points = []
    
    # Method 1: Check multi-season columns across matching rows
    for season_code, col_key in seasonal_nlc_cols:
        if col_key in trend_df.columns:
            vals = pd.to_numeric(trend_df[col_key], errors="coerce").dropna()
            vals = vals[vals > 0]
            if not vals.empty:
                trend_points.append({
                    "Season": season_code,
                    "Average NLC": round(vals.mean(), 2),
                    "Sample Count": len(vals),
                    "Source Column": col_key
                })

    # Include Actual NLC dynamically with actual season tag if available
    if "Actual NLC" in trend_df.columns:
        actual_vals = pd.to_numeric(trend_df["Actual NLC"], errors="coerce").dropna()
        actual_vals = actual_vals[actual_vals > 0]
        if not actual_vals.empty:
            actual_seasons = trend_df.loc[actual_vals.index, "Season"].dropna().astype(str).str.strip().unique()
            s_tag = f" ({actual_seasons[0]})" if (len(actual_seasons) > 0 and actual_seasons[0] != "" and actual_seasons[0].lower() != "nan") else ""
            season_label = f"Actual NLC{s_tag}"
            source_label = f"Actual NLC{s_tag}"
            trend_points.append({
                "Season": season_label,
                "Average NLC": round(actual_vals.mean(), 2),
                "Sample Count": len(actual_vals),
                "Source Column": source_label
            })

    # Method 2: Fallback if Season column is populated across rows
    if not trend_points and "Season" in trend_df.columns and "Actual NLC" in trend_df.columns:
        t_clean = trend_df.copy()
        t_clean["Actual NLC"] = pd.to_numeric(t_clean["Actual NLC"], errors="coerce")
        t_clean = t_clean.dropna(subset=["Actual NLC", "Season"])
        if not t_clean.empty:
            grp = t_clean.groupby("Season", as_index=False)["Actual NLC"].mean().round(2)
            for _, r in grp.iterrows():
                trend_points.append({
                    "Season": str(r["Season"]).strip(),
                    "Average NLC": r["Actual NLC"],
                    "Sample Count": 1,
                    "Source Column": f"Actual NLC ({r['Season']})"
                })

    if trend_points:
        import plotly.express as px
        
        plot_df = pd.DataFrame(trend_points)
        
        # Create line chart
        fig = px.line(
            plot_df,
            x="Season",
            y="Average NLC",
            markers=True,
            title=f"NLC Negotiation Trend for {selected_vendor} ({sel_comp} | {sel_cnt})",
            labels={"Average NLC": "NLC (₹/m)", "Season": "Season / Source"},
            template="plotly_dark"
        )
        fig.update_traces(line=dict(width=3, color="#F2871F"), marker=dict(size=9, color="#D62E1F"))
        fig.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

        # Negotiation KPI Insights across all seasons & line items for selected spec
        season_cols = ["AW23 NLC", "SS24 NLC", "AW24 NLC", "SS25 NCL", "AW25 NLC", "SS26 NLC", "AW26 NLC", "Actual NLC"]
        existing_seasons = [c for c in season_cols if c in trend_df.columns]
        
        all_spec_nlcs = []
        for c in existing_seasons:
            vals = pd.to_numeric(trend_df[c], errors="coerce").dropna()
            vals = vals[vals > 0]
            all_spec_nlcs.extend(vals.tolist())
            
        # Market Benchmark comparison for same composition across other vendors
        other_v_df = df[(df["Vendor Name"] != selected_vendor) & (df[comp_col_name].astype(str).str.strip() == str(sel_comp).strip())] if sel_comp != "All" else df[df["Vendor Name"] != selected_vendor]
        other_nlcs = pd.to_numeric(other_v_df["Actual NLC"], errors="coerce").dropna()
        other_nlcs = other_nlcs[other_nlcs > 0]
        mkt_avg = other_nlcs.mean() if not other_nlcs.empty else None

        if all_spec_nlcs:
            nlc_series = pd.Series(all_spec_nlcs)
            min_nlc = nlc_series.min()
            avg_nlc = nlc_series.mean()
            max_nlc = nlc_series.max()
            
            # Variance vs Market Benchmark
            var_delta = None
            if mkt_avg and mkt_avg > 0:
                diff_pct = ((avg_nlc - mkt_avg) / mkt_avg) * 100
                var_delta = f"{diff_pct:+.1f}% vs Market Avg (₹{mkt_avg:,.2f})"
            
            n1, n2, n3, n4 = st.columns(4)
            n1.metric(
                "Lowest Quoted NLC", 
                f"₹{min_nlc:,.2f}", 
                delta="Min Seasonal Quote", 
                delta_color="off"
            )
            n2.metric(
                "Average Seasonal NLC", 
                f"₹{avg_nlc:,.2f}", 
                delta=var_delta if var_delta else f"Mean of {len(nlc_series)} Quotes", 
                delta_color="off" if not var_delta else ("inverse" if diff_pct > 0 else "normal")
            )
            n3.metric(
                "Highest Quoted NLC", 
                f"₹{max_nlc:,.2f}", 
                delta="Peak Seasonal Quote", 
                delta_color="off"
            )
            n4.metric(
                "Matching Spec Quotes", 
                f"{len(trend_df)} Line Items", 
                delta=f"Market Pool: {len(other_v_df)} Items", 
                delta_color="off"
            )

        # Technical Specification Summary Matrix Card
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.caption("📋 **Technical Fabric Specification Matrix behind Filtered NLC**")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            spec_row = trend_df.iloc[0] if not trend_df.empty else v
            m_col1.markdown(f"**Composition:** {sel_comp if sel_comp != 'All' else spec_row.get(comp_col_name, 'N/A')}")
            m_col2.markdown(f"**Yarn Count:** {sel_cnt if sel_cnt != 'All' else spec_row.get(cnt_col_name, 'N/A')}")
            m_col3.markdown(f"**Weave:** {spec_row.get('Weave', 'N/A')}")
            m_col4.markdown(f"**Finish / Dye:** {spec_row.get('Finish', spec_row.get('Dye Type', 'N/A'))}")
    else:
        st.info("No multi-season NLC trend data available for the selected technical profile.")

    st.divider()

    # --- SECTION 5: VENDOR ANALYTICS ---
    st.subheader("5. Vendor Analytics")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Products", vendor_info["Product"].nunique() if "Product" in vendor_info.columns else vendor_info["Product "].nunique() if "Product " in vendor_info.columns else 1)
    k2.metric("Brands", vendor_info["Brand"].nunique() if "Brand" in vendor_info.columns else 1)
    k3.metric("Countries", vendor_info["Country"].nunique() if "Country" in vendor_info.columns else 1)
    k4.metric("Seasons", vendor_info["Season"].nunique() if "Season" in vendor_info.columns else 1)
    k5.metric("Fiber Types", vendor_info["Fiber"].nunique() if "Fiber" in vendor_info.columns else vendor_info["Composition"].nunique() if "Composition" in vendor_info.columns else 1)
    st.divider()

    # --- SECTION 6: 🤖 SOURCING INTELLIGENCE & DECISION ENGINE ---
    st.subheader("6. 🤖 Sourcing Intelligence & Decision Engine")
    st.markdown("Automated historical supplier scoring and negotiation decision support based on overall master data analytics.")

    # Calculate Decision Indicators
    vendor_avg_nlc = pd.to_numeric(vendor_info["Actual NLC"], errors="coerce").dropna().mean()
    cur_comp = v.get(comp_col_name, "")
    
    cat_df = df[df[comp_col_name].astype(str).str.strip() == str(cur_comp).strip()] if cur_comp else df
    cat_avg_nlc = pd.to_numeric(cat_df["Actual NLC"], errors="coerce").dropna().mean()

    # 1. Cost Competitiveness Rating
    if pd.notnull(vendor_avg_nlc) and pd.notnull(cat_avg_nlc) and cat_avg_nlc > 0:
        diff_pct = ((vendor_avg_nlc - cat_avg_nlc) / cat_avg_nlc) * 100
        if diff_pct < -4:
            cost_rating = f"🟢 Competitive ({abs(diff_pct):.1f}% below avg)"
            cost_status = "cheaper"
        elif diff_pct > 4:
            cost_rating = f"🔴 Premium (+{diff_pct:.1f}% vs avg)"
            cost_status = "premium"
        else:
            cost_rating = f"🟡 Market Aligned (±{abs(diff_pct):.1f}%)"
            cost_status = "aligned"
    else:
        cost_rating = "🟡 Market Aligned"
        cost_status = "aligned"

    # 2. NLC Price Stability Rating
    nlc_series = pd.to_numeric(vendor_info["Actual NLC"], errors="coerce").dropna()
    if len(nlc_series) > 1 and nlc_series.mean() > 0:
        cv = (nlc_series.std() / nlc_series.mean()) * 100
        if cv < 5:
            stability_rating = f"🟢 High Stability ({cv:.1f}% variance)"
            stable_status = True
        elif cv < 12:
            stability_rating = f"🟡 Moderate Variance ({cv:.1f}%)"
            stable_status = True
        else:
            stability_rating = f"🔴 High Fluctuation ({cv:.1f}%)"
            stable_status = False
    else:
        stability_rating = "🟢 High Stability"
        stable_status = True

    # 3. Portfolio Versatility Rating
    fabric_types_count = vendor_info['Product'].nunique() if 'Product' in vendor_info.columns else 1
    if fabric_types_count >= 3:
        versatility_rating = f"🟢 Multi-Category ({fabric_types_count} Types)"
    else:
        versatility_rating = f"🟡 Specialized ({fabric_types_count} Line)"

    # 4. Vendor Sourcing Tier
    if cost_status == "cheaper" and stable_status:
        tier_rating = "⭐ Tier 1 Preferred Supplier"
    elif cost_status == "premium":
        tier_rating = "⚠️ Tier 2 (Renegotiation Target)"
    else:
        tier_rating = "🔹 Tier 2 Commercial Supplier"

    # Render Metric Cards with Simplified Business Titles
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Cost Competitiveness vs Market", cost_rating)
    d2.metric("Historical Price Volatility Risk", stability_rating)
    d3.metric("Product Range Specialization", versatility_rating)
    d4.metric("Vendor Strategic Rating", tier_rating)

    # 5. Dynamic AI Advice Banner
    if cost_status == "premium":
        st.warning(
            f"💡 **Sourcing Negotiation Advice:** {selected_vendor}'s historical NLC is {diff_pct:.1f}% above the category average for {cur_comp}. "
            "Leverage the historical NLC trend chart above in vendor discussions to negotiate prices down toward category benchmarks."
        )
    elif cost_status == "cheaper":
        st.success(
            f"💡 **Sourcing Negotiation Advice:** {selected_vendor} offers highly competitive historical NLC ({abs(diff_pct):.1f}% below category benchmark). "
            "Recommended for primary volume allocation in upcoming development cycles."
        )
    else:
        st.info(
            f"💡 **Sourcing Negotiation Advice:** {selected_vendor} maintains consistent, market-aligned historical pricing. "
            "Recommended as a reliable secondary sourcing partner for core fabric developments."
        )
