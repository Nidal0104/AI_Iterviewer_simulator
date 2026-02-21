import streamlit as st
from openai import OpenAI
import tempfile

# Ensure API key exists
if "OPENAI_API_KEY" not in st.secrets:
    st.error("OPENAI_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def text_to_speech(text):
    try:
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text
        )

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_file.write(response.content)
        temp_file.close()

        return temp_file.name

    except Exception as e:
        st.error("Text-to-Speech Error:")
        st.write(str(e))
        return None


def speech_to_text(audio_file):
    try:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcript.text

    except Exception as e:
        st.error("Speech-to-Text Error:")
        st.write(str(e))
        return ""
