from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from flask_cors import CORS
from textblob import TextBlob
import os
import csv
import io
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()

from services.firebase_service import (
    create_user, 
    verify_user, 
    get_user, 
    get_all_users, 
    save_chat_log, 
    get_sentiment_stats,
    get_logs_by_date_range
)
from services.llm_service import get_llm_response, generate_zen_story, transcribe_audio

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "Everthing is okay")
CORS(app)

def clean_text(text):
    if not text: return ""
    try:
        return text.encode('latin-1', 'ignore').decode('latin-1')
    except:
        return ""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').lower()
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

@app.route('/google_login', methods=['POST'])
def google_login():
    data = request.get_json()
    email = data.get('email').lower()
    name = data.get('name')
    
    create_user(name, email, "google_auth_user")
    
    existing_user = get_user(email)
    role = 'user'
    if existing_user:
        role = existing_user.get('role', 'user')

    session['user_email'] = email
    session['user_name'] = name
    session['role'] = role
    session['history'] = []
    
    if role == 'admin':
        target_url = url_for('admin_dashboard')
    else:
        target_url = url_for('chat')
    
    return jsonify({'status': 'success', 'redirect_url': target_url})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email').lower()
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

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    text = transcribe_audio(file)
    return jsonify({'text': text})

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

@app.route('/admin/reports')
def admin_reports():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'admin':
        return redirect(url_for('chat'))
        
    return render_template('reports.html')

@app.route('/admin/download_report', methods=['POST'])
def download_report():
    if session.get('role') != 'admin':
        return "Access Denied"

    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    file_format = request.form.get('format')

    logs = get_logs_by_date_range(start_date, end_date)

    if file_format == 'csv':
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['Date', 'Email', 'Message', 'Sentiment'])
        for log in logs:
            cw.writerow([log.get('date', 'N/A'), log.get('email', 'Anon'), log.get('message', ''), log.get('sentiment', '')])
        
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=report_{start_date}_to_{end_date}.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    elif file_format == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.cell(200, 10, txt=f"MindEase Report: {start_date} to {end_date}", ln=1, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(40, 10, "Date", 1)
        pdf.cell(30, 10, "Sentiment", 1)
        pdf.cell(120, 10, "Message (Preview)", 1)
        pdf.ln()
        
        pdf.set_font("Arial", size=9)
        for log in logs:
            msg_raw = log.get('message', '')
            msg_clean = clean_text(msg_raw)
            
            msg_preview = (msg_clean[:60] + '...') if len(msg_clean) > 60 else msg_clean
            
            pdf.cell(40, 10, str(log.get('date', 'N/A')), 1)
            pdf.cell(30, 10, clean_text(str(log.get('sentiment', 'N/A'))), 1)
            pdf.cell(120, 10, msg_preview, 1)
            pdf.ln()

        response = make_response(pdf.output(dest='S').encode('latin-1'))
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=report_{start_date}.pdf'
        return response

    return "Invalid Format Selected"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')