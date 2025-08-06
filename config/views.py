from django.shortcuts import render, redirect
from .models import BotConfiguration
from .forms import BotConfigurationForm
from django.contrib import messages
from .smartapi_helper import fetch_ohlc_data
# ⬇️ ✅ UPDATED: Import EMA strategy function
from .strategies import calculate_ema_signals 

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
            selected_index=index_map.get(instance.index,"NSE:NIFTY 50")
        

    # ✅ Fetch OHLC only initially
    ohlc_data = fetch_ohlc_data(symbol=selected_index,interval=selected_interval)
    
    # ⬇️ ✅ UPDATED: Calculate EMA Buy/Sell signals
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
                form.save()
                messages.success(request, 'New configuration created successfully.')
                return redirect('bot_config')

        else:
            # ✅ Handle only time frame change without DB update
            selected_timeframe = request.POST.get('time_frame')
            selected_interval = interval_map.get(selected_timeframe, "ONE_MINUTE")
            
            selected_index_form=request.POST.get('index')
            selected_index=index_map.get(selected_index_form,"NSE:NIFTY 50")
            
            
            
            ohlc_data = fetch_ohlc_data(symbol=selected_index,interval=selected_interval)
            
             # ⬇️ ✅ UPDATED: Recalculate EMA after change
            ema_df = calculate_ema_signals(ohlc_data)

            form = BotConfigurationForm(request.POST, instance=instance)
            return render(request, 'config/bot_config.html', {
                'form': form,
                # 'ohlc': ohlc_data
                'ohlc': ema_df.to_numpy().tolist()  # ✅ UPDATED: Pass EMA data
            })

    form = BotConfigurationForm(instance=instance)
    return render(request, 'config/bot_config.html', {
        'form': form,
        # 'ohlc': ohlc_data
        'ohlc': ema_df.to_numpy().tolist()  # ✅ UPDATED: Pass EMA data
    })
