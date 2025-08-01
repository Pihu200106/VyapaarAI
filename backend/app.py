from flask import Flask, request, jsonify
import pandas as pd
from twilio.rest import Client
from biz_insights import generate_insights, generate_personalized_advice
import os
from dotenv import load_dotenv

app = Flask(__name__)

# ---------------------------------------
# 🔐 Load Twilio Credentials from .env
# ---------------------------------------
load_dotenv()  # Load .env file

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("FROM_NUMBER", "whatsapp:+14155238886")

if not TWILIO_SID or not TWILIO_AUTH:
    raise ValueError("❌ TWILIO_SID or TWILIO_AUTH_TOKEN is missing in .env file")

client = Client(TWILIO_SID, TWILIO_AUTH)

# ---------------------------------------
# ✅ Health Check
# ---------------------------------------
@app.route('/')
def home():
    return "✅ IntelliVyapaar Flask API is running."

# ---------------------------------------
# 📥 Upload CSV and return insights only
# ---------------------------------------
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    try:
        df = pd.read_csv(request.files['file'])
        insights = generate_insights(df)
        return jsonify(insights)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------
# 🧠 Upload CSV and return insights + suggestion
# ---------------------------------------
@app.route('/smart-insight', methods=['POST'])
def smart_insight():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    try:
        df = pd.read_csv(request.files['file'])
        insights = generate_insights(df)
        suggestion = generate_personalized_advice(insights)
        return jsonify({
            "insights": insights,
            "smart_suggestion": suggestion
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------
# 📲 Send WhatsApp Message via Twilio
# ---------------------------------------
@app.route('/send-whatsapp', methods=['POST'])
def send_whatsapp():
    data = request.json
    phone = data.get('phone')
    message = data.get('message')

    if not phone or not message:
        return jsonify({"status": "error", "message": "Missing phone or message"}), 400

    try:
        client.messages.create(
            body=message,
            from_=FROM_NUMBER,
            to=f"whatsapp:{phone}"
        )
        return jsonify({"status": "success", "message": "Message sent successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------------------------------
# 🚀 Run the Flask App
# ---------------------------------------
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

