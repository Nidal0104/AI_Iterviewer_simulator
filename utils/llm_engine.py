import streamlit as st
from groq import Groq
import json
import random

# Ensure API key exists
if "GROQ_API_KEY" not in st.secrets:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

# Initialize Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Active Groq model (supported)
MODEL = "llama-3.1-8b-instant"


def generate_questions(job_role):
    num_questions = random.randint(5, 8)

    prompt = f"""
You are a professional interview question generator.

Generate {num_questions} professional interview questions
for the job role: {job_role}.

Distribution:
- 40% technical
- 30% behavioral
- 30% scenario-based

Return ONLY a valid JSON array of strings.
No explanations.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You generate structured interview questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        content = response.choices[0].message.content.strip()

        # Try parsing JSON safely
        try:
            questions = json.loads(content)
            if isinstance(questions, list):
                return questions
        except:
            pass

        # Fallback if model returns bullet list instead of JSON
        lines = content.split("\n")
        questions = [line.strip("- ").strip() for line in lines if line.strip()]
        return questions[:num_questions]

    except Exception as e:
        st.error("Groq API Error:")
        st.write(str(e))
        st.stop()
