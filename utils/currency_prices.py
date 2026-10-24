"""
Currency Market Price Fetcher
============================
Exchange rates for the Home Command Center snapshot.
"""
import streamlit as st
from datetime import datetime
import json
import os

MANUAL_PRICES_FILE = "data/manual_currency_prices.json"

@st.cache_data(ttl=900)  # refresh every 15 min
def get_live_currency_rate(ticker, flag, country, symbol):
    """
    Live currency rate via Yahoo Finance.
    Requires: pip install yfinance
    """
    try:
        import yfinance as yf
        hist = yf.Ticker(ticker).history(period="5d")
        if len(hist) < 2:
            return {"error": "not enough data"}
        last_close = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2]
        change_pct = ((last_close - prev_close) / prev_close) * 100
        return {
            "flag": flag,
            "country": country,
            "price_line": f"{symbol}{last_close:.2f}",
            "change_pct": round(change_pct, 2),
        }
    except Exception as e:
        return {"error": str(e)}

def load_manual_currency_prices():
    if not os.path.exists(MANUAL_PRICES_FILE):
        return {}
    with open(MANUAL_PRICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_manual_currency_prices(data):
    os.makedirs(os.path.dirname(MANUAL_PRICES_FILE), exist_ok=True)
    data["updated"] = datetime.now().strftime("%d %b %Y %I:%M %p")
    with open(MANUAL_PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_currency_snapshot():
    manual = load_manual_currency_prices()
    
    usd = get_live_currency_rate("USDINR=X", "🇺🇸", "USD / INR", "₹")
    aud = get_live_currency_rate("AUDINR=X", "🇦🇺", "AUD / INR", "₹")
    cny = get_live_currency_rate("CNYINR=X", "🇨🇳", "CNY / INR", "₹")
    
    snapshot = {
        "currencies": [],
        "updated": manual.get("updated", datetime.now().strftime("%d %b %Y %I:%M %p")),
        "source": manual.get("source", "Yahoo Finance / Manual"),
    }
    
    def append_rate(key, live_data):
        if live_data and "error" not in live_data:
            snapshot["currencies"].append(live_data)
        elif key in manual:
            snapshot["currencies"].append(manual[key])
        else:
            defaults = {
                "usd_inr": {"flag": "🇺🇸", "country": "USD / INR", "price_line": "₹83.50", "change_pct": 0.0},
                "aud_inr": {"flag": "🇦🇺", "country": "AUD / INR", "price_line": "₹55.20", "change_pct": 0.0},
                "cny_inr": {"flag": "🇨🇳", "country": "CNY / INR", "price_line": "₹11.50", "change_pct": 0.0},
            }
            snapshot["currencies"].append(defaults[key])
            
    append_rate("usd_inr", usd)
    append_rate("aud_inr", aud)
    append_rate("cny_inr", cny)
    
    return snapshot
