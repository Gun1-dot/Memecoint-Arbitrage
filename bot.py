import requests
import os

TOKEN_LIST = ["pepe", "bome", "wif", "doge", "shib"]
PRICE_DIFF_THRESHOLD = 0.5  # percent
LIQUIDITY_THRESHOLD = 10000  # USD
VALID_CHAINS = ["solana", "ethereum"]  # only show opportunities on these chains

def get_token_data(token_name):
    url = f"https://api.dexscreener.com/latest/dex/search/?q={token_name}"
    response = requests.get(url)
    return response.json()

def send_telegram(msg):
    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

def find_arbitrage(token_name):
    data = get_token_data(token_name)
    pairs = data.get("pairs", [])
    prices = []

    for p in pairs:
        try:
            price = float(p["priceUsd"])
            dex = p["dexId"]
            chain = p["chainId"]
            url = p["url"]
            liquidity = float(p["liquidity"]["usd"])
            if liquidity >= LIQUIDITY_THRESHOLD:
                prices.append((price, dex, chain, url, liquidity))
        except:
            continue

    if len(prices) < 2:
        return

    prices.sort()
    lowest = prices[0]
    highest = prices[-1]
    diff_pct = ((highest[0] - lowest[0]) / lowest[0]) * 100

    if (
        diff_pct >= PRICE_DIFF_THRESHOLD
        and (lowest[2].lower() in VALID_CHAINS or highest[2].lower() in VALID_CHAINS)
    ):
        msg = (
            f"🚨 Arbitrage Detected for {token_name.upper()}\n"
            f"Buy on {lowest[1]} ({lowest[2]}) at ${lowest[0]:.8f} (liq: ${lowest[4]:,.0f})\n"
            f"Sell on {highest[1]} ({highest[2]}) at ${highest[0]:.8f} (liq: ${highest[4]:,.0f})\n"
            f"Spread: {diff_pct:.2f}%\n"
            f"Buy URL: {lowest[3]}\nSell URL: {highest[3]}"
        )
        send_telegram(msg)

for token in TOKEN_LIST:
    find_arbitrage(token)
