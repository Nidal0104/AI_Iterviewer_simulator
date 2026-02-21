import streamlit as st
from utils.database import init_db, save_interview, save_question_answer
from utils.llm_engine import generate_questions
from utils.evaluation_engine import evaluate_answer
from utils.voice_engine import text_to_speech
from utils.analytics import calculate_overall

# -----------------------------
# INITIAL SETUP
# -----------------------------
st.set_page_config(page_title="AI Interview Simulator", layout="centered")

init_db()

st.title("🎤 AI Voice Interview Simulator")

# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = None

if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = False

if "scores" not in st.session_state:
    st.session_state.scores = []

# -----------------------------
# INTERVIEW SETUP
# -----------------------------
if not st.session_state.interview_started:

    job_role = st.text_input("Enter Job Role")

    if st.button("Start Interview"):

        if job_role.strip() == "":
            st.warning("Please enter a job role.")
        else:
            questions = generate_questions(job_role)

            if questions:
                st.session_state.questions = questions
                st.session_state.job_role = job_role
                st.session_state.interview_started = True
                st.session_state.current_question = 0
                st.rerun()

# -----------------------------
# INTERVIEW FLOW
# -----------------------------
else:

    questions = st.session_state.questions
    index = st.session_state.current_question

    # If interview completed
    if index >= len(questions):

        st.success("🎉 Interview Completed!")

        overall_score = calculate_overall(st.session_state.scores)

        st.subheader("📊 Final Score")
        st.write(f"Overall Performance: {overall_score}/10")

        if st.button("Restart Interview"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    else:

        question = questions[index]

        st.subheader(f"Question {index + 1}")
        st.write(question)

        # 🔊 Text to Speech
        audio_path = text_to_speech(question)
        if audio_path:
            st.audio(audio_path)

        answer = st.text_area("Your Answer")

        # -----------------------------
        # SUBMIT BUTTON
        # -----------------------------
        if not st.session_state.show_feedback:

            if st.button("Submit Answer"):

                if answer.strip() == "":
                    st.warning("Please enter your answer.")
                else:
                    result = evaluate_answer(
                        st.session_state.job_role,
                        question,
                        answer
                    )

                    # Save score
                    st.session_state.scores.append(result["overall_score"])

                    # Save evaluation to state
                    st.session_state.evaluation_result = result
                    st.session_state.show_feedback = True

                    # Save to DB
                    save_question_answer(
                        question,
                        answer,
                        result["overall_score"],
                        result["feedback"]
                    )

                    st.rerun()

        # -----------------------------
        # FEEDBACK SECTION
        # -----------------------------
        if st.session_state.show_feedback and st.session_state.evaluation_result:

            result = st.session_state.evaluation_result

            st.divider()
            st.subheader("📊 Evaluation Result")

            st.write(f"Technical Score: {result['technical_score']}/10")
            st.write(f"Grammar Score: {result['grammar_score']}/10")
            st.write(f"Clarity Score: {result['clarity_score']}/10")
            st.write(f"Confidence Score: {result['confidence_score']}/10")
            st.write(f"Overall Score: {result['overall_score']}/10")

            st.subheader("💬 Feedback")
            st.write(result["feedback"])

            st.subheader("✨ Improved Answer")
            st.write(result["improved_answer"])

            # -----------------------------
            # NEXT QUESTION BUTTON
            # -----------------------------
            if st.button("Next Question"):

                st.session_state.current_question += 1
                st.session_state.show_feedback = False
                st.session_state.evaluation_result = None

                st.rerun()
