import pandas as pd
import numpy as np
import os
from SmartApi import SmartConnect
from django.conf import settings
import datetime
import pyotp
import requests
import pathlib
# :white_check_mark: Cache session and data to avoid repeated API calls
smartapi_session = None
ohlc_cache = {}
instrument_cache = None

#                 Get SmartAPI Session
def get_smartapi_session():
    """Create or reuse an existing SmartAPI session"""
    global smartapi_session
    if smartapi_session is None:
        obj = SmartConnect(api_key=settings.SMARTAPI_API_KEY)
        totp = pyotp.TOTP(settings.SMARTAPI_TOTP_SECRET).now()
        obj.generateSession(
            settings.SMARTAPI_USERNAME,
            settings.SMARTAPI_PASSWORD,
            totp
        )
        smartapi_session = obj
    return smartapi_session

#                 Fetch OHLC Data
def fetch_ohlc_data(symbol="NSE:NIFTY 50", interval="ONE_MINUTE", days=1, save_csv=False):
    try:
        global ohlc_cache
        cache_key = f"{symbol}_{interval}_{days}"
        if cache_key in ohlc_cache:
            return ohlc_cache[cache_key]
        obj = get_smartapi_session()
        to_date = datetime.datetime.now()
        from_date = to_date - datetime.timedelta(days=days)
        symbol_token_map = {
            "NSE:NIFTY 50": "3045",
            "BANKNIFTY": "99926000",
            "TATASTEEL-EQ": "3499",
            "WIPRO-EQ": "3787",
            "RELIANCE-EQ": "2885",
            "GOLD": "217",
            "BTCUSD": "1234",
            "US30": "5678",
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
            print(":bar_chart: OHLC Data Fetched:", len(df))
            if save_csv:
                export_dir = os.path.join(os.path.dirname(__file__), "csv_exports")
                os.makedirs(export_dir, exist_ok=True)
                file_name = f"ohlc_data_{symbol.replace(':', '_')}.csv"
                csv_path = os.path.join(export_dir, file_name)
                df.to_csv(csv_path, index=False)
                print(f":white_check_mark: CSV saved successfully at: {csv_path}")
        ohlc_cache[cache_key] = data
        return data
    except Exception as e:
        print("SmartAPI Error:", e)
        return []
 #                 Place Order  
def place_order(symbol_name, transaction_type, quantity=1, price=0.0, order_type="MARKET", product_type="INTRADAY"):
    try:
        obj = get_smartapi_session()
        tradingsymbol, symboltoken = get_symbol_token(symbol_name, "NSE")
        if not tradingsymbol:
            return {"error": f"Symbol {symbol_name} not found", "status": "FAILED"}
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": tradingsymbol,
            "symboltoken": symboltoken,
            "transactiontype": transaction_type,
            "exchange": "NSE",
            "ordertype": order_type,
            "producttype": product_type,
            "duration": "DAY",
            "price": price,
            "quantity": quantity,
        }
        print(":octagonal_sign: Order Params:", order_params)  # Debug
        response = obj.placeOrder(order_params)
        print(":octagonal_sign: Order Response:", response)   # Debug
        if isinstance(response, str):
            response = {
                "data": {"orderid": response},
                "message": "SUCCESS",
                "status": "PENDING"
            }
        if isinstance(response, dict):
            order_id = response.get("data", {}).get("orderid")
            response["order_id"] = order_id
            response["status"] = response.get("status", "PENDING")
        else:
            response = {"error": "Invalid response type", "status": "FAILED"}
        return response
    except Exception as e:
        return {"error": str(e), "status": "FAILED"}
#                 Get ALL Instruments    
def get_all_instruments(save_excel=True):
    """Download and cache Angel One instruments list and optionally save as Excel"""
    global instrument_cache
    if instrument_cache is None:
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        response = requests.get(url)
        instrument_cache = pd.DataFrame(response.json())
        if save_excel:
            home_dir = pathlib.Path.home()
            downloads_dir = home_dir / "Downloads"
            downloads_dir.mkdir(parents=True, exist_ok=True)
            excel_path = downloads_dir / "angel_instruments.xlsx"
            instrument_cache.to_excel(excel_path, index=False)
            print(f":white_check_mark: Instruments saved as Excel at: {excel_path}")
    return instrument_cache

#                 Get Symbol Token
def get_symbol_token(symbol_name, exchange="NSE"):
    """Get tradingsymbol + token for a given symbol from instruments list"""
    instruments = get_all_instruments()
    row = instruments[
        (instruments["symbol"] == symbol_name) &
        (instruments["exch_seg"] == exchange)
    ]
    if not row.empty:
        return row.iloc[0]["symbol"], row.iloc[0]["token"]
    return None, None

# ---------------- ORDER STATUS ----------------
def get_order_status(order_id):
    """Get exact/updated order status"""
    try:
        obj = get_smartapi_session()
        orders = obj.orderBook()  # Fetch all orders
        if isinstance(orders, dict) and "data" in orders:
            for order in orders["data"]:
                if order.get("orderid") == str(order_id):
                    return order.get("status")  # COMPLETE, REJECTED, PENDING, CANCELLED
        return "UNKNOWN"
    except Exception as e:
        print("Error fetching order status:", e)
        return "FAILED"
