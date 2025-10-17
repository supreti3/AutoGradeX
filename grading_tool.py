import pandas as pd
import os
import time
import argparse
from rich.console import Console
from rich.progress import track
from rich.table import Table
from rich import box

console = Console()

def main():
    start_time = time.time()
    console.rule("[bold cyan]🚀 AutoGradeX – Weighted Grading and Analytics[/bold cyan]")

    # CLI argument support
    parser = argparse.ArgumentParser(description="AutoGradeX - Automated Weighted Grading Tool")
    parser.add_argument("--submissions", default="data/submissions.csv", help="Path to submissions CSV")
    parser.add_argument("--answer_key", default="data/answer_key.csv", help="Path to answer key CSV")
    parser.add_argument("--output_dir", default="output", help="Directory to save output files")
    args = parser.parse_args()

    # Verify folders and files
    if not os.path.exists(args.submissions):
        console.print(f"[red]❌ Submissions file not found at {args.submissions}[/red]")
        return
    if not os.path.exists(args.answer_key):
        console.print(f"[red]❌ Answer key file not found at {args.answer_key}[/red]")
        return

    # Load data
    try:
        submissions = pd.read_csv(args.submissions)
        answer_key = pd.read_csv(args.answer_key)
        console.print("[green]✅ Files loaded successfully[/green]")
    except Exception as e:
        console.print(f"[red]❌ Error reading files: {e}[/red]")
        return

    # Validate data
    if "student_id" not in submissions.columns:
        console.print("[red]❌ Missing 'student_id' column in submissions file[/red]")
        return
    if submissions["student_id"].isnull().any():
        console.print("[red]❌ Missing student IDs detected[/red]")
        return
    if submissions["student_id"].duplicated().any():
        console.print("[red]❌ Duplicate student IDs detected[/red]")
        return

    # Create answer maps
    answer_dict = dict(zip(answer_key["question"], answer_key["correct_answer"]))
    weight_dict = dict(zip(answer_key["question"], answer_key["points"]))
    total_points = sum(weight_dict.values())

    # Weighted grading function
    def grade_student(row):
        score = 0
        for q, correct in answer_dict.items():
            if q in row and str(row[q]).strip().upper() == str(correct).strip().upper():
                score += weight_dict[q]
        return round((score / total_points) * 100, 2)

    console.print("\n[bold yellow]📊 Grading students...[/bold yellow]")
    submissions["score_percent"] = [
        grade_student(row) for _, row in track(submissions.iterrows(), total=len(submissions))
    ]

    # Question-level analytics
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
    min_accuracy = question_stats["accuracy_percent"].min()
    hardest = question_stats[question_stats["accuracy_percent"] == min_accuracy]["question"].tolist()

    # Output
    os.makedirs(args.output_dir, exist_ok=True)
    graded_path = os.path.join(args.output_dir, "graded_results.csv")
    stats_path = os.path.join(args.output_dir, "question_stats.csv")

    submissions[["student_id", "score_percent"]].to_csv(graded_path, index=False)
    question_stats.to_csv(stats_path, index=False)

    # Display summary table
    table = Table(title="AutoGradeX Summary", box=box.DOUBLE_EDGE, header_style="bold magenta")
    table.add_column("Metric", justify="right")
    table.add_column("Value", justify="left")
    table.add_row("Total Students", str(len(submissions)))
    table.add_row("Total Points", str(total_points))
    table.add_row("Hardest Question(s)", ", ".join(hardest))
    table.add_row("Lowest Accuracy", f"{min_accuracy}%")
    table.add_row("Results CSV", graded_path)
    table.add_row("Question Stats CSV", stats_path)
    console.print(table)

    elapsed = round(time.time() - start_time, 2)
    console.print(f"\n[green]✅ Grading completed in {elapsed} seconds![/green]")
    console.rule("[bold cyan]End of Report[/bold cyan]")

if __name__ == "__main__":
    main()
