from django.shortcuts import render, redirect
from .models import BotConfiguration
from .forms import BotConfigurationForm
from django.contrib import messages
from .smartapi_helper import fetch_ohlc_data

def bot_config_view(request):
    existing_configs = BotConfiguration.objects.all()
    instance = existing_configs.first() if existing_configs.exists() else None

    # Fetch OHLC data from SmartAPI
    ohlc_data = fetch_ohlc_data()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save' and instance:
            form = BotConfigurationForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Configuration updated successfully.')

        elif action == 'submit':
            form = BotConfigurationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'New configuration created successfully.')

        return redirect('bot_config')

    form = BotConfigurationForm(instance=instance)
    return render(request, 'config/bot_config.html', {
    'form': form,
    'ohlc': ohlc_data   # ✅ changed key name
})
