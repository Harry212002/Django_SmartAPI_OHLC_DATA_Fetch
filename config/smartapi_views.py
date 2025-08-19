import pandas as pd
import numpy as np
import os
from SmartApi import SmartConnect
from django.conf import settings
import datetime
import pyotp
import requests
import pathlib

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
        # print("✅ SmartAPI Session Created:", session_data)
        smartapi_session = obj
    return smartapi_session

def fetch_ohlc_data(symbol="NSE:NIFTY 50", interval="ONE_MINUTE", days=1, save_csv=False):
    try:
        global ohlc_cache
        cache_key = f"{symbol}_{interval}_{days}"

        # ✅ Return cached data if available
        if cache_key in ohlc_cache:
            # print("⚡ Using cached OHLC data")
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
            print("📊 OHLC Data Fetched")

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

        response = obj.placeOrder(order_params)

        # ✅ If response is a string, wrap it in dict
        if isinstance(response, str):
            response = {
                "data": {"orderid": response},
                "message": "SUCCESS",
                "status": "PENDING"
            }

        # ✅ Ensure response is dict before accessing keys
        if isinstance(response, dict):
            order_id = response.get("data", {}).get("orderid")
            response["order_id"] = order_id
            response["status"] = response.get("status", "PENDING")
        else:
            response = {"error": "Invalid response type", "status": "FAILED"}

        return response

    except Exception as e:
        return {"error": str(e), "status": "FAILED"}

instrument_cache = None

def get_all_instruments(save_excel=True):
    """Download and cache Angel One instruments list and optionally save as Excel"""
    global instrument_cache
    if instrument_cache is None:
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        response = requests.get(url)
        instrument_cache = pd.DataFrame(response.json())
        # print("This is instruments:")
        # print(instrument_cache)

        # ✅ Save to Excel
        if save_excel:
            # Get the user's home directory
            home_dir = pathlib.Path.home()
            # Construct the path to the Downloads folder
            downloads_dir = home_dir / "Downloads"

            # Create the Downloads folder if it doesn't exist
            downloads_dir.mkdir(parents=True, exist_ok=True)
            
            excel_path = downloads_dir / "angel_instruments.xlsx"
            instrument_cache.to_excel(excel_path, index=False)
            
            # export_dir = os.path.join(os.path.dirname(__file__), "csv_exports")
            # os.makedirs(export_dir, exist_ok=True)
            # excel_path = os.path.join(export_dir, "angel_instruments.xlsx")
            # instrument_cache.to_excel(excel_path, index=False)
            print(f"✅ Instruments saved as Excel at: {excel_path}")

    return instrument_cache

def get_symbol_token(symbol_name, exchange="NSE"):
    """
    Get tradingsymbol + token for a given symbol from instruments list
    """
    instruments = get_all_instruments()
    row = instruments[
        (instruments["symbol"] == symbol_name) & 
        (instruments["exch_seg"] == exchange)
    ]
    if not row.empty:
        return row.iloc[0]["symbol"], row.iloc[0]["token"]
    return None, None



# from django.shortcuts import render, redirect
# from .models import *
# from .forms import BotConfigurationForm
# from django.contrib import messages
# from .smartapi_helper import fetch_ohlc_data,place_order
# # ⬇️ ✅ UPDATED: Import EMA strategy function
# from .strategies import calculate_ema_signals 

# def bot_config_view(request):
#     existing_configs = BotConfiguration.objects.all()
#     instance = existing_configs.first() if existing_configs.exists() else None

#     interval_map = {
#         "5 minute": "FIVE_MINUTE",
#         "15 minute": "FIFTEEN_MINUTE",
#         "30 minute": "THIRTY_MINUTE",
#         "1 hour": "ONE_HOUR",
#     }
#     index_map = {
#         "NSE NIFTY 50": "NSE:NIFTY 50",
#         "BANKNIFTY": "BANKNIFTY",
#         "Tata": "TATASTEEL",
#         "WIPRO": "WIPRO",
#         "RELIANCE": "RELIANCE",
#         "XAUUSD": "GOLD",
#         "BTCUSD": "BTCUSD",
#         "US30": "US30",
#         "ETHUSD": "ETHUSD",
#     }

#     selected_interval = "ONE_MINUTE"
#     selected_index = "NSE:NIFTY 50"

#     if instance:
#         if instance.time_frame:
#             selected_interval = interval_map.get(instance.time_frame, "ONE_MINUTE")
#         if instance.index:
#             selected_index=index_map.get(instance.index,"NSE:NIFTY 50")
        

#     # ✅ Fetch OHLC only initially
#     ohlc_data = fetch_ohlc_data(symbol=selected_index,interval=selected_interval)
    
#     # ⬇️ ✅ UPDATED: Calculate EMA Buy/Sell signals
#     ema_df = calculate_ema_signals(ohlc_data)

#     if request.method == 'POST':
#         action = request.POST.get('action')

#         if action == 'save' and instance:
#             form = BotConfigurationForm(request.POST, instance=instance)
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, 'Configuration updated successfully.')
#                 return redirect('bot_config')

#         elif action == 'submit':
#             form = BotConfigurationForm(request.POST)
#             if form.is_valid():
#                 bot_config =form.save()
#                 messages.success(request, 'New configuration created successfully.')
                
#                 # ✅ Fetch fresh OHLC based on form
#                 selected_timeframe = form.cleaned_data['time_frame']
#                 selected_interval = interval_map.get(selected_timeframe, "ONE_MINUTE")

#                 selected_index_form = form.cleaned_data['index']
#                 selected_index = index_map.get(selected_index_form, "NSE:NIFTY 50")

#                 ohlc_data = fetch_ohlc_data(symbol=selected_index, interval=selected_interval)
#                 ema_df = calculate_ema_signals(ohlc_data)
                
#                 # ✅ Store only BUY/SELL signals
#                 signal_rows = ema_df[ema_df["Signal"].isin(["BUY", "SELL"])]
#                 for _, row in signal_rows.iterrows():
                    

#                     trade=TradeSignal.objects.create(
#                         datetime=row["Datetime"],
#                         open_price=row["Open"],
#                         high_price=row["High"],
#                         low_price=row["Low"],
#                         close_price=row["Close"],
#                         signal=row["Signal"],
#                         index=selected_index,
#                         time_frame=selected_interval,
#                     )
#                     # ✅ Place order for each BUY/SELL
#                     response = place_order(
#                          # ⚠️ Map from index → tokensymbol_token="3045", 
#                         symbol_name=selected_index,   # e.g. "RELIANCE-EQ" or "NIFTY 50"
#                         transaction_type=row["Signal"],
#                         quantity=bot_config.quantity,
#                     )
#                     if response and "data" in response:
#                         trade.order_id = response["data"]["orderid"]
#                         trade.order_status = response.get("status", "PENDING")
#                         trade.save()
                
                
#                 return redirect('bot_config')

#         else:
#             # ✅ Handle only time frame change without DB update
#             selected_timeframe = request.POST.get('time_frame')
#             selected_interval = interval_map.get(selected_timeframe, "ONE_MINUTE")
            
#             selected_index_form=request.POST.get('index')
#             selected_index=index_map.get(selected_index_form,"NSE:NIFTY 50")
            
                        
#             ohlc_data = fetch_ohlc_data(symbol=selected_index,interval=selected_interval)
#             ema_df = calculate_ema_signals(ohlc_data)  # ⬇️ ✅ UPDATED: Recalculate EMA after change

#             form = BotConfigurationForm(request.POST, instance=instance)
#             return render(request, 'config/bot_config.html', {
#                 'form': form,
#                 # 'ohlc': ohlc_data
#                 'ohlc': ema_df.to_numpy().tolist()  # ✅ UPDATED: Pass EMA data
#             })

#     form = BotConfigurationForm(instance=instance)

#     return render(request, 'config/bot_config.html', {
#         'form': form,
#         'ohlc': ema_df.to_numpy().tolist(),# ✅ UPDATED: Pass EMA data

#     })


from django.shortcuts import render, redirect
from .models import *
from .forms import BotConfigurationForm
from django.contrib import messages
from .smartapi_helper import fetch_ohlc_data, place_order
from .strategies import calculate_ema_signals
import pandas as pd

def bot_config_view(request):
    existing_configs = BotConfiguration.objects.all()
    instance = existing_configs.first() if existing_configs.exists() else None

    interval_map = {
        "5 minute": "FIVE_MINUTE",
        "15 minute": "FIFTEEN_MINUTE",
        "30 minute": "THIRTY_MINUTE",
        "1 hour": "ONE_HOUR",
    }
    index_map = {
        "NSE NIFTY 50": "NSE:NIFTY 50",
        "BANKNIFTY": "BANKNIFTY",
        "Tata": "TATASTEEL",
        "WIPRO": "WIPRO",
        "RELIANCE": "RELIANCE",
        "XAUUSD": "GOLD",
        "BTCUSD": "BTCUSD",
        "US30": "US30",
        "ETHUSD": "ETHUSD",
    }

    selected_interval = "ONE_MINUTE"
    selected_index = "NSE:NIFTY 50"

    if instance:
        if instance.time_frame:
            selected_interval = interval_map.get(instance.time_frame, "ONE_MINUTE")
        if instance.index:
            selected_index = index_map.get(instance.index, "NSE:NIFTY 50")

    # Fetch OHLC data
    ohlc_data = fetch_ohlc_data(symbol=selected_index, interval=selected_interval)
    print("Fetched OHLC length:", len(ohlc_data))

    # Calculate EMA signals
    ema_df = calculate_ema_signals(ohlc_data)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save' and instance:
            form = BotConfigurationForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Configuration updated successfully.')
                return redirect('bot_config')

        elif action == 'submit':
            form = BotConfigurationForm(request.POST)
            if form.is_valid():
                bot_config = form.save()
                messages.success(request, 'New configuration created successfully and alos your Order is Placed.')

                # Fetch fresh OHLC based on form
                selected_timeframe = form.cleaned_data['time_frame']
                selected_interval = interval_map.get(selected_timeframe, "ONE_MINUTE")

                selected_index_form = form.cleaned_data['index']
                selected_index = index_map.get(selected_index_form, "NSE:NIFTY 50")

                ohlc_data = fetch_ohlc_data(symbol=selected_index, interval=selected_interval)
                print("Fetched OHLC length (POST submit):", len(ohlc_data))

                ema_df = calculate_ema_signals(ohlc_data)

                # ✅ Safely filter BUY/SELL signals
                if "Signal" in ema_df.columns:
                    signal_rows = ema_df[ema_df["Signal"].isin(["BUY", "SELL"])]
                else:
                    signal_rows = pd.DataFrame()

                for _, row in signal_rows.iterrows():
                    trade = TradeSignal.objects.create(
                        datetime=row["Datetime"],
                        open_price=row["Open"],
                        high_price=row["High"],
                        low_price=row["Low"],
                        close_price=row["Close"],
                        signal=row["Signal"],
                        index=selected_index,
                        time_frame=selected_interval,
                    )

                    # Place order for each BUY/SELL
                    response = place_order(
                        symbol_name=selected_index,
                        transaction_type=row["Signal"],
                        quantity=bot_config.quantity,
                    )
                    print("📦 Order Response:", response)

                    trade.order_status = response.get("status", "FAILED")
                    trade.order_id = response.get("order_id")
                    trade.save()
                    print(f"✅ Saved Trade: ID={trade.order_id}, Status={trade.order_status}")

                return redirect('bot_config')

        else:
            # Handle only time frame or index change without DB update
            selected_timeframe = request.POST.get('time_frame')
            selected_interval = interval_map.get(selected_timeframe, "ONE_MINUTE")

            selected_index_form = request.POST.get('index')
            selected_index = index_map.get(selected_index_form, "NSE:NIFTY 50")

            ohlc_data = fetch_ohlc_data(symbol=selected_index, interval=selected_interval)
            print("Fetched OHLC length (POST change):", len(ohlc_data))

            ema_df = calculate_ema_signals(ohlc_data)

            form = BotConfigurationForm(request.POST, instance=instance)
            return render(request, 'config/bot_config.html', {
                'form': form,
                'ohlc': ema_df.to_numpy().tolist() if not ema_df.empty else [],
            })

    form = BotConfigurationForm(instance=instance)
    return render(request, 'config/bot_config.html', {
        'form': form,
        'ohlc': ema_df.to_numpy().tolist() if not ema_df.empty else [],
    })
