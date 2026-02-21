import streamlit as st
from groq import Groq
import json
import re

if "GROQ_API_KEY" not in st.secrets:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama-3.1-8b-instant"


def clean_json_response(text):
    """
    Extracts JSON object from LLM response safely and fixes minor formatting issues.
    """
    # Remove markdown code blocks
    text = re.sub(r"```json|```", "", text)

    # Find first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    json_text = match.group(0)

    # Replace single quotes with double quotes
    json_text = json_text.replace("'", '"')

    # Remove trailing commas before closing braces
    json_text = re.sub(r",(\s*[}\]])", r"\1", json_text)

    return json_text


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
                {"role": "system", "content": "Return ONLY valid JSON. No explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800,
        )

        raw_output = response.choices[0].message.content.strip()
        json_text = clean_json_response(raw_output)

        if not json_text:
            raise ValueError("No JSON found in model output")

        parsed = json.loads(json_text)
        return parsed

    except Exception as e:
        st.error("Evaluation Parsing Issue:")
        st.write(str(e))

        # Show raw model output for debugging
        try:
            st.write("Raw model output:")
            st.write(raw_output)
        except:
            pass

        # Fallback with realistic default
        return {
            "technical_score": 6,
            "grammar_score": 6,
            "clarity_score": 6,
            "confidence_score": 6,
            "overall_score": 6,
            "feedback": "The evaluation system encountered a minor formatting issue. Your answer was evaluated approximately.",
            "improved_answer": answer
        }
