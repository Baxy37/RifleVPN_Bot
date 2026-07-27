import requests

PANEL_URL = "http://78.17.146.181:2087/PcivqLmWUwUset3XAI/"
USERNAME = "admin"  # Ваш логин
PASSWORD = "admin"  # Ваш пароль

# Создаем сессию
session = requests.Session()

# Логинимся
print("🔍 Логинимся...")
login_data = {"username": USERNAME, "password": PASSWORD}
response = session.post(f"{PANEL_URL}login", json=login_data)
print(f"Статус логина: {response.status_code}")
print(f"Cookies: {session.cookies.get_dict()}")
print()

# Список возможных эндпоинтов для проверки
endpoints = [
    "panel/api/inbounds",
    "api/inbounds", 
    "inbounds",
    "xui/API/inbounds",
    "server/api/inbounds",
    "panel/inbounds",
    "api/v1/inbounds",
    "panel/api/v1/inbounds",
]

print("🔍 Проверяем эндпоинты...")
for endpoint in endpoints:
    url = f"{PANEL_URL}{endpoint}"
    try:
        response = session.get(url, timeout=5)
        status = response.status_code
        preview = response.text[:100] if response.text else "empty"
        print(f"📌 {endpoint} -> {status}")
        if status == 200:
            print(f"   ✅ РАБОТАЕТ! Ответ: {preview}...")
    except Exception as e:
        print(f"📌 {endpoint} -> Ошибка: {e}")
    print()

# Проверяем получение конкретного inbound
print("🔍 Проверяем получение inbound...")
for endpoint in [f"panel/api/inbounds/get/{INBOUND_ID}", f"api/inbounds/get/{INBOUND_ID}"]:
    url = f"{PANEL_URL}{endpoint}"
    try:
        response = session.get(url, timeout=5)
        print(f"📌 {endpoint} -> {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ РАБОТАЕТ! Ответ: {response.text[:200]}")
    except Exception as e:
        print(f"📌 {endpoint} -> Ошибка: {e}")
    print()

print("✅ Диагностика завершена!")
