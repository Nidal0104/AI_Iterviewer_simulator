import streamlit as st
from groq import Groq
import json
import random

# Make sure key exists
if "GROQ_API_KEY" not in st.secrets:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Use confirmed stable model
MODEL = "llama3-8b-8192"

def generate_questions(job_role):
    num_questions = random.randint(5, 8)

    prompt = f"""
You are a professional interview question generator.

Generate {num_questions} professional interview questions
for the job role: {job_role}.

40% technical
30% behavioral
30% scenario-based

Return ONLY a valid JSON array of strings.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You generate structured interview questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
        )

        content = response.choices[0].message.content.strip()

        st.write("DEBUG RAW RESPONSE:", content)

        # Try JSON parsing
        questions = json.loads(content)

        if not isinstance(questions, list):
            raise ValueError("Response is not a list")

        return questions

    except Exception as e:
        st.error("Groq Error Details:")
        st.write(str(e))
        st.stop()
