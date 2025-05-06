import requests
import os
import time

VOLUME_SPIKE_THRESHOLD = 300
PRICE_SPIKE_THRESHOLD = 20
LIQUIDITY_THRESHOLD = 10000
FDV_MAX = 5_000_000
MIN_SCORE = 3
SLEEP_INTERVAL = 300  # 5 minutes

def get_new_listings():
    url = "https://api.dexscreener.com/latest/dex/pairs"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("pairs", [])
    return []

def send_telegram(msg):
    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})

def analyze_pair(p):
    score = 0
    summary = []

    try:
        volume_change = float(p.get("volume24hChange", 0))
        if volume_change > VOLUME_SPIKE_THRESHOLD:
            score += 2
            summary.append(f"🔥 Volume spike: {volume_change:.1f}%")

        price_change = float(p.get("priceChange", {}).get("h15", 0))
        if price_change > PRICE_SPIKE_THRESHOLD:
            score += 2
            summary.append(f"🚀 Price surge: {price_change:.1f}%")

        liquidity = float(p.get("liquidity", {}).get("usd", 0))
        if liquidity > LIQUIDITY_THRESHOLD:
            score += 1
            summary.append(f"💧 Liquidity: ${liquidity:,.0f}")

        fdv = float(p.get("fdv", 0))
        if fdv < FDV_MAX:
            score += 1
            summary.append(f"📉 MCap: ${fdv:,.0f}")

        txns = p.get("txns", {}).get("h1", {})
        buys = int(txns.get("buys", 0))
        sells = int(txns.get("sells", 1))
        if buys / (buys + sells) > 0.85:
            score += 1
            summary.append(f"🟢 Buy ratio: {buys}/{sells}")

        age_ms = int(p.get("pairCreatedAt", 0))
        age_minutes = (time.time() * 1000 - age_ms) / 60000
        if age_minutes < 1440:
            score += 1
            summary.append("🍼 New token (<24h)")

        return score, summary
    except:
        return 0, []

def run_bot():
    seen_urls = set()
    while True:
        print("🔄 Checking new listings...")
        pairs = get_new_listings()
        for p in pairs:
            url = p.get("url")
            if url in seen_urls:
                continue
            score, summary = analyze_pair(p)
            if score >= MIN_SCORE:
                seen_urls.add(url)
                name = p["baseToken"]["name"]
                symbol = p["baseToken"]["symbol"]
                price = p["priceUsd"]
                chain = p["chainId"]
                dex = p["dexId"]
                msg = (
                    f"📈 *{name} ({symbol})* on *{chain}* [{dex}]\n"
                    f"Score: {score}/9\n"
                    + "\n".join(summary) +
                    f"\n\n💸 Price: ${price}\n🔗 [Buy here]({url})"
                )
                send_telegram(msg)
        time.sleep(SLEEP_INTERVAL)

run_bot()
