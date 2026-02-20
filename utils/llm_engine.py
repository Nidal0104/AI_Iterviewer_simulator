import streamlit as st
from groq import Groq
import json
import random

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

MODEL = "llama3-70b-8192"

def generate_questions(job_role):

    num_questions = random.randint(5, 8)

    prompt = f"""
    Generate {num_questions} professional interview questions
    for the job role: {job_role}.

    40% technical
    30% behavioral
    30% scenario-based

    Return only a JSON list.
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    questions = response.choices[0].message.content

    try:
        return json.loads(questions)
    except:
        return [q.strip("- ") for q in questions.split("\n") if q.strip()]
