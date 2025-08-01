from django.shortcuts import render, redirect
from .models import BotConfiguration
from .forms import BotConfigurationForm
from django.contrib import messages
from .smartapi_helper import fetch_ohlc_data

def bot_config_view(request):
    existing_configs = BotConfiguration.objects.all()
    instance = existing_configs.first() if existing_configs.exists() else None

    interval_map = {
        "5 minute": "FIVE_MINUTE",
        "15 minute": "FIFTEEN_MINUTE",
        "30 minute": "THIRTY_MINUTE",
        "1 hour": "ONE_HOUR",
    }

    selected_interval = "ONE_MINUTE"
    if instance and instance.time_frame:
        selected_interval = interval_map.get(instance.time_frame, "ONE_MINUTE")

    # ✅ Fetch OHLC only initially
    ohlc_data = fetch_ohlc_data(interval=selected_interval)

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
            ohlc_data = fetch_ohlc_data(interval=selected_interval)

            form = BotConfigurationForm(request.POST, instance=instance)
            return render(request, 'config/bot_config.html', {
                'form': form,
                'ohlc': ohlc_data
            })

    form = BotConfigurationForm(instance=instance)
    return render(request, 'config/bot_config.html', {
        'form': form,
        'ohlc': ohlc_data
    })
