import requests
import os
import threading
import sys
import json

def force_log(message):
    sys.stderr.write(f"EMAIL_LOG: {message}\n")
    sys.stderr.flush()

def _send_email_thread(user_email, user_name, latitude, longitude):
    api_key = os.environ.get("BREVO_API_KEY")
    sender_email = os.environ.get("MAIL_USERNAME")
    
    # Destination email
    receiver_email = "soleindianguy@gmail.com" 

    if not api_key or not sender_email:
        force_log("❌ CONFIG ERROR: Missing BREVO_API_KEY or MAIL_USERNAME.")
        return

    maps_link = f"http://maps.google.com/?q={latitude},{longitude}"
    
    # API Endpoint (HTTPS Port 443 - Allowed on Hugging Face)
    url = "https://api.brevo.com/v3/smtp/email"

    # JSON Payload
    payload = {
        "sender": {
            "name": "MindEase SOS",
            "email": sender_email
        },
        "to": [
            {
                "email": receiver_email,
                "name": "Emergency Contact"
            }
        ],
        "subject": f"🚨 SOS ALERT: {user_name} needs help!",
        "htmlContent": f"""
        <html>
            <body>
                <h1>EMERGENCY ALERT SYSTEM</h1>
                <p><strong>User:</strong> {user_name}</p>
                <p><strong>Email:</strong> {user_email}</p>
                <hr>
                <h3>Current Location</h3>
                <p><strong>Latitude:</strong> {latitude}</p>
                <p><strong>Longitude:</strong> {longitude}</p>
                <p><a href="{maps_link}" style="background-color: #d9534f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">OPEN LOCATION IN MAPS</a></p>
                <hr>
                <p>Please dispatch the nearest emergency response team immediately.</p>
            </body>
        </html>
        """
    }

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    try:
        force_log(f"🚀 Sending SOS via Brevo API (HTTPS)...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 201:
            force_log("✅ SUCCESS: SOS Email sent successfully via API!")
        else:
            force_log(f"❌ API FAILED: {response.status_code} - {response.text}")
            
    except Exception as e:
        force_log(f"❌ CONNECTION ERROR: {e}")

def send_sos_email(user_email, user_name, latitude, longitude):
    try:
        t = threading.Thread(target=_send_email_thread, args=(user_email, user_name, latitude, longitude))
        t.start()
        return True
    except Exception as e:
        force_log(f"Error starting thread: {e}")
        return False