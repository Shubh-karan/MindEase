from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from textblob import TextBlob
import os

# Import all necessary services
from services.firebase_service import (
    create_user, 
    verify_user, 
    get_user, 
    get_all_users, 
    save_chat_log, 
    get_sentiment_stats
)
from services.llm_service import get_llm_response, generate_zen_story

app = Flask(__name__)
app.secret_key = "Everthing is okay" 
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = verify_user(email, password)
        
        if user:
            session['user_email'] = user['email']
            session['user_name'] = user['name']
            session['role'] = user.get('role', 'user')
            session['history'] = [] 
            
            if session['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('chat'))
        else:
            return render_template('login.html', error="Invalid email or password")
            
    return render_template('login.html')

# --- UPDATED GOOGLE LOGIN ROUTE ---
@app.route('/google_login', methods=['POST'])
def google_login():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    
    # 1. Register if new
    create_user(name, email, "google_auth_user")
    
    # 2. Get real role from DB
    existing_user = get_user(email)
    role = 'user'
    if existing_user:
        role = existing_user.get('role', 'user')

    # 3. Set Session
    session['user_email'] = email
    session['user_name'] = name
    session['role'] = role
    session['history'] = []
    
    # 4. Decide where to send them
    if role == 'admin':
        target_url = url_for('admin_dashboard')
    else:
        target_url = url_for('chat')
    
    # Send the target URL back to the frontend
    return jsonify({'status': 'success', 'redirect_url': target_url})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        success = create_user(name, email, password)
        
        if success:
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error="User already exists")

    return render_template('register.html')

@app.route('/chat')
def chat():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session.get('user_name'))

@app.route('/chat/message', methods=['POST'])
def chat_message():
    data = request.get_json()
    user_message = data.get('message')
    user_email = session.get('user_email', 'anonymous') 
    
    blob = TextBlob(user_message)
    polarity = blob.sentiment.polarity 
    
    if polarity > 0.1: sentiment = "Positive"
    elif polarity < -0.1: sentiment = "Negative"
    else: sentiment = "Neutral"
        
    save_chat_log(user_email, user_message, sentiment)
    
    history = session.get('history', [])
    bot_reply = get_llm_response(user_message, history)
    
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": bot_reply})
    
    if len(history) > 10:
        history = history[-10:]
        
    session['history'] = history
    session.modified = True 
    
    return jsonify({'reply': bot_reply})

@app.route('/zen_mode', methods=['POST'])
def zen_mode():
    data = request.get_json()
    worry = data.get('worry')
    story = generate_zen_story(worry)
    return jsonify({'story': story})

@app.route('/admin')
def admin_dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        return "<h1>Access Denied</h1><p>You do not have permission to view this page.</p><a href='/chat'>Go to Chat</a>"
    
    all_users = get_all_users()
    total_users = len(all_users)
    mood_stats = get_sentiment_stats()
    
    return render_template('admin.html', users=all_users, count=total_users, mood_data=mood_stats)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)