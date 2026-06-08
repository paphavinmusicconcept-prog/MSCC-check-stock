# ============================================================
# bot.py — LINE Bot รับข้อความ ส่งไป Local API
# Deploy บน server ภายนอก (เช่น Render, Railway, หรือ VPS)
# ============================================================

from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
import requests
from stock_cleaning import normalize_product

app = Flask(__name__)

# ── ตั้งค่า LINE ────────────────────────────────────────────
LINE_CHANNEL_SECRET = "ใส่ Channel Secret จาก LINE Developers"
LINE_CHANNEL_TOKEN  = "ใส่ Channel Access Token จาก LINE Developers"

# ── URL ของ Local API (ได้จาก ngrok) ───────────────────────
LOCAL_API_URL = "https://xxxx-xxxx.ngrok-free.app/stock"
# ตัวอย่าง: "https://abcd-1234.ngrok-free.app/stock"

configuration = Configuration(access_token=LINE_CHANNEL_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip()

    # ── ตรวจรูปแบบคำสั่ง "ชื่อสินค้า - SKU" ──────────────
    if " - " not in text:
        reply = (
            "รูปแบบไม่ถูกต้อง\n"
            "กรุณาพิมพ์: ชื่อสินค้า - SKU\n"
            "ตัวอย่าง: แอปเปิ้ล - SKU001"
        )
        send_reply(event.reply_token, reply)
        return

    parts = text.split(" - ", 1)
    sku = parts[1].strip()

    # ── ดึงสต็อกจาก Local API ──────────────────────────────
    try:
        resp = requests.get(LOCAL_API_URL, params={"sku": sku}, timeout=5)
        result = resp.json()

        if result.get("found"):
            d = result["data"]
            product = normalize_product(
                d.get("sku"),
                d.get("name"),
                d.get("qty", d.get("quantity")),
                d.get("unit"),
                d.get("warehouse"),
            )
            reply = (
                f"สินค้า: {product.get('name') or '-'}\n"
                f"SKU: {product.get('sku') or '-'}\n"
                f"คงเหลือ: {product.get('qty', 0)} {product.get('unit') or 'ตัว'}"
            )
        else:
            reply = f"ไม่พบสินค้า SKU: {sku}"

    except Exception:
        reply = "เกิดข้อผิดพลาด ไม่สามารถเชื่อมต่อระบบได้"

    send_reply(event.reply_token, reply)


def send_reply(reply_token, text):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)]
            )
        )


if __name__ == "__main__":
    app.run(port=8000)
