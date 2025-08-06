import pandas as pd
import numpy as np
import os
from SmartApi import SmartConnect
from django.conf import settings
import datetime
import pyotp

# ✅ Cache session and data to avoid repeated API calls
smartapi_session = None
ohlc_cache = {}

def get_smartapi_session():
    """Create or reuse an existing SmartAPI session"""
    global smartapi_session
    if smartapi_session is None:
        obj = SmartConnect(api_key=settings.SMARTAPI_API_KEY)
        totp = pyotp.TOTP(settings.SMARTAPI_TOTP_SECRET).now()
        session_data = obj.generateSession(
            settings.SMARTAPI_USERNAME,
            settings.SMARTAPI_PASSWORD,
            totp
        )
        print("✅ SmartAPI Session Created:", session_data)
        smartapi_session = obj
    return smartapi_session

def fetch_ohlc_data(symbol="NSE:NIFTY 50", interval="ONE_MINUTE", days=1, save_csv=False):
    try:
        global ohlc_cache
        cache_key = f"{symbol}_{interval}_{days}"

        # ✅ Return cached data if available
        if cache_key in ohlc_cache:
            print("⚡ Using cached OHLC data")
            return ohlc_cache[cache_key]

        obj = get_smartapi_session()

        to_date = datetime.datetime.now()
        from_date = to_date - datetime.timedelta(days=days)

        symbol_token_map = {
            "NSE:NIFTY 50": "3045",
            "BANKNIFTY": "99926000",
            "TATASTEEL": "3499",
            "WIPRO": "3787",
            "RELIANCE": "2885",
            "GOLD": "217",     # Example token for GOLD
            "BTCUSD": "1234",  # Replace with actual token
            "US30": "5678",    # Replace with actual token
            "ETHUSD": "91011",
        }
        symbol_token = symbol_token_map.get(symbol, "3045")

        historic_params = {
            "exchange": "NSE",
            "symboltoken": symbol_token,
            "interval": interval,
            "fromdate": from_date.strftime('%Y-%m-%d %H:%M'),
            "todate": to_date.strftime('%Y-%m-%d %H:%M')
        }
        ohlc_data = obj.getCandleData(historic_params)
        data = ohlc_data.get('data', [])

        if data:
            df = pd.DataFrame(
                np.array(data),
                columns=["Datetime", "Open", "High", "Low", "Close", "Volume"]
            )
            print("📊 OHLC Data Fetched",df)

            if save_csv:
                export_dir = os.path.join(os.path.dirname(__file__), "csv_exports")
                os.makedirs(export_dir, exist_ok=True)
                file_name = f"ohlc_data_{symbol.replace(':', '_')}.csv"
                csv_path = os.path.join(export_dir, file_name)
                df.to_csv(csv_path, index=False)
                print(f"✅ CSV saved successfully at: {csv_path}")

        # ✅ Cache the result
        ohlc_cache[cache_key] = data
        return data

    except Exception as e:
        print("SmartAPI Error:", e)
        return []
