import pandas as pd
import numpy as np
import os
from SmartApi import SmartConnect
from django.conf import settings
import datetime
import pyotp

def fetch_ohlc_data(symbol="NSE:NIFTY 50", interval="ONE_MINUTE", days=1, save_csv=False):
    try:
        obj = SmartConnect(api_key=settings.SMARTAPI_API_KEY)

        totp = pyotp.TOTP(settings.SMARTAPI_TOTP_SECRET).now()
        print("Generated OTP:", totp)

        session_data = obj.generateSession(
            settings.SMARTAPI_USERNAME,
            settings.SMARTAPI_PASSWORD,
            totp
        )
        print("Session Data:", session_data)

        to_date = datetime.datetime.now()
        from_date = to_date - datetime.timedelta(days=days)

        symbol_token_map = {
            "NSE:NIFTY 50": "3045",
            "BANKNIFTY": "99926000",
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
            print("\n📊 OHLC Data:\n", df)

            # 🔥 ✅ NEW: CSV Export Functionality
            if save_csv:  
                export_dir = os.path.join(os.path.dirname(__file__), "csv_exports")
                os.makedirs(export_dir, exist_ok=True)  # Create folder if not exists

                file_name = f"ohlc_data_{symbol.replace(':', '_')}.csv"
                csv_path = os.path.join(export_dir, file_name)

                df.to_csv(csv_path, index=False)
                print(f"\n✅ CSV saved successfully at: {csv_path}")
        return data

    except Exception as e:
        print("SmartAPI Error:", e)
        return []
