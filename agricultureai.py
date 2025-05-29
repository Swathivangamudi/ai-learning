import google.genai as genai
import cv2  # Import OpenCV
from PIL import Image
import io
import numpy as np
from gtts import gTTS
import os
import speech_recognition as sr  # For speech recognition

# Google API Key and Client setup
GOOGLE_API_KEY = "AIzaSyAQ_VbZQ4Z0vJYYSBnRtQRm_KAPER2Bfus"
client = genai.Client(api_key=GOOGLE_API_KEY)
model_name = "gemini-2.0-flash"  # You can change this as needed

# Initialize recognizer
recognizer = sr.Recognizer()

# Set up the webcam (0 is the default webcam)
cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Capture a frame from the webcam
ret, frame = cap.read()

if ret:
    # Convert the frame from OpenCV (BGR) to PIL (RGB)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(frame_rgb)

    # Resize the image to match the model's input size
    pil_image.thumbnail([1024, 1024], Image.Resampling.LANCZOS)

    # Listen to the microphone for a spoken prompt in Telugu
    with sr.Microphone() as source:
        print("మీరు కోరుకుంటున్న ప్రశ్నను మీరు మాట్లాడండి:")  # "Please speak your request:" in Telugu
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio = recognizer.listen(source)  # Listen to the audio

    try:
        # Convert speech to text (in Telugu if spoken in Telugu)
        prompt = recognizer.recognize_google(audio, language="te-IN")  # 'te-IN' for Telugu
        print(f"Recognized speech: {prompt}")

        # Run the model to analyze the image with the prompt in Telugu
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, pil_image]
        )

        # Get the response and print it in Telugu
        response_text = response.text
        print(response_text)

        # Convert the response text to speech in Telugu using gTTS
        tts = gTTS(response_text, lang='te')  # 'te' is the language code for Telugu
        tts.save("output.mp3")  # Save the audio file
        os.system("start output.mp3")  # Play the audio (use 'afplay' on macOS, or 'mpg321' on Linux)

    except sr.UnknownValueError:
        print("క్షమించండి, నేను శబ్దాన్ని అర్థం చేసుకోలేను.")  # "Sorry, I couldn't understand the audio." in Telugu
    except sr.RequestError as e:
        print(f"గూగుల్ స్పీచ్ రికగ్నిషన్ సేవ నుండి ఫలితాలు పొందలేకపోయింది; {e}")  # Error message in Telugu
    except Exception as e:
        print(f"చిత్రంతో మోడల్ ప్రాసెసింగ్ లో లోపం: {e}")  # General error message in Telugu
else:
    print("Error: Failed to capture image from webcam.")

# Release the webcam and close any OpenCV windows
cap.release()
cv2.destroyAllWindows()
