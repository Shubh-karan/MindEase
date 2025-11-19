import firebase_admin
from firebase_admin import credentials, firestore
import os

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
key_path = os.path.join(base_path, "firebase_key.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

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
            'password': password 
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