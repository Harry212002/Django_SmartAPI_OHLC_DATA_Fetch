from django.db import models

class BotConfiguration(models.Model):
    TIME_FRAMES = [
        ("5 minute", "5 minute"),
        ("15 minute", "15 minute"),
        ("30 minute", "30 minute"),
        ("1 hour", "1 hour"),
    ]

    BROKERS = [
        ("Exness", "Exness"),
        ("IC Markets", "IC Markets"),
        ("OANDA", "OANDA"),
        ("XM", "XM"),
    ]

    STRATEGIES = [
        ("EMA High Low Strategy", "EMA High Low Strategy"),
        ("MACD Crossover", "MACD Crossover"),
        ("Bollinger Bands", "Bollinger Bands"),
        ("RSI Reversal", "RSI Reversal"),
    ]

    EXIT_TYPES = [
        ("Exit By Signal", "Exit By Signal"),
        ("Exit By Target", "Exit By Target"),
        ("Exit By Stoploss", "Exit By Stoploss"),
    ]

    INDEX_CHOICES = [
        ("XAUUSD", "XAUUSD"),
        ("BTCUSD", "BTCUSD"),
        ("US30", "US30"),
        ("ETHUSD", "ETHUSD"),
    ]

    time_frame = models.CharField(max_length=20, choices=TIME_FRAMES)
    quantity = models.FloatField()
    broker = models.CharField(max_length=50, choices=BROKERS)
    strategy = models.CharField(max_length=50, choices=STRATEGIES)
    exit_type = models.CharField(max_length=30, choices=EXIT_TYPES)
    index = models.CharField(max_length=10, choices=INDEX_CHOICES)
    target = models.FloatField()
    stoploss = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)
    quantity = models.FloatField(null=True, blank=True)


    def __str__(self):
        return f"BotConfig: {self.index} - {self.strategy}"
