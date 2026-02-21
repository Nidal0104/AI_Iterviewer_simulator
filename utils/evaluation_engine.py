import streamlit as st
from groq import Groq
import json
import re

# Check API key
if "GROQ_API_KEY" not in st.secrets:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama-3.1-8b-instant"


def clean_json_response(text):
    # Remove markdown formatting
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    # Extract JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)

    return text


def evaluate_answer(job_role, question, answer):

    prompt = f"""
You are a professional interview evaluator.

Evaluate the candidate answer strictly in JSON format.

Job Role: {job_role}
Question: {question}
Candidate Answer: {answer}

Return ONLY valid JSON in this format:

{{
    "technical_score": 0-10 number,
    "grammar_score": 0-10 number,
    "clarity_score": 0-10 number,
    "confidence_score": 0-10 number,
    "overall_score": 0-10 number,
    "feedback": "short professional feedback",
    "improved_answer": "improved version"
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You return ONLY valid JSON. No explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800,
        )

        raw_output = response.choices[0].message.content.strip()

        # Clean and extract JSON
        json_text = clean_json_response(raw_output)

        parsed = json.loads(json_text)

        return parsed

    except Exception as e:
        st.error("Evaluation Error:")
        st.write(str(e))

        # Show raw output for debugging (important!)
        try:
            st.write("Raw model output:")
            st.write(raw_output)
        except:
            pass

        return {
            "technical_score": 6,
            "grammar_score": 6,
            "clarity_score": 6,
            "confidence_score": 6,
            "overall_score": 6,
            "feedback": "Evaluation formatting issue occurred.",
            "improved_answer": answer
        }
