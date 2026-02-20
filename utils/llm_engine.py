import streamlit as st
from groq import Groq
import json
import random

# Initialize Groq client safely
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Use a stable currently supported model
MODEL = "llama3-8b-8192"  # safer & widely available


def generate_questions(job_role):
    num_questions = random.randint(5, 8)

    prompt = f"""
You are a professional interview question generator.

Generate {num_questions} realistic and professional interview questions
for the job role: {job_role}.

Rules:
- 40% technical
- 30% behavioral
- 30% scenario-based
- Clear and concise
- No explanations
- Return ONLY a valid JSON array of strings
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You generate structured interview questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024
        )

        content = response.choices[0].message.content.strip()

        # Attempt JSON parsing
        try:
            questions = json.loads(content)
            if isinstance(questions, list):
                return questions
        except:
            pass

        # Fallback parsing if JSON fails
        lines = content.split("\n")
        questions = [line.strip("- ").strip() for line in lines if line.strip()]
        return questions[:num_questions]

    except Exception as e:
        st.error("Error generating interview questions.")
        st.stop()
