import yfinance as yf
import json
from datetime import datetime

def fetch_live_bitcoin():
    print("[SYSTEM] Connecting to global markets...")
    try:
        btc = yf.Ticker("BTC-USD")
        btc_usd_price = btc.fast_info['last_price']

        # live Exchange Rate (USD to MYR)
        exchange = yf.Ticker("MYR=X") 
        usd_to_myr_rate = exchange.fast_info['last_price']
        
        btc_myr_price = btc_usd_price * usd_to_myr_rate
        
        crypto_state = {
            "asset": "Bitcoin",
            "symbol": "BTC",
            "current_price_usd": round(btc_usd_price, 2),
            "exchange_rate_usd_myr": round(usd_to_myr_rate, 4),
            "current_price_myr": round(btc_myr_price, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "market_status": "Live"
        }
        
        return crypto_state
    
    except Exception as e:
        print(f"[ERROR] Failed to fetch data: {e}")
        return None

if __name__ == "__main__":
    live_data = fetch_live_bitcoin()
    if live_data:
        print("\n--- LIVE MARKET DATA ---\n")
        print(json.dumps(live_data, indent=4))
    else:
        print("Failed to fetch live data")