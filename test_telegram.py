import requests

TELEGRAM_TOKEN = "8115132882:AAGMHQovlrHYKS7tYG6yLbLkEb1SSzooBTo"
TELEGRAM_CHAT_ID = "7685414166"

def send_test():
    msg = "✅ *Test successful!* This is a Telegram alert from your bot."
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    res = requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    })
    print("Telegram API response:", res.text)

send_test()
