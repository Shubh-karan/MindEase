from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from services.firebase_service import create_user, verify_user
from services.llm_service import get_llm_response  # <--- New Import
import os

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
            session['history'] = [] 
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', error="Invalid email or password")
            
    return render_template('login.html')

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
    
    history = session.get('history', [])
    
    bot_reply = get_llm_response(user_message, history)
    
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": bot_reply})
    
    if len(history) > 10:
        history = history[-10:]
        
    session['history'] = history
    session.modified = True 
    
    return jsonify({'reply': bot_reply})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)