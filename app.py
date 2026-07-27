from flask import Flask, request
import requests
import json
import uuid
import os
import time
import base64

app = Flask(__name__)

# ===== ТОКЕН БОТА =====
BOT_TOKEN = "8909921481:AAGl9552Mbx3O0Vniw_My-UC9fLnCvffIFs"
ADMIN_ID = "8551946505"

# ===== ЮKASSA =====
YOOKASSA_SHOP_ID = "1394514"
YOOKASSA_SECRET_KEY = "live_as3gtSKJqCrZffH2scrrjM8qg_CtjqrTAKvPH-6DXb8"
PRICE_RUB = 99

# ===== TELEGRAM STARS =====
PRICE_STARS = 99

# ===== 3X-UI =====
PANEL_URL = "http://78.17.146.181:2087/PcivqLmWUwUset3XAI/"
PANEL_USERNAME = "admin"  # ВАШ ЛОГИН
PANEL_PASSWORD = "admin"  # ВАШ ПАРОЛЬ
INBOUND_ID = 1
SERVER_IP = "78.17.146.181"
SERVER_PORT = 8443

# Параметры REALITY
REALITY_SETTINGS = {
    "public_key": "0e9hJ0HmBGPkdRVTSrWd1r2eXPH5YRKDNfKY1FKvRCY",
    "short_id": "d776282dcf1f",
    "sni": "apple.com",
    "fingerprint": "chrome",
    "flow": "xtls-rprx-vision"
}

db = {}
session = None

LINK_TEMPLATE = "vless://{uuid}@{server_ip}:{server_port}?encryption=none&security=reality&sni={sni}&fp={fingerprint}&pbk={public_key}&sid={short_id}&type=tcp&flow={flow}#RifleVPN"

def login_to_panel():
    """Логин в панель 3x-ui 3.5.0"""
    global session
    try:
        send_message(ADMIN_ID, "🔍 Авторизация в панели...")
        
        # Создаём сессию
        session = requests.Session()
        
        # Сначала получаем CSRF токен (для версии 3.5.0)
        try:
            csrf_response = session.get(f"{PANEL_URL}login", timeout=10)
            send_message(ADMIN_ID, f"🔍 CSRF статус: {csrf_response.status_code}")
        except:
            pass
        
        # Данные для логина
        login_data = {
            "username": PANEL_USERNAME,
            "password": PANEL_PASSWORD
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Пробуем логин через /login
        response = session.post(
            f"{PANEL_URL}login",
            json=login_data,
            headers=headers,
            timeout=10
        )
        
        send_message(ADMIN_ID, f"🔍 Статус логина: {response.status_code}")
        send_message(ADMIN_ID, f"🔍 Cookies: {session.cookies.get_dict()}")
        
        if response.status_code == 200:
            send_message(ADMIN_ID, "✅ Успешный вход в панель!")
            
            # Проверяем API
            return test_api()
        else:
            send_message(ADMIN_ID, f"❌ Ошибка логина: {response.status_code}")
            send_message(ADMIN_ID, f"❌ Ответ: {response.text[:200]}")
            return False
            
    except Exception as e:
        send_message(ADMIN_ID, f"❌ Ошибка логина: {e}")
        return False

def test_api():
    """Проверяет доступ к API"""
    global session
    try:
        response = session.get(
            f"{PANEL_URL}panel/api/inbounds",
            timeout=10
        )
        
        send_message(ADMIN_ID, f"🔍 Проверка API: {response.status_code}")
        
        if response.status_code == 200:
            send_message(ADMIN_ID, "✅ API доступно!")
            return True
        else:
            send_message(ADMIN_ID, f"❌ API недоступно: {response.status_code}")
            return False
            
    except Exception as e:
        send_message(ADMIN_ID, f"❌ Ошибка проверки API: {e}")
        return False

def restart_xray():
    """Перезапускает Xray"""
    global session
    try:
        send_message(ADMIN_ID, "🔄 Перезапуск Xray...")
        
        response = session.post(
            f"{PANEL_URL}panel/api/inbounds/restart",
            timeout=10
        )
        
        if response.status_code == 200:
            send_message(ADMIN_ID, "✅ Xray перезапущен!")
            return True
        else:
            send_message(ADMIN_ID, f"⚠️ Ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        send_message(ADMIN_ID, f"⚠️ Ошибка: {e}")
        return False

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        requests.post(url, json=data, timeout=10)
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
            requests.post(url, files=files, data=data, timeout=10)
    except Exception as e:
        print(f"Ошибка фото: {e}")
        send_message(chat_id, caption)

def send_key_message(chat_id, key, expiry_date):
    send_message(chat_id, "✅ <b>КЛЮЧ АКТИВИРОВАН!</b>\n\n📅 Подписка на 30 дней")
    send_message(chat_id, f"📅 Действует до: <b>{expiry_date}</b>")
    send_message(chat_id, "🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑")
    send_message(chat_id, f"<code>{key}</code>")
    send_message(chat_id, "🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑🔑")
    send_message(chat_id, "🌟 <b>Приятного использования!</b> 🌟\n\n🚀 RifLeVPN")

def add_client_to_panel(user_id, uuid_str, expiry_seconds):
    """Добавляет клиента в панель 3x-ui"""
    global session
    try:
        send_message(ADMIN_ID, f"🔍 Добавление клиента...")
        
        # Проверяем сессию
        if not session:
            if not login_to_panel():
                return False, "Не удалось авторизоваться в панели"
        
        client_data = {
            "id": uuid_str,
            "email": f"user_{user_id}",
            "limitIp": 1,
            "totalGB": 0,
            "expiryTime": int(expiry_seconds * 1000),
            "enable": True
        }
        
        # Пробуем добавить клиента
        response = session.post(
            f"{PANEL_URL}panel/api/inbounds/addClient",
            json={
                "inboundId": INBOUND_ID,
                "clients": [client_data]
            },
            timeout=10
        )
        
        send_message(ADMIN_ID, f"🔍 Статус addClient: {response.status_code}")
        send_message(ADMIN_ID, f"🔍 Ответ: {response.text[:200]}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success") == True:
                restart_xray()
                return True, None
        
        # Если не сработало, пробуем через update
        return add_client_via_update(user_id, uuid_str, expiry_seconds)
        
    except Exception as e:
        send_message(ADMIN_ID, f"💥 Ошибка: {e}")
        return False, str(e)

def add_client_via_update(user_id, uuid_str, expiry_seconds):
    """Альтернативный метод через update"""
    global session
    try:
        send_message(ADMIN_ID, "🔍 Альтернативный метод...")
        
        # Получаем inbound
        get_response = session.get(
            f"{PANEL_URL}panel/api/inbounds/get/{INBOUND_ID}",
            timeout=10
        )
        
        send_message(ADMIN_ID, f"🔍 Статус GET: {get_response.status_code}")
        
        if get_response.status_code != 200:
            return False, f"Ошибка получения inbound: {get_response.status_code}"
        
        data = get_response.json()
        inbound = data.get("obj", data)
        
        # Добавляем клиента
        settings = inbound.get("settings", {})
        if isinstance(settings, str):
            settings = json.loads(settings)
        
        clients = settings.get("clients", [])
        clients.append({
            "id": uuid_str,
            "email": f"user_{user_id}",
            "limitIp": 1,
            "totalGB": 0,
            "expiryTime": int(expiry_seconds * 1000),
            "enable": True
        })
        
        settings["clients"] = clients
        inbound["settings"] = settings
        
        # Обновляем
        update_response = session.post(
            f"{PANEL_URL}panel/api/inbounds/update/{INBOUND_ID}",
            json=inbound,
            timeout=10
        )
        
        send_message(ADMIN_ID, f"🔍 Статус UPDATE: {update_response.status_code}")
        
        if update_response.status_code == 200:
            result = update_response.json()
            if result.get("success") == True:
                restart_xray()
                return True, None
        
        return False, "Не удалось добавить клиента"
        
    except Exception as e:
        return False, str(e)

def generate_vless_link(uuid_str):
    """Генерирует ссылку VLESS для Reality"""
    return LINK_TEMPLATE.format(
        uuid=uuid_str,
        server_ip=SERVER_IP,
        server_port=SERVER_PORT,
        sni=REALITY_SETTINGS["sni"],
        fingerprint=REALITY_SETTINGS["fingerprint"],
        public_key=REALITY_SETTINGS["public_key"],
        short_id=REALITY_SETTINGS["short_id"],
        flow=REALITY_SETTINGS["flow"]
    )

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
        send_message(chat_id, "⏳ Создаю платёж...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if response.status_code in [200, 201]:
            return result["id"], result["confirmation"]["confirmation_url"]
        else:
            send_message(chat_id, "❌ Ошибка создания платежа")
            return None, None
    except Exception as e:
        send_message(chat_id, "❌ Ошибка")
        return None, None

def send_stars_invoice(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendInvoice"
    payload = {
        "chat_id": chat_id,
        "title": "Подписка RifLeVPN",
        "description": "VPN-доступ на 30 дней. VLESS+Reality",
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
        response = requests.post(url, json=payload, timeout=10)
        return response.json().get("ok", False)
    except:
        return False

@app.route("/yookassa-webhook", methods=["POST"])
def yookassa_webhook():
    data = request.get_json()
    if not data:
        return "OK", 200
    if data.get("event") == "payment.succeeded":
        user_id = data["object"]["metadata"]["user_id"]
        send_message(ADMIN_ID, f"✅ Оплата от {user_id}")
        
        new_uuid = str(uuid.uuid4())
        current_time = int(time.time())
        expiry_seconds = current_time + 30 * 24 * 60 * 60
        
        success, error = add_client_to_panel(user_id, new_uuid, expiry_seconds)
        
        if success:
            key = generate_vless_link(new_uuid)
            db["user_" + user_id + "_key"] = key
            db["user_" + user_id + "_expiry"] = expiry_seconds
            expiry_date = time.strftime("%d.%m.%Y", time.localtime(expiry_seconds))
            send_key_message(int(user_id), key, expiry_date)
        else:
            send_message(ADMIN_ID, f"❌ Ошибка: {error}")
            send_message(int(user_id), "❌ Ошибка активации")
    return "OK", 200

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return "OK", 200
    
    if "pre_checkout_query" in data:
        query_id = data["pre_checkout_query"]["id"]
        answer_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerPreCheckoutQuery"
        requests.post(answer_url, json={"pre_checkout_query_id": query_id, "ok": True}, timeout=5)
        return "OK", 200
    
    if "message" in data:
        chat_id = str(data["message"]["chat"]["id"])
        text = data["message"].get("text", "")
        
        if text and not text.startswith("/"):
            return "OK", 200
        
        if data["message"].get("successful_payment"):
            user_id = chat_id
            send_message(ADMIN_ID, f"✅ Оплата Stars от {user_id}")
            
            new_uuid = str(uuid.uuid4())
            current_time = int(time.time())
            expiry_seconds = current_time + 30 * 24 * 60 * 60
            
            success, error = add_client_to_panel(user_id, new_uuid, expiry_seconds)
            
            if success:
                key = generate_vless_link(new_uuid)
                db["user_" + user_id + "_key"] = key
                db["user_" + user_id + "_expiry"] = expiry_seconds
                expiry_date = time.strftime("%d.%m.%Y", time.localtime(expiry_seconds))
                send_key_message(int(user_id), key, expiry_date)
                send_message(ADMIN_ID, f"✅ Ключ выдан {user_id}")
            else:
                send_message(ADMIN_ID, f"❌ Ошибка: {error}")
                send_message(int(user_id), "❌ Ошибка активации")
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
🛡️ <b>RifLeVPN — твой ключ к свободе в сети</b>

🌐 Неограниченный трафик
⚡ Высокая скорость
🔐 Протокол: VLESS + Reality

💰 <b>Способы оплаты:</b>
⭐ Telegram Stars — 99 Stars
💳 Банковская карта — 99₽

📌 Выбери способ оплаты:
            """, keyboard)
        
        elif text == "/status":
            user_key = db.get("user_" + chat_id + "_key")
            user_expiry = db.get("user_" + chat_id + "_expiry")
            if user_key and user_expiry:
                if time.time() > user_expiry:
                    send_message(chat_id, "⏰ Ключ истёк!")
                else:
                    days_left = int((user_expiry - time.time()) / 86400)
                    expiry_date = time.strftime("%d.%m.%Y", time.localtime(user_expiry))
                    send_message(chat_id, f"✅ Ключ активен!\n📅 До: {expiry_date}\n⏳ Осталось: {days_left} дней")
            else:
                send_message(chat_id, "❌ Нет активного ключа.")
        
        elif text.startswith("/give") and chat_id == ADMIN_ID:
            parts = text.split()
            if len(parts) == 2:
                user_id = parts[1]
                new_uuid = str(uuid.uuid4())
                current_time = int(time.time())
                expiry_seconds = current_time + 30 * 24 * 60 * 60
                success, error = add_client_to_panel(user_id, new_uuid, expiry_seconds)
                if success:
                    key = generate_vless_link(new_uuid)
                    db["user_" + user_id + "_key"] = key
                    db["user_" + user_id + "_expiry"] = expiry_seconds
                    expiry_date = time.strftime("%d.%m.%Y", time.localtime(expiry_seconds))
                    send_key_message(int(user_id), key, expiry_date)
                    send_message(chat_id, f"✅ Ключ выдан {user_id}")
                else:
                    send_message(chat_id, f"❌ Ошибка: {error}")
            else:
                send_message(chat_id, "❌ Используй: /give ID")
        
        elif text == "/help" and chat_id == ADMIN_ID:
            send_message(chat_id, """
<b>👑 АДМИН-КОМАНДЫ:</b>
/give ID — выдать ключ
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
        except:
            pass
        
        if callback == "buy_stars":
            if send_stars_invoice(chat_id):
                send_message(chat_id, "⭐ Счёт отправлен!")
            else:
                send_message(chat_id, "❌ Ошибка")
        
        elif callback == "buy_card":
            payment_id, payment_url = create_yookassa_payment(PRICE_RUB, "Подписка RifLeVPN", chat_id, chat_id)
            if payment_id and payment_url:
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "💳 Перейти к оплате", "url": payment_url}],
                        [{"text": "❌ Отмена", "callback_data": "cancel"}]
                    ]
                }
                send_message(chat_id, f"""
💳 <b>Платёж создан!</b>
💰 Сумма: {PRICE_RUB}₽
📅 Подписка: 30 дней

<i>После оплаты ключ придёт автоматически!</i>
                """, keyboard)
            else:
                send_message(chat_id, "❌ Ошибка создания платежа")
        
        elif callback == "cancel":
            send_message(chat_id, "❌ Отменено")
        
        elif callback == "status":
            user_key = db.get("user_" + chat_id + "_key")
            user_expiry = db.get("user_" + chat_id + "_expiry")
            if user_key and user_expiry:
                if time.time() > user_expiry:
                    send_message(chat_id, "⏰ Ключ истёк!")
                else:
                    days_left = int((user_expiry - time.time()) / 86400)
                    expiry_date = time.strftime("%d.%m.%Y", time.localtime(user_expiry))
                    send_message(chat_id, f"✅ Ключ активен!\n📅 До: {expiry_date}\n⏳ Осталось: {days_left} дней")
            else:
                send_message(chat_id, "❌ Нет активного ключа.")
        
        elif callback == "support":
            send_message(chat_id, "📞 Админ: https://t.me/RifleMan_Admin")
    
    return "OK", 200

if __name__ == "__main__":
    # Пробуем авторизоваться при запуске
    print("🔍 Авторизация в панели 3x-ui 3.5.0...")
    login_to_panel()
    app.run(host="0.0.0.0", port=10000)
