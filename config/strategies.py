import pandas as pd

def calculate_ema_signals(ohlc_data):
    """
    Takes OHLC data (list from SmartAPI) → returns DataFrame with EMA signals.
    """
    if not ohlc_data:
        return pd.DataFrame()

    df = pd.DataFrame(
        ohlc_data,
        columns=["Datetime", "Open", "High", "Low", "Close", "Volume"]
    )

    # Convert Close column to float
    df["Close"] = df["Close"].astype(float)

    # ✅ Calculate EMAs
    df["EMA_9"] = df["Close"].ewm(span=9, adjust=False).mean()
    df["EMA_21"] = df["Close"].ewm(span=21, adjust=False).mean()

    # ✅ Generate Buy/Sell signals
    df["Signal"] = ""
    for i in range(1, len(df)):
        if df["EMA_9"].iloc[i] > df["EMA_21"].iloc[i] and df["EMA_9"].iloc[i - 1] <= df["EMA_21"].iloc[i - 1]:
            df.loc[df.index[i], "Signal"] = "BUY"
        elif df["EMA_9"].iloc[i] < df["EMA_21"].iloc[i] and df["EMA_9"].iloc[i - 1] >= df["EMA_21"].iloc[i - 1]:
            df.loc[df.index[i], "Signal"] = "SELL"

    return df
