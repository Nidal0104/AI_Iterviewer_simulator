import streamlit as st
from groq import Groq
import json
import re

# Ensure API key exists
if "GROQ_API_KEY" not in st.secrets:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

MODEL = "llama-3.1-8b-instant"


def extract_json(text):
    """
    Extract JSON object from LLM response safely.
    """
    # Remove markdown code blocks
    text = re.sub(r"```json|```", "", text)

    # Find first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)

    return None


def evaluate_answer(job_role, question, answer):

    prompt = f"""
You are a professional interview evaluator.

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
                {"role": "system", "content": "You evaluate interview answers strictly in JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        raw_output = response.choices[0].message.content.strip()

        # Extract clean JSON
        json_text = extract_json(raw_output)

        if not json_text:
            raise ValueError("No JSON found in model response.")

        parsed = json.loads(json_text)

        return parsed

    except Exception as e:
        st.error("Evaluation Error:")
        st.write(str(e))

        # Return safe fallback so app doesn't crash
        return {
            "technical_score": 5,
            "grammar_score": 5,
            "clarity_score": 5,
            "confidence_score": 5,
            "overall_score": 5,
            "feedback": "Evaluation failed. Default score assigned.",
            "improved_answer": answer
        }
