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
API_TOKEN = "4KphmtzMl3wsRMyGOaYSR4H7KoUYaDem7phNc1Nx2Qor0kRN"
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

# Хранилище ключей пользователей
user_keys = {}

LINK_TEMPLATE = "vless://{uuid}@{server_ip}:{server_port}?encryption=none&security=reality&sni={sni}&fp={fingerprint}&pbk={public_key}&sid={short_id}&type=tcp&flow={flow}#RifleVPN"

def make_api_request(method, endpoint, data=None):
    """Универсальная функция для запросов к API"""
    try:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = f"{PANEL_URL}{endpoint}"
        
        send_message(ADMIN_ID, f"🔍 Запрос: {method} {endpoint}")
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=15)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=15)
        else:
            return None, "Unknown method"
        
        send_message(ADMIN_ID, f"🔍 Статус: {response.status_code}")
        
        if response.status_code == 200:
            try:
                return response.json(), None
            except:
                return {"success": True}, None
        else:
            return None, f"HTTP {response.status_code}: {response.text[:200]}"
        
    except Exception as e:
        return None, str(e)

def add_client_to_panel(user_id, uuid_str, expiry_seconds):
    """Добавляет клиента через /panel/api/clients/add (правильный эндпоинт)"""
    try:
        send_message(ADMIN_ID, f"🔍 Добавление клиента через clients/add...")
        
        # Данные клиента для /panel/api/clients/add
        client_data = {
            "email": f"user_{user_id}",
            "inboundIds": [INBOUND_ID],
            "enable": True,
            "expiryTime": int(expiry_seconds * 1000),
            "totalGB": 0,  # 0 = безлимит
            "limitIp": 1
        }
        
        send_message(ADMIN_ID, f"🔍 Данные: {json.dumps(client_data)}")
        
        # Используем правильный эндпоинт из документации
        result, error = make_api_request(
            "POST",
            "panel/api/clients/add",
            client_data
        )
        
        if error:
            send_message(ADMIN_ID, f"❌ Ошибка clients/add: {error}")
            # Пробуем альтернативный метод
            return add_client_via_update(user_id, uuid_str, expiry_seconds)
        
        send_message(ADMIN_ID, f"✅ Клиент добавлен через clients/add!")
        
        # Перезапускаем Xray
        make_api_request("POST", "panel/api/server/restartXrayService")
        
        return True, uuid_str
        
    except Exception as e:
        send_message(ADMIN_ID, f"💥 Ошибка: {e}")
        return False, None

def add_client_via_update(user_id, uuid_str, expiry_seconds):
    """Запасной метод через обновление inbound"""
    try:
        send_message(ADMIN_ID, "🔍 Запасной метод через update...")
        
        # Получаем текущий inbound
        result, error = make_api_request("GET", f"panel/api/inbounds/get/{INBOUND_ID}")
        
        if error:
            return False, None
            
        inbound = result.get("obj", result)
        
        # Получаем клиентов
        settings = inbound.get("settings", {})
        if isinstance(settings, str):
            settings = json.loads(settings)
        
        clients = settings.get("clients", [])
        
        # Добавляем нового клиента
        clients.append({
            "id": uuid_str,
            "email": f"user_{user_id}",
            "limitIp": 1,
            "totalGB": 0,
            "expiryTime": int(expiry_seconds * 1000),
            "enable": True,
            "flow": REALITY_SETTINGS["flow"]
        })
        
        settings["clients"] = clients
        inbound["settings"] = settings
        
        # Обновляем inbound
        result, error = make_api_request(
            "POST",
            f"panel/api/inbounds/update/{INBOUND_ID}",
            inbound
        )
        
        if error:
            return False, None
            
        send_message(ADMIN_ID, "✅ Клиент добавлен через update!")
        
        # Перезапускаем Xray
        make_api_request("POST", "panel/api/server/restartXrayService")
        
        return True, uuid_str
        
    except Exception as e:
        send_message(ADMIN_ID, f"💥 Ошибка: {e}")
        return False, None

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

def process_payment(user_id):
    """Обработка оплаты - создание ключа"""
    try:
        # Генерируем новый UUID
        new_uuid = str(uuid.uuid4())
        current_time = int(time.time())
        expiry_seconds = current_time + 30 * 24 * 60 * 60
        
        send_message(ADMIN_ID, f"🔍 Создание ключа для {user_id}")
        send_message(ADMIN_ID, f"🔍 UUID: {new_uuid}")
        
        # Добавляем клиента в панель
        success, result = add_client_to_panel(user_id, new_uuid, expiry_seconds)
        
        if success:
            # Генерируем ссылку
            key = generate_vless_link(new_uuid)
            
            # Сохраняем в память
            user_keys[user_id] = {
                "key": key,
                "expiry": expiry_seconds,
                "uuid": new_uuid
            }
            
            # Отправляем пользователю
            expiry_date = time.strftime("%d.%m.%Y", time.localtime(expiry_seconds))
            send_key_message(int(user_id), key, expiry_date)
            send_message(ADMIN_ID, f"✅ Ключ выдан {user_id}")
            return True
        else:
            send_message(ADMIN_ID, f"❌ Ошибка создания клиента для {user_id}")
            send_message(int(user_id), "❌ Ошибка активации. Обратитесь к администратору.")
            return False
            
    except Exception as e:
        send_message(ADMIN_ID, f"💥 Ошибка: {e}")
        return False

# Остальные функции (create_yookassa_payment, send_stars_invoice, webhook) остаются без изменений
# ... (код из предыдущего сообщения)

if __name__ == "__main__":
    print("🚀 БОТ ЗАПУЩЕН!")
    print(f"🔗 Панель: {PANEL_URL}")
    print(f"📋 Inbound ID: {INBOUND_ID}")
    app.run(host="0.0.0.0", port=10000)
