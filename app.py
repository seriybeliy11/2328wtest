import json
import hmac
import hashlib
import base64
import httpx
from flask import Flask, request, jsonify

app = Flask(__name__)

PROJECT_UUID = os.getenv("PROJECT_UUID")
API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def api_sign(body: str, api_key: str) -> str:
    b64 = base64.b64encode(body.encode())
    return hmac.new(api_key.encode(), b64, hashlib.sha256).hexdigest()


@app.route("/", methods=["POST"])
def webhook():
    update = request.json
    chat_id = update["message"]["chat"]["id"]

    if "/start" in update["message"].get("text"):
        data = {
            "order_id": f"INV_{chat_id}_{update['message']['date']}",
            "amount": "5.00000000",
            "currency": "USDT"
        }

        body = json.dumps(data, separators=(',', ':'))
        sign = api_sign(body, API_KEY)

        headers = {
            "Content-Type": "application/json",
            "project": PROJECT_UUID,
            "sign": sign
        }

        resp = httpx.post(
            "https://api.2328.io/v1/payment",
            content=body.encode(),
            headers=headers
        ).json()

        link = resp["result"]["tg_deeplink"]
        httpx.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            params={"chat_id": chat_id, "text": link}
        )

    return jsonify(ok=True)
