
# AutoGradeX

AutoGradeX is a Python-based automated grading tool that processes student submissions and answer keys from CSV files. It applies weighted scoring, validates data, and visualizes performance analytics using Streamlit and Plotly.

## Features
- Upload student submissions and answer key CSV files
- Weighted grading based on point values per question
- Validation for missing or duplicate student IDs
- Displays overall results and hardest questions
- Generates downloadable CSV reports for grades and question stats
- Interactive Streamlit dashboard with data visualizations

## Tech Stack
Python, Pandas, Streamlit, Plotly, CSV

## Setup Instructions

1. Clone the repository
```

git clone [https://github.com/supreti3/AutoGradeX.git](https://github.com/supreti3/AutoGradeX.git)
cd AutoGradeX

```

2. Install dependencies
```

pip install -r requirements.txt

```

3. Run the Streamlit app
```

python -m streamlit run autogradex_app.py

```

4. Access the app
Open http://localhost:8501 in your browser.

## Folder Structure
```

AutoGradeX/
│
├── data/                # Input CSV files (submissions, answer_key)
├── output/              # Generated graded results and question stats
├── grading_tool.py      # CLI-based grading script
├── autogradex_app.py    # Streamlit dashboard application
└── README.md

```

