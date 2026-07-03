from flask import Flask, request
import requests
import json
import uuid
import os
import time
import base64
import urllib.parse
import subprocess

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
PANEL_URL = "http://78.17.146.181:2053"
API_TOKEN = "f4pFaBiFLSvKMzWolorwByeg4v4VncUDyH6qZOBCs1ZYzQIg"
INBOUND_ID = 1
SERVER_IP = "78.17.146.181"

# ===== ЗАПАСНАЯ ССЫЛКА =====
FALLBACK_LINK = "vless://5315968d-d0c4-4ac2-8cac-26db9e0123ba@78.17.146.181:8443/?type=ws&encryption=none&path=%2F&host=&security=none#RifleVPN"

db = {}

# Глобальные переменные для настроек
PANEL_SETTINGS = {
    "port": "8443",
    "path": "/",
    "host": "",
    "security": "none",
    "flow": "xtls-rprx-vision"
}

def restart_xray():
    """Перезапускает Xray процесс"""
    try:
        send_message(ADMIN_ID, "🔍 Перезапуск Xray...")
        
        # Останавливаем Xray
        send_message(ADMIN_ID, "🔍 Останавливаем Xray...")
        os.system("pkill -f xray-linux-amd64")
        time.sleep(2)
        
        # Запускаем Xray из /root
        send_message(ADMIN_ID, "🔍 Запускаем Xray из /root...")
        os.system("cd /root && nohup ./bin/xray-linux-amd64 -c bin/config.json > /dev/null 2>&1 &")
        time.sleep(3)
        
        # Проверяем запустился ли
        result = os.popen("pgrep -f xray-linux-amd64").read().strip()
        if result:
            send_message(ADMIN_ID, f"✅ Xray перезапущен! PID: {result}")
            return True
        else:
            send_message(ADMIN_ID, "❌ Xray не запустился! Пробую альтернативный способ...")
            
            # Альтернативный способ запуска
            os.system("cd / && nohup ./bin/xray-linux-amd64 -c bin/config.json > /dev/null 2>&1 &")
            time.sleep(3)
            
            result2 = os.popen("pgrep -f xray-linux-amd64").read().strip()
            if result2:
                send_message(ADMIN_ID, f"✅ Xray перезапущен! PID: {result2}")
                return True
            else:
                send_message(ADMIN_ID, "❌ Не удалось перезапустить Xray!")
                return False
            
    except Exception as e:
        send_message(ADMIN_ID, f"⚠️ Ошибка перезапуска Xray: {e}")
        return False

def get_panel_settings():
    """Получает настройки из панели"""
    global PANEL_SETTINGS
    try:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{PANEL_URL}/panel/api/inbounds/get/{INBOUND_ID}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "obj" in data:
                inbound = data["obj"]
                
                if "port" in inbound:
                    PANEL_SETTINGS["port"] = str(inbound["port"])
                
                stream_settings = inbound.get("streamSettings", {})
                if isinstance(stream_settings, str):
                    try:
                        stream_settings = json.loads(stream_settings)
                    except:
                        stream_settings = {}
                
                ws_settings = stream_settings.get("wsSettings", {})
                if isinstance(ws_settings, str):
                    try:
                        ws_settings = json.loads(ws_settings)
                    except:
                        ws_settings = {}
                
                if "path" in ws_settings:
                    PANEL_SETTINGS["path"] = ws_settings["path"]
                if "host" in ws_settings:
                    PANEL_SETTINGS["host"] = ws_settings["host"]
                
                if "security" in stream_settings:
                    PANEL_SETTINGS["security"] = stream_settings["security"]
                
                settings = inbound.get("settings", {})
                if isinstance(settings, str):
                    try:
                        settings = json.loads(settings)
                    except:
                        settings = {}
                
                if "clients" in settings and settings["clients"]:
                    first_client = settings["clients"][0]
                    if "flow" in first_client:
                        PANEL_SETTINGS["flow"] = first_client["flow"]
                
                send_message(ADMIN_ID, f"🔍 Настройки панели: {json.dumps(PANEL_SETTINGS)}")
                return True
    except Exception as e:
        send_message(ADMIN_ID, f"⚠️ Ошибка получения настроек: {e}")
    
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
    send_message(chat_id, "🌟 <b>Приятного использования!</b> 🌟\n\n🚀 RifLeVPN — твой ключ к свободе в сети")

def add_client_to_panel(user_id, uuid_str, expiry_seconds):
    try:
        send_message(ADMIN_ID, f"🔍 Добавление клиента в панель...")
        
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        get_response = requests.get(
            f"{PANEL_URL}/panel/api/inbounds/get/{INBOUND_ID}",
            headers=headers,
            timeout=10
        )
        
        if get_response.status_code != 200:
            return False, f"Ошибка получения Inbound: {get_response.status_code}"
        
        inbound_data = get_response.json()
        
        if "obj" in inbound_data:
            inbound = inbound_data["obj"]
        else:
            inbound = inbound_data
        
        send_message(ADMIN_ID, f"🔍 Inbound: {inbound.get('remark', 'unknown')}")
        
        clients = []
        
        if "settings" in inbound:
            settings = inbound["settings"]
            
            if isinstance(settings, str):
                try:
                    settings_obj = json.loads(settings)
                    if "clients" in settings_obj:
                        clients = settings_obj["clients"]
                except:
                    pass
            elif isinstance(settings, dict) and "clients" in settings:
                clients = settings["clients"]
        
        if not clients:
            clients = []
        
        send_message(ADMIN_ID, f"🔍 Найдено клиентов: {len(clients)}")
        
        new_client = {
            "id": uuid_str,
            "email": f"user_{user_id}",
            "limitIp": 1,
            "totalGB": 0,
            "expiryTime": int(expiry_seconds * 1000),
            "enable": True,
            "flow": PANEL_SETTINGS.get("flow", "xtls-rprx-vision"),
            "encryption": "none"
        }
        
        send_message(ADMIN_ID, f"🔍 Новый клиент: {json.dumps(new_client)}")
        
        clients.append(new_client)
        
        if "settings" in inbound:
            if isinstance(inbound["settings"], str):
                settings_obj = json.loads(inbound["settings"])
                settings_obj["clients"] = clients
                inbound["settings"] = json.dumps(settings_obj)
            elif isinstance(inbound["settings"], dict):
                inbound["settings"]["clients"] = clients
        else:
            inbound["settings"] = {
                "clients": clients,
                "decryption": "none",
                "fallbacks": []
            }
        
        update_response = requests.post(
            f"{PANEL_URL}/panel/api/inbounds/update/{INBOUND_ID}",
            json=inbound,
            headers=headers,
            timeout=10
        )
        
        send_message(ADMIN_ID, f"🔍 Статус обновления: {update_response.status_code}")
        
        if update_response.status_code == 200:
            try:
                result = update_response.json()
                if result.get("success") == True:
                    restart_xray()
                    return True, None
                else:
                    return False, f"Ошибка: {result.get('msg', 'unknown error')}"
            except:
                return False, "Ошибка парсинга ответа"
        else:
            return False, f"Ошибка: {update_response.status_code}"
            
    except Exception as e:
        send_message(ADMIN_ID, f"💥 Исключение: {e}")
        return False, str(e)

def generate_vless_link(uuid_str):
    port = PANEL_SETTINGS.get("port", "8443")
    path = PANEL_SETTINGS.get("path", "/")
    host = PANEL_SETTINGS.get("host", "")
    security = PANEL_SETTINGS.get("security", "none")
    
    if path and path != "/":
        encoded_path = urllib.parse.quote(path, safe='')
    else:
        encoded_path = "%2F" if path == "/" else ""
    
    if security == "tls" or security == "reality":
        link = f"vless://{uuid_str}@{SERVER_IP}:{port}/?type=ws&encryption=none&path={encoded_path}&host={host}&security={security}&sni={host or SERVER_IP}#RifleVPN"
    else:
        link = f"vless://{uuid_str}@{SERVER_IP}:{port}/?type=ws&encryption=none&path={encoded_path}&host={host}&security={security}#RifleVPN"
    
    send_message(ADMIN_ID, f"🔍 Сгенерирована ссылка: {link[:100]}...")
    return link

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
        response = requests.post(url, json=payload, timeout=10)
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
        current_time = int(time.time())
        expiry_seconds = current_time + 30 * 24 * 60 * 60
        
        success, error = add_client_to_panel(user_id, new_uuid, expiry_seconds)
        
        if success:
            key = generate_vless_link(new_uuid)
            db["user_" + user_id + "_key"] = key
            db["user_" + user_id + "_expiry"] = expiry_seconds
            expiry_date = time.strftime("%d.%m.%Y", time.localtime(expiry_seconds))
            send_key_message(int(user_id), key, expiry_date)
            send_message(ADMIN_ID, f"✅ Ключ выдан {user_id} до {expiry_date}")
        else:
            key = FALLBACK_LINK
            db["user_" + user_id + "_key"] = key
            db["user_" + user_id + "_expiry"] = expiry_seconds
            expiry_date = time.strftime("%d.%m.%Y", time.localtime(expiry_seconds))
            send_key_message(int(user_id), key, expiry_date)
            send_message(ADMIN_ID, f"⚠️ Использован запасной ключ для {user_id}")
    return "OK", 200

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return "OK", 200
    
    if "message" in data and data["message"].get("text") == "/start":
        get_panel_settings()
    
    if "pre_checkout_query" in data:
        query_id = data["pre_checkout_query"]["id"]
        answer_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerPreCheckoutQuery"
        requests.post(answer_url, json={"pre_checkout_query_id": query_id, "ok": True}, timeout=5)
        return "OK", 200
    
    if "message" in data:
        chat_id = str(data["message"]["chat"]["id"])
        text = data["message"].get("text", "")
        
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
                send_message(ADMIN_ID, f"✅ Ключ выдан {user_id} до {expiry_date}")
            else:
                key = FALLBACK_LINK
                db["user_" + user_id + "_key"] = key
                db["user_" + user_id + "_expiry"] = expiry_seconds
                expiry_date = time.strftime("%d.%m.%Y", time.localtime(expiry_seconds))
                send_key_message(int(user_id), key, expiry_date)
                send_message(ADMIN_ID, f"⚠️ Использован запасной ключ для {user_id}")
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
                    expiry_date = time.strftime("%d.%m.%Y", time.localtime(user_expiry))
                    send_message(chat_id, f"✅ Ключ активен!\n\n📅 Действует до: {expiry_date}\n⏳ Осталось дней: {days_left}")
            else:
                send_message(chat_id, "❌ У тебя нет активного ключа.")
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
                    send_message(chat_id, f"✅ Ключ выдан пользователю {user_id} до {expiry_date}")
                else:
                    key = FALLBACK_LINK
                    db["user_" + user_id + "_key"] = key
                    db["user_" + user_id + "_expiry"] = expiry_seconds
                    expiry_date = time.strftime("%d.%m.%Y", time.localtime(expiry_seconds))
                    send_key_message(int(user_id), key, expiry_date)
                    send_message(chat_id, f"⚠️ Использован запасной ключ для {user_id}")
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
                    expiry_date = time.strftime("%d.%m.%Y", time.localtime(user_expiry))
                    send_message(chat_id, f"✅ Ключ активен!\n\n📅 Действует до: {expiry_date}\n⏳ Осталось дней: {days_left}")
            else:
                send_message(chat_id, "❌ Нет активного ключа.")
        elif callback == "support":
            send_message(chat_id, "📞 Свяжись с администратором.")
    
    return "OK", 200

if __name__ == "__main__":
    get_panel_settings()
    app.run(host="0.0.0.0", port=10000)
