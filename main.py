import os
import requests
from flask import Flask, request
from google import genai

app = Flask(__name__)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

# İstemciyi küresel (global) olarak tek kez başlat, bellek tasarrufu sağla
client = genai.Client(api_key=GEMINI_KEY)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram gonderim hatasi: {e}")

@app.route("/telegram", methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        incoming_msg = data["message"]["text"]
        
        try:
            # Doğrudan hafif istek yap
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=incoming_msg,
            )
            reply = response.text if response.text else "Yanıt üretilemedi."
        except Exception as e:
            reply = f"Ajan Hatasi: {str(e)}"
            print(f"Gemini hatasi: {e}")
            
        send_telegram_message(chat_id, reply)
        
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
