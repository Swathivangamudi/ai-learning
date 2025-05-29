import streamlit as st
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import os
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import docx

# === Setup ===

# Gemini API key
genai.configure(api_key="AIzaSyDt3A2o3AgDclNg9MgMgdcsKVTCZ0Rp96I")  # Replace securely

# Tesseract path for Windows (adjust if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# TTS engine setup
tts_engine = pyttsx3.init()
tts_engine_running = False
paused = False

def speak_text(text):
    global tts_engine_running, paused
    tts_engine_running = True
    for word in text.split():
        if paused:
            break
        tts_engine.say(word)
        tts_engine.runAndWait()
    tts_engine_running = False

def stop_speaking():
    global paused, tts_engine_running
    if tts_engine_running:
        paused = True
        tts_engine.stop()

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening...")
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio, language="en-IN")
            return text
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError as e:
            return f"Speech recognition service error: {e}"

def generate_explanation(query):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(query)
    return response.text

def extract_text_from_pdf(uploaded_pdf):
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(uploaded_docx):
    doc = docx.Document(uploaded_docx)
    return "\n".join([para.text for para in doc.paragraphs])

# === UI Configuration ===
st.set_page_config(page_title="AI-Powered Learning Companion", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #fee0f9 !important; }
        section[data-testid="stSidebar"] { background-color: pink !important; padding: 15px; border-radius: 10px; }
        .stSidebar h2, .stSidebar h3, .stSidebar label, .stSidebar div { color: black !important; font-weight: bold; }
        h1, h2 { color: black !important; }
        .stTextInput>label { color: black !important; font-weight: bold !important; }
        .stTextInput>div>div>input { background-color: #BEE1E6 !important; color: black !important; border-radius: 5px !important; padding: 10px; }
        .stButton>button { color: white !important; background-color: #008585 !important; font-weight: bold; }
        .ai-response { color: black !important; font-weight: bold !important; font-size: 16px !important; padding: 10px; background-color: #f0f0f0 !important; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# === Sidebar UI ===
if os.path.exists("chatbot_sticker.png"):
    st.sidebar.image("chatbot_sticker.png", width=120, caption="Chatbot Assistant")
else:
    st.sidebar.info("AI Chatbot Assistant")

st.sidebar.subheader("🌍 Select Language")
language = st.sidebar.radio("Choose:", ["English", "Telugu", "Hindi"], index=0)

# === File Upload ===
st.sidebar.header("📂 Upload a File")
uploaded_file = st.sidebar.file_uploader("Upload a text, PDF, or Word file", type=["txt", "pdf", "docx"])
if uploaded_file is not None:
    st.sidebar.write("Uploaded file:", uploaded_file.name)
    if uploaded_file.type == "text/plain":
        file_content = uploaded_file.read().decode("utf-8", errors="ignore")
    elif uploaded_file.type == "application/pdf":
        file_content = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        file_content = extract_text_from_docx(uploaded_file)
    else:
        file_content = ""

    st.sidebar.text_area("📖 Extracted File Text:", file_content, height=150)

    if file_content.strip():
        ai_response = generate_explanation(file_content)
        st.sidebar.markdown(f"<div class='ai-response'>{ai_response}</div>", unsafe_allow_html=True)
        speak_text(ai_response)

# === Image Upload with OCR ===
st.sidebar.header("🖼️ Upload an Image of Your Question")
image_file = st.sidebar.file_uploader("Choose an image (JPG/PNG)", type=["jpg", "jpeg", "png"])
if image_file is not None:
    st.sidebar.image(image_file, caption="Uploaded Image", use_column_width=True)
    image = Image.open(image_file)
    extracted_text = pytesseract.image_to_string(image)

    if extracted_text.strip():
        st.sidebar.subheader("📝 Extracted Question")
        st.sidebar.write(extracted_text)
        ai_response = generate_explanation(extracted_text)
        st.markdown(f"<div class='ai-response'>{ai_response}</div>", unsafe_allow_html=True)
        speak_text(ai_response)
    else:
        st.sidebar.warning("No readable text found. Please upload a clearer image.")

# === Language UI ===
if language == "Telugu":
    st.markdown("<h1 style='color:black;'>🎓 AI ఆధారిత విద్యా సహాయకుడు</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:black;'>AI గురువును అడగండి</h2>", unsafe_allow_html=True)
elif language == "Hindi":
    st.markdown("<h1 style='color:black;'>🎓 एआई-संचालित शिक्षण साथी</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:black;'>एआई ट्यूटर से पूछें</h2>", unsafe_allow_html=True)
else:
    st.markdown("<h1 style='color:black;'>🎓 AI-Powered Learning Companion</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:black;'>Ask the AI Tutor</h2>", unsafe_allow_html=True)

# === Direct Text Query ===
user_query = st.text_input("Enter your math, physics, or chemistry question:")
if st.button("Get Answer"):
    if user_query:
        ai_response = generate_explanation(user_query)
        st.markdown(f"<div class='ai-response'>{ai_response}</div>", unsafe_allow_html=True)
        speak_text(ai_response)
