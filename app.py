from flask import Flask, request
import requests
import json
import uuid
import os
import time
import base64

app = Flask(__name__)

BOT_TOKEN = "8809321059:AAH0NR4bzE8JFGjj2xKddJIej3H9NaJtpqc"
ADMIN_ID = "8551946505"

# ===== ЮKASSA =====
YOOKASSA_SHOP_ID = "1394514"
YOOKASSA_SECRET_KEY = "live_as3gtSKJqCrZffH2scrrjM8qg_CtjqrTAKvPH-6DXb8"
PRICE_RUB = 99

# ===== TELEGRAM STARS =====
PRICE_STARS = 99

# ===== 3X-UI =====
PANEL_URL = "http://78.17.216.68:2083/x7k9m3r4"
API_TOKEN = "Fcc2EioLUPAZ5WCWCJ7j5nrjuwOJiS7JZeNkUwHZ6cAod1Wx"
INBOUND_ID = 1
SERVER_IP = "78.17.216.68"
PORT = "44920"

db = {}

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        requests.post(url, json=data)
    except Exception as e:
        print(f"Ошибка: {e}")

def send_photo_file(chat_id, photo_path, caption):
    try:
        if not os.path.exists(photo_path):
            send_message(chat_id, caption)
            return
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': caption}
            requests.post(url, files=files, data=data)
    except Exception as e:
        print(f"Ошибка фото: {e}")
        send_message(chat_id, caption)

def send_key_message(chat_id, key):
    send_message(chat_id, "✅ <b>КЛЮЧ АКТИВИРОВАН!</b>\n\n📅 Подписка на 30 дней")
    send_message(chat_id, "🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑")
    send_message(chat_id, f"<code>{key}</code>")
    send_message(chat_id, "🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑")
    send_message(chat_id, "🌟 <b>Приятного использования!</b> 🌟\n\n🚀 RifLeVPN — твой ключ к свободе в сети")

def add_client_to_panel(user_id, uuid_str, expiry_seconds):
    try:
        send_message(ADMIN_ID, f"🔍 Попытка подключения к панели через API-токен")
        
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        client_data = {
            "id": uuid_str,
            "email": f"user_{user_id}",
            "limitIp": 1,
            "totalGB": 0,
            "expiryTime": expiry_seconds,
            "enable": True,
            "flow": "xtls-rprx-vision",
            "encryption": "none"
        }
        payload = {"id": INBOUND_ID, "settings": json.dumps({"clients": [client_data]})}
        
        add_response = requests.post(
            f"{PANEL_URL}/xray/inbound/addClient",
            json=payload,
            headers=headers
        )
        
        send_message(ADMIN_ID, f"🔍 Статус создания клиента: {add_response.status_code}")
        send_message(ADMIN_ID, f"🔍 Ответ создания: {add_response.text[:200]}")
        
        if add_response.status_code == 200:
            return True, None
        return False, f"Ошибка: {add_response.status_code}"
    except Exception as e:
        send_message(ADMIN_ID, f"💥 Исключение в панели: {e}")
        return False, str(e)

def generate_vless_link(uuid_str):
    return f"vless://{uuid_str}@{SERVER_IP}:{PORT}/?type=ws&encryption=none&path=%2F&host=&security=none#RifLeVPN"

def create_yookassa_payment(amount, description, user_id, chat_id):
    url = "https://api.yookassa.ru/v3/payments"
    auth_str = f"{YOOKASSA_SHOP_ID}:{YOOKASSA_SECRET_KEY}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_b64}",
        "Idempotence-Key": str(uuid.uuid4())
    }
    payload = {
        "amount": {"value": str(amount), "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": "https://t.me/RifLeVPN_bot"},
        "description": description,
        "metadata": {"user_id": str(user_id)},
        "capture": True
    }
    try:
        send_message(chat_id, "⏳ Создаю платёж в ЮKassa...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        send_message(ADMIN_ID, f"🔍 Статус ЮKassa: {response.status_code}")
        send_message(ADMIN_ID, f"📄 Ответ ЮKassa: {response.text[:300]}")
        
        if response.status_code in [200, 201]:
            return result["id"], result["confirmation"]["confirmation_url"]
        else:
            send_message(chat_id, "❌ Ошибка создания платежа. Попробуйте позже.")
            send_message(ADMIN_ID, f"❌ ЮKassa ошибка: {result}")
            return None, None
    except Exception as e:
        send_message(chat_id, "❌ Ошибка создания платежа. Попробуйте позже.")
        send_message(ADMIN_ID, f"💥 ЮKassa исключение: {e}")
        return None, None

def send_stars_invoice(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendInvoice"
    payload = {
        "chat_id": chat_id,
        "title": "Подписка RifLeVPN",
        "description": "VPN-доступ на 30 дней. Безлимитный трафик, высокая скорость.",
        "payload": "vpn_subscription",
        "provider_token": "",
        "currency": "XTR",
        "prices": [{"label": "Подписка на 30 дней", "amount": PRICE_STARS}],
        "start_parameter": "vpn_sub",
        "photo_url": "https://rifleman.pythonanywhere.com/banner.jpg",
        "photo_width": 1280,
        "photo_height": 720
    }
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        return result.get("ok", False)
    except Exception as e:
        print(f"Ошибка Stars: {e}")
        return False

@app.route("/yookassa-webhook", methods=["POST"])
def yookassa_webhook():
    data = request.get_json()
    if not data:
        return "OK", 200
    if data.get("event") == "payment.succeeded":
        user_id = data["object"]["metadata"]["user_id"]
        send_message(ADMIN_ID, f"✅ Оплата ЮKassa от {user_id}")
        new_uuid = str(uuid.uuid4())
        expiry = int(time.time() + 30 * 24 * 60 * 60)
        success, error = add_client_to_panel(user_id, new_uuid, expiry)
        if success:
            key = generate_vless_link(new_uuid)
            db["user_" + user_id + "_key"] = key
            db["user_" + user_id + "_expiry"] = expiry
            send_key_message(int(user_id), key)
            send_message(ADMIN_ID, f"✅ Ключ выдан {user_id}")
        else:
            send_message(ADMIN_ID, f"❌ Ошибка: {error}")
    return "OK", 200

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return "OK", 200
    if "pre_checkout_query" in data:
        query_id = data["pre_checkout_query"]["id"]
        answer_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerPreCheckoutQuery"
        requests.post(answer_url, json={"pre_checkout_query_id": query_id, "ok": True})
        return "OK", 200
    if "message" in data:
        chat_id = str(data["message"]["chat"]["id"])
        text = data["message"].get("text", "")
        if data["message"].get("successful_payment"):
            user_id = chat_id
            send_message(ADMIN_ID, f"✅ Оплата Stars от {user_id}")
            new_uuid = str(uuid.uuid4())
            expiry = int(time.time() + 30 * 24 * 60 * 60)
            success, error = add_client_to_panel(user_id, new_uuid, expiry)
            if success:
                key = generate_vless_link(new_uuid)
                db["user_" + user_id + "_key"] = key
                db["user_" + user_id + "_expiry"] = expiry
                send_key_message(int(user_id), key)
                send_message(ADMIN_ID, f"✅ Ключ выдан {user_id}")
            else:
                send_message(ADMIN_ID, f"❌ Ошибка: {error}")
                send_message(int(user_id), "❌ Ошибка активации. Обратитесь к администратору.")
            return "OK", 200
        if text == "/start":
            photo_path = os.path.join(os.path.dirname(__file__), "banner.jpg")
            caption = "🔐 Добро пожаловать в RifLeVPN!"
            send_photo_file(chat_id, photo_path, caption)
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": "⭐ Оплатить Stars (99⭐)", "callback_data": "buy_stars"}],
                    [{"text": "💳 Оплатить онлайн (99₽)", "callback_data": "buy_card"}],
                    [{"text": "📊 Проверить статус", "callback_data": "status"}],
                    [{"text": "📞 Поддержка", "callback_data": "support"}]
                ]
            }
            send_message(chat_id, """
🛡️ Защита на всех устройствах
🌐 Неограниченный трафик
⚡ Высокая скорость

💰 <b>Способы оплаты:</b>
⭐ Telegram Stars — 99 Stars (мгновенно)
💳 Банковская карта / СБП — 99₽ (онлайн)

📌 Выбери способ оплаты ниже:
            """, keyboard)
        elif text == "/status":
            user_key = db.get("user_" + chat_id + "_key")
            user_expiry = db.get("user_" + chat_id + "_expiry")
            if user_key and user_expiry:
                if time.time() > user_expiry:
                    send_message(chat_id, "⏰ Ключ истёк! Приобрети новый.")
                else:
                    days_left = int((user_expiry - time.time()) / 86400)
                    send_message(chat_id, f"✅ Ключ активен! Осталось {days_left} дней.")
            else:
                send_message(chat_id, "❌ У тебя нет активного ключа.")
        elif text.startswith("/give") and chat_id == ADMIN_ID:
            parts = text.split()
            if len(parts) == 2:
                user_id = parts[1]
                new_uuid = str(uuid.uuid4())
                expiry = int(time.time() + 30 * 24 * 60 * 60)
                success, error = add_client_to_panel(user_id, new_uuid, expiry)
                if success:
                    key = generate_vless_link(new_uuid)
                    db["user_" + user_id + "_key"] = key
                    db["user_" + user_id + "_expiry"] = expiry
                    send_key_message(int(user_id), key)
                    send_message(chat_id, f"✅ Ключ выдан пользователю {user_id}")
                else:
                    send_message(chat_id, f"❌ Ошибка: {error}")
            else:
                send_message(chat_id, "❌ Используй: /give ID")
        elif text == "/help" and chat_id == ADMIN_ID:
            send_message(chat_id, """
<b>👑 АДМИН-КОМАНДЫ:</b>

/give ID — выдать ключ пользователю вручную
            """)
        else:
            send_message(chat_id, "Используй: /start, /status")
    elif "callback_query" in data:
        chat_id = str(data["callback_query"]["message"]["chat"]["id"])
        callback = data["callback_query"]["data"]
        callback_id = data["callback_query"]["id"]
        try:
            answer_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
            requests.post(answer_url, json={"callback_query_id": callback_id}, timeout=5)
        except Exception as e:
            print(f"Ошибка answer: {e}")
        if callback == "buy_stars":
            success = send_stars_invoice(chat_id)
            if success:
                send_message(chat_id, "⭐ Счёт отправлен! Нажми на кнопку оплаты внизу.")
            else:
                send_message(chat_id, "❌ Ошибка создания счёта. Попробуйте позже.")
        elif callback == "buy_card":
            send_message(chat_id, "⏳ Создаю платёж в ЮKassa...")
            payment_id, payment_url = create_yookassa_payment(PRICE_RUB, "Подписка RifLeVPN на 30 дней", chat_id, chat_id)
            if payment_id and payment_url:
                db["payment_" + payment_id] = {"user_id": chat_id, "status": "pending"}
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "💳 Перейти к оплате", "url": payment_url}],
                        [{"text": "❌ Отмена", "callback_data": "cancel"}]
                    ]
                }
                send_message(chat_id, f"""
💳 <b>Платёж создан!</b>

💰 <b>Сумма:</b> {PRICE_RUB}₽
📅 <b>Подписка:</b> 30 дней

📌 Нажми на кнопку ниже, чтобы оплатить картой или через СБП.

<i>После оплаты ключ придёт автоматически!</i>
                """, keyboard)
            else:
                send_message(chat_id, "❌ Ошибка создания платежа. Попробуйте позже.")
        elif callback == "cancel":
            send_message(chat_id, "❌ Оплата отменена.")
        elif callback == "status":
            user_key = db.get("user_" + chat_id + "_key")
            user_expiry = db.get("user_" + chat_id + "_expiry")
            if user_key and user_expiry:
                if time.time() > user_expiry:
                    send_message(chat_id, "⏰ Ключ истёк!")
                else:
                    days_left = int((user_expiry - time.time()) / 86400)
                    send_message(chat_id, f"✅ Ключ активен! Осталось {days_left} дней.")
            else:
                send_message(chat_id, "❌ Нет активного ключа.")
        elif callback == "support":
            send_message(chat_id, "📞 Свяжись с администратором.")
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
