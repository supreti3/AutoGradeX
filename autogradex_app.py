import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------- Page Config ----------------------
st.set_page_config(page_title="AutoGradeX Dashboard", page_icon="🚀", layout="wide")

# ---------------------- Custom Styling ----------------------
st.markdown("""
    <style>
        .main-title {
            text-align: center;
            font-size: 2.6rem;
            font-weight: 800;
            color: #8e7dff;
            margin-bottom: 0.3rem;
        }
        .subtitle {
            text-align: center;
            color: #cfcfcf;
            font-size: 1.1rem;
            margin-bottom: 1.8rem;
        }
        .stDownloadButton>button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            height: 3em;
        }
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
        }
        h2, h3, h4 {
            color: #ffffff !important;
        }
        .block-container {
            max-width: 1200px;
            margin: auto;
            padding-top: 1.5rem;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------------------- Header ----------------------
st.markdown("<div class='main-title'>AutoGradeX</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Weighted Grading Dashboard – Upload, Analyze, and Export Student Results Instantly.</div>", unsafe_allow_html=True)
st.divider()

# ---------------------- File Uploads ----------------------
st.subheader("📥 Upload CSV Files")
col1, col2 = st.columns(2)
with col1:
    submissions_file = st.file_uploader("Upload Submissions CSV", type=["csv"])
with col2:
    answer_key_file = st.file_uploader("Upload Answer Key CSV", type=["csv"])

# ---------------------- Main Logic ----------------------
if submissions_file and answer_key_file:
    try:
        submissions = pd.read_csv(submissions_file)
        answer_key = pd.read_csv(answer_key_file)
    except Exception as e:
        st.error(f"Error reading uploaded files: {e}")
        st.stop()

    if "student_id" not in submissions.columns:
        st.error("❌ Missing 'student_id' column in submissions file.")
        st.stop()

    if not {"question", "correct_answer", "points"}.issubset(answer_key.columns):
        st.error("❌ Answer key must include 'question', 'correct_answer', and 'points' columns.")
        st.stop()

    # Build answer + weight maps
    answer_dict = dict(zip(answer_key["question"], answer_key["correct_answer"]))
    weight_dict = dict(zip(answer_key["question"], answer_key["points"]))
    total_points = sum(weight_dict.values())

    # Weighted grading logic
    def grade_student(row):
        score = 0
        for q, correct in answer_dict.items():
            if q in row and str(row[q]).strip().upper() == str(correct).strip().upper():
                score += weight_dict[q]
        return round((score / total_points) * 100, 2)

    st.subheader("⚙️ Grading in Progress...")
    submissions["score_percent"] = submissions.apply(grade_student, axis=1)

    # Analytics per question
    stats = []
    for q in answer_key["question"]:
        if q not in submissions.columns:
            continue
        total = len(submissions)
        correct = (submissions[q].astype(str).str.strip().str.upper() ==
                   str(answer_dict[q]).strip().upper()).sum()
        accuracy = round((correct / total) * 100, 2)
        stats.append({
            "question": q,
            "correct_answer": answer_dict[q],
            "points": weight_dict[q],
            "total_students": total,
            "correct_count": correct,
            "accuracy_percent": accuracy
        })

    question_stats = pd.DataFrame(stats)
    min_acc = question_stats["accuracy_percent"].min()
    hardest = question_stats[question_stats["accuracy_percent"] == min_acc]["question"].tolist()

    # ---------------------- Display Results ----------------------
    st.success("🎉 Grading Complete!")
    st.markdown(f"**Hardest Question(s):** {', '.join(hardest)} (Accuracy: {min_acc}%)")
    st.divider()

    # Two-column layout for results and analytics
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Student Scores")
        st.dataframe(submissions[["student_id", "score_percent"]], use_container_width=True)
    with col2:
        st.subheader("🧠 Question Statistics")
        st.dataframe(question_stats, use_container_width=True)

    st.divider()

    # ---------------------- Charts ----------------------
    st.subheader("📈 Visual Analytics")
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.histogram(
            submissions,
            x="score_percent",
            nbins=10,
            title="Distribution of Student Scores",
            labels={"score_percent": "Score (%)"},
            color_discrete_sequence=["#8e7dff"]
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(
            question_stats,
            x="question",
            y="accuracy_percent",
            title="Accuracy by Question",
            text="accuracy_percent",
            color_discrete_sequence=["#6EC1E4"],
            labels={"question": "Question", "accuracy_percent": "Accuracy (%)"}  # ✅ Capitalized axis labels
        )
        fig2.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ---------------------- Downloads ----------------------
    st.subheader("📥 Download Results")
    csv1 = submissions.to_csv(index=False).encode("utf-8")
    csv2 = question_stats.to_csv(index=False).encode("utf-8")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("⬇️ Download Graded Results", csv1, "graded_results.csv", "text/csv")
    with col2:
        st.download_button("⬇️ Download Question Stats", csv2, "question_stats.csv", "text/csv")

else:
    st.info("⬆️ Please upload both CSV files to begin grading.")

# ---------------------- Footer ----------------------
st.markdown("""
    <hr style="margin-top:3rem; margin-bottom:1rem; border: 1px solid #333;">
    <div style="text-align:center; color:#aaa; font-size:0.9rem;">
        Made with ❤️ by <strong style="color:#8e7dff;">Sneha Upreti</strong> |
        <a href="https://github.com/supreti3" target="_blank" style="color:#8e7dff; text-decoration:none;">
            GitHub
        </a> •
        <a href="https://www.linkedin.com/in/sneha-upreti/" target="_blank" style="color:#8e7dff; text-decoration:none;">
            LinkedIn
        </a>
    </div>
""", unsafe_allow_html=True)
