"""
========================================================
Fibre Market Intelligence Module
ABLBL Sourcing Intelligence Platform
========================================================
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.header import render_header
from utils.theme import load_css
from data.loaders import load_fibre_master
from utils.formatters import fmt_price_with_unit
def format_currency(val, unit):
    """Professional formatting based on unit type."""
    try:
        val = float(val)
        if '₹' in str(unit):
            return f"₹{val:,.0f} / {str(unit).split('/')[-1]}"
        elif 'US cents/lb' in str(unit):
            return f"{val:,.1f} US cents/lb"
        else:
            return f"{val:,.2f} {unit}"
    except:
        return f"{val} {unit}"

def render_fibre_market():
    load_css()
    render_header(
        page_title="📈 Fibre Market Intelligence",
        page_description="Enterprise market movement and sourcing decision support"
    )

    st.info(
        "💡 **Page Purpose:** Global Fibre Commodity Market Intelligence. "
        "Track price movements across global fiber origins (USA, India, China), compare standardized costs, view multi-year historical price cycles, and execute buying signals."
    )

    df = load_fibre_master()
    if df.empty:
        st.error("Market data unavailable.")
        return

    df['Date'] = pd.to_datetime(df['Date'])
    df['Month_Name'] = df['Date'].dt.strftime('%b')
    df['Month_Idx'] = df['Date'].dt.month
    df['Quarter'] = df['Month_Idx'].apply(lambda x: f"Q{(x-1)//3 + 1}")

    # --- 1. SMART FILTERS ---
    st.markdown("### 🔍 Market Filters")
    f1, f2, f3, f4, f5 = st.columns(5)
    
    unique_fibres = sorted([str(x) for x in df["Fibre"].dropna().unique()])
    fibre = f1.selectbox("Fibre", unique_fibres)
    f_df = df[df["Fibre"] == fibre]
    
    unique_origins = sorted([str(x) for x in f_df["Origin"].dropna().unique()])
    origin = f2.selectbox("Origin", unique_origins)
    fo_df = f_df[f_df["Origin"] == origin]
    
    unique_varieties = sorted([str(x) for x in fo_df["Variety"].dropna().unique()])
    variety = f3.selectbox("Variety", unique_varieties)
    fov_df = fo_df[fo_df["Variety"] == variety]
    
    unique_years = sorted([int(x) for x in fov_df["Year"].dropna().unique() if pd.notna(x)], reverse=True)
    year = f4.selectbox("Year", unique_years)
    
    # Chronological sort for months
    month_data = fov_df[fov_df["Year"] == year].sort_values('Month_Idx')
    months_in_year = month_data[['Month', 'Month_Idx']].drop_duplicates().sort_values('Month_Idx')
    month = f5.selectbox("Month", months_in_year['Month'].tolist())
    selected_month_idx = months_in_year.loc[months_in_year['Month'] == month, 'Month_Idx'].iloc[0]

    kpi_df = fov_df[(fov_df["Year"] == year) & (fov_df["Month"] == month)]
    latest = kpi_df.sort_values('Date').iloc[-1] if not kpi_df.empty else fov_df.sort_values('Date').iloc[-1]

    # Dynamic MoM, YoY, and 52-Week Range Calculations
    fov_sorted = fov_df.sort_values('Date').reset_index(drop=True)
    sel_date = latest['Date']
    
    # 1. MoM Change %
    prev_m = fov_sorted[fov_sorted['Date'] < sel_date]
    if not prev_m.empty:
        p_m_val = prev_m.iloc[-1]['Standard Price']
        c_m_val = latest['Standard Price']
        mom_chg = ((c_m_val - p_m_val) / p_m_val) * 100 if p_m_val > 0 else 0
    else:
        mom_chg = latest.get('Daily Change %', 0)

    # 2. Dynamic YoY Change %
    prev_y = fov_sorted[fov_sorted['Date'] <= (sel_date - pd.DateOffset(months=11))]
    if not prev_y.empty:
        p_y_val = prev_y.iloc[0]['Standard Price']
        c_y_val = latest['Standard Price']
        yoy_chg = ((c_y_val - p_y_val) / p_y_val) * 100 if p_y_val > 0 else 0
    else:
        yoy_raw = latest.get('YoY Change %')
        yoy_chg = (yoy_raw * 100) if (pd.notnull(yoy_raw) and abs(yoy_raw) < 2) else (yoy_raw if pd.notnull(yoy_raw) else 0)

    # 3. 52-Week Percentile Rank
    p_12m = fov_sorted[(fov_sorted['Date'] <= sel_date) & (fov_sorted['Date'] >= (sel_date - pd.DateOffset(months=12)))]
    if not p_12m.empty and len(p_12m) > 1:
        p_min = p_12m['Standard Price'].min()
        p_max = p_12m['Standard Price'].max()
        if p_max > p_min:
            perc_rank = int(((latest['Standard Price'] - p_min) / (p_max - p_min)) * 100)
        else:
            perc_rank = 50
    else:
        p_min, p_max, perc_rank = latest['Standard Price'], latest['Standard Price'], 50

    # --- 2. MARKET OVERVIEW ---
    st.subheader("📊 Market Overview")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    
    k1.metric("Current Market Quote", format_currency(latest['Original Price'], latest['Original Unit']))
    k2.metric("Standardized Price", format_currency(latest['Standard Price'], latest['Standard Unit']))
    
    k3.metric("MoM Change %", f"{mom_chg:+.2f}%")
    k4.metric("YoY Change %", f"{yoy_chg:+.2f}%")
    
    ex_rate = latest.get('Exchange Rate')
    k5.metric("Exchange Rate", "Not Applicable" if ex_rate == 1 else (f"{ex_rate:.2f}" if pd.notnull(ex_rate) else "Not Available"))
    
    if mom_chg > 0.5: direction = "🟢 Rising"
    elif mom_chg < -0.5: direction = "🔴 Falling"
    else: direction = "🟡 Stable"
    k6.metric("Market Direction", direction)

    # --- 3. MARKET QUOTE VS STANDARDIZED PRICE ---
    st.markdown("---")
    col_a, col_arrow, col_b = st.columns([1, 0.2, 1])
    with col_a:
        st.info(f"**Original Market Quote**\n\n{format_currency(latest['Original Price'], latest['Original Unit'])}")
    with col_arrow:
        st.markdown("<br><h2 style='text-align: center;'>→</h2>", unsafe_allow_html=True)
    with col_b:
        st.success(f"**Equivalent Standardized Price**\n\n{format_currency(latest['Standard Price'], latest['Standard Unit'])}")
    st.markdown("---")

    # --- 4. HISTORICAL PRICE TREND ---
    st.subheader(f"📈 {variety} {fibre} Price Trend")
    st.caption(f"Market Quote Unit: {latest['Original Unit']}")
    
    view_mode = st.radio("Trend View", ["Monthly (Selected Year)", "Quarterly (Selected Year)", "Multi-Year Macro Trend"], horizontal=True)
    trend_df = fov_df[fov_df["Year"] == year].copy()
    unit_label = latest['Original Unit']
    
    if view_mode == "Monthly (Selected Year)":
        chart_data = trend_df.groupby(['Month_Name', 'Month_Idx'], as_index=False).agg({
            'Original Price': 'mean', 'Daily Change %': 'last', 'Source': 'first'
        }).sort_values('Month_Idx')
        
        fig = px.line(chart_data, x='Month_Name', y='Original Price', markers=True, template="plotly_dark",
                     labels={'Month_Name': 'Month', 'Original Price': f'Price ({unit_label})', 'Daily Change %': 'Daily Change', 'Source': 'Source'},
                     hover_data={'Month_Name': True, 'Original Price': True, 'Daily Change %': True, 'Source': True})
        
        if selected_month_idx in chart_data['Month_Idx'].values:
            highlight = chart_data[chart_data['Month_Idx'] == selected_month_idx]
            fig.add_trace(go.Scatter(x=highlight['Month_Name'], y=highlight['Original Price'], mode='markers', 
                                    marker=dict(size=12, color='#636EFA', line=dict(width=2, color='white')), showlegend=False))
    elif view_mode == "Quarterly (Selected Year)":
        chart_data = trend_df.groupby('Quarter', as_index=False)['Original Price'].mean().sort_values('Quarter')
        fig = px.line(chart_data, x='Quarter', y='Original Price', markers=True, template="plotly_dark",
                     labels={'Quarter': 'Quarter', 'Original Price': f'Average Price ({unit_label})'},
                     hover_data={'Quarter': True, 'Original Price': True})
    else:
        # Multi-Year Macro Trend across all historical years
        my_df = fov_df.copy().sort_values('Date')
        my_df['Year_Month'] = my_df['Date'].dt.strftime('%b %Y')
        chart_data = my_df.groupby(['Year_Month', 'Date'], as_index=False)['Original Price'].mean().sort_values('Date')
        fig = px.line(chart_data, x='Year_Month', y='Original Price', markers=True, template="plotly_dark",
                     title=f"Multi-Year Price Evolution for {variety} {fibre}",
                     labels={'Year_Month': 'Period', 'Original Price': f'Average Price ({unit_label})'},
                     hover_data={'Year_Month': True, 'Original Price': True})

    fig.update_layout(height=360, margin=dict(l=20, r=20, t=30, b=20))
    fig.update_traces(line=dict(width=3, color="#00CC96" if view_mode == "Multi-Year Macro Trend" else "#636EFA"))
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. GLOBAL FIBRE COMPARISON ---
    std_unit_label = latest.get("Standard Unit", "Candy")
    st.subheader(f"🌍 Global {fibre} Price Comparison for {month} {year}")
    st.caption(f"Standardized Unit: {std_unit_label} | Comparing global fiber origin quotes for {month} {year}")
    
    comp_mask = (df["Fibre"] == fibre) & (df["Year"] == year) & (df["Month"] == month)
    comp_data = df[comp_mask].copy()
    
    if not comp_data.empty:
        summary_list = []
        for (o, v), group in comp_data.groupby(["Origin", "Variety"]):
            latest_row = group.sort_values('Date').iloc[-1]
            
            summary_list.append({
                "Origin": o,
                "Variety": v,

                "Market Quote": format_currency(
                    latest_row["Original Price"],
                    latest_row["Original Unit"]
                ),

                # Numeric value (used for calculations)
                "Numeric Price": latest_row["Standard Price"],

                # Formatted value (displayed in table)
                "Standardized Price": fmt_price_with_unit(
                    latest_row["Standard Price"],
                    latest_row["Standard Unit"]
                ),

                "Currency": latest_row["Currency"],
                "Source": latest_row["Source"]
            })

        c_df = pd.DataFrame(summary_list)
        min_price = c_df["Numeric Price"].min()
        c_df["Difference vs Lowest"] = (
            (c_df["Numeric Price"] - min_price)
            / min_price * 100
        ).round(1).apply(lambda x: f"+{x}%" if x > 0 else f"{x}%")

        # Find lowest and highest priced suppliers
        lowest_idx = c_df["Numeric Price"].idxmin()
        highest_idx = c_df["Numeric Price"].idxmax()

        def style_rows(row):
            row_index = row.name

            if row_index == lowest_idx:
                return ["background-color: #2e7d32"] * len(row)

            if row_index == highest_idx:
                return ["background-color: #8b0000"] * len(row)

            return [""] * len(row)

        # Create presentation dataframe
        display_df = c_df.drop(columns=["Numeric Price", "Currency"])

        # Apply styling using original dataframe index
        styled_df = display_df.style.apply(style_rows, axis=1)

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )

    # --- 6. PROCUREMENT INSIGHT ---
    st.subheader("💡 Procurement Insight")

    if not comp_data.empty and len(c_df) > 1:
        best = c_df.loc[c_df["Numeric Price"].idxmin()]
        highest = c_df.loc[c_df["Numeric Price"].idxmax()]
        
        abs_savings = highest["Numeric Price"] - best["Numeric Price"]
        std_unit_text = str(latest.get("Standard Unit", "Candy")).split('/')[-1]

        # Action Signal logic
        if perc_rank <= 35 or yoy_chg < -5:
            action_signal = "🟢 STRONG BUY / LOCK CONTRACTS"
            action_desc = "Current fiber prices sit in an attractive historical buying window. Recommended to lock 3-month procurement contracts."
        elif perc_rank >= 70 or yoy_chg > 15:
            action_signal = "🔴 HOLD BULK ORDERS"
            action_desc = "Prices sit near historical high. Recommend delaying non-urgent bulk purchases."
        else:
            action_signal = "🟡 SPOT BUYING ONLY"
            action_desc = "Market is in standard pricing band. Recommend hand-to-mouth spot buying."

        st.markdown(f"""
- **Recommended Sourcing Decision:** {best['Origin']} | {best['Variety']}
- **Market Quote:** {best['Market Quote']}
- **Standardized Cost:** {best['Standardized Price']}
- **Cost Savings Opportunity:** Save **₹{abs_savings:,.0f} / {std_unit_text} ({highest['Difference vs Lowest']})** vs highest priced source ({highest['Origin']} | {highest['Variety']}).
- **52-Week Price Positioning:** Sitting at the **{perc_rank}th Percentile** of the 12-month price range (52-Wk Low: ₹{p_min:,.0f} | 52-Wk High: ₹{p_max:,.0f}).
- **Procurement Action Signal:** **{action_signal}** — {action_desc}
""")

    else:
        st.write("No comparison available.")

    # ------------------------------------------------------------------
    # MARKET INTELLIGENCE SUMMARY
    # ------------------------------------------------------------------
    def get_market_driver(latest, variety, fibre, month, year, mom_chg, yoy_chg):
        product_name = variety or fibre or "Selected Fibre"
        remarks = latest.get("Remarks")

        if pd.notnull(remarks) and str(remarks).strip():
            text = str(remarks).strip()
            if yoy_chg > 10:
                text += f" Prices remain {yoy_chg:.1f}% above the same period last year."
            elif yoy_chg < -10:
                text += f" Prices remain {abs(yoy_chg):.1f}% below the previous year's level."
            return text

        if mom_chg > 2 and yoy_chg > 5:
            return f"Strong buying activity supported higher {product_name} prices (+{mom_chg:.1f}% MoM) during {month} {year}."
        elif mom_chg < -2 and yoy_chg < -5:
            return f"Improved supply conditions and weak demand eased {product_name} prices ({mom_chg:.1f}% MoM) during {month} {year}."
        elif -1 <= mom_chg <= 1:
            return f"Trading activity remained stable with limited movement in {product_name} prices during {month} {year}."
        return f"Moderate market movement was observed for {product_name} ({mom_chg:+.1f}% MoM) during {month} {year}."

    def get_supply_outlook(yoy_chg):
        if yoy_chg > 15:
            return "Very Tight Supply"
        elif yoy_chg >= 8:
            return "Tight Supply"
        elif yoy_chg >= -5:
            return "Balanced Supply"
        else:
            return "Adequate Supply"

    def get_procurement_watch(best, month, year, mom_chg, yoy_chg):
        if best is None:
            return "No procurement recommendation available."

        origin_name = str(best["Origin"])
        variety_name = str(best["Variety"])

        text = f"For {month} {year}, {variety_name} ({origin_name}) offers the lowest standardized procurement cost. "

        if "India" in origin_name:
            text += "Domestic procurement is currently the preferred cost-effective strategy. "
        else:
            text += "Monitor ocean freight tariffs and USD/INR exchange rate fluctuations before confirming import PO placement. "

        if mom_chg > 3:
            text += "Prices are picking up momentum; consider securing high-volume requirements early."
        elif mom_chg < -3:
            text += "Prices continue to decline; monitor market arrivals before locking long-term contracts."
        return text

    st.subheader("📌 Market Intelligence Summary")

    best_supplier = c_df.loc[c_df["Numeric Price"].idxmin()] if (not comp_data.empty and len(c_df) > 1) else None

    driver = get_market_driver(latest, variety, fibre, month, year, mom_chg, yoy_chg)
    outlook = get_supply_outlook(yoy_chg)
    watch = get_procurement_watch(best_supplier, month, year, mom_chg, yoy_chg)
    last_updated = latest["Date"].strftime("%d-%b-%Y")

    # Executive KPI Cockpit with Simplified Business Titles
    m1, m2, m3, m4 = st.columns(4)
    
    if perc_rank <= 35:
        m1.metric("Recommended Buying Action", "🟢 LOCK CONTRACTS")
    elif perc_rank >= 70:
        m1.metric("Recommended Buying Action", "🔴 HOLD BULK POs")
    else:
        m1.metric("Recommended Buying Action", "🟡 SPOT BUYING")

    m2.metric("52-Week Price Position", f"{perc_rank}th Percentile", f"Min: ₹{p_min:,.0f}")
    
    if best_supplier is not None:
        best_diff = c_df.loc[c_df["Numeric Price"].idxmax(), "Difference vs Lowest"]
        m3.metric("Best-Value Global Origin", f"{str(best_supplier['Origin']).strip()}", f"{best_diff} premium on max")
    else:
        m3.metric("Best-Value Global Origin", "N/A")

    month_num = latest['Date'].month
    if month_num in [10, 11, 12]:
        m4.metric("Supply & Harvest Season", "🌾 Peak Arrival Window", "Softening Market")
    else:
        m4.metric("Supply & Harvest Season", "📦 Standard Season", "Balanced Arrivals")

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        left, right = st.columns(2)
        with left:
            st.caption("Market Driver")
            st.markdown(driver)
            st.caption("Procurement Watch")
            st.markdown(watch)
        with right:
            st.caption("Supply Outlook")
            if outlook == "Very Tight Supply":
                st.error(outlook)
            elif outlook == "Tight Supply":
                st.warning(outlook)
            elif outlook == "Balanced Supply":
                st.info(outlook)
            else:
                st.success(outlook)

            st.caption("Last Updated")
            st.markdown(f"**{last_updated}**")