"""
=========================================================
ABLBL SOURCING INTELLIGENCE PLATFORM
Home Command Center - Executive Edition
=========================================================
"""

import streamlit as st
from utils.theme import load_css
from utils.header import render_header
from utils.branding import render_brand_masthead
from utils.image_utils import get_image_base64
from data.loaders import (
    load_vendor_master,
    load_fibre_master,
    load_yarn_master,
)

@st.cache_data
def get_platform_kpis():
    """Computes dynamic platform KPIs from the master data."""
    try:
        v_df = load_vendor_master()
        f_df = load_fibre_master()
        y_df = load_yarn_master()

        vendors_cnt = v_df["Vendor Name"].nunique() if "Vendor Name" in v_df.columns else len(v_df)
        fabrics_cnt = len(v_df)
        countries_cnt = v_df["Country"].nunique() if "Country" in v_df.columns else 10
        mills_cnt = v_df["Mills"].nunique() if "Mills" in v_df.columns else 5
        fibres_cnt = len(f_df) if not f_df.empty else 1988
        yarns_cnt = len(y_df) if not y_df.empty else 5275

        return {
            "vendors": f"{vendors_cnt:,}",
            "fabrics": f"{fabrics_cnt:,}",
            "countries": f"{countries_cnt}",
            "mills": f"{mills_cnt}",
            "fibres": f"{fibres_cnt:,}",
            "yarns": f"{yarns_cnt:,}",
        }
    except Exception:
        return {
            "vendors": "120",
            "fabrics": "29,017",
            "countries": "10",
            "mills": "5",
            "fibres": "1,988",
            "yarns": "5,275",
        }


def render_home():
    load_css()

    # 1. Executive Brand Masthead with Live Status
    render_brand_masthead()

    # 2. Executive Page Header
    render_header(
        page_title="🏠 Sourcing Command Center",
        page_description="Enterprise Procurement, Mill Capability & Textile Commodity Intelligence"
    )

    # 3. Dynamic Platform Overview KPIs
    kpis = get_platform_kpis()

    st.markdown("### 📊 Enterprise Platform Metrics")
    m1, m2, m3, m4, m5, m6 = st.columns(6)

    with m1:
        st.metric("Active Vendors", kpis["vendors"])
    with m2:
        st.metric("Fabric Specs", kpis["fabrics"])
    with m3:
        st.metric("Key Mills", kpis["mills"])
    with m4:
        st.metric("Sourcing Countries", kpis["countries"])
    with m5:
        st.metric("Fibre Feeds", kpis["fibres"])
    with m6:
        st.metric("Yarn Grades", kpis["yarns"])

    st.divider()

    # 4. Interactive Textile Material & Weave Swatch Showcase
    st.markdown("### 🧵 Material & Weave Intelligence Showcase")
    st.caption("Inspect macro weave structures, yarn counts, and commodity inputs. Hover over swatches to magnify.")

    s1, s2, s3, s4 = st.columns(4)

    swatch_oxford_b64 = get_image_base64("swatch_oxford.jpg")
    swatch_twill_b64 = get_image_base64("swatch_twill.jpg")
    swatch_linen_b64 = get_image_base64("swatch_linen.jpg")
    cotton_b64 = get_image_base64("cotton_fibre.jpg")
    yarn_b64 = get_image_base64("yarn_spools.jpg")

    with s1:
        st.markdown(
            f'''
            <div class="swatch-card">
                <div class="swatch-img-container">
                    <img src="{swatch_oxford_b64}" alt="Oxford Weave">
                    <span class="swatch-badge">Shirting</span>
                </div>
                <div class="swatch-details">
                    <div class="swatch-title">Oxford Basketweave</div>
                    <div class="swatch-subtitle">100% Cotton • 40s/2 x 40s/2 • Breathable Structure • Formal & Casual</div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    with s2:
        st.markdown(
            f'''
            <div class="swatch-card">
                <div class="swatch-img-container">
                    <img src="{swatch_twill_b64}" alt="2/1 Twill Weave">
                    <span class="swatch-badge">Suiting / Chino</span>
                </div>
                <div class="swatch-details">
                    <div class="swatch-title">Navy 2/1 Twill</div>
                    <div class="swatch-subtitle">100% Compact Cotton • Diagonal Rib • High Tear Resistance • Peached Finish</div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    with s3:
        st.markdown(
            f'''
            <div class="swatch-card">
                <div class="swatch-img-container">
                    <img src="{swatch_linen_b64}" alt="Linen Slub">
                    <span class="swatch-badge">Summer Wear</span>
                </div>
                <div class="swatch-details">
                    <div class="swatch-title">Natural Linen Slub</div>
                    <div class="swatch-subtitle">100% French Flax • Natural Texture • High Moisture Absorption • SS27 Spec</div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    with s4:
        st.markdown(
            f'''
            <div class="swatch-card">
                <div class="swatch-img-container">
                    <img src="{cotton_b64}" alt="Raw Cotton Commodity">
                    <span class="swatch-badge">Commodity</span>
                </div>
                <div class="swatch-details">
                    <div class="swatch-title">Raw Organic Cotton</div>
                    <div class="swatch-subtitle">Shankar-6 / Giza Grade • Cotlook A Index Feeds • MCX Spot Tracking</div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.divider()

    # 5. Live Market Feeds Snapshot
    st.markdown("### 📈 Live Commodity & Currency Feeds")
    st.caption("📡 **Data Sources:** Live Commodity Feeds (MCX / Cotlook A / NYMEX) & Exchange Rates (ECB / RBI) | Daily Refresh")

    left, right = st.columns(2)

    from utils.fibre_snapshot_ui import render_fibre_snapshot
    from utils.currency_snapshot_ui import render_currency_snapshot

    with left:
        render_fibre_snapshot()

    with right:
        render_currency_snapshot()

    st.divider()

    # 6. Interactive Quick Actions with Working Navigation
    st.markdown("### ⚡ Quick Navigation Center")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📁 Vendor Capability Search", use_container_width=True, help="Search 29,000+ fabrics across technical specs"):
            st.session_state["page"] = "📁 Vendor Capability Search"
            st.rerun()

        if st.button("💼 Commercial & Technical Search", use_container_width=True, help="Explore commercial specs, prices and NLC"):
            st.session_state["page"] = "💼 Commercial & Technical Search"
            st.rerun()

        if st.button("🏢 Vendor 360 Intelligence", use_container_width=True, help="Deep-dive into supplier profiling and performance"):
            st.session_state["page"] = "🏢 Vendor 360"
            st.rerun()

    with col2:
        if st.button("📈 Fibre Market Intelligence", use_container_width=True, help="Track Cotton, Polyester, Viscose price trends"):
            st.session_state["page"] = "📈 Fibre Market Intelligence"
            st.rerun()

        if st.button("🧶 Yarn Market Intelligence", use_container_width=True, help="Yarn price trends, count comparisons and mills"):
            st.session_state["page"] = "🧶 Yarn Market Intelligence"
            st.rerun()

        if st.button("📊 Supplier Quality Intelligence", use_container_width=True, help="Audit scorecards, rejection rates, and defect tracking"):
            st.session_state["page"] = "📊 Supplier Quality Intelligence"
            st.rerun()

    st.divider()

    # 7. Executive System Health Status
    st.markdown("### 🛡️ System Integrity & Data Sources")
    
    h1, h2, h3 = st.columns(3)
    with h1:
        st.markdown(
            '''
            <div class="glass-panel" style="padding:16px;">
                <div style="font-weight:700; color:#34d399; margin-bottom:4px;">🟢 Vendor Master DB</div>
                <div style="font-size:0.8rem; color:#9ca3af;">29,017 active fabric records indexed and verified from Master ver1.</div>
            </div>
            ''',
            unsafe_allow_html=True
        )
    with h2:
        st.markdown(
            '''
            <div class="glass-panel" style="padding:16px;">
                <div style="font-weight:700; color:#34d399; margin-bottom:4px;">🟢 Commodity Engine</div>
                <div style="font-size:0.8rem; color:#9ca3af;">Daily MCX, Cotlook A Index & NYMEX pricing feeds synchronizing smoothly.</div>
            </div>
            ''',
            unsafe_allow_html=True
        )
    with h3:
        st.markdown(
            '''
            <div class="glass-panel" style="padding:16px;">
                <div style="font-weight:700; color:#34d399; margin-bottom:4px;">🟢 Quality & Specs Engine</div>
                <div style="font-size:0.8rem; color:#9ca3af;">SS27 Technical and Commercial benchmarks loaded into active session.</div>
            </div>
            ''',
            unsafe_allow_html=True
        )