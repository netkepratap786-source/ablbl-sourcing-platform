"""
Fibre Market Price Fetcher
============================
Cotton & wool prices for the Home Command Center snapshot.
"""

import streamlit as st
from datetime import datetime
import json
import os

MANUAL_PRICES_FILE = "data/manual_fibre_prices.json"


@st.cache_data(ttl=900)  # refresh every 15 min
def get_us_cotton_price():
    """
    Live USA cotton price (ICE Cotton No.2 futures) via Yahoo Finance.
    Requires: pip install yfinance
    """
    try:
        import yfinance as yf
        hist = yf.Ticker("CT=F").history(period="5d")
        if len(hist) < 2:
            return {"error": "not enough data"}
        last_close = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2]
        change_pct = ((last_close - prev_close) / prev_close) * 100
        return {
            "flag": "🇺🇸",
            "country": "USA",
            "price_line": f"{last_close:.2f} US¢/lb",
            "change_pct": round(change_pct, 2),
        }
    except Exception as e:
        return {"error": str(e)}


def load_manual_prices():
    if not os.path.exists(MANUAL_PRICES_FILE):
        return {}
    try:
        with open(MANUAL_PRICES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Clean any corrupted mojibake symbols if present
            for k in ["india_cotton", "china_cotton", "australia_wool"]:
                if k in data and isinstance(data[k], dict):
                    price_line = data[k].get("price_line", "")
                    if "â,¹" in price_line or "â" in price_line:
                        price_line = price_line.replace("â,¹", "₹").replace("â", "")
                        data[k]["price_line"] = price_line
                    if "Å¥" in price_line or "Å" in price_line:
                        price_line = price_line.replace("Å¥", "¥").replace("Å", "")
                        data[k]["price_line"] = price_line
                    flag = data[k].get("flag", "")
                    if "â" in flag or "Å" in flag or "ï¿½" in flag:
                        defaults_flags = {"india_cotton": "🇮🇳", "china_cotton": "🇨🇳", "australia_wool": "🇦🇺"}
                        data[k]["flag"] = defaults_flags.get(k, flag)
            return data
    except Exception:
        return {}


def save_manual_prices(data):
    os.makedirs(os.path.dirname(MANUAL_PRICES_FILE), exist_ok=True)
    data["updated"] = datetime.now().strftime("%d %b %Y %I:%M %p")
    with open(MANUAL_PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_fibre_snapshot():
    """Assembles the full snapshot dict used by render_fibre_snapshot()."""
    manual = load_manual_prices()
    us = get_us_cotton_price()

    snapshot = {
        "cotton": [],
        "wool": [],
        "updated": manual.get("updated", datetime.now().strftime("%d %b %Y %I:%M %p")),
        "source": manual.get("source", "CAI / Trading Economics / Yahoo Finance"),
    }

    if "india_cotton" in manual:
        snapshot["cotton"].append(manual["india_cotton"])
    else:
        snapshot["cotton"].append({
            "flag": "🇮🇳", "country": "India",
            "price_line": "₹31,800 / Candy", "change_pct": 0.0
        })

    if us and "error" not in us:
        snapshot["cotton"].append(us)
    elif "usa_cotton" in manual:  # fallback if yfinance call fails
        snapshot["cotton"].append(manual["usa_cotton"])
    else:
        snapshot["cotton"].append({
            "flag": "🇺🇸", "country": "USA",
            "price_line": "80.50 US¢/lb", "change_pct": 1.37
        })

    if "china_cotton" in manual:
        snapshot["cotton"].append(manual["china_cotton"])
    else:
        snapshot["cotton"].append({
            "flag": "🇨🇳", "country": "China",
            "price_line": "¥15,785 / MT", "change_pct": 0.38
        })

    if "australia_wool" in manual:
        snapshot["wool"].append(manual["australia_wool"])
    else:
        snapshot["wool"].append({
            "flag": "🇦🇺", "country": "Australia",
            "price_line": "AU$18.73 / kg", "change_pct": 0.0
        })

    return snapshot
