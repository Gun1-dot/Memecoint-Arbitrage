import requests
import os

MEME_TOKEN_NAME = "pepe"
PRICE_DIFF_THRESHOLD = 0.01 # percent

def get_token_data(token_name):
    url = f"https://api.dexscreener.com/latest/dex/search/?q={token_name}"
    response = requests.get(url)
    return response.json()

def send_telegram(msg):
    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

def find_arbitrage_opportunities(token_name):
    data = get_token_data(token_name)
    pairs = data.get("pairs", [])

    prices = []
    for p in pairs:
        try:
            price_usd = float(p["priceUsd"])
            dex = p["dexId"]
            chain = p["chainId"]
            prices.append((price_usd, dex, chain, p["url"]))
        except:
            continue

    if len(prices) < 2:
        return

    prices.sort()
    lowest = prices[0]
    highest = prices[-1]
    diff_pct = ((highest[0] - lowest[0]) / lowest[0]) * 100

    if diff_pct > PRICE_DIFF_THRESHOLD:
        msg = (
            f"🚨 Arbitrage Alert for {token_name.upper()}\n"
            f"Buy on {lowest[1]} ({lowest[2]}) at ${lowest[0]:.8f}\n"
            f"Sell on {highest[1]} ({highest[2]}) at ${highest[0]:.8f}\n"
            f"Diff: {diff_pct:.2f}%\n"
            f"Buy URL: {lowest[3]}\nSell URL: {highest[3]}"
        )
        send_telegram(msg)

find_arbitrage_opportunities(MEME_TOKEN_NAME)
send_telegram("✅ Test Message: Memecoin Arbitrage Bot is working!")

