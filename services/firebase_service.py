import firebase_admin
from firebase_admin import credentials, firestore
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(backend_dir)

key_filename = "firebase_key.json"
key_path_backend = os.path.join(backend_dir, key_filename)
key_path_root = os.path.join(root_dir, key_filename)

if os.path.exists(key_path_backend):
    key_path = key_path_backend
    print(f"✅ Found key in backend folder: {key_path}")
elif os.path.exists(key_path_root):
    key_path = key_path_root
    print(f"✅ Found key in root folder: {key_path}")
else:
    print(f"❌ ERROR: Could not find {key_filename} in either:")
    print(f"   1. {key_path_backend}")
    print(f"   2. {key_path_root}")
    
if not firebase_admin._apps:
    if os.path.exists(key_path):
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    else:
        print("⚠️ Firebase NOT initialized due to missing key.")

db = firestore.client()

def create_user(name, email, password):
    """Creates a new user in Firestore"""
    try:
        doc_ref = db.collection('users').document(email)
        doc = doc_ref.get()
        if doc.exists:
            return False 
        
        doc_ref.set({
            'name': name,
            'email': email,
            'password': password,
            'role': 'user'
        })
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def verify_user(email, password):
    """Checks if email/password match"""
    try:
        doc_ref = db.collection('users').document(email)
        doc = doc_ref.get()
        
        if doc.exists:
            user_data = doc.to_dict()
            if user_data['password'] == password:
                return user_data
        return None
    except Exception as e:
        print(f"Error verifying user: {e}")
        return None

def get_user(email):
    """Fetches user data by email (useful for Google Login)"""
    try:
        doc_ref = db.collection('users').document(email)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def get_all_users():
    """Fetches all users for the admin dashboard"""
    try:
        users_ref = db.collection('users')
        docs = users_ref.stream()
        
        users_list = []
        for doc in docs:
            users_list.append(doc.to_dict())
        return users_list
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

def save_chat_log(email, message, sentiment):
    """Saves every chat message to a 'logs' collection for analytics"""
    try:
        db.collection('chat_logs').add({
            'email': email,
            'message': message,
            'sentiment': sentiment,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception as e:
        print(f"Error logging chat: {e}")
        return False

def get_sentiment_stats():
    """Counts positive, negative, and neutral messages for the dashboard"""
    try:
        docs = db.collection('chat_logs').stream()
        
        stats = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
        
        for doc in docs:
            data = doc.to_dict()
            sent = data.get('sentiment', 'Neutral')
            if sent in stats:
                stats[sent] += 1
                
        return stats
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    
from datetime import datetime

# ... (Existing code) ...

# --- NEW REPORT FUNCTION ---
def get_logs_by_date_range(start_date_str, end_date_str):
    """
    Fetches chat logs between two dates.
    Dates must be strings in 'YYYY-MM-DD' format.
    """
    try:
        # Convert strings to datetime objects
        start = datetime.strptime(start_date_str, "%Y-%m-%d")
        # For end date, we set time to 23:59:59 to include the whole day
        end = datetime.strptime(end_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        # Query Firestore
        logs_ref = db.collection('chat_logs')
        query = logs_ref.where('timestamp', '>=', start).where('timestamp', '<=', end).stream()

        report_data = []
        for doc in query:
            data = doc.to_dict()
            # Format the timestamp for the report
            if 'timestamp' in data and data['timestamp']:
                data['date'] = data['timestamp'].strftime("%Y-%m-%d %H:%M")
            else:
                data['date'] = "Unknown"
            report_data.append(data)
            
        return report_data
    except Exception as e:
        print(f"Error fetching report data: {e}")
        return []