import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(backend_dir)

key_filename = "firebase_key.json"

if os.environ.get("FIREBASE_KEY_CONTENT"):
    print("Creating firebase_key.json from Environment Secret...")
    with open(os.path.join(root_dir, key_filename), "w") as f:
        f.write(os.environ.get("FIREBASE_KEY_CONTENT"))

key_path_backend = os.path.join(backend_dir, key_filename)
key_path_root = os.path.join(root_dir, key_filename)

if os.path.exists(key_path_backend):
    key_path = key_path_backend
elif os.path.exists(key_path_root):
    key_path = key_path_root
else:
    print(f"❌ ERROR: Could not find {key_filename}")
    key_path = None

if not firebase_admin._apps and key_path:
    try:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"⚠️ Firebase Init Error: {e}")

db = firestore.client()

def create_user(name, email, password):
    try:
        doc_ref = db.collection('users').document(email)
        doc = doc_ref.get()
        if doc.exists:
            return False 
        
        doc_ref.set({
            'name': name,
            'email': email,
            'password': password,
            'role': 'user',
            'settings': { 'language': 'en-US' }, # Default settings
            'last_gift_date': ''
        })
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def verify_user(email, password):
    try:
        doc_ref = db.collection('users').document(email)
        doc = doc_ref.get()
        if doc.exists:
            user_data = doc.to_dict()
            if user_data.get('password') == password:
                return user_data
        return None
    except Exception as e:
        print(f"Error verifying user: {e}")
        return None

def get_user(email):
    try:
        doc_ref = db.collection('users').document(email)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

# --- NEW: SETTINGS & GIFT PERSISTENCE ---
def update_user_settings(email, settings):
    try:
        db.collection('users').document(email).update({'settings': settings})
        return True
    except Exception as e:
        print(f"Error updating settings: {e}")
        return False

def check_daily_gift(email):
    """Returns True if user can claim a gift today"""
    try:
        doc = db.collection('users').document(email).get()
        if not doc.exists: return True
        
        data = doc.to_dict()
        last_date = data.get('last_gift_date', '')
        today = datetime.now().strftime('%Y-%m-%d')
        
        return last_date != today
    except:
        return True

def claim_daily_gift(email):
    """Updates the last claimed date to today"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        db.collection('users').document(email).update({'last_gift_date': today})
        return True
    except:
        return False
# ----------------------------------------

def get_all_users():
    try:
        users_ref = db.collection('users')
        docs = users_ref.stream()
        users_list = []
        for doc in docs:
            users_list.append(doc.to_dict())
        return users_list
    except Exception as e:
        return []

def save_chat_log(email, message, sentiment):
    try:
        db.collection('chat_logs').add({
            'email': email,
            'message': message,
            'sentiment': sentiment,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception as e:
        return False

def get_sentiment_stats():
    try:
        docs = db.collection('chat_logs').stream()
        stats = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
        for doc in docs:
            data = doc.to_dict()
            sent = data.get('sentiment', 'Neutral')
            if sent in stats: stats[sent] += 1
        return stats
    except Exception as e:
        return {'Positive': 0, 'Negative': 0, 'Neutral': 0}

def get_logs_by_date_range(start_date_str, end_date_str):
    try:
        start = datetime.strptime(start_date_str, "%Y-%m-%d")
        end = datetime.strptime(end_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        logs_ref = db.collection('chat_logs')
        query = logs_ref.where('timestamp', '>=', start).where('timestamp', '<=', end).stream()
        report_data = []
        for doc in query:
            data = doc.to_dict()
            if 'timestamp' in data and data['timestamp']:
                data['date'] = data['timestamp'].strftime("%Y-%m-%d %H:%M")
            else:
                data['date'] = "Unknown"
            report_data.append(data)
        return report_data
    except Exception as e:
        return []

def get_user_sentiment_history(email):
    try:
        logs_ref = db.collection('chat_logs')
        query = logs_ref.where('email', '==', email).stream()
        history = []
        for doc in query:
            data = doc.to_dict()
            if 'timestamp' in data and data['timestamp']:
                history.append({
                    'date': data['timestamp'].strftime('%Y-%m-%d'),
                    'sentiment': data.get('sentiment', 'Neutral'),
                    'message': data.get('message', '')
                })
        return history
    except Exception as e:
        return []