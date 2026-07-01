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

# ===== 3X-UI (ID 1, ПОРТ 44920) =====
PANEL_URL = "http://78.17.216.68:2083/x7k9m3r4"
API_TOKEN = "Fcc2EioLUPAZ5WCWCJ7j5nrjuwOJiS7JZeNkUwHZ6cAod1Wx"
INBOUND_ID = 1
SERVER_IP = "78.17.216.68"
PORT = "44920"

db = {}

# ... (остальные функции без изменений, только generate_vless_link)

def generate_vless_link(uuid_str):
    # ТОЧНАЯ КОПИЯ ссылки, которая работала раньше
    return f"vless://{uuid_str}@{SERVER_IP}:{PORT}/?type=ws&security=none&encryption=none#RifLeVPN"

# ... (остальной код бота без изменений)
