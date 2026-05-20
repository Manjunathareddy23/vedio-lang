import streamlit as st
import os
import tempfile
import subprocess
import uuid

import speech_recognition as sr

from deep_translator import GoogleTranslator
from gtts import gTTS

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Video Language Translator",
    page_icon="🎬",
    layout="wide"
)

# =========================================================
# PROFESSIONAL UI
# =========================================================
st.markdown("""
<style>

/* Main App */
.stApp {

    background: linear-gradient(
        135deg,
        #0f172a,
        #111827,
        #1e293b
    );

    color: white;

    font-family: 'Segoe UI', sans-serif;
}

/* Main Title */
.main-title {

    text-align: center;

    font-size: 4rem;

    font-weight: 800;

    color: white;

    margin-top: 10px;

    text-shadow:
        0px 0px 15px rgba(59,130,246,0.7),
        0px 0px 35px rgba(124,58,237,0.4);
}

/* Subtitle */
.subtitle {

    text-align: center;

    color: #cbd5e1;

    font-size: 1.2rem;

    margin-bottom: 40px;
}

/* Upload */
.stFileUploader {

    background: rgba(255,255,255,0.05);

    border-radius: 15px;

    padding: 10px;
}

/* Select Box */
.stSelectbox div[data-baseweb="select"] {

    background: rgba(255,255,255,0.08);

    border-radius: 15px;
}

/* Button */
div.stButton > button {

    width: 100%;

    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    );

    color: white;

    border: none;

    border-radius: 15px;

    padding: 15px;

    font-size: 18px;

    font-weight: bold;

    transition: 0.3s ease;
}

div.stButton > button:hover {

    transform: scale(1.02);

    box-shadow:
        0px 0px 25px rgba(59,130,246,0.5);
}

/* Audio */
audio {

    width: 100%;
}

/* Footer */
.footer {

    text-align: center;

    color: #94a3b8;

    margin-top: 50px;

    padding: 20px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="main-title">
🎬 AI Video Language Translator
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="subtitle">
Upload a video, extract speech, translate it into another language,
and generate translated voice audio using AI.
</div>
""", unsafe_allow_html=True)

# =========================================================
# LANGUAGES
# =========================================================
languages = {

    "English": "en",
    "Telugu": "te",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese": "zh-cn",
    "Japanese": "ja",
    "Arabic": "ar",
    "Russian": "ru"
}

# =========================================================
# FILE UPLOAD
# =========================================================
uploaded_file = st.file_uploader(
    "📂 Upload Video File",
    type=[
        "mp4",
        "mkv",
        "avi",
        "mov",
        "webm"
    ]
)

# =========================================================
# TARGET LANGUAGE
# =========================================================
target_language_name = st.selectbox(
    "🌍 Select Target Language",
    list(languages.keys())
)

target_language = languages[target_language_name]

# =========================================================
# EXTRACT AUDIO
# =========================================================
def extract_audio(video_file):

    temp_dir = tempfile.mkdtemp()

    unique_id = str(uuid.uuid4())

    video_path = os.path.join(
        temp_dir,
        f"{unique_id}.mp4"
    )

    audio_path = os.path.join(
        temp_dir,
        f"{unique_id}.wav"
    )

    # Save uploaded video
    with open(video_path, "wb") as f:

        f.write(video_file.getbuffer())

    # FFmpeg command
    command = [

        "ffmpeg",

        "-y",

        "-i", video_path,

        "-vn",

        "-acodec", "pcm_s16le",

        "-ar", "16000",

        "-ac", "1",

        audio_path
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Check FFmpeg result
    if result.returncode != 0:

        raise Exception(
            f"FFmpeg Error:\n\n{result.stderr}"
        )

    # Ensure audio file exists
    if not os.path.exists(audio_path):

        raise Exception(
            "Audio extraction failed."
        )

    return audio_path, temp_dir

# =========================================================
# TRANSCRIBE AUDIO
# =========================================================
def transcribe_audio(audio_path):

    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_path) as source:

        audio = recognizer.record(source)

    try:

        transcript = recognizer.recognize_google(audio)

        return transcript

    except sr.UnknownValueError:

        raise Exception(
            "Speech could not be understood."
        )

    except sr.RequestError:

        raise Exception(
            "Google Speech Recognition API unavailable."
        )

# =========================================================
# TRANSLATE TEXT
# =========================================================
def translate_text(text, target_language):

    translated_text = GoogleTranslator(
        source='auto',
        target=target_language
    ).translate(text)

    return translated_text

# =========================================================
# TEXT TO SPEECH
# =========================================================
def text_to_speech(text, language):

    temp_dir = tempfile.mkdtemp()

    output_path = os.path.join(
        temp_dir,
        "translated_audio.mp3"
    )

    tts = gTTS(
        text=text,
        lang=language
    )

    tts.save(output_path)

    return output_path

# =========================================================
# MAIN BUTTON
# =========================================================
if st.button("🚀 Translate Video"):

    if uploaded_file is None:

        st.warning(
            "Please upload a video file."
        )

    else:

        temp_dir = None

        try:

            # =============================================
            # EXTRACT AUDIO
            # =============================================
            with st.spinner(
                "🎵 Extracting audio from video..."
            ):

                audio_path, temp_dir = extract_audio(
                    uploaded_file
                )

            st.success(
                "✅ Audio extracted successfully!"
            )

            # =============================================
            # TRANSCRIBE
            # =============================================
            with st.spinner(
                "📝 Transcribing speech..."
            ):

                transcript = transcribe_audio(
                    audio_path
                )

            st.subheader(
                "📄 Transcript"
            )

            st.write(transcript)

            # =============================================
            # TRANSLATE
            # =============================================
            with st.spinner(
                "🌍 Translating text..."
            ):

                translated_text = translate_text(
                    transcript,
                    target_language
                )

            st.subheader(
                "🌐 Translated Text"
            )

            st.write(translated_text)

            # =============================================
            # TEXT TO SPEECH
            # =============================================
            with st.spinner(
                "🔊 Generating translated audio..."
            ):

                translated_audio = text_to_speech(
                    translated_text,
                    target_language
                )

            st.success(
                "✅ Translation completed!"
            )

            # =============================================
            # AUDIO PLAYER
            # =============================================
            st.subheader(
                "🎧 Listen to Translated Audio"
            )

            st.audio(translated_audio)

            # =============================================
            # DOWNLOAD BUTTON
            # =============================================
            with open(
                translated_audio,
                "rb"
            ) as audio_file:

                st.download_button(
                    label="⬇ Download Audio",
                    data=audio_file,
                    file_name="translated_audio.mp3",
                    mime="audio/mp3"
                )

        except Exception as e:

            st.error(
                f"❌ Error:\n\n{str(e)}"
            )

        finally:

            # =============================================
            # CLEANUP
            # =============================================
            try:

                if temp_dir and os.path.exists(temp_dir):

                    for file in os.listdir(temp_dir):

                        os.remove(
                            os.path.join(temp_dir, file)
                        )

                    os.rmdir(temp_dir)

            except:
                pass

# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div class="footer">
Built with ❤️ using Streamlit, FFmpeg,
Speech Recognition, Deep Translator & gTTS
</div>
""", unsafe_allow_html=True)
