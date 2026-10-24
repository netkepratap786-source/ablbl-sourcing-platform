"""
====================================================
Yarn Market Intelligence Module
ABLBL Sourcing Intelligence Platform
====================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.header import render_header
from utils.theme import load_css
from data.loaders import load_yarn_master

def format_currency(val, unit):
    """Professional formatting for currency values."""
    try:
        val = float(val)
        return f"₹{val:,.0f} / {unit}" if "₹" in str(unit) else f"{val:,.0f} {unit}"
    except (ValueError, TypeError):
        return "—"

def get_month_num(m):
    """Helper for calendar-based sorting."""
    month_map = {
        'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
        'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
        'aug': 8, 'august': 8, 'sep': 9, 'september': 9, 'oct': 10, 'october': 10,
        'nov': 11, 'november': 11, 'dec': 12, 'december': 12
    }
    return month_map.get(str(m).lower(), 99)

def render_yarn_market():
    load_css()
    render_header(
        page_title="🧶 Yarn Market Intelligence",
        page_description="Enterprise sourcing dashboard"
    )

    df = load_yarn_master()
    if df.empty:
        st.error("Market data unavailable.")
        return

    # Data Preparation
    df['Year'] = df['Year'].astype(str)
    df['Date'] = pd.to_datetime(df['Year'] + '-' + df['Month'].astype(str) + '-01', errors='coerce')
    df = df.dropna(subset=['Date', 'Standard Price'])

    # --- 1. MARKET FILTERS ---
    st.markdown("### 🔍 Market Filters")
    f_df = df.copy()
    r1, r2 = st.columns(4), st.columns(4)

    # Row 1 Cascading
    cat = r1[0].selectbox("Yarn Category", ["All"] + sorted(f_df["Yarn Category"].dropna().unique()))
    if cat != "All": f_df = f_df[f_df["Yarn Category"] == cat]
    
    mat = r1[1].selectbox("Material", ["All"] + sorted(f_df["Material"].dropna().unique()))
    if mat != "All": f_df = f_df[f_df["Material"] == mat]
    
    ori = r1[2].selectbox("Origin", ["All"] + sorted(f_df["Origin"].dropna().unique()))
    if ori != "All": f_df = f_df[f_df["Origin"] == ori]
    
    cnt = r1[3].selectbox("Count", ["All"] + sorted(f_df["Count"].dropna().unique(), key=lambda x: str(x)))
    if cnt != "All": f_df = f_df[f_df["Count"] == cnt]

    # Row 2 Cascading
    var = r2[0].selectbox("Variant", ["All"] + sorted(f_df["Variant"].dropna().unique()))
    if var != "All": f_df = f_df[f_df["Variant"] == var]
    
    yr = r2[1].selectbox("Year", ["All"] + sorted(f_df["Year"].dropna().unique(), reverse=True))
    if yr != "All": f_df = f_df[f_df["Year"] == yr]
    
    mo_vals = sorted(f_df["Month"].dropna().unique(), key=get_month_num)
    mo = r2[2].selectbox("Month", ["All"] + mo_vals)
    if mo != "All": f_df = f_df[f_df["Month"] == mo]
    
    supp = r2[3].selectbox("Supplier", ["All"] + sorted(f_df["Supplier / Mill"].dropna().unique()))
    
    # Dataset Architecture
    comparison_df = f_df.copy()
    display_df = f_df[f_df["Supplier / Mill"] == supp] if supp != "All" else f_df.copy()

    if display_df.empty:
        st.warning("No data found for selected specifications.")
        return

    latest = display_df.sort_values('Date').iloc[-1]

    # --- 2. MARKET SNAPSHOT ---
    st.subheader("📊 Market Snapshot")
    k1, k2, k3, k4, k5 = st.columns(5)
    
    hist = display_df.sort_values('Date')
    if len(hist) > 1:
        prev_price = hist.iloc[-2]['Standard Price']
        m_chg = ((latest['Standard Price'] - prev_price) / prev_price * 100)
        chg_str = f"{m_chg:+.1f}%"
    else:
        chg_str = "Not Available"

    k1.metric("Current Market Quote", format_currency(latest['Original Price'], latest['Original Unit']))
    k2.metric("Standard Price", format_currency(latest['Standard Price'], latest['Standard Unit']))
    k3.metric("Monthly Change %", chg_str)
    k4.metric("Qualified Suppliers", f_df['Supplier / Mill'].nunique())
    k5.metric("Terms", f"{latest.get('Price Basis', 'N/A')} | {latest.get('GST Included', 'N/A')}")

    # --- 3. MARKET TREND ANALYSIS ---
    st.subheader("📈 Market Trend Analysis")
    compare_suppliers = st.checkbox("Compare Suppliers", value=False)

    trend_df = f_df.copy()
    trend_df['Month_Num'] = trend_df['Month'].apply(get_month_num)
    trend_df = trend_df.sort_values(['Year', 'Month_Num'])
    trend_df['Month-Year'] = trend_df['Month'] + '-' + trend_df['Year'].str[-2:]

    if compare_suppliers:
        # Multi-supplier comparison line chart
        fig = px.line(
            trend_df.sort_values('Date'), 
            x='Date', 
            y='Standard Price', 
            color='Supplier / Mill', 
            markers=True,
            template="plotly_dark",
            hover_data=['Month', 'Supplier / Mill', 'Original Price', 'Standard Price', 'Price Basis', 'Source', 'Remarks']
        )
    else:
        if supp == "All" and yr == "All":
            # Average Market Trend (Line Chart across all months/years)
            avg_trend = trend_df.groupby(['Year', 'Month_Num', 'Month-Year', 'Date'], as_index=False)['Standard Price'].mean()
            avg_trend = avg_trend.sort_values(['Year', 'Month_Num'])
            
            fig = px.line(
                avg_trend, 
                x='Date', 
                y='Standard Price', 
                markers=True,
                template="plotly_dark"
            )
            fig.update_traces(line=dict(width=3, color='#1f77b4'), marker=dict(size=8))
        elif yr != "All" and supp == "All":
            # Year-Specific View: Bar Chart (Month vs Average Standard Price)
            year_trend = trend_df[trend_df['Year'] == str(yr)].groupby(['Month', 'Month_Num'], as_index=False)['Standard Price'].mean()
            year_trend = year_trend.sort_values('Month_Num')
            
            # Identify latest month in that year to highlight green
            latest_month = latest['Month'] if str(latest['Year']) == str(yr) else None
            colors = ['#1f77b4' if m != latest_month else '#2ca02c' for m in year_trend['Month']]

            fig = go.Figure(data=[
                go.Bar(
                    x=year_trend['Month'],
                    y=year_trend['Standard Price'],
                    marker_color=colors,
                    text=year_trend['Standard Price'].round(0),
                    textposition='auto'
                )
            ])
            fig.update_layout(template="plotly_dark")
        else:
            # Selected Supplier Trend
            supp_trend = trend_df[trend_df['Supplier / Mill'] == supp].sort_values(['Year', 'Month_Num'])
            fig = px.line(
                supp_trend, 
                x='Month-Year', 
                y='Standard Price', 
                markers=True,
                template="plotly_dark",
                hover_data=['Month', 'Supplier / Mill', 'Original Price', 'Standard Price', 'Price Basis', 'Source', 'Remarks']
            )
            fig.update_traces(line=dict(width=3, color='#1f77b4'), marker=dict(size=8))

    fig.update_layout(
        height=350, 
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Period",
        yaxis_title="Standard Price (₹/kg)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- 4. SUPPLIER COMPARISON ---
    st.subheader("🏢 Supplier Comparison")
    comp_df = comparison_df.sort_values('Date', ascending=False).drop_duplicates('Supplier / Mill')
    
    # Exclude 0 or near-zero data outliers for accurate baseline calculation
    valid_comp = comp_df[comp_df['Standard Price'] > 1.0]
    if not valid_comp.empty:
        comp_df = valid_comp.copy()
    comp_df = comp_df.sort_values('Standard Price')
    
    min_p = comp_df['Standard Price'].min()
    
    def calc_diff(x):
        if pd.isna(x) or min_p <= 0:
            return "—"
        diff = ((x - min_p) / min_p) * 100
        if abs(diff) < 0.05:
            return "0.0%"
        return f"+{diff:.1f}%" if diff > 0 else f"{diff:.1f}%"

    comp_df["Difference vs Cheapest %"] = comp_df["Standard Price"].apply(calc_diff)
    comp_df["Recommendation"] = comp_df["Standard Price"].apply(
        lambda x: "Best Buy" if (pd.notnull(x) and abs(x - min_p) < 0.05) else ("Competitive" if (pd.notnull(x) and (x - min_p)/min_p <= 0.05) else "Higher Cost")
    )

    # Format prices cleanly without trailing zeros for table display only (e.g. 115 instead of 115.000000, 177.3 instead of 177.300000)
    def format_clean_price(val):
        if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', '']:
            return "—"
        try:
            fval = float(val)
            rounded = round(fval, 1)
            if rounded % 1 == 0:
                return str(int(rounded))
            return f"{rounded:.1f}"
        except (ValueError, TypeError):
            return str(val)

    display_table_df = comp_df.copy()
    display_table_df["Standard Price"] = display_table_df["Standard Price"].apply(format_clean_price)
    if "Original Price" in display_table_df.columns:
        display_table_df["Original Price"] = display_table_df["Original Price"].apply(format_clean_price)

    def get_style(val, row_data):
        recommendation = str(row_data.get("Recommendation", ""))
        if recommendation == "Best Buy":
            return 'background-color: #15803d; color: #ffffff; font-weight: bold;'
        elif recommendation == "Competitive":
            return 'background-color: #b45309; color: #ffffff; font-weight: bold;'
        elif recommendation == "Higher Cost":
            return 'background-color: #b91c1c; color: #ffffff; font-weight: bold;'
        return ''

    st.dataframe(
        display_table_df[['Supplier / Mill', 'Origin', 'Original Price', 'Standard Price', 'Difference vs Cheapest %', 'Recommendation', 'Price Basis', 'GST Included', 'Source']]
        .style.apply(lambda row: [get_style(x, row) if row.index[i] == 'Recommendation' else '' for i, x in enumerate(row)], axis=1),
        use_container_width=True, hide_index=True
    )

    # --- 5. PROCUREMENT INSIGHT ---
    st.subheader("💡 Procurement Insight")
    best = comp_df.iloc[0]
    worst_p = float(comp_df['Standard Price'].max())
    best_p = float(best['Standard Price'])
    adv = ((worst_p - best_p) / worst_p * 100) if worst_p > best_p else 0
    
    # 52-Week Yarn Percentile Calculation
    y_sorted = display_df.sort_values('Date').reset_index(drop=True)
    sel_date = latest['Date']
    y_12m = y_sorted[(y_sorted['Date'] <= sel_date) & (y_sorted['Date'] >= (sel_date - pd.DateOffset(months=12)))]
    if not y_12m.empty and len(y_12m) > 1:
        y_p_min = y_12m['Standard Price'].min()
        y_p_max = y_12m['Standard Price'].max()
        if y_p_max > y_p_min:
            y_perc_rank = int(((latest['Standard Price'] - y_p_min) / (y_p_max - y_p_min)) * 100)
        else:
            y_perc_rank = 50
    else:
        y_p_min, y_p_max, y_perc_rank = latest['Standard Price'], latest['Standard Price'], 50

    # Fabric Cost Impact Pass-Through (1 kg Yarn approx 3.0 to 4.5 meters woven fabric)
    if len(hist) > 1:
        prev_p = hist.iloc[-2]['Standard Price']
        price_diff_kg = latest['Standard Price'] - prev_p
        m_chg_val = ((latest['Standard Price'] - prev_p) / prev_p * 100)
    else:
        price_diff_kg = 0
        m_chg_val = 0

    fab_impact_min = abs(price_diff_kg) / 4.5
    fab_impact_max = abs(price_diff_kg) / 3.0

    # Action Signal logic
    if y_perc_rank <= 35 or m_chg_val < -3:
        y_action_signal = "🟢 HIGH FABRIC NEGOTIATION LEVERAGE"
        y_action_desc = "Yarn prices sit near historical low. Demand fabric cost reductions or lock long-term fabric POs at lower baselines."
    elif y_perc_rank >= 70 or m_chg_val > 5:
        y_action_signal = "🔴 YARN PRICE SPIKE ALERT"
        y_action_desc = "Yarn prices are rising. Finalize fabric POs quickly before mills push fabric price hikes."
    else:
        y_action_signal = "🟡 STABLE YARN BASELINE"
        y_action_desc = "Yarn market is steady. Focus fabric negotiations on finishing & processing charges."

    st.markdown(f"""
- **Recommended Yarn Supplier:** {best['Supplier / Mill']} | **Origin:** {best['Origin']}
- **Current Quote:** {format_currency(best['Original Price'], best['Original Unit'])} | **Standard Price:** ₹{best_p:,.1f} / kg
- **Yarn Mill Price Spread:** **{adv:.1f}% cost difference** between lowest and highest yarn quotations in the market.
- **52-Week Price Positioning:** Sitting at the **{y_perc_rank}th Percentile** of the 12-month yarn price range (52-Wk Low: ₹{y_p_min:,.1f}/kg | 52-Wk High: ₹{y_p_max:,.1f}/kg).
- **Fabric Buyer's Negotiation Leverage:** Yarn prices moved **{m_chg_val:+.1f}%** MoM. For SS27 fabric negotiations with mills, this translates to an estimated **₹{fab_impact_min:.2f} – ₹{fab_impact_max:.2f} / meter {"price reduction" if price_diff_kg <= 0 else "cost impact"}**.
- **Fabric PO Action Signal:** **{y_action_signal}** — {y_action_desc}
""")

    # --- 6. MARKET COMMENTARY & SOURCING SUMMARY ---
    st.subheader("📌 Market Commentary & Sourcing Summary")

    # Top Executive KPI Cockpit for Fabric Sourcing Team
    yc1, yc2, yc3, yc4 = st.columns(4)
    
    if y_perc_rank <= 35:
        yc1.metric("Fabric Buyer Position", "🟢 HIGH LEVERAGE")
    elif y_perc_rank >= 70:
        yc1.metric("Fabric Buyer Position", "🔴 RISING YARN COST")
    else:
        yc1.metric("Fabric Buyer Position", "🟡 STABLE BASELINE")

    yc2.metric("52-Wk Yarn Percentile", f"{y_perc_rank}th Percentile", f"Min: ₹{y_p_min:,.0f}/kg")
    
    if price_diff_kg < 0:
        yc3.metric("Fabric Cost Impact", f"📉 -₹{fab_impact_min:.1f} to ₹{fab_impact_max:.1f}/m", f"{m_chg_val:.1f}% MoM Yarn")
    elif price_diff_kg > 0:
        yc3.metric("Fabric Cost Impact", f"📈 +₹{fab_impact_min:.1f} to ₹{fab_impact_max:.1f}/m", f"{m_chg_val:+.1f}% MoM Yarn")
    else:
        yc3.metric("Fabric Cost Impact", "🟡 Neutral / Stable", "0.0% MoM Yarn")

    yc4.metric("Mill Price Spread", f"{adv:.1f}% Variance", f"Cheapest: ₹{best_p:,.0f}/kg")

    st.markdown("<br>", unsafe_allow_html=True)

    remarks = latest.get('Remarks')
    yarn_name = f"{latest.get('Count', '')} {latest.get('Material', '')} Yarn".strip()

    if pd.notnull(remarks) and str(remarks).strip() != "":
        driver_text = str(remarks).strip()
    else:
        if m_chg_val < -2:
            driver_text = f"Easing raw material fiber costs placed downward pressure on {yarn_name} prices ({m_chg_val:.1f}% MoM)."
        elif m_chg_val > 2:
            driver_text = f"Strong demand from weaving mills supported higher {yarn_name} quotations (+{m_chg_val:.1f}% MoM)."
        else:
            driver_text = f"{yarn_name} prices remained stable with balanced spinning mill production."

    if price_diff_kg <= 0:
        watch_text = f"Use current ₹{best_p:,.1f}/kg yarn benchmark during SS27 fabric discussions to push for fabric price reductions with suppliers."
    else:
        watch_text = f"Yarn prices are hardening (+{m_chg_val:.1f}%). Finalize pending fabric purchase orders promptly before mills issue fabric rate increases."

    with st.container(border=True):
        left, right = st.columns(2)
        with left:
            st.caption("Market Driver")
            st.markdown(driver_text)
            st.caption("Fabric Sourcing Negotiation Watch")
            st.markdown(watch_text)
        with right:
            st.caption("Yarn Supply Outlook")
            if m_chg_val > 5:
                st.warning("Tight Yarn Supply")
            elif m_chg_val < -5:
                st.success("Adequate Yarn Supply")
            else:
                st.info("Balanced Yarn Supply")

            st.caption("Last Updated Period")
            st.markdown(f"**{latest.get('Month', '')} {latest.get('Year', '')}**")