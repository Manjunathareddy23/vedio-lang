import streamlit as st
from pydub import AudioSegment
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
import tempfile
from io import BytesIO

# Function to extract audio from video using pydub
def extract_audio(video_file):
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "temp_audio.wav")
    
    # Save the uploaded video file in a temporary path
    video_path = os.path.join(temp_dir, "uploaded_video.mp4")
    with open(video_path, "wb") as f:
        f.write(video_file.getbuffer())

    # Use pydub to extract audio
    video = AudioSegment.from_file(video_path)
    video.export(audio_path, format="wav")
    return audio_path

# Function to recognize speech and detect language
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    # Recognize and detect language
    try:
        text = recognizer.recognize_google(audio, show_all=True)
        if text:
            transcript = text['alternative'][0]['transcript']
            detected_language = text.get('language', 'unknown')
            return transcript, detected_language
    except sr.UnknownValueError:
        return None, None
    except sr.RequestError:
        return None, None

# Function to translate text
def translate_text(text, target_language):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_language).text
    return translated_text

# Function to convert text to speech
def text_to_speech(text, lang):
    tts = gTTS(text=text, lang=lang)
    output_path = "translated_audio.mp3"
    tts.save(output_path)
    return output_path

# Streamlit UI
st.title("Video Language Translator")

# File upload
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mkv", "avi", "mov"])
if uploaded_file:
    st.success("Video uploaded successfully!")

    # Extract audio
    with st.spinner("Extracting audio..."):
        audio_path = extract_audio(uploaded_file)
        st.success("Audio extracted!")

    # Transcribe and detect language
    with st.spinner("Transcribing and detecting language..."):
        transcript, detected_language = transcribe_audio(audio_path)
        if transcript:
            st.write("Detected Language:", detected_language)
            st.write("Transcript:", transcript)
        else:
            st.error("Failed to transcribe audio.")

    # Select target language
    target_language = st.selectbox(
        "Select the language to translate to",
        ["en", "te", "es", "fr", "de", "hi", "zh", "ja", "ar"]  # Add more language codes if needed
    )

    # Translate text and convert to speech
    if st.button("Translate and Convert to Audio"):
        with st.spinner("Translating text..."):
            translated_text = translate_text(transcript, target_language)
            st.write("Translated Text:", translated_text)

            # Convert to audio
            with st.spinner("Generating audio..."):
                output_path = text_to_speech(translated_text, target_language)
                st.audio(output_path)
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="Download Translated Audio",
                        data=file,
                        file_name="translated_audio.mp3",
                        mime="audio/mp3"
                    )
                st.success("Translation complete!")
