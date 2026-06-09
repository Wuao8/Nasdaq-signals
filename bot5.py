import os
import requests
import pandas as pd
import yfinance as yf

# ======================
# TELEGRAM
# ======================

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=20
        )
    except:
        pass


# ======================
# FOREX UNIVERSE
# ======================

def get_forex_universe():

    pairs = [

        # Majors
        "EURUSD=X",
        "GBPUSD=X",
        "AUDUSD=X",
        "NZDUSD=X",
        "USDJPY=X",
        "USDCHF=X",
        "USDCAD=X",

        # Euro Crosses
        "EURGBP=X",
        "EURJPY=X",
        "EURCHF=X",
        "EURAUD=X",
        "EURNZD=X",
        "EURCAD=X",

        # GBP Crosses
        "GBPJPY=X",
        "GBPCHF=X",
        "GBPAUD=X",
        "GBPNZD=X",
        "GBPCAD=X",

        # AUD Crosses
        "AUDJPY=X",
        "AUDNZD=X",
        "AUDCHF=X",
        "AUDCAD=X",

        # NZD Crosses
        "NZDJPY=X",
        "NZDCHF=X",
        "NZDCAD=X",

        # CAD Crosses
        "CADJPY=X",
        "CADCHF=X",

        # CHF Crosses
        "CHFJPY=X",

        # Additional liquid pairs
        "SGDJPY=X",
        "EURSGD=X",
        "GBPSGD=X",
        "AUDSGD=X",
        "USDSEK=X",
        "USDNOK=X",
        "USDMXN=X",
        "USDZAR=X",
        "USDTRY=X",
        "USDPLN=X",
        "USDHUF=X",
        "USDCZK=X"
    ]

    return pairs


# ======================
# DATA
# ======================

def get_data(symbol):

    try:

        df = yf.download(
            symbol,
            period="6mo",
            interval="1d",
            progress=False,
            auto_adjust=True,
            threads=False
        )

        if df is None or df.empty:
            return None

        df = df[["Close"]].copy()

        df["Close"] = pd.to_numeric(
            df["Close"],
            errors="coerce"
        )

        df = df.dropna()

        if len(df) < 50:
            return None

        return df

    except:
        return None


# ======================
# INDICATORS
# ======================

def ema20(df):
    return df["Close"].ewm(span=20).mean()


def macd(df):

    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()

    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9).mean()

    return macd_line, signal_line


# ======================
# SIGNAL LOGIC
# ======================

def check_signal(df):

    df["ema20"] = ema20(df)

    macd_line, signal_line = macd(df)

    df["macd"] = macd_line
    df["signal"] = signal_line

    prev = df.iloc[-2]
    last = df.iloc[-1]

    long_ema = (
        prev["Close"] < prev["ema20"]
        and last["Close"] > last["ema20"]
    )

    short_ema = (
        prev["Close"] > prev["ema20"]
        and last["Close"] < last["ema20"]
    )

    long_macd = (
        last["macd"] > last["signal"]
    )

    short_macd = (
        last["macd"] < last["signal"]
    )

    if long_ema and long_macd:
        return "LONG"

    if short_ema and short_macd:
        return "SHORT"

    return None


# ======================
# ENGINE
# ======================

def run_scan():

    signals = []

    symbols = get_forex_universe()

    for symbol in symbols:

        try:

            df = get_data(symbol)

            if df is None:
                continue

            signal = check_signal(df)

            if signal:

                price = float(df.iloc[-1]["Close"])

                clean_symbol = symbol.replace("=X", "")

                signals.append(
                    f"{signal} | {clean_symbol} @ {round(price, 5)}"
                )

        except:
            continue

    return signals


# ======================
# MAIN
# ======================

if __name__ == "__main__":

    print("FOREX BOT STARTING SCAN...")

    results = run_scan()

    if results:

        msg = (
            "💱 FOREX DAILY SIGNALS\n"
            "EMA20 + MACD\n\n"
            + "\n".join(results[:20])
        )

        send_message(msg)

        print("Signals sent:")
        print(results)

    else:
        print("No signals found")
