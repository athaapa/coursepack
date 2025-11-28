import json
import os
import subprocess
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import typing_extensions as typing
from dotenv import load_dotenv
from google import genai
from google.genai import types
from icalendar import Calendar, Event

# --- Templates ---

# Common LaTeX Preamble for Scheme styling
SCHEME_PREAMBLE = r"""
\usepackage{xcolor}
\definecolor{keywordblue}{rgb}{0.0, 0.0, 0.6}
\definecolor{commentgreen}{rgb}{0.0, 0.4, 0.0}

\lstdefinelanguage{Scheme}{
  morekeywords={define,lambda,if,cond,else,let,let*,letrec,begin,quote,car,cdr,
    cons,list,apply,eval,define-syntax,syntax-rules,delay,and,or,case,do,set!},
  sensitive=true,
  morecomment=[l]{;},
  morestring=[b]"
}

% Configure Scheme listings
\lstdefinestyle{scheme}{
  language=Scheme,
  basicstyle=\fontsize{14pt}{16pt}\ttfamily,
  keywordstyle=\color{keywordblue}\bfseries,
  showstringspaces=false,
  breaklines=true,
  frame=none,
  numbers=none,
  xleftmargin=0pt,
  tabsize=2
}

\lstset{style=scheme}
"""

# One-shot example for Homework to ensure consistent formatting
HW_ONE_SHOT_EXAMPLE = r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{listings}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{xcolor}

% --- SCHEME LISTING STYLE START ---
\definecolor{keywordblue}{rgb}{0.0, 0.0, 0.6}
\definecolor{commentgreen}{rgb}{0.0, 0.4, 0.0}

\lstdefinelanguage{Scheme}{
  morekeywords={define,lambda,if,cond,else,let,let*,letrec,begin,quote,car,cdr,
    cons,list,apply,eval,define-syntax,syntax-rules,delay,and,or,case,do,set!},
  sensitive=true,
  morecomment=[l]{;},
  morestring=[b]"
}

\lstdefinestyle{scheme}{
  language=Scheme,
  basicstyle=\ttfamily,
  keywordstyle=\color{keywordblue}\bfseries,
  commentstyle=\color{commentgreen}\itshape,
  showstringspaces=false,
  breaklines=true,
  frame=none,
  numbers=none,
  xleftmargin=2em,
  tabsize=2
}

\lstset{style=scheme}
% --- SCHEME LISTING STYLE END ---

\title{Course Assignment}
\author{}
\date{}

\begin{document}
\maketitle

\section*{Instructions}
Please solve the following problems using Scheme.

\section*{Problem 1: Linear Recursion (10 points)}
Write a Scheme procedure \texttt{(factorial n)} that computes $n!$ using a linear recursive process.

\begin{lstlisting}
(define (factorial n)
  (if (= n 0)
      1
      (* n (factorial (- n 1)))))
\end{lstlisting}

\section*{Problem 2: Box and Pointer (5 points)}
Draw the box-and-pointer diagram for the list \texttt{(list 1 2 3)}.
\vspace{3cm} % Space for student drawing

\end{document}
"""

# One-shot example for Exams to ensure consistent formatting
EXAM_ONE_SHOT_EXAMPLE = r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{listings}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{enumitem}
\usepackage{xcolor}

% --- SCHEME LISTING STYLE START ---
\definecolor{keywordblue}{rgb}{0.0, 0.0, 0.6}
\definecolor{commentgreen}{rgb}{0.0, 0.4, 0.0}

\lstdefinelanguage{Scheme}{
  morekeywords={define,lambda,if,cond,else,let,let*,letrec,begin,quote,car,cdr,
    cons,list,apply,eval,define-syntax,syntax-rules,delay,and,or,case,do,set!},
  sensitive=true,
  morecomment=[l]{;},
  morestring=[b]"
}

\lstdefinestyle{scheme}{
  language=Scheme,
  basicstyle=\ttfamily,
  keywordstyle=\color{keywordblue}\bfseries,
  commentstyle=\color{commentgreen}\itshape,
  showstringspaces=false,
  breaklines=true,
  frame=none,
  numbers=none,
  xleftmargin=2em,
  tabsize=2
}

\lstset{style=scheme}
% --- SCHEME LISTING STYLE END ---

\begin{document}

\begin{center}
    \Large{\textbf{Course: Structure and Interpretation of Computer Programs}} \\
    \large{\textbf{Final Examination}} \\
    \normalsize{\textbf{Semester: Spring 2024}}
\end{center}

\vspace{1cm}

\textbf{Instructions:} Please read each question carefully.

\hrulefill

\section*{Question 1 (Short Answer) [5 pts]}
Explain the concept of a "black-box abstraction".

\textbf{Answer:}
\vspace{3cm}

\hrulefill

\section*{Question 2 (Coding) [10 pts]}
Implement a Scheme function \texttt{is-prime?}.

\begin{lstlisting}
(define (is-prime? n)
  ; Implement the primality test here.
)
\end{lstlisting}

\textbf{Answer:}
\vspace{6cm}

\hrulefill

\end{document}
"""

GITHUB_WORKFLOW_TEMPLATE = """
name: Verify Homework
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0 # Fetch full history to allow diffing
      - name: Install Guile (Scheme)
        run: |
          sudo apt-get update
          sudo apt-get install -y guile-3.0
      - name: Run Tests (Submitted Week Only)
        run: |
          # 1. Identify Changed Files
          if [ "${{ github.event_name }}" == "pull_request" ]; then
            # Compare PR branch vs base
            CHANGED_FILES=$(git diff --name-only origin/${{ github.base_ref }} HEAD)
          else
            # Compare vs previous commit (handle initial commit case)
            if git rev-parse HEAD^ >/dev/null 2>&1; then
              CHANGED_FILES=$(git diff --name-only HEAD^ HEAD)
            else
              CHANGED_FILES=$(git ls-tree -r HEAD --name-only)
            fi
          fi

          echo "Modified files:"
          echo "$CHANGED_FILES"

          # 2. Extract Unique Modified Homework Directories
          # Looks for patterns like 'homework/week_01/...'
          CHANGED_WEEKS=$(echo "$CHANGED_FILES" | grep -o "homework/week_[0-9]*" | sort -u)

          if [ -z "$CHANGED_WEEKS" ]; then
            echo "No homework files modified. Skipping autograder."
            exit 0
          fi

          # 3. Run Tests for Modified Weeks
          FAILED=0
          for week_dir in $CHANGED_WEEKS; do
            # Find the test file in this directory (e.g., test_week_01.scm)
            TEST_FILE=$(find "$week_dir" -name "test_*.scm" | head -n 1)

            if [ -f "$TEST_FILE" ]; then
              echo "----------------------------------------"
              echo "Testing Submission: $week_dir"
              echo "Running $TEST_FILE..."

              if ! guile --no-auto-compile "$TEST_FILE"; then
                echo "❌ FAILED: $TEST_FILE"
                FAILED=1
              else
                echo "✅ PASSED: $TEST_FILE"
              fi
            else
              echo "Warning: No test file found in $week_dir"
            fi
          done

          exit $FAILED
"""

STUDENT_README_TEMPLATE = """
# Course Homework Repository

Welcome to your course homework repository. This repository contains all your weekly assignments, verifying tests, and exam materials.

## Prerequisites

You need **Guile Scheme** installed to run the code and tests.
- **Mac (Homebrew):** `brew install guile`
- **Ubuntu/Debian:** `sudo apt-get install guile-3.0`
- **Windows:** Use WSL (Ubuntu) or a Guile installer.

## How to Submit Homework

1. **Navigate** to the current week's folder (e.g., `homework/week_01/`).
2. **Open** the solution file (e.g., `solution_week_01.scm`). It will contain empty function definitions or placeholders.
3. **Implement** your solution in Scheme.
4. **Test Locally** by running the test file:
   ```bash
   guile test_week_01.scm
   ```
   * If it prints `PASS`, you are good!
   * If it prints `FAIL`, check your logic.
5. **Submit** by pushing your changes to GitHub:
   ```bash
   git add .
   git commit -m "Solved Week 1"
   git push origin main
   ```
6. **Verify** on GitHub. Go to the "Actions" tab in your repository to see if the autograder passed.

## Structure

* `homework/`: Weekly assignments.
    * `assignment.tex`: The PDF problem set (compile with LaTeX).
    * `solution_week_X.scm`: **EDIT THIS FILE**.
    * `test_week_X.scm`: The verification script.
* `exams/`: Midterm and Final Exam PDFs.
"""

# --- Schema Definitions ---


class Lecture(typing.TypedDict):
    """Represents a lecture in the course plan."""

    title: str
    topics: List[str]


class Homework(typing.TypedDict):
    """Represents homework for a week."""

    exercises: List[str]
    description: str


class WeekPlan(typing.TypedDict):
    """Represents the plan for a single week."""

    lectures: List[Lecture]
    homework: Homework
    key_concepts: List[str]


# --- Helper Functions ---


def _ensure_directory(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def _generate_content_with_ai(
    client: genai.Client, model: str, prompt: str, mime_type: str = "text/plain"
) -> str:
    """Helper to generate text content (LaTeX, Scheme, etc.) via AI."""
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type=mime_type),
        )
        text = response.text.strip()

        # Clean up Markdown backticks if present
        if text.startswith("```"):
            lines = text.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        return text
    except Exception as e:
        print(f"Error generating content: {e}")
        return f"; Error generating content: {e}"


def _compile_latex(file_path: Path) -> None:
    """Compiles a .tex file to PDF using pdflatex."""
    try:
        print(f"Compiling {file_path.name}...")
        # Run pdflatex.
        # -interaction=nonstopmode prevents it from hanging on errors.
        # -output-directory ensures output stays with source.
        subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                f"-output-directory={file_path.parent}",
                str(file_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,  # Suppress noisy output
            stderr=subprocess.PIPE,
        )
        print(f"✓ PDF generated for {file_path.name}")
    except FileNotFoundError:
        print("⚠ pdflatex not found. Skipping PDF generation.")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to compile {file_path.name}. Check LaTeX source.")
    except Exception as e:
        print(f"✗ Error compiling LaTeX: {e}")


# --- Core Logic ---


def generate_course_artifacts(
    client: genai.Client,
    plan: Dict[str, Any],
    config: Dict[str, Any],
    output_dir: str = "course_repo",
) -> None:
    """Generates the physical files for the course (LaTeX, Tests, Workflows)."""

    base_path = Path(output_dir)
    _ensure_directory(base_path)

    print(f"\n--- Generating Course Repository in '{output_dir}' ---")

    # 1. GitHub Workflow
    workflow_path = base_path / ".github" / "workflows"
    _ensure_directory(workflow_path)
    with open(workflow_path / "verify.yml", "w") as f:
        f.write(GITHUB_WORKFLOW_TEMPLATE)
    print("✓ Created GitHub Workflow (Guile Scheme)")

    # 2. Student README (Instructions)
    with open(base_path / "README.md", "w") as f:
        f.write(STUDENT_README_TEMPLATE)
    print("✓ Created Student README.md")

    # 3. Iterate Weeks for Homework
    weeks = plan.get("weeks", [])
    model_name = "gemini-2.5-flash-lite"  # Use a fast model for bulk generation

    all_topics = []  # Collect topics for exam generation

    for week in weeks:
        week_num = week["week"]
        topics = week.get("key_concepts", [])
        all_topics.extend(topics)

        week_dir = base_path / "homework" / f"week_{week_num:02d}"
        _ensure_directory(week_dir)

        # A. Generate COMPLETE LaTeX Document (Scheme Context)
        hw_prompt = f"""
        Act as a Computer Science professor teaching SICP.
        Generate a COMPLETE LaTeX document (including preamble, \\begin{{document}}, and \\end{{document}}) for a Scheme programming assignment.

        Topics: {", ".join(topics)}
        Textbook Exercises: {", ".join(week["homework"]["exercises"])}
        Description: {week["homework"]["description"]}

        Format requirements:
        - Use clean LaTeX.
        - Include 3-4 distinct problems that require writing Scheme code.
        - **MIMIC THE FOLLOWING FORMATTING STYLE STRICTLY (Same packages, header style, colors, listings settings):**
        - Do not include extraneous information such as name, date, or student ID.
        - Do not include a due date.
        - The title of the homework should be "Homework {week_num}"

        {HW_ONE_SHOT_EXAMPLE}
        """

        latex_code = _generate_content_with_ai(client, model_name, hw_prompt)

        tex_file = week_dir / "assignment.tex"
        with open(tex_file, "w") as f:
            f.write(latex_code)

        # Compile PDF
        # _compile_latex(tex_file)

        # B. Generate Verification Code (Scheme Test)
        test_prompt = f"""
        Act as a QA Engineer for a Scheme course.
        Create a Scheme test file to verify the homework concepts for this week.

        Topics: {", ".join(topics)}

        Requirements:
        1. The test file MUST load the student solution: `(load "solution_week_{week_num}.scm")`.
        2. It MUST define simple test cases using standard Scheme comparisons.
        3. It MUST print "PASS: <testname>" or "FAIL: <testname>".
        4. CRITICAL: If any test fails, the script MUST exit with `(exit 1)`. If all pass, `(exit 0)`.

        STRICT FORMATTING RULES:
        - Return ONLY the Scheme code.
        - Do NOT use markdown code blocks (no backticks).
        - Do NOT include comments saying "Assume solution.py exists" or "Placeholder functions".
        - Do NOT use Python comments (#) or file extensions (.py). Use Scheme comments (;).
        - Assume `solution_week_{week_num}.scm` is the ONLY source of truth for the function implementations.
        """

        test_code = _generate_content_with_ai(client, model_name, test_prompt)

        # Create a dummy solution file so tests pass (or fail gracefully)
        with open(week_dir / f"solution_week_{week_num}.scm", "w") as f:
            f.write(f"; Student solution for Week {week_num}\n\n(define (solve) #t)\n")

        with open(week_dir / f"test_week_{week_num}.scm", "w") as f:
            f.write(test_code)

        print(f"✓ Generated Scheme Artifacts for Week {week_num}")

    # 4. Generate Exams (2 Midterms, 1 Final)
    exams_dir = base_path / "exams"
    _ensure_directory(exams_dir)

    total_weeks = len(weeks)
    if total_weeks > 0:
        # Determine Checkpoints
        m1_idx = total_weeks // 3
        m2_idx = (total_weeks * 2) // 3

        exam_configs = [
            ("Midterm 1", all_topics[: m1_idx * 3]),  # Rough approximation of topics
            ("Midterm 2", all_topics[m1_idx * 3 : m2_idx * 3]),
            ("Final Exam", all_topics),
        ]

        for title, topics_subset in exam_configs:
            print(f"... Generating {title}")
            exam_prompt = f"""
            Act as a Computer Science professor teaching SICP.
            Generate a COMPLETE LaTeX document for a {title}.

            Topics Covered: {", ".join(topics_subset[:20])}... (list truncated)

            Requirements:
            - 5 conceptual questions about Scheme / Lisp.
            - 2 coding questions (write Scheme code on paper).
            - Formal academic tone.
            - **MIMIC THE FOLLOWING FORMATTING STYLE STRICTLY (Same packages, colors, listings settings):**

            {EXAM_ONE_SHOT_EXAMPLE}
            """

            exam_code = _generate_content_with_ai(client, model_name, exam_prompt)

            filename = title.lower().replace(" ", "_") + ".tex"
            tex_file = exams_dir / filename
            with open(tex_file, "w") as f:
                f.write(exam_code)

            # Compile PDF
            # _compile_latex(tex_file)


def export_calendar(
    plan: Dict[str, Any], config: Dict[str, Any], filename: str = "plan.ics"
) -> None:
    """Exports the course plan to an iCalendar (.ics) file."""
    cal = Calendar()
    cal.add("prodid", "-//Coursepack AI Planner//coursepack.dev//")
    cal.add("version", "2.0")

    quarter_conf = config.get("quarter", {})
    start_time_str = quarter_conf.get("lecture_start_time", "12:30")
    duration_min = quarter_conf.get("lecture_duration_minutes", 50)

    try:
        h, m = map(int, start_time_str.split(":"))
        lecture_start_time = time(h, m)
    except ValueError:
        lecture_start_time = time(12, 30)

    weeks = plan.get("weeks", [])
    total_weeks = len(weeks)

    # Calculate Exam Weeks
    exam_indices = {
        total_weeks // 3: "Midterm 1",
        (total_weeks * 2) // 3: "Midterm 2",
        total_weeks: "Final Exam",
    }

    for week in weeks:
        week_num = week["week"]
        dates = week.get("dates", {})
        available_days = ["monday", "wednesday", "friday"]
        lectures = week.get("lectures", [])

        # 1. Lectures
        for lecture, day_key in zip(lectures, available_days):
            date_str = dates.get(day_key)
            if not date_str:
                continue

            try:
                lecture_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                dt_start = datetime.combine(lecture_date, lecture_start_time)
                dt_end = dt_start + timedelta(minutes=duration_min)

                event = Event()
                event.add("summary", f"Lecture: {lecture['title']}")
                event.add("description", f"Topics: {', '.join(lecture['topics'])}")
                event.add("dtstart", dt_start)
                event.add("dtend", dt_end)
                cal.add_component(event)
            except ValueError:
                pass

        # 2. Homework Due (Sunday)
        monday_str = dates.get("monday")
        if monday_str and week.get("homework"):
            try:
                monday_date = datetime.strptime(monday_str, "%Y-%m-%d").date()
                sunday_date = monday_date + timedelta(days=6)
                due_dt = datetime.combine(sunday_date, time(23, 59))

                event = Event()
                event.add(
                    "summary", f"HW Due: {week.get('section', 'Week ' + str(week_num))}"
                )
                event.add("dtstart", due_dt)
                event.add("dtend", due_dt)
                cal.add_component(event)
            except ValueError:
                pass

        # 3. Exams
        # We schedule exams on the Friday of their respective weeks
        if week_num in exam_indices:
            exam_name = exam_indices[week_num]
            friday_str = dates.get("friday")
            if friday_str:
                try:
                    friday_date = datetime.strptime(friday_str, "%Y-%m-%d").date()
                    # Schedule exam at lecture time (or slightly longer)
                    exam_start = datetime.combine(friday_date, lecture_start_time)
                    exam_end = exam_start + timedelta(minutes=90)  # 1.5 hours for exam

                    event = Event()
                    event.add("summary", f"EXAM: {exam_name}")
                    event.add("description", "Location: TBD")
                    event.add("dtstart", exam_start)
                    event.add("dtend", exam_end)
                    event.add("priority", 1)  # High priority
                    cal.add_component(event)
                except ValueError:
                    pass

    with open(filename, "wb") as f:
        f.write(cal.to_ical())
    print(f"Calendar exported to {filename}")


def generate_plan(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a course plan, calendar, and full course repository."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY") or config.get("gemini_api_key")
    if not api_key:
        raise ValueError(
            "Missing GEMINI_API_KEY in .env or gemini_api_key in configuration."
        )

    client = genai.Client(api_key=api_key)

    plan = {"weeks": []}
    current_date = datetime.fromisoformat(config["quarter"]["start"])

    # --- 1. Plan Generation (Schedule) ---
    subsections = config.get("book", {}).get("subsections", [])
    sections_map: Dict[str, List[str]] = {}

    # Simple grouper
    for sub in subsections:
        try:
            numbering = sub.split(" ")[0]
            parts = numbering.split(".")
            section_key = f"{parts[0]}.{parts[1]}" if len(parts) >= 2 else numbering
        except:
            section_key = "General"
        if section_key not in sections_map:
            sections_map[section_key] = []
        sections_map[section_key].append(sub)

    print(f"Generating plan for {len(sections_map)} sections...")

    for i, (section_key, section_subs) in enumerate(sections_map.items()):
        subs_list_str = "\n".join(f"- {s}" for s in section_subs)
        prompt = f"""
        Context: Generating a course plan for SICP. Section: "{section_key}"
        Subsections: {subs_list_str}
        Task: Create a 1-week lesson plan covering this section.
        """

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", response_schema=WeekPlan
                ),
            )
            week_data = json.loads(response.text)
            week_data.update(
                {
                    "section": section_key,
                    "week": i + 1,
                    "dates": {
                        "monday": current_date.date().isoformat(),
                        "wednesday": (current_date + timedelta(days=2))
                        .date()
                        .isoformat(),
                        "friday": (current_date + timedelta(days=4)).date().isoformat(),
                    },
                }
            )
            plan["weeks"].append(week_data)
            print(f"✓ Planned Week {i + 1}")
        except Exception as e:
            print(f"✗ Error Planning Week {i + 1}: {e}")

        current_date += timedelta(weeks=1)

    # --- 2. Exports ---
    with open("plan.json", "w") as f:
        json.dump(plan, f, indent=2)

    export_calendar(plan, config)

    # --- 3. Artifact Generation (Repo, LaTeX, Tests) ---
    generate_course_artifacts(client, plan, config)

    return plan


if __name__ == "__main__":
    # Example usage
    try:
        with open("config.json") as f:
            config = json.load(f)
        generate_plan(config)
    except FileNotFoundError:
        print("config.json not found.")
