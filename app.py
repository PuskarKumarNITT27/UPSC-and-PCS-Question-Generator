import streamlit as st
from quiz_manager import QuizManager


def init_session_state():
    """Initialize all session state variables."""
    if 'quiz_manager' not in st.session_state:
        st.session_state.quiz_manager = QuizManager()
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'generating' not in st.session_state:
        st.session_state.generating = False


def render_sidebar() -> dict:
    """Render sidebar settings and return config dict."""
    st.sidebar.header("Quiz Settings")

    topic = st.sidebar.text_input(
        "Enter Topic",
        placeholder="e.g. Indian History, Geography, Polity"
    )

    question_type = st.sidebar.selectbox(
        "Question Type",
        ["Multiple Choice", "Fill in the Blank"]
    )

    difficulty = st.sidebar.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard"],
        index=1
    )

    num_questions = st.sidebar.number_input(
        "Number of Questions",
        min_value=1,
        max_value=10,
        value=5
    )

    generate_clicked = st.sidebar.button(
        "Generate Quiz",
        use_container_width=True,
        type="primary"
    )

    return {
        'topic': topic,
        'question_type': question_type,
        'difficulty': difficulty,
        'num_questions': num_questions,
        'generate_clicked': generate_clicked
    }


def render_quiz(qm: QuizManager):
    """Render quiz questions and collect answers."""
    st.header("Quiz")

    for i, q in enumerate(qm.questions):
        st.markdown(f"**Q{i+1}. {q['question']}**")

        if q['type'] == 'MCQ':
            answer = st.radio(
                f"Select answer for Q{i+1}",
                q['options'],
                key=f"q_{i}",
                label_visibility="collapsed"
            )
        else:
            answer = st.text_input(
                f"Your answer for Q{i+1}",
                key=f"q_{i}",
                placeholder="Type your answer here..."
            )

        qm.store_answer(i, answer if answer else "")
        st.markdown("---")

    if st.button("Submit Quiz", type="primary", use_container_width=True):
        # Validate all fill-in-the-blank answered
        unanswered = [
            i + 1 for i, q in enumerate(qm.questions)
            if q['type'] == 'Fill in the Blank'
            and not qm.user_answers[i].strip()
        ]
        if unanswered:
            st.warning(f"Please answer question(s): {unanswered}")
        else:
            qm.evaluate_quiz()
            st.session_state.quiz_submitted = True
            st.rerun()


def render_results(qm: QuizManager):
    """Render quiz results with score and per-question breakdown."""
    st.header("Results")

    score = qm.get_score()

    # Score summary
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{score['correct']}/{score['total']}")
    col2.metric("Percentage", f"{score['percentage']}%")
    col3.metric(
        "Result",
        "Pass" if score['percentage'] >= 60 else "Fail",
    )

    st.markdown("---")

    # Per-question breakdown
    for result in qm.results:
        q_num = result['question_number']

        if result['is_correct']:
            st.success(f"✅ Q{q_num}: {result['question']}")
        else:
            st.error(f"❌ Q{q_num}: {result['question']}")

            if result['options']:
                st.write(f"**Your answer:** {result['user_answer']}")
                st.write(f"**Correct answer:** {result['correct_answer']}")
            else:
                col_a, col_b = st.columns(2)
                col_a.write(f"**Your answer:** {result['user_answer']}")
                col_b.write(f"**Correct answer:** {result['correct_answer']}")

        st.markdown("---")

    # Save & download
    st.subheader("Save Results")
    if st.button("Save to CSV", use_container_width=True):
        try:
            filepath = qm.save_to_csv()
            with open(filepath, 'rb') as f:
                st.download_button(
                    label="Download CSV",
                    data=f.read(),
                    file_name=f"quiz_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            st.success(f"Saved to `{filepath}`")
        except Exception as e:
            st.error(f"Failed to save: {e}")

    # Retry button
    st.markdown("---")
    if st.button("Start New Quiz", use_container_width=True):
        st.session_state.quiz_generated = False
        st.session_state.quiz_submitted = False
        st.session_state.quiz_manager = QuizManager()
        st.rerun()


def main():
    st.set_page_config(
        page_title="UPSC & PCS Question Generator",
        page_icon="📝",
        layout="centered"
    )

    st.title("📝 UPSC & PCS Question Generator")
    st.caption("AI-powered quiz generator for exam preparation")

    init_session_state()
    config = render_sidebar()
    qm = st.session_state.quiz_manager

    # --- Generate quiz ---
    if config['generate_clicked']:
        if not config['topic'].strip():
            st.sidebar.error("Please enter a topic first.")
        else:
            st.session_state.quiz_submitted = False
            st.session_state.quiz_generated = False

            with st.spinner(f"Generating {config['num_questions']} questions on '{config['topic']}'..."):
                try:
                    qm.generate_questions(
                        topic=config['topic'],
                        question_type=config['question_type'],
                        difficulty=config['difficulty'],
                        num_questions=config['num_questions']
                    )
                    st.session_state.quiz_generated = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate questions: {e}")

    # --- Show quiz or results ---
    if st.session_state.quiz_submitted:
        render_results(qm)
    elif st.session_state.quiz_generated and qm.questions:
        render_quiz(qm)
    else:
        # Landing state
        st.info("👈 Configure your quiz in the sidebar and click **Generate Quiz** to begin.")


if __name__ == "__main__":
    main()