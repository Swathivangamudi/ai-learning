import streamlit as st
import speech_recognition as sr
import google.generativeai as genai
genai.configure(api_key="AIzaSyBmfkQgq0WpcbumMZGXDqPla_K4YfiLokk")
import os
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import docx

# === Setup ===

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Please speak now.")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="en-IN")
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            return f"Speech recognition error: {e}"
        except Exception as e:
            return f"Error: {e}"

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
        section[data-testid="stSidebar"] { background-color: #FADADD !important; padding: 15px; border-radius: 10px; }
        .stSidebar h2, .stSidebar h3, .stSidebar label, .stSidebar div { color: black !important; font-weight: bold; }
        h1, h2 { color: black !important; }
        .stTextInput>label { color: black !important; font-weight: bold !important; }
        .stTextInput>div>div>input { background-color: #BEE1E6 !important; color: black !important; border-radius: 5px !important; padding: 10px; }
        .stButton>button { color: white !important; background-color: #008585 !important; font-weight: bold; }
        .ai-response { color: black !important;
            font-weight: bold !important;
            font-size: 16px !important;
            padding: 15px;
            background-color: #f0f0f0 !important;
            border-radius: 10px;
            width: 100% !important;
            max-width: none !important;
        }
    </style>
""", unsafe_allow_html=True)

if os.path.exists("chatbot_sticker.png"):
    st.sidebar.image("chatbot_sticker.png", width=120, caption="Chatbot Assistant")
else:
    st.sidebar.info("AI Chatbot Assistant")

st.sidebar.subheader("🌍 Select Language")
language = st.sidebar.radio("Choose:", ["English", "Telugu", "Hindi"], index=0)

# === Unified Upload Section (Images + Files) in Sidebar ===
st.sidebar.header("📂 Upload Image or File")
uploaded = st.sidebar.file_uploader(
    "Upload image (JPG/PNG) or document (PDF, DOCX, TXT)",
    type=["jpg", "jpeg", "png", "pdf", "docx", "txt"]
)

extracted_text = ""
if uploaded:
    if uploaded.type.startswith("image"):
        image = Image.open(uploaded)
        st.sidebar.image(image, caption="Uploaded Image", use_container_width=True)

        extracted_text = pytesseract.image_to_string(image)
        if extracted_text.strip():
            st.sidebar.subheader("📝 Extracted Text from Image")
            st.sidebar.write(extracted_text)
        else:
            st.sidebar.warning("No text found in image.")
    elif uploaded.type == "application/pdf":
        extracted_text = extract_text_from_pdf(uploaded)
        st.sidebar.subheader("📄 Extracted Text from PDF")
        st.sidebar.write(extracted_text[:1000])
    elif uploaded.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extracted_text = extract_text_from_docx(uploaded)
        st.sidebar.subheader("📄 Extracted Text from DOCX")
        st.sidebar.write(extracted_text[:1000])
    elif uploaded.type == "text/plain":
        extracted_text = uploaded.read().decode("utf-8", errors="ignore")
        st.sidebar.subheader("📄 Extracted Text from TXT")
        st.sidebar.write(extracted_text[:1000])
    else:
        st.sidebar.warning("Unsupported file type.")

# === Main Page Content ===
if language == "Telugu":
    st.markdown("<h1 style='color:black;'>🎓 AI ఆధారిత విద్యా సహాయకుడు</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:black;'>AI గురువును అడగండి</h2>", unsafe_allow_html=True)
elif language == "Hindi":
    st.markdown("<h1 style='color:black;'>🎓 एआई-संचालित शिक्षण साथी</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:black;'>एआई ट्यूटर से पूछें</h2>", unsafe_allow_html=True)
else:
    st.markdown("<h1 style='color:black;'>🎓 AI-Powered Learning Companion</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:black;'>Ask the AI Tutor</h2>", unsafe_allow_html=True)

# === Unified Input Mode Section ===
input_mode = st.radio("Choose input type:", ["Text", "Voice"], horizontal=True)
voice_query = None
text_query = ""

if input_mode == "Text":
    text_query = st.text_input("Enter your math, physics, or chemistry question:")

elif input_mode == "Voice":
    if st.button("🎤 Speak your question"):
        voice_result = recognize_speech()
        if voice_result and not (voice_result.startswith("Error") or voice_result is None):
            voice_query = voice_result
            st.success(f"Recognized speech: {voice_query}")
        else:
            st.error("Speech not recognized or error occurred.")

# === Final Query Resolution ===
final_query = ""
if extracted_text.strip():
    final_query = extracted_text.strip()
elif voice_query:
    final_query = voice_query.strip()
elif text_query.strip():
    final_query = text_query.strip()

# === Get Answer Button ===
if st.button("Get Answer"):
    if final_query:
        with st.spinner("Generating answer..."):
            try:
                ai_response = generate_explanation(final_query)
                st.markdown(f"<div class='ai-response'>{ai_response}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error generating response: {e}")
    else:
        st.warning("Please provide a question by typing, speaking, or uploading an image/file.")

# === Sidebar AI Response for Upload ===
if extracted_text.strip():
    try:
        ai_response_file = generate_explanation(extracted_text)
        st.sidebar.markdown(f"<div class='ai-response'>{ai_response_file}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.sidebar.error(f"Error generating AI response for uploaded content: {e}")
