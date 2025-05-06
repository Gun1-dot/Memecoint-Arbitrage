import requests
import os

# Use your actual bot token and chat ID
TELEGRAM_TOKEN = "8115132882:AAGMHQovlrHYKS7tYG6yLbLkEb1SSzooBTo"
TELEGRAM_CHAT_ID = "7685414166"
PRICE_DIFF_THRESHOLD = 0.01  # 1%

def get_token_data(token_name):
    url = f"https://api.dexscreener.com/latest/dex/search/?q={token_name}"
    response = requests.get(url)
    return response.json()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    requests.post(url, data=data)

def find_arbitrage_opportunities(token_name):
    data = get_token_data(token_name)
    pairs = data.get("pairs", [])
    prices = []

    for p in pairs:
        try:
            price_usd = float(p["priceUsd"])
            dex = p["dexId"]
            chain = p["chainId"]
            url = p["url"]
            liquidity = p.get("liquidity", {}).get("usd", "N/A")
            prices.append((price_usd, dex, chain, url, liquidity))
        except:
            continue

    prices.sort()
    if len(prices) < 2:
        return

    low = prices[0]
    high = prices[-1]
    spread = (high[0] - low[0]) / low[0]

    if spread > PRICE_DIFF_THRESHOLD:
        msg = (
            f"🚨 Arbitrage Detected for {token_name.upper()}\n"
            f"Buy on {low[1]} ({low[2]}) at ${low[0]:.8f} (liq: ${low[4]})\n"
            f"Sell on {high[1]} ({high[2]}) at ${high[0]:.8f} (liq: ${high[4]})\n"
            f"Spread: {spread * 100:.2f}%\n"
            f"Buy URL: {low[3]}\n"
            f"Sell URL: {high[3]}"
        )
        send_telegram(msg)

def main():
    print("✅ Bot started")
    token_list = ["pepe", "shib", "doge", "floki", "baby", "elon", "jeet", "rekt", "moon", "snek"]
    for token in token_list:
        find_arbitrage_opportunities(token)

if __name__ == "__main__":
    main()
