import requests
import os
from datetime import datetime

# ✅ Your Telegram bot credentials
TELEGRAM_TOKEN = "8115132882:AAGMHQovlrHYKS7tYG6yLbLkEb1SSzooBTo"
TELEGRAM_CHAT_ID = "7685414166"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)

def is_high_opportunity(token):
    try:
        vol_5m = float(token.get("volume", {}).get("m5", 0))
        price_change = float(token.get("priceChange", {}).get("m15", 0))
        mcap = float(token.get("fdv", 0))
        buy_tx = int(token.get("txns", {}).get("m30", {}).get("buys", 0))
        sell_tx = int(token.get("txns", {}).get("m30", {}).get("sells", 0))
        buy_ratio = (buy_tx / (buy_tx + sell_tx)) * 100 if (buy_tx + sell_tx) > 0 else 0
        return vol_5m > 3000 and 20 <= price_change <= 100 and mcap < 5000000 and buy_ratio > 85
    except:
        return False

def main():
    url = "https://api.dexscreener.com/latest/dex/pairs"
    response = requests.get(url)
    if response.status_code != 200:
        send_telegram("⚠️ Failed to fetch Dexscreener data.")
        return

    tokens = response.json().get("pairs", [])
    hot_tokens = [t for t in tokens if is_high_opportunity(t)]

    if not hot_tokens:
        print("✅ No strong opportunities now.")
        return

    for token in hot_tokens:
        name = token.get("baseToken", {}).get("name", "?")
        symbol = token.get("baseToken", {}).get("symbol", "?")
        price = token.get("priceUsd", "?")
        vol = token.get("volume", {}).get("m5", "?")
        change = token.get("priceChange", {}).get("m15", "?")
        mcap = token.get("fdv", "?")
        buys = token.get("txns", {}).get("m30", {}).get("buys", 0)
        sells = token.get("txns", {}).get("m30", {}).get("sells", 0)
        link = token.get("url", "")

        msg = f"""
🔥 *Opportunity Detected for {symbol}!*
Name: {name}
Price: ${price}
5m Volume: {vol}
15m Change: {change}%
Market Cap: ${mcap}
Buy/Sell (30m): {buys}/{sells}
[🔗 Chart]({link})
        """.strip()

        send_telegram(msg)

if __name__ == "__main__":
    main()
