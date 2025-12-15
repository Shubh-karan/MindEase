import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_sos_email(user_email, user_name, latitude, longitude):
    sender_email = os.environ.get("MAIL_USERNAME")
    sender_password = os.environ.get("MAIL_PASSWORD")
    smtp_server = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    
    try:
        smtp_port = int(os.environ.get("MAIL_PORT", 587))
    except ValueError:
        smtp_port = 587
    
    if not sender_email or not sender_password:
        return False

    receiver_email = "soleindianguy@gmail.com" 

    maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
    
    subject = f"🚨 SOS ALERT: {user_name} needs help!"
    
    body = f"""
    EMERGENCY ALERT SYSTEM
    ----------------------
    User: {user_name}
    Email: {user_email}
    
    Current Location:
    Latitude: {latitude}
    Longitude: {longitude}
    
    Map Link: {maps_link}
    
    Please dispatch the nearest emergency response team immediately.
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False