import requests

# ✅ Your hardcoded Telegram credentials
TELEGRAM_TOKEN = "8115132882:AAGMHQovlrHYKS7tYG6yLbLkEb1SSzooBTo"
TELEGRAM_CHAT_ID = "7685414166"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    res = requests.post(url, data=data)
    print("Telegram response:", res.text)

def check_dexscreener():
    url = "https://api.dexscreener.com/latest/dex/pairs"
    response = requests.get(url)
    if response.status_code != 200:
        send_telegram("❌ Failed to fetch data from Dexscreener API.")
        return

    pairs = response.json().get("pairs", [])[:50]  # scan top 50
    found = False

    for token in pairs:
        try:
            name = token.get("baseToken", {}).get("name", "?")
            symbol = token.get("baseToken", {}).get("symbol", "?")
            price = float(token.get("priceUsd", 0))
            change = float(token.get("priceChange", {}).get("m15", 0))
            volume = float(token.get("volume", {}).get("m5", 0))
            mcap = float(token.get("fdv", 0))
            link = token.get("url", "")

            # Basic filter logic: price pump + low mcap + high 5m volume
            if change > 20 and volume > 3000 and mcap < 5_000_000:
                found = True
                msg = f"""
🚀 <b>Opportunity Detected!</b>
Token: {symbol} ({name})
Price: ${price:.6f}
15m Change: +{change:.2f}%
5m Volume: ${volume:,.0f}
Market Cap: ${mcap:,.0f}
<a href="{link}">🔗 View on Dexscreener</a>
                """.strip()
                send_telegram(msg)

        except Exception as e:
            print("Error scanning token:", e)

    if not found:
        send_telegram("✅ Bot ran. No high-potential memecoin opportunities found.")

if __name__ == "__main__":
    check_dexscreener()
