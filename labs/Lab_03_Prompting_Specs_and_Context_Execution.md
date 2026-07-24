# Lab 03 - Prompt Engineering, Specifications, and Context Management

**Course:** Advanced Software Development with Agentic AI (ASD)  
**Theme:** Prompt Engineering, Specifications, and Context Management  
**Primary IDE:** VS Code (Optional IDE: AWS Kiro)  
**AI Runtime:** Ollama  
**Implementation Agent:** Qwen 2.5 0.5B  
**Review Agent:** Llama 3.1 8B  
**Duration:** 60 minutes

---

## 1. Overview

<details>
<summary>Goal</summary>

Extend Lab 02 by externalizing prompt text into files and adding context-based response flow.

</details>

<details>
<summary>Agentic Workflow</summary>

```text
PLAN -> ACT -> OBSERVE -> PROMPT AGENT -> REVIEW AGENT -> HUMAN REVIEW -> ADAPT
```

</details>

<details>
<summary>Expected Results</summary>

By the end of this lab, students should have:

- Reused the Lab 02 application
- Created prompt files under prompts/
- Added and tested POST /ask-with-context
- Updated the HTMX frontend with a context form
- Loaded prompts from files in app.py
- Executed the prompt and review loop in agentic_loop.py
- Completed boundary/context tests
- Recorded evidence

</details>

---

## 2. Prerequisites and Configuration

<details>
<summary>Prerequisites</summary>

Complete first:

- Lab 01
- Lab 02
- AI Agent Configuration Guide: [AI Agent Configuration Guide](./AI_Agent_Configuration_Guide.md)

Required models:

- qwen2.5:0.5b
- llama3.1:8b

Verify:

```bash
ollama list
```

</details>

---

## 3. Scenario Setup

<details>
<summary>Project Structure</summary>

```text
enrolment-app-open-ai/
├── prompts/
│   ├── system_prompt.txt
│   ├── task_prompt.txt
│   ├── context_prompt.txt
│   ├── review_prompt.txt
│   ├── agent_system_prompt.txt
│   ├── agent_task_prompt.txt
│   └── agent_review_prompt.txt
├── app.py
├── agentic_loop.py
└── templates/
    └── index.html
```

</details>

<details>
<summary>Create Prompt Folder and Files in the App Folder</summary>

Linux/macOS:

```bash
cd enrolment-app-open-ai
mkdir -p prompts
touch prompts/system_prompt.txt prompts/task_prompt.txt prompts/context_prompt.txt prompts/review_prompt.txt
touch prompts/agent_system_prompt.txt prompts/agent_task_prompt.txt prompts/agent_review_prompt.txt
```

Windows PowerShell:

```powershell
cd enrolment-app-open-ai
mkdir prompts
New-Item prompts/system_prompt.txt -ItemType File
New-Item prompts/task_prompt.txt -ItemType File
New-Item prompts/context_prompt.txt -ItemType File
New-Item prompts/review_prompt.txt -ItemType File
New-Item prompts/agent_system_prompt.txt -ItemType File
New-Item prompts/agent_task_prompt.txt -ItemType File
New-Item prompts/agent_review_prompt.txt -ItemType File
```

</details>

---

## 4. Application Setup and Development

<details>
<summary>Use Lab 02 App</summary>

Confirm these exist:

- requirements.txt
- .env
- .gitignore
- enrolment.db
- css/styles.css
- templates/index.html

Reuse Lab 02 application. Do not create a new app.

</details>

<details>
<summary>Prompt Specification Files</summary>

prompts/system_prompt.txt

```text
You are a software engineering assistant.

Use only supplied context.

Do not invent database fields.
Do not invent endpoints.
Do not invent functionality.

If information is unavailable, say:

Information unavailable in supplied context.
```

prompts/task_prompt.txt

```text
Explain the Student Enrolment App.

Use only supplied context.

Maximum 120 words.
```

prompts/context_prompt.txt

```text
Application Name:
Student Enrolment App

Database Fields:
- student_id
- student_name
- subject_code

Endpoints:
- GET /students
- GET /students/{student_id}
- GET /students/by-id
- GET /students/by-subject
- POST /ask
- POST /ask-with-context
```

prompts/review_prompt.txt

```text
Review the generated answer.

Return:

Risk:
Correction:
Retest:
```

prompts/agent_system_prompt.txt

```text
You are a software engineering implementation assistant.

Use only supplied evidence.
```

prompts/agent_task_prompt.txt

```text
Review validation evidence.

Recommend one improvement.

Return exactly two bullet points.
```

prompts/agent_review_prompt.txt

```text
Review the implementation recommendation.

Return:

Risk:
Correction:
Retest:
```

</details>

<details>
<summary>Backend Flask API</summary>

```python
from flask import Flask, render_template, request, send_from_directory
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
import sqlite3
import os
import shutil
import subprocess
import threading

load_dotenv()

DATABASE_NAME = "enrolment.db"

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")

app = Flask(__name__)

client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="ollama"
)

PROMPT_DIR = Path(__file__).with_name("prompts")


def load_prompt(filename):
    prompt_path = PROMPT_DIR / filename
    return prompt_path.read_text(encoding="utf-8").strip()


def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/css/<path:filename>")
def css(filename):
    return send_from_directory("css", filename)


@app.route("/students")
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        "SELECT student_id, student_name, subject_code FROM students"
    ).fetchall()
    conn.close()

    html = "<ul>"
    for student in students:
        html += (
            f"<li>"
            f"{student['student_id']} - "
            f"{student['student_name']} - "
            f"{student['subject_code']}"
            f"</li>"
        )
    html += "</ul>"

    return html


@app.route("/students/<int:student_id>")
def get_student(student_id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT student_id, student_name, subject_code FROM students WHERE student_id = ?",
        (student_id,)
    ).fetchone()
    conn.close()

    if student is None:
        return "<p>Student not found.</p>", 404

    return (
        f"<p>"
        f"ID: {student['student_id']}<br>"
        f"Name: {student['student_name']}<br>"
        f"Subject: {student['subject_code']}"
        f"</p>"
    )


@app.route("/students/by-id")
def get_student_by_id():
    student_id_raw = request.args.get("student_id", "").strip()

    if not student_id_raw:
        return "<p>Student ID is required.</p>", 400

    if not student_id_raw.isdigit():
        return "<p>Student ID must be a positive integer.</p>", 400

    return get_student(int(student_id_raw))


@app.route("/students/by-subject")
def get_students_by_subject():
    subject_code = request.args.get("subject_code", "").strip().upper()

    if not subject_code:
        return "<p>Subject code is required.</p>", 400

    conn = get_db_connection()
    students = conn.execute(
        "SELECT student_id, student_name, subject_code FROM students WHERE subject_code = ?",
        (subject_code,)
    ).fetchall()
    conn.close()

    if not students:
        return f"<p>No students found for subject code {subject_code}.</p>", 404

    html = "<ul>"
    for student in students:
        html += (
            f"<li>"
            f"{student['student_id']} - "
            f"{student['student_name']} - "
            f"{student['subject_code']}"
            f"</li>"
        )
    html += "</ul>"

    return html


@app.route("/ask", methods=["POST"])
def ask_local_agent():
    question = request.form.get("question", "").strip()

    if not question:
        return "<p>Question is required.</p>", 400

    try:
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise software engineering assistant. "
                        "Answer in one short paragraph unless asked otherwise."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=200,
            temperature=0.2,
        )

        answer = response.choices[0].message.content

        return f"<p>{answer}</p>"

    except Exception as exc:
        return (
            "<p>Local AI agent request failed. "
            "Check that Ollama is running and that qwen2.5:0.5b is installed.</p>"
            f"<pre>{exc}</pre>",
            503,
        )


@app.route("/ask-with-context", methods=["POST"])
def ask_with_context():
    question = request.form.get("question", "").strip()

    if not question:
        return "<p>Question is required.</p>", 400

    try:
        system_prompt = load_prompt("system_prompt.txt")
        task_prompt = load_prompt("task_prompt.txt")
        context_prompt = load_prompt("context_prompt.txt")

        final_prompt = f"""
{task_prompt}

{context_prompt}

User Question:

{question}
"""

        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": final_prompt
                }
            ],
            max_tokens=300,
            temperature=0.2,
        )

        answer = response.choices[0].message.content
        return f"<p>{answer}</p>"

    except Exception as exc:
        return (
            "<p>Context-aware request failed.</p>"
            f"<pre>{exc}</pre>",
            503,
        )


def launch_chrome(url):
    chrome_candidates = [
        "google-chrome",
        "google-chrome-stable",
        "chromium-browser",
        "chromium",
    ]

    for browser in chrome_candidates:
        executable = shutil.which(browser)
        if executable:
            subprocess.Popen(
                [executable, "--new-window", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True

    return False


if __name__ == "__main__":
    if os.getenv("FLASK_OPEN_CHROME", "1") == "1":
        is_reloader_process = os.environ.get("WERKZEUG_RUN_MAIN") == "true"
        if is_reloader_process or not app.debug:
            threading.Timer(1.0, launch_chrome, args=("http://127.0.0.1:5000",)).start()

    app.run(debug=True)
```

</details>

<details>
<summary>HTMX Frontend</summary>

```html
<!DOCTYPE html>
<html>
<head>
    <title>Student Enrolment App</title>
    <script src="https://unpkg.com/htmx.org@2.0.4"></script>
    <link rel="stylesheet" href="/css/styles.css">
</head>
<body>
<main class="app-shell">
    <header class="app-header">
        <h1>Student Enrolment App</h1>
        <p>Use HTMX to query students and ask the local model.</p>
    </header>

    <div class="layout-grid">
        <section class="card card-left">
            <h2>Students</h2>

            <button id="toggle-students-btn" type="button">
                Show All Students
            </button>

            <div id="students-result" class="panel is-hidden"></div>

            <h2>Find Student by ID</h2>

            <form hx-get="/students/by-id" hx-target="#student-result">
                <label for="student_id">Student ID</label>
                <input id="student_id" name="student_id" type="number" min="1" placeholder="Enter student ID">
                <button type="submit">Get Student</button>
            </form>

            <div id="student-result" class="panel"></div>

            <h2>Find Students by Subject Code</h2>

            <form hx-get="/students/by-subject" hx-target="#subject-result">
                <label for="subject_code">Subject Code</label>
                <input id="subject_code" name="subject_code" type="text" placeholder="Example: ASD101">
                <button type="submit">Find Students</button>
            </form>

            <div id="subject-result" class="panel"></div>
        </section>

        <section class="card card-right">
            <h2>Ask Local AI Agent</h2>

            <form hx-post="/ask" hx-target="#agent-result">
                <label for="question">Question</label>
                <textarea id="question" name="question" rows="7">Explain what this Student Enrolment App does in one short paragraph.</textarea>
                <button type="submit">Ask Local Agent</button>
            </form>

            <div id="agent-result" class="panel"></div>

            <h2>Ask With Context</h2>

            <form hx-post="/ask-with-context" hx-target="#context-result">
                <label for="context-question">Question</label>
                <textarea id="context-question" name="question" rows="4">Explain the Student Enrolment App.</textarea>
                <button type="submit">Ask With Context</button>
            </form>

            <div id="context-result" class="panel"></div>
        </section>
    </div>
</main>

<script>
const toggleStudentsBtn = document.getElementById("toggle-students-btn");
const studentsPanel = document.getElementById("students-result");

toggleStudentsBtn.addEventListener("click", () => {
    const isHidden = studentsPanel.classList.contains("is-hidden");

    if (isHidden) {
        studentsPanel.classList.remove("is-hidden");
        toggleStudentsBtn.textContent = "Hide All Students";

        if (!studentsPanel.dataset.loaded) {
            htmx.ajax("GET", "/students", {
                target: "#students-result",
                swap: "innerHTML"
            });
            studentsPanel.dataset.loaded = "true";
        }
    } else {
        studentsPanel.classList.add("is-hidden");
        toggleStudentsBtn.textContent = "Show All Students";
    }
});
</script>

</body>
</html>
```

</details>

---

## 5. Application Testing

<details>
<summary>Run the Python-HTMX app <code>app.py</code></summary>

```bash
cd enrolment-app-open-ai
.venv/bin/python app.py
```

The app opens `http://127.0.0.1:5000` in Chrome automatically on startup.

To disable auto-open for one run:

```bash
FLASK_OPEN_CHROME=0 .venv/bin/python app.py
```

```powershell
$env:FLASK_OPEN_CHROME="0"
.venv\Scripts\python app.py
```

Open:

```text
http://127.0.0.1:5000
```

</details>

<details>
<summary>Endpoints Testing</summary>

| Function | Browser Validation | API Validation |
|---|---|---|
| Home Page | `http://127.0.0.1:5000` | N/A |
| View Students | `http://127.0.0.1:5000/students` | `curl http://127.0.0.1:5000/students` |
| Get Student | `http://127.0.0.1:5000/students/1` | `curl http://127.0.0.1:5000/students/1` |
| Get Student by ID | `http://127.0.0.1:5000/students/by-id?student_id=1` | `curl "http://127.0.0.1:5000/students/by-id?student_id=1"` |
| Student Not Found | `http://127.0.0.1:5000/students/99` | `curl http://127.0.0.1:5000/students/99` |
| Search by Subject | `http://127.0.0.1:5000/students/by-subject?subject_code=ASD101` | `curl "http://127.0.0.1:5000/students/by-subject?subject_code=ASD101"` |
| Subject Not Found | `http://127.0.0.1:5000/students/by-subject?subject_code=ABC999` | `curl "http://127.0.0.1:5000/students/by-subject?subject_code=ABC999"` |
| AI Assistant | Submit home page form | `curl -X POST http://127.0.0.1:5000/ask -d "question=Test"` |
| Context Assistant | Submit context form | `curl -X POST http://127.0.0.1:5000/ask-with-context -d "question=What endpoints exist?"` |

Expected:

```text
All endpoints return valid responses.
```

</details>

<details>
<summary>NFR Validation</summary>

Requirement:

```text
GET /students/by-subject?subject_code=ASD101 returns within 500 ms.
```

Pass condition:

```text
At least 19 out of 20 requests complete in <= 0.500 seconds.
```

Linux/macOS:

```bash
for i in $(seq 1 20); do
    curl -s -o /dev/null -w "%{time_total}\n" \
    "http://127.0.0.1:5000/students/by-subject?subject_code=ASD101"
done
```

Windows PowerShell:

```powershell
1..20 | ForEach-Object {
    curl.exe -s -o NUL -w "%{time_total}`n" `
    "http://127.0.0.1:5000/students/by-subject?subject_code=ASD101"
}
```

Record results in the evidence log.

</details>

---

## 6. Agentic Loop

<details>
<summary>Python Agentic Loop</summary>

Update `agentic_loop.py`

```python
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ENV_PATH = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=ENV_PATH)

DATABASE_NAME = Path(__file__).with_name("enrolment.db")
PROMPT_DIR = Path(__file__).with_name("prompts")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
IMPLEMENTATION_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
REVIEW_MODEL = os.getenv("OLLAMA_REVIEW_MODEL", "llama3.1:8b")

PLAN = {
    "goal": "Validate Student Enrolment App using external prompt assets",
    "checks": [
        "/students",
        "/students/{student_id}",
        "/students/by-id",
        "/students/by-subject",
        "/ask",
        "/ask-with-context",
    ],
}


def load_prompt(filename):
    return (PROMPT_DIR / filename).read_text(encoding="utf-8").strip()


def validate_student(student):
    student_id, student_name, subject_code = student

    if not isinstance(student_id, int):
        return False, "student_id must be integer"
    if not student_name:
        return False, "student_name required"
    if not subject_code:
        return False, "subject_code required"

    return True, "ok"


def observe_data_quality():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    students = cursor.execute(
        """
        SELECT
            student_id,
            student_name,
            subject_code
        FROM students
        """
    ).fetchall()

    conn.close()

    if len(students) != 10:
        return False, "Expected 10 students"

    for student in students:
        ok, msg = validate_student(student)
        if not ok:
            return False, msg

    return True, "Data validation passed"


def observe_subject_search(subject_code):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    students = cursor.execute(
        """
        SELECT
            student_id,
            student_name,
            subject_code
        FROM students
        WHERE subject_code = ?
        """,
        (subject_code,),
    ).fetchall()

    conn.close()

    if not students:
        return False, f"No students found for {subject_code}"

    return True, f"Subject search validation passed for {subject_code}"


def call_model(model_name, system_prompt, user_prompt, max_tokens=150):
    try:
        client = OpenAI(
            base_url=OLLAMA_BASE_URL,
            api_key="ollama",
            timeout=180.0,
        )

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.1,
        )

        content = response.choices[0].message.content
        if content and content.strip():
            return content.strip(), None

        return "No response generated.", None

    except Exception as exc:
        return None, f"{model_name} unavailable ({exc})"


def get_implementation_advice(observe_message):
    system_prompt = load_prompt("agent_system_prompt.txt")
    task_prompt = load_prompt("agent_task_prompt.txt")

    user_prompt = f"""
Validation Evidence:

{observe_message}
"""

    return call_model(
        IMPLEMENTATION_MODEL,
        system_prompt,
        f"{task_prompt}\n\n{user_prompt}",
    )


def get_review_advice(implementation_message, observe_message):
    review_prompt = load_prompt("agent_review_prompt.txt")

    review_request = f"""
Implementation Recommendation:

{implementation_message}

Validation Evidence:

{observe_message}
"""

    return call_model(
        REVIEW_MODEL,
        review_prompt,
        review_request,
    )


def human_review():
    print()
    print("HUMAN REVIEW")
    print("1 - Accept")
    print("2 - Partially Accept")
    print("3 - Reject")

    decision = input("Decision: ").strip()

    if decision == "1":
        return "Accept"
    if decision == "2":
        return "Partially Accept"
    return "Reject"


def adapt(decision):
    print()

    if decision == "Accept":
        print("ADAPT: Apply recommendation.")
    elif decision == "Partially Accept":
        print("ADAPT: Apply selected changes.")
    else:
        print("ADAPT: Document rationale.")


def main():
    print("=" * 60)
    print("ASD LAB 03 PROMPT ENGINEERING")
    print("=" * 60)

    print()
    print("PLAN")
    print(PLAN)

    print()
    print("ACT")

    ok_data, msg_data = observe_data_quality()
    ok_subject, msg_subject = observe_subject_search("ASD101")

    print()
    print("OBSERVE")
    print(msg_data)
    print(msg_subject)

    observe_message = f"{msg_data}. {msg_subject}."

    print()
    print("PROMPT AGENT")

    implementation_advice, err = get_implementation_advice(observe_message)
    if implementation_advice:
        print()
        print(implementation_advice)
    else:
        print(err)
        implementation_advice = "Prompt agent unavailable."

    print()
    print("REVIEW AGENT")

    review_advice, err = get_review_advice(implementation_advice, observe_message)
    if review_advice:
        print()
        print(review_advice)
    else:
        print(err)

    print()
    print("HUMAN DECISION")

    decision = human_review()

    print()
    print(f"Decision: {decision}")

    adapt(decision)

    print()
    print("LOOP COMPLETE")


if __name__ == "__main__":
    main()
```

</details>

<details>
<summary>Run the Agentic Loop</summary>

```bash
cd enrolment-app-open-ai
.venv/bin/python init_db.py
.venv/bin/python agentic_loop.py
```

Expected:

```text
PLAN
ACT
OBSERVE
PROMPT AGENT
REVIEW AGENT
HUMAN REVIEW
ADAPT
LOOP COMPLETE
```

</details>

<details>
<summary>Prompt Boundary Test</summary>

Question:

```text
What cloud provider hosts this application?
```

Expected:

```text
Information unavailable in supplied context.
```

Record result.

</details>

<details>
<summary>Context Management Testing</summary>

Remove this line from prompts/context_prompt.txt:

```text
- GET /students/by-subject
```

Ask:

```text
What endpoints exist?
```

Observe output, then restore prompts/context_prompt.txt and record result.

</details>

---

## 7. Improvement Cycle

<details>
<summary>Improve and Record</summary>

Choose one:

- Improve system prompt
- Improve task prompt
- Improve context prompt
- Improve review prompt

Re-run:

- Endpoint tests
- Agentic loop

Record before and after.

</details>

---

## 8. Evidence Log

<details>
<summary>Record Evidence</summary>

| Check | Expected Result | Actual Result | Pass/Fail |
|---|---|---|---|
| Prompt folder created | Yes | | |
| Prompt files created | Yes | | |
| qwen2.5:0.5b installed | Yes | | |
| llama3.1:8b installed | Yes | | |
| /ask-with-context works | Yes | | |
| Prompt agent output | Returned | | |
| Review agent output | Returned | | |
| Prompt boundary exercise | Completed | | |
| Context exercise | Completed | | |
| Improvement applied | Recorded | | |

</details>

---

## 9. Reflection

<details>
<summary>Answer Briefly</summary>

1. Which prompt change improved output quality most?
2. What boundary risk appeared?
3. Which context item had the highest impact?
4. What should be automated next?

</details>

---

## 10. Key Learning Point

<details>
<summary>Learning Outcome</summary>

Keep these concerns separate:

- Code
- Runtime configuration
- Prompt assets
- Validation evidence

Focus:

```text
Human -> Prompt -> Agent -> Evidence -> Review -> Adaptation
```

</details>
