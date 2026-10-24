"""
=========================================================
ABLBL SOURCING INTELLIGENCE PLATFORM
Brand Masthead Component (Aditya Birla Lifestyle Brands theme)
=========================================================
"""

import base64
from pathlib import Path
import streamlit as st

LOGO_PATH = Path(__file__).parent.parent / "assets" / "aditya_birla_logo.png"

@st.cache_data
def _logo_base64():
    if LOGO_PATH.exists():
        return base64.b64encode(LOGO_PATH.read_bytes()).decode()
    return None

def render_brand_masthead():
    """Renders the ABLBL logo + company name in an executive maroon-to-gold glass banner with live pulse."""
    logo_b64 = _logo_base64()
    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" '
        f'style="height:48px; border-radius:8px; background:#ffffff; padding:5px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">'
        if logo_b64 else ''
    )

    st.markdown(
        f'''
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:16px; 
                    padding:14px 24px; 
                    background:linear-gradient(90deg, rgba(92,15,15,0.95) 0%, rgba(139,26,26,0.92) 40%, rgba(214,46,31,0.88) 75%, rgba(242,135,31,0.85) 100%); 
                    backdrop-filter: blur(14px);
                    border: 1px solid rgba(255,255,255,0.14);
                    border-radius:16px; margin-bottom:22px; 
                    box-shadow:0 8px 30px rgba(0,0,0,0.5), 0 0 25px rgba(214,46,31,0.2);">
            <div style="display:flex; align-items:center; gap:18px;">
                {logo_html}
                <div>
                    <div style="font-size:1.3rem; font-weight:800; color:#ffffff; letter-spacing:0.02em; line-height:1.2;">
                        ADITYA BIRLA LIFESTYLE BRANDS LIMITED
                    </div>
                    <div style="font-size:0.82rem; font-weight:700; color:#ffe3be; letter-spacing:0.08em; margin-top:2px;">
                        ENTERPRISE SOURCING INTELLIGENCE PLATFORM &nbsp;•&nbsp; ABLBL SIP
                    </div>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:12px;">
                <div class="live-pulse">
                    <span class="pulse-dot"></span>
                    <span>LIVE SOURCING ENGINE</span>
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
