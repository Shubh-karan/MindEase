# 🧠 MindEase: AI-Powered Mental Health Companion

[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Live_App-yellow?style=for-the-badge)](https://shubhkaran-mindease.hf.space)
[![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask-black?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![TensorFlow](https://img.shields.io/badge/AI-TensorFlow-orange?style=for-the-badge&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

> **"See, Listen, Protect."** > An intelligent digital ecosystem integrating **Computer Vision** and **Generative AI** to provide immediate mental health support and emergency safety.

---

## 🚀 Live Demo
Experience the app directly in your browser:  
👉 **[Click Here to Launch MindEase](https://shubhkaran-mindease.hf.space)**

---

## 🌟 Key Features

### 🎭 **1. AI Emotion Recognition (The "See" Module)**
* **Real-time Analysis:** Uses **DeepFace** & **OpenCV** to analyze facial expressions via the webcam.
* **Mood Detection:** Instantly identifies emotions (Happy, Sad, Neutral, Angry) to tailor the conversation.
* **Privacy-First:** Video streams are processed in RAM and never stored.

### 🤖 **2. Empathetic AI Chatbot (The "Listen" Module)**
* **Context Aware:** Powered by **Groq/Llama 3**, the bot adjusts its tone based on your detected emotion.
* **Therapeutic Support:** Trained to provide comforting, non-judgmental dialogue.

### 🚨 **3. SOS Emergency System (The "Protect" Module)**
* **One-Click Safety:** Instantly captures your **Live Geolocation** (Lat/Long).
* **Smart Alerts:** Bypasses cloud firewalls using **Webhooks (Make.com)** to send emergency emails with Google Maps links to trusted contacts.

### 🔐 **4. Secure & Scalable**
* **Authentication:** Secure Google Login via **Firebase Auth**.
* **Cloud Native:** Dockerized deployment running on high-performance **Hugging Face Spaces (16GB RAM)**.

---

## 🛠️ Technology Stack

| Component | Technology Used |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript (Jinja2 Templates) |
| **Backend** | Python (Flask Framework) |
| **Computer Vision** | OpenCV (`cv2`), DeepFace (TensorFlow/Keras) |
| **LLM / AI** | Groq API (Llama 3), TextBlob (Sentiment Analysis) |
| **Database** | Firebase Firestore |
| **DevOps** | Docker, Hugging Face Spaces |

---

---

## 💻 Installation (Run Locally)

Want to run this on your own machine? Follow these steps:

**1. Clone the Repository**
```bash
git clone [https://github.com/Shubh-karan/MindEase.git](https://github.com/Shubh-karan/MindEase.git)
cd MindEase
