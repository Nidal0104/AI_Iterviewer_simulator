import streamlit as st
from gtts import gTTS
import tempfile


def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang="en")

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)

        return temp_file.name

    except Exception as e:
        st.error("Text-to-Speech Error:")
        st.write(str(e))
        return None


def speech_to_text(audio_file):
    st.warning("Speech-to-Text disabled (OpenAI removed due to quota).")
    return ""
