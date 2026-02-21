import streamlit as st
from groq import Groq
import json

# Check API key
if "GROQ_API_KEY" not in st.secrets:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

MODEL = "llama-3.1-8b-instant"


def evaluate_answer(job_role, question, answer):

    prompt = f"""
Evaluate the following interview answer.

Job Role: {job_role}
Question: {question}
Candidate Answer: {answer}

Return ONLY valid JSON in this exact format:

{{
    "technical_score": number (0-10),
    "grammar_score": number (0-10),
    "clarity_score": number (0-10),
    "confidence_score": number (0-10),
    "overall_score": number (0-10),
    "feedback": "short professional feedback",
    "improved_answer": "improved version of the answer"
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a strict interview evaluator that responds only in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800,
            response_format={"type": "json_object"}  # 🔥 THIS FIXES EVERYTHING
        )

        result = response.choices[0].message.content

        parsed = json.loads(result)

        return parsed

    except Exception as e:
        st.error("Evaluation Error:")
        st.write(str(e))

        # Realistic fallback
        return {
            "technical_score": 6,
            "grammar_score": 6,
            "clarity_score": 6,
            "confidence_score": 6,
            "overall_score": 6,
            "feedback": "The evaluation system encountered a formatting issue. Please try again.",
            "improved_answer": answer
        }
