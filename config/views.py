from django.shortcuts import render, redirect
from .models import BotConfiguration, TradeSignal
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
        "NSE NIFTY 50": "NIFTY",
        "BANKNIFTY": "BANKNIFTY",
        "Tata": "TATASTEEL-EQ",
        "WIPRO": "WIPRO-EQ",
        "RELIANCE": "RELIANCE-EQ",
        "XAUUSD": "GOLD",
        "BTCUSD": "BTCUSD",
        "US30": "US30",
        "ETHUSD": "ETHUSD",
    }
    selected_interval = "ONE_MINUTE"
    selected_index = "NIFTY"
    if instance:
        if instance.time_frame:
            selected_interval = interval_map.get(instance.time_frame, "ONE_MINUTE")
        if instance.index:
            selected_index = index_map.get(instance.index, "NIFTY")
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
                messages.success(request, 'New configuration created successfully and also your Order is Placed.')
                selected_timeframe = form.cleaned_data['time_frame']
                selected_interval = interval_map.get(selected_timeframe, "ONE_MINUTE")
                selected_index_form = form.cleaned_data['index']
                selected_index = index_map.get(selected_index_form, "NIFTY")
                ohlc_data = fetch_ohlc_data(symbol=selected_index, interval=selected_interval)
                print("Fetched OHLC length (POST submit):", len(ohlc_data))
                ema_df = calculate_ema_signals(ohlc_data)
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
                    response = place_order(
                        symbol_name=selected_index,
                        transaction_type=row["Signal"],
                        quantity=bot_config.quantity,
                    )
                    print(":package: Order Response:", response)
                    trade.order_status = response.get("status", "FAILED")
                    trade.order_id = response.get("order_id")
                    trade.save()
                    print(f":white_check_mark: Saved Trade: ID={trade.order_id}, Status={trade.order_status}")
                return redirect('bot_config')
        else:
            selected_timeframe = request.POST.get('time_frame')
            selected_interval = interval_map.get(selected_timeframe, "ONE_MINUTE")
            selected_index_form = request.POST.get('index')
            selected_index = index_map.get(selected_index_form, "NIFTY")
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