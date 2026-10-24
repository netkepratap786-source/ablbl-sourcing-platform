import streamlit as st
from datetime import datetime
from utils.fibre_prices import get_fibre_snapshot, load_manual_prices, save_manual_prices


def _card(item, accent):
    change = item.get("change_pct", 0)
    up = change >= 0
    arrow = "▲" if up else "▼"
    badge_bg = "rgba(34,197,94,0.15)" if up else "rgba(239,68,68,0.15)"
    badge_fg = "#4ade80" if up else "#f87171"
    return (
        f'<div style="background:#161b22; border:1px solid rgba(255,255,255,0.08); '
        f'border-top:3px solid {accent}; border-radius:12px; padding:14px 16px; '
        f'min-width:140px; flex:1;">'
        f'<div style="font-size:0.8rem; letter-spacing:0.04em; color:#9ca3af; '
        f'text-transform:uppercase; margin-bottom:4px;">{item["flag"]} {item["country"]}</div>'
        f'<div style="font-size:1.45rem; font-weight:700; color:#f3f4f6; line-height:1.2;">{item["price_line"]}</div>'
        f'<div style="display:inline-block; margin-top:8px; padding:3px 10px; border-radius:999px; '
        f'background:{badge_bg}; color:{badge_fg}; font-size:0.9rem; font-weight:600;">{arrow} {abs(change)}%</div>'
        f'</div>'
    )


def _section_label(text, accent):
    return (
        f'<div style="font-size:0.85rem; font-weight:700; letter-spacing:0.08em; '
        f'text-transform:uppercase; color:{accent}; margin:14px 0 8px 0;">{text}</div>'
    )


def render_fibre_snapshot():
    st.markdown("""
        <style>
        /* Zero out the anchor container */
        div.element-container:has(#update-fibre-btn-anchor) {
            height: 0px !important;
            min-height: 0px !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }

        /* Make the button's outer container zero-height and positioned */
        div.element-container:has(#update-fibre-btn-anchor) + div.element-container {
            height: 0px !important;
            min-height: 0px !important;
            margin: 0 !important;
            padding: 0 !important;
            position: relative !important;
            z-index: 9999 !important;
            overflow: visible !important;
            width: 100% !important;
        }

        /* Absolute position the actual button div to the top right */
        div.element-container:has(#update-fibre-btn-anchor) + div.element-container > div {
            position: absolute !important;
            right: 20px !important;
            top: 15px !important;
            width: auto !important;
        }

        /* Glossy 3D Button Aesthetic */
        div.element-container:has(#update-fibre-btn-anchor) + div.element-container button {
            background: linear-gradient(180deg, #383838 0%, #151515 40%, #000000 100%) !important;
            color: #ffffff !important;
            border: 2px solid #5a5a5a !important;
            border-radius: 12px !important;
            box-shadow: 
                0 6px 15px rgba(0,0,0,0.8), 
                inset 0 3px 6px rgba(255,255,255,0.3), 
                inset 0 -2px 5px rgba(0,0,0,0.9) !important;
            padding: 6px 22px !important;
            font-weight: 800 !important;
            font-size: 0.95rem !important;
            letter-spacing: 1.2px !important;
            text-shadow: 0 0 10px rgba(255,255,255,0.9) !important;
            min-height: 40px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            white-space: nowrap !important;
            transition: all 0.2s ease !important;
        }

        div.element-container:has(#update-fibre-btn-anchor) + div.element-container button:hover {
            border-color: #888888 !important;
            box-shadow: 
                0 8px 20px rgba(0,0,0,0.95), 
                inset 0 4px 8px rgba(255,255,255,0.5), 
                inset 0 -2px 5px rgba(0,0,0,0.9) !important;
            text-shadow: 0 0 15px rgba(255,255,255,1.0) !important;
            transform: translateY(-1px) !important;
        }

        div.element-container:has(#update-fibre-btn-anchor) + div.element-container button:active {
            background: linear-gradient(180deg, #151515 0%, #000000 100%) !important;
            box-shadow: inset 0 5px 10px rgba(0,0,0,0.9) !important;
            transform: translateY(2px) !important;
        }
        </style>
        <div id="update-fibre-btn-anchor"></div>
    """, unsafe_allow_html=True)

    if st.button("🔄 UPDATE", key="update_fibre_btn"):
        update_fibre_dialog()

    data = get_fibre_snapshot()

    COTTON_ACCENT = "#f59e0b"  # amber / orange accent for Cotton
    WOOL_ACCENT = "#3b82f6"    # blue accent for Wool

    html = '<div style="background:#0d1117; border:1px solid rgba(255,255,255,0.06); border-radius:16px; padding:18px 20px;">'
    html += '<div style="font-size:1.25rem; font-weight:800; color:#f3f4f6; display:flex; align-items:center; gap:8px;">📈 Live Fibre Market Snapshot</div>'

    if data.get("cotton"):
        html += _section_label("COTTON", COTTON_ACCENT)
        html += '<div style="display:flex; flex-wrap:wrap; gap:12px;">'
        html += "".join(_card(i, COTTON_ACCENT) for i in data["cotton"])
        html += '</div>'

    if data.get("wool"):
        html += _section_label("WOOL", WOOL_ACCENT)
        html += '<div style="display:flex; flex-wrap:wrap; gap:12px;">'
        html += "".join(_card(i, WOOL_ACCENT) for i in data["wool"])
        html += '</div>'

    html += (
        f'<div style="margin-top:16px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.08); '
        f'font-size:0.85rem; color:#6b7280;">'
        f'Updated: {data["updated"]} &nbsp;•&nbsp; Source: {data["source"]}'
        f'</div>'
    )
    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)


@st.dialog("✏️ Update Manual Fibre Prices")
def update_fibre_dialog():
    st.markdown("""
        <style>
        div[data-testid="stDialog"] {
            border-radius: 16px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
        }
        div[data-testid="stDialog"] div[data-testid="stMarkdownContainer"] p {
            font-size: 1.05rem;
            color: #e5e7eb;
            margin-bottom: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    manual = load_manual_prices()

    with st.form("manual_fibre_form", border=False):
        def parse_price(key, default, symbol, suffix):
            if key in manual:
                val = manual[key].get("price_line", str(default))
                val = val.replace(symbol, "").replace(suffix, "").replace(",", "").strip()
                for bad in ["â,¹", "â", "¹", "Å¥", "Å", "¥", "AU$", "₹"]:
                    val = val.replace(bad, "")
                val = val.strip()
                try:
                    return float(val)
                except ValueError:
                    return float(default)
            return float(default)

        in_p = parse_price("india_cotton", 31800.0, "₹", "/ Candy")
        in_c = manual.get("india_cotton", {}).get("change_pct", 0.0) if "india_cotton" in manual else 0.0

        cn_p = parse_price("china_cotton", 15785.0, "¥", "/ MT")
        cn_c = manual.get("china_cotton", {}).get("change_pct", 0.38) if "china_cotton" in manual else 0.38

        au_p = parse_price("australia_wool", 18.73, "AU$", "/ kg")
        au_c = manual.get("australia_wool", {}).get("change_pct", 0.0) if "australia_wool" in manual else 0.0

        st.markdown("**🇮🇳 India — Cotton (CAI Candy Price)**")
        col1, col2 = st.columns(2)
        in_price = col1.number_input("Price (₹)", value=in_p, step=100.0, key="in_price")
        in_change = col2.number_input("Change %", value=in_c, key="in_change")
        st.write("")

        st.markdown("**🇨🇳 China — Cotton (Spot)**")
        col3, col4 = st.columns(2)
        cn_price = col3.number_input("Price (¥)", value=cn_p, step=10.0, key="cn_price")
        cn_change = col4.number_input("Change %", value=cn_c, key="cn_change")
        st.write("")

        st.markdown("**🇦🇺 Australia — Wool (AWEX)**")
        col5, col6 = st.columns(2)
        au_price = col5.number_input("Price (AU$)", value=au_p, step=0.05, key="au_price")
        au_change = col6.number_input("Change %", value=au_c, key="au_change")
        st.write("")

        source = st.text_input("Source label", value=manual.get("source", "CAI / Trading Economics"))
        st.write("")

        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            submitted = st.form_submit_button("Save Updates", type="primary", use_container_width=True)

        if submitted:
            save_manual_prices({
                "india_cotton": {
                    "flag": "🇮🇳", "country": "India",
                    "price_line": f"₹{in_price:,.0f} / Candy",
                    "change_pct": in_change,
                },
                "china_cotton": {
                    "flag": "🇨🇳", "country": "China",
                    "price_line": f"¥{cn_price:,.0f} / MT",
                    "change_pct": cn_change,
                },
                "australia_wool": {
                    "flag": "🇦🇺", "country": "Australia",
                    "price_line": f"AU${au_price:.2f} / kg",
                    "change_pct": au_change,
                },
                "source": source,
            })
            st.rerun()
