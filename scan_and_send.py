# === Standar Library ===
import os
import csv 
import smtplib
import datetime

# === Third-party library ===
import requests
from ping3 import ping 
from email.message import EmailMessage
from dotenv import load_dotenv
import paramiko

load_dotenv("secrets.env")

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
output_file = "scan_log.csv"

# 1️⃣ SCANARE Apple (telefoane + ceasuri)
print("📦 Scanare pornită. Apasă Enter fără cod pentru a trimite datele.")
with open(output_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    while True:
        code = input("Scan Apple: ").strip()
        if code == "":
            break
        timestamp = datetime.datetime.now()
        writer.writerow([code, timestamp])
        print(f"✅ Salvat: {code} | {timestamp}")
        

# 2️⃣ PING la device-uri (ex: scanner, router, IoT)
print("\n🌐 Ping la device-uri:")
with open("devices.txt") as f:
    for ip in f:
        ip = ip.strip()
        response = ping(ip, timeout=1)
        status = "✅ OK" if response else "❌ FAIL"
        print(f"{ip}: {status}")

# 3️⃣ SSH la device (dacă ai switch sau Raspberry Pi etc.)
print("\n🔐 SSH la device-uri:")
ssh_ip = os.getenv("SSH_IP")
ssh_user = os.getenv("SSH_USER")
ssh_pass = os.getenv("SSH_PASS")

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ssh_ip, username=ssh_user, password=ssh_pass)
    stdin, stdout, stderr = client.exec_command("uptime")
    print("SSH Output:", stdout.read().decode())
    client.close()
except Exception as e:
    print("SSH failed:", e)

# 4️⃣ API extern – simulăm că trimitem scanările
print("\n📡 Trimitere date la API extern:")
try:
    with open(output_file, 'r') as f:
        content = f.read()
    response = requests.post("https://httpbin.org/post", data={'scan_data': content})
    print("API response:", response.status_code)
except Exception as e:
    print("API call failed:", e)

# 5️⃣ EMAIL cu scan_log.csv atașat
print("\n📧 Trimitere Email:")
msg = EmailMessage()
msg["Subject"] = "📦 Raport Apple Scanare + Rețea"
msg["From"] = EMAIL_SENDER
msg["To"] = EMAIL_RECEIVER
msg.set_content("Salut, atașez scanările Apple și status rețea.")

with open(output_file, "rb") as f:
    msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename=output_file)

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
    smtp.send_message(msg)

print("✅ Email trimis cu succes!")
