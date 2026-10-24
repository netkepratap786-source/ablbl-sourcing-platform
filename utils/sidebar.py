"""
=========================================================
ABLBL SOURCING INTELLIGENCE PLATFORM
Reusable Sidebar Component — single, clickable navigation
=========================================================
Replaces the old static text list. Each item is a real button
that drives st.session_state["page"] — the exact same page
values app.py already routes on, so routing logic is unchanged.
"""

from pathlib import Path

import streamlit as st

from config import APP_SHORT_NAME, VERSION

# Kept as one line so Markdown never mistakes indented CSS for a code block.
_NAV_CSS = (
    '<style>'
    'section[data-testid="stSidebar"] .stButton>button{'
    'text-align:left; justify-content:flex-start; height:auto; padding:8px 14px; '
    'font-weight:500; font-size:0.85rem; border-radius:8px; margin-bottom:2px; '
    'border:1px solid transparent; transition:all .12s ease;}'
    'section[data-testid="stSidebar"] .stButton>button[kind="secondary"]{'
    'background:transparent; color:#c9d1d9;}'
    'section[data-testid="stSidebar"] .stButton>button[kind="secondary"]:hover{'
    'background:#1f2937; color:#e6edf3; border-color:#30363d;}'
    'section[data-testid="stSidebar"] .stButton>button[kind="primary"]{'
    'background:linear-gradient(90deg, rgba(214,46,31,0.22), rgba(242,135,31,0.10)); '
    'color:#ffffff; border-left:3px solid #D62E1F; font-weight:700; box-shadow:none;}'
    'section[data-testid="stSidebar"] .stButton>button[kind="primary"]:hover{'
    'background:linear-gradient(90deg, rgba(214,46,31,0.30), rgba(242,135,31,0.14));}'
    '</style>'
)

# (section_label_or_None, icon, display_label, page_value)
# page_value MUST exactly match the strings app.py routes on — unchanged.
NAV_ITEMS = [
    (None,     "🏠", "Home",                      "🏠 Home"),
    ("VENDOR", "📁", "Vendor Capability Search",  "📁 Vendor Capability Search"),
    ("VENDOR", "🏢", "Vendor 360",                "🏢 Vendor 360"),
    ("VENDOR", "📊", "Supplier Quality",          "📊 Supplier Quality Intelligence"),
    ("COMMERCIAL & TECH", "💼", "Commercial & Tech Search", "💼 Commercial & Technical Search"),
    ("COMMERCIAL & TECH", "🏢", "Vendor 360 (Tech + Comm)", "🏢 Vendor 360 (Tech + Comm)"),
    ("FIBRE",  "📈", "Fibre Market Intelligence", "📈 Fibre Market Intelligence"),
    ("YARN",   "🧶", "Yarn Market Intelligence",  "🧶 Yarn Market Intelligence"),
]


def render_sidebar():
    """Render the single, unified, clickable sidebar for the platform."""

    st.sidebar.markdown(_NAV_CSS, unsafe_allow_html=True)

    with st.sidebar:
        logo_path = Path(__file__).parent.parent / "assets" / "aditya_birla_logo.png"
        if logo_path.exists():
            st.image(str(logo_path), width=110)

        st.markdown(
            f'<div style="margin:6px 0 18px 0;">'
            f'<div style="font-size:1.05rem; font-weight:800; color:#f3f4f6; letter-spacing:0.01em;">🧵 {APP_SHORT_NAME}</div>'
            f'<div style="font-size:0.72rem; color:#8b949e; margin-top:2px;">Sourcing Intelligence Platform</div>'
            f'<div style="display:inline-block; margin-top:6px; padding:2px 9px; border-radius:999px; '
            f'background:#1f2937; color:#F2871F; font-size:0.68rem; font-weight:600; border:1px solid #30363d;">v{VERSION}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    current_page = st.session_state.get("page", "🏠 Home")
    last_section = "___first___"

    for section, icon, label, page_value in NAV_ITEMS:
        if section != last_section:
            if section:
                st.sidebar.markdown(
                    f'<div style="font-size:0.68rem; font-weight:700; letter-spacing:0.08em; '
                    f'text-transform:uppercase; color:#8b949e; margin:10px 0 4px 6px;">{section}</div>',
                    unsafe_allow_html=True,
                )
            last_section = section

        is_active = (current_page == page_value)
        if st.sidebar.button(
            f"{icon}  {label}",
            key=f"nav_{page_value}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state["page"] = page_value
            st.rerun()

    st.sidebar.divider()
    st.sidebar.caption("⚖ Decision Center")
    st.sidebar.caption("💰 Cost Simulator")
    st.sidebar.caption("🤖 AI Copilot")

    st.sidebar.divider()
    st.sidebar.caption("ABLBL Sourcing Intelligence Platform")
