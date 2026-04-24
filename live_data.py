import yfinance as yf
import json
from datetime import datetime

def fetch_live_bitcoin():
    print("[SYSTEM] Connecting to global markets...")
    try:
        btc = yf.Ticker("BTC-USD")
        
        # Pull the absolute most recent market price using the fast_info method
        live_price = btc.fast_info['last_price']
        
        # Package it into a clean JSON 
        crypto_state = {
            "asset": "Bitcoin",
            "symbol": "BTC",
            "current_price_usd": round(live_price, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "market_status": "Live"
        }
        
        return json.dumps(crypto_state, indent=4)
    
    except Exception as e:
        return f"[ERROR] Failed to fetch data: {e}"

if __name__ == "__main__":
    live_json = fetch_live_bitcoin()
    print("\n--- LIVE MARKET DATA ---\n")
    print(live_json)
