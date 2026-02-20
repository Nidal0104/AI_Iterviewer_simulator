import streamlit as st
from openai import OpenAI
import tempfile

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def text_to_speech(text):
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.write(speech.content)
    temp_file.close()

    return temp_file.name


def speech_to_text(audio_file):
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    return transcript.text
