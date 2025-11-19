import firebase_admin
from firebase_admin import credentials, firestore
import os

# --- ROBUST PATH FINDING ---
# 1. Get the folder where THIS file is (backend/services)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 2. Get the backend folder (parent of services)
backend_dir = os.path.dirname(current_dir)
# 3. Get the main project folder (parent of backend)
root_dir = os.path.dirname(backend_dir)

# Try finding the key in 'backend' first, then 'root'
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
    # Allow it to fail naturally below if path is wrong

# Initialize Firebase only once
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