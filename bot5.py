import os
import json
import time
import requests
import pandas as pd

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

STATE_FILE = "state.json"

BASE_URL = "https://api.mexc.com"

FAST = 12
SLOW = 26
SIGNAL = 9


# ---------------- TELEGRAM ---------------- #

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        },
        timeout=30
    )


# ---------------- STATE ---------------- #

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


# ---------------- MEXC ---------------- #

def get_symbols():

    r = requests.get(
        BASE_URL + "/api/v3/exchangeInfo",
        timeout=30
    )

    data = r.json()

    symbols = []

    for s in data["symbols"]:

        if s["status"] != "1":
            continue

        if s["quoteAsset"] != "USDT":
            continue

        symbols.append(s["symbol"])

    return sorted(symbols)


def get_klines(symbol):

    url = BASE_URL + "/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1d",
        "limit": 120
    }

    r = requests.get(
        url,
        params=params,
        timeout=30
    )

    return r.json()


# ---------------- INDICATORI ---------------- #

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def macd(close):

    ema_fast = ema(close, FAST)
    ema_slow = ema(close, SLOW)

    macd_line = ema_fast - ema_slow

    signal = ema(macd_line, SIGNAL)

    hist = macd_line - signal

    return macd_line, signal, hist


# ---------------- ANALISI ---------------- #

def analyze(symbol):

    try:

        candles = get_klines(symbol)

        closes = pd.Series(
            [float(x[4]) for x in candles]
        )

        macd_line, signal, hist = macd(closes)

        prev = macd_line.iloc[-2]
        curr = macd_line.iloc[-1]

        if prev < 0 and curr > 0:
            return "LONG", curr

        if prev > 0 and curr < 0:
            return "SHORT", curr

        return None

    except Exception as e:

        print(symbol, e)

        return None


# ---------------- MAIN ---------------- #

def main():

    state = load_state()

    symbols = get_symbols()

    print("Totale coppie:", len(symbols))

    changed = False

    for symbol in symbols:

        result = analyze(symbol)

        if result is None:
            continue

        side, value = result

        last = state.get(symbol)

        if last == side:
            continue

        state[symbol] = side

        changed = True

        signals = load_signals()

        signals.append({
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": symbol,
            "side": side,
            "value": float(value)
        })

save_signals(signals)

        emoji = "🟢" if side == "LONG" else "🔴"

        message = (
            f"{emoji} <b>{side}</b>\n\n"
            f"{symbol}\n"
            f"Timeframe: 1D\n"
            f"MACD Zero Cross\n\n"
            f"MACD = {value:.6f}"
        )

        print(message)

        send_telegram(message)

        time.sleep(1)

# ---------------- MAIN ENTRY ---------------- #

SIGNALS_FILE = "signals.json"


def load_signals():
    if os.path.exists(SIGNALS_FILE):
        with open(SIGNALS_FILE, "r") as f:
            return json.load(f)
    return []


def save_signals(signals):
    with open(SIGNALS_FILE, "w") as f:
        json.dump(signals[-200:], f, indent=2)
        

if __name__ == "__main__":

    print("Starting MACD Zero Cross Bot...")

    try:
        main()
    except Exception as e:
        print("Fatal error:", e)
