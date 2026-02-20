import streamlit as st
from groq import Groq
import json

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama3-70b-8192"

def evaluate_answer(job_role, question, answer):

    prompt = f"""
    You are a professional interview evaluator.

    Job Role: {job_role}
    Question: {question}
    Candidate Answer: {answer}

    Evaluate and return STRICT JSON:

    {{
        "technical_score": number (0-10),
        "grammar_score": number (0-10),
        "clarity_score": number (0-10),
        "confidence_score": number (0-10),
        "overall_score": number (0-10),
        "feedback": "...",
        "improved_answer": "..."
    }}
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.choices[0].message.content

    return json.loads(result)
