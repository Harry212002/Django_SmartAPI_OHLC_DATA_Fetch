from django.db import models
class BotConfiguration(models.Model):
    TIME_FRAMES = [
        ('1m', '1 minute'),
        ("5 minute", "5 minute"),
        ("15 minute", "15 minute"),
        ("30 minute", "30 minute"),
        ("1 hour", "1 hour"),
    ]
    BROKERS = [
        ("Angle one","Angle one"),
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
        ("NSE NIFTY 50", "NSE NIFTY 50"),
        ("BANKNIFTY", "BANKNIFTY"),
        ("Tata", "Tata"),
        ("WIPRO", "WIPRO"),
        ("RELIANCE", "RELIANCE"),
        ("XAUUSD", "XAUUSD"),
        ("BTCUSD", "BTCUSD"),
        ("US30", "US30"),
        ("ETHUSD", "ETHUSD"),
    ]
    time_frame = models.CharField(max_length=20, choices=TIME_FRAMES)
    broker = models.CharField(max_length=50, choices=BROKERS)
    strategy = models.CharField(max_length=50, choices=STRATEGIES)
    exit_type = models.CharField(max_length=30, choices=EXIT_TYPES)
    index = models.CharField(max_length=30, choices=INDEX_CHOICES)
    target = models.FloatField()
    stoploss = models.FloatField()
    quantity = models.FloatField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"BotConfig: {self.index} - {self.strategy}"
class TradeSignal(models.Model):
    SIGNAL_CHOICES = [
        ("BUY", "BUY"),
        ("SELL", "SELL"),
    ]
    index = models.CharField(max_length=30, null=True, blank=True)
    time_frame = models.CharField(max_length=20, null=True, blank=True)
    datetime = models.DateTimeField()
    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    close_price = models.FloatField()
    signal = models.CharField(max_length=4, choices=SIGNAL_CHOICES)
    # :white_check_mark: New fields
    order_id = models.CharField(max_length=100, null=True, blank=True)
    order_status = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return f"{self.datetime} - {self.index} - {self.signal} - {self.order_status or 'PENDING'}"