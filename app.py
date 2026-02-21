import streamlit as st
from utils.database import init_db, save_interview, save_question_answer, get_interview_history
from utils.llm_engine import generate_questions
from utils.evaluation_engine import evaluate_answer
from utils.voice_engine import text_to_speech, speech_to_text
from utils.analytics import calculate_overall, plot_scores
import tempfile

init_db()

st.set_page_config(page_title="AI Interview Simulator", layout="wide")

st.title("🎯 AI Voice Interview Simulator")

job_roles = [
    "Software Engineer",
    "AI Engineer",
    "Data Scientist",
    "Database Engineer",
    "Business Analyst",
    "Digital Marketer",
    "Teacher",
    "Lawyer",
    "Civil Servant"
]

st.sidebar.header("Interview Setup")
job_role = st.sidebar.selectbox("Select Job Role", job_roles)

# -------------------------
# SESSION STATE FIX
# -------------------------
if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = False

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if st.sidebar.button("Start Interview"):
    st.session_state.questions = generate_questions(job_role)
    st.session_state.current = 0
    st.session_state.scores = []
    st.session_state.qa_data = []
    st.session_state.job_role = job_role
    st.session_state.show_feedback = False
    st.session_state.last_result = None


if "questions" in st.session_state:

    if st.session_state.current < len(st.session_state.questions):

        question = st.session_state.questions[st.session_state.current]

        st.subheader(f"Question {st.session_state.current + 1}")
        st.write(question)

        audio_path = text_to_speech(question)
        st.audio(audio_path)

        answer = st.text_area("Your Answer")

        audio_input = st.file_uploader("Or Upload Voice Answer", type=["mp3", "wav"])

        # -------------------------
        # SUBMIT BUTTON
        # -------------------------
        if not st.session_state.show_feedback:

            if st.button("Submit Answer"):

                if audio_input:
                    answer = speech_to_text(audio_input)

                result = evaluate_answer(job_role, question, answer)

                # Save result in session
                st.session_state.last_result = result
                st.session_state.show_feedback = True

                st.session_state.scores.append(result["overall_score"])
                st.session_state.qa_data.append({
                    "question": question,
                    "user_answer": answer,
                    **result
                })

                st.rerun()

        # -------------------------
        # FEEDBACK SECTION (FIXED)
        # -------------------------
        if st.session_state.show_feedback and st.session_state.last_result:

            result = st.session_state.last_result

            st.write("### Feedback")
            st.write(result["feedback"])

            st.write("### Improved Answer")
            st.write(result["improved_answer"])

            # NEXT QUESTION BUTTON
            if st.button("Next Question"):

                st.session_state.current += 1
                st.session_state.show_feedback = False
                st.session_state.last_result = None

                st.rerun()

    else:

        overall = calculate_overall(st.session_state.scores)
        result_text = "PASS" if overall >= 7 else "FAIL"

        st.success(f"Interview Completed - {result_text}")
        st.metric("Overall Score", round(overall, 2))

        interview_id = save_interview(
            st.session_state.job_role,
            overall,
            result_text
        )

        for qa in st.session_state.qa_data:
            save_question_answer(interview_id, qa)

        metrics = {
            "Technical": sum(q["technical_score"] for q in st.session_state.qa_data) / len(st.session_state.qa_data),
            "Grammar": sum(q["grammar_score"] for q in st.session_state.qa_data) / len(st.session_state.qa_data),
            "Clarity": sum(q["clarity_score"] for q in st.session_state.qa_data) / len(st.session_state.qa_data),
            "Confidence": sum(q["confidence_score"] for q in st.session_state.qa_data) / len(st.session_state.qa_data)
        }

        fig = plot_scores(metrics)
        st.pyplot(fig)

        if st.button("New Interview"):
            st.session_state.clear()
            st.rerun()


st.sidebar.header("Interview History")

if st.sidebar.button("View History"):
    history = get_interview_history()
    for row in history:
        st.sidebar.write(row)
