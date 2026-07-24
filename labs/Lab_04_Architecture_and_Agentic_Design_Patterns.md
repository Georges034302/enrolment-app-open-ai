# Lab 04 - Software Architecture and Design Patterns for Agentic AI Systems

**Course:** Advanced Software Development with Agentic AI (ASD)
**Theme:** Architecture and Agentic Decision Patterns
**Primary IDE:** VS Code (Optional IDE: AWS Kiro)
**AI Runtime:** Ollama
**Duration:** 60 Minutes

## 1. Overview

<details>
<summary>Goal</summary>

Transform the Lab 03 monolithic Student Enrolment App into a containerized microservices architecture consisting of:

- frontend-service
- enrolment-service
- database-service

Students will design the architecture, define service boundaries, create architecture artifacts, and prepare the solution for CI/CD in Lab 05.

</details>

<details>
<summary>Workflow</summary>

PLAN → IMPLEMENT → TEST → REVIEW → IMPROVE

</details>

<details>
<summary>Expected Results</summary>

By the end of this lab, students should have:

- Architecture Decision Record (ADR)
- Service Boundary Diagram
- Architecture Analysis Activities
- Docker Compose Architecture
- Three-Service Design
- Container Project Structure
- Evidence Log

</details>


---

## 2. Prerequisites and Configuration

<details>
<summary>Prerequisites</summary>

To start this lab, students should have:

Complete:

- Lab 01
- Lab 02
- Lab 03

Required:

- Docker Desktop
- Ollama

Verify:

```bash
docker --version
docker-compose --version
ollama list
```

If `docker` is not found on Ubuntu:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker
docker --version
docker-compose --version
```

Windows PowerShell (Docker Desktop):

Install Docker Desktop (run PowerShell as Administrator):

```powershell
winget install -e --id Docker.DockerDesktop
```

```powershell
docker --version
docker-compose --version
```

After installation, start Docker Desktop, then restart PowerShell and verify again.
</details>

---

## 3. Scenario

<details>
<summary>Student enrolment app</summary>

The Lab 03 application currently exists as a single deployment unit.

The business now requires:

- Independent frontend deployment
- Independent backend deployment
- Independent database lifecycle
- Future CI/CD automation
- Future cloud deployment

A microservices architecture is required.

</details>

<details>
<summary>Microservices Architecture</summary>

```text
+-------------------+
| frontend-service  |
+-------------------+
          |
          v
+-------------------+
| enrolment-service |
+-------------------+
          |
          v
+-------------------+
| database-service  |
+-------------------+
```

Responsibilities:

Frontend:

- HTMX
- HTML
- CSS

Backend:

- REST APIs
- Business Logic
- Prompt Loading
- Agent Integration

Database:

- SQLite or PostgreSQL
- Persistence

</details>

<details>
<summary>Project Structure</summary>

```text
enrolment-app-open-ai/
│
├── .env
├── .gitignore
├── docker-compose.yml
│
├── frontend-service/
│   ├── Dockerfile
│   ├── templates/
│   │   └── index.html
│   └── css/
│       └── styles.css
│
├── enrolment-service/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── prompts/
│       ├── architecture_system_prompt.txt
│       ├── architecture_task_prompt.txt
│       ├── architecture_review_prompt.txt
│       ├── pattern_selection_prompt.txt
│       ├── service_boundary_prompt.txt
│       ├── adr_generation_prompt.txt
│       ├── adr_review_prompt.txt
│       ├── system_prompt.txt
│       ├── task_prompt.txt
│       ├── context_prompt.txt
│       ├── review_prompt.txt
│       ├── agent_system_prompt.txt
│       ├── agent_task_prompt.txt
│       └── agent_review_prompt.txt
│
├── database-service/
│   ├── app.py
│   ├── requirements.txt
│   ├── init_db.py
│   ├── Dockerfile
│   └── data/
│ 
└── legacy-lab3/
    ├── app.py
    ├── agentic_loop.py
    ├── init_db.py
    ├── requirements.txt
    ├── templates/
    ├── css/
    ├── prompts/
    └── enrolment.db
```

</details>

<details>
<summary>Create Project Workspace</summary>

Use the existing `enrolment-app-open-ai` created in Labs 01-03.

**Linux / macOS**

```bash
mkdir -p enrolment-app-open-ai/frontend-service/templates
mkdir -p enrolment-app-open-ai/frontend-service/css

mkdir -p enrolment-app-open-ai/enrolment-service/prompts

mkdir -p enrolment-app-open-ai/database-service/data

touch enrolment-app-open-ai/docker-compose.yml

## Frontend Service
touch enrolment-app-open-ai/frontend-service/Dockerfile
touch enrolment-app-open-ai/frontend-service/templates/index.html
touch enrolment-app-open-ai/frontend-service/css/styles.css

## Enrolment Service
touch enrolment-app-open-ai/enrolment-service/app.py
touch enrolment-app-open-ai/enrolment-service/Dockerfile
touch enrolment-app-open-ai/enrolment-service/requirements.txt

## Database Service
touch enrolment-app-open-ai/database-service/Dockerfile
touch enrolment-app-open-ai/database-service/app.py
touch enrolment-app-open-ai/database-service/requirements.txt
touch enrolment-app-open-ai/database-service/init_db.py
```

**Windows PowerShell**

```powershell
mkdir enrolment-app-open-ai

mkdir enrolment-app-open-ai/frontend-service
mkdir enrolment-app-open-ai/frontend-service/templates
mkdir enrolment-app-open-ai/frontend-service/css

mkdir enrolment-app-open-ai/enrolment-service
mkdir enrolment-app-open-ai/enrolment-service/prompts

mkdir enrolment-app-open-ai/database-service
mkdir enrolment-app-open-ai/database-service/data

New-Item enrolment-app-open-ai/docker-compose.yml -ItemType File

## Frontend Service
New-Item enrolment-app-open-ai/frontend-service/Dockerfile -ItemType File
New-Item enrolment-app-open-ai/frontend-service/templates/index.html -ItemType File
New-Item enrolment-app-open-ai/frontend-service/css/styles.css -ItemType File

## Enrolment Service
New-Item enrolment-app-open-ai/enrolment-service/app.py -ItemType File
New-Item enrolment-app-open-ai/enrolment-service/Dockerfile -ItemType File
New-Item enrolment-app-open-ai/enrolment-service/requirements.txt -ItemType File

## Database Service
New-Item enrolment-app-open-ai/database-service/Dockerfile -ItemType File
New-Item enrolment-app-open-ai/database-service/app.py -ItemType File
New-Item enrolment-app-open-ai/database-service/requirements.txt -ItemType File
New-Item enrolment-app-open-ai/database-service/init_db.py -ItemType File
```

</details>

## 4. Application Setup and Development

### Frontend Service (HTMX)

<details>
<summary>frontend-service description</summary>

The frontend service is a static Nginx container responsible for:

* HTML
* HTMX
* CSS
* User interaction

The frontend service does **not**:

* Access the database
* Execute business logic
* Load prompts
* Call AI models directly

All requests are sent to the `enrolment-service`.

</details>

<details>
<summary>frontend-service/Dockerfile</summary>

```dockerfile
FROM nginx:alpine

COPY templates/index.html /usr/share/nginx/html/index.html
COPY css/styles.css /usr/share/nginx/html/css/styles.css

EXPOSE 80
```

</details>

<details>
<summary>frontend-service/templates/index.html</summary>

```html
<!DOCTYPE html>
<html>
<head>
    <title>Student Enrolment App</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
<main class="app-shell">
    <header class="app-header">
        <h1>Student Enrolment App</h1>
        <p>Microservices mode: frontend-service + enrolment-service + database-service.</p>
    </header>

    <div class="layout-grid">
        <section class="card card-left">
            <h2>Students</h2>

            <button id="toggle-students-btn" type="button">
                Show All Students
            </button>

            <div id="students-result" class="panel is-hidden"></div>

            <h2>Find Student by ID</h2>

            <form id="student-by-id-form">
                <label for="student_id">Student ID</label>
                <input id="student_id" name="student_id" type="number" min="1" placeholder="Enter student ID">
                <button type="submit">Get Student</button>
            </form>

            <div id="student-result" class="panel"></div>

            <h2>Find Students by Subject Code</h2>

            <form id="students-by-subject-form">
                <label for="subject_code">Subject Code</label>
                <input id="subject_code" name="subject_code" type="text" placeholder="Example: ASD101">
                <button type="submit">Find Students</button>
            </form>

            <div id="subject-result" class="panel"></div>
        </section>

        <section class="card card-right">
            <h2>Ask Local AI Agent</h2>

            <form id="ask-form">
                <label for="question">Question</label>
                <textarea id="question" name="question" rows="5">Explain what this Student Enrolment App does in one short paragraph.</textarea>
                <button type="submit">Ask Local Agent</button>
            </form>

            <div id="agent-result" class="panel"></div>

            <h2>Ask With Context</h2>

            <form id="ask-with-context-form">
                <label for="context-question">Question</label>
                <textarea id="context-question" name="question" rows="4">Explain the Student Enrolment App.</textarea>
                <button type="submit">Ask With Context</button>
            </form>

            <div id="context-result" class="panel"></div>

            <h2>Architecture Review</h2>

            <form id="architecture-review-form">
                <label for="architecture_request">Request</label>
                <textarea id="architecture_request" name="architecture_request" rows="4">Review service boundaries for frontend-service, enrolment-service, and database-service.</textarea>
                <button type="submit">Run Architecture Review</button>
            </form>

            <div id="architecture-result" class="panel"></div>
        </section>
    </div>
</main>

<script>
const toggleStudentsBtn = document.getElementById("toggle-students-btn");
const studentsPanel = document.getElementById("students-result");
const studentByIdForm = document.getElementById("student-by-id-form");
const studentsBySubjectForm = document.getElementById("students-by-subject-form");
const askForm = document.getElementById("ask-form");
const askWithContextForm = document.getElementById("ask-with-context-form");
const architectureReviewForm = document.getElementById("architecture-review-form");

async function renderIntoPanel(panelId, url, options = {}) {
    const panel = document.getElementById(panelId);

    try {
        const response = await fetch(url, options);
        const body = await response.text();
        panel.innerHTML = body;
    } catch (error) {
        panel.innerHTML = `<p>Request failed.</p><pre>${error}</pre>`;
    }
}

toggleStudentsBtn.addEventListener("click", () => {
    const isHidden = studentsPanel.classList.contains("is-hidden");

    if (isHidden) {
        studentsPanel.classList.remove("is-hidden");
        toggleStudentsBtn.textContent = "Hide All Students";

        if (!studentsPanel.dataset.loaded) {
            renderIntoPanel("students-result", "http://localhost:5001/students");
            studentsPanel.dataset.loaded = "true";
        }
    } else {
        studentsPanel.classList.add("is-hidden");
        toggleStudentsBtn.textContent = "Show All Students";
    }
});

studentByIdForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(studentByIdForm);
    const query = new URLSearchParams(formData).toString();
    renderIntoPanel("student-result", `http://localhost:5001/students/by-id?${query}`);
});

studentsBySubjectForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(studentsBySubjectForm);
    const query = new URLSearchParams(formData).toString();
    renderIntoPanel("subject-result", `http://localhost:5001/students/by-subject?${query}`);
});

askForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new URLSearchParams(new FormData(askForm));
    renderIntoPanel("agent-result", "http://localhost:5001/ask", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
    });
});

askWithContextForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new URLSearchParams(new FormData(askWithContextForm));
    renderIntoPanel("context-result", "http://localhost:5001/ask-with-context", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
    });
});

architectureReviewForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new URLSearchParams(new FormData(architectureReviewForm));
    renderIntoPanel("architecture-result", "http://localhost:5001/architecture-review", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
    });
});
</script>

</body>
</html>
```

</details>

<details>
<summary>frontend-service/css/styles.css</summary>

```css
:root {
    --bg-0: #0b1020;
    --bg-1: #111a31;
    --bg-2: #1a2645;
    --surface: #0f172b;
    --surface-alt: #15213d;
    --text: #e8edf8;
    --muted: #9eb0d3;
    --accent: #45c9ff;
    --accent-strong: #1eb1ee;
    --border: #2b3a63;
    --radius: 12px;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.5;
    color: var(--text);
    background:
        radial-gradient(1100px 540px at 10% -10%, #1e3263 0%, transparent 60%),
        radial-gradient(900px 480px at 100% 0%, #1a4e74 0%, transparent 58%),
        linear-gradient(160deg, var(--bg-0) 0%, var(--bg-1) 46%, var(--bg-2) 100%);
}

.app-shell {
    max-width: 1100px;
    margin: 0 auto;
    padding: 1.25rem;
}

.app-header {
    margin-bottom: 1rem;
}

.app-header h1 {
    margin: 0;
    font-size: 1.9rem;
}

.app-header p {
    margin: 0.4rem 0 0;
    color: var(--muted);
}

.layout-grid {
    display: grid;
    grid-template-columns: 1.4fr 1fr;
    gap: 1rem;
}

.card {
    background: linear-gradient(180deg, rgba(20, 31, 56, 0.95), rgba(13, 22, 41, 0.95));
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
    box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
}

h2 {
    margin: 0 0 0.6rem;
    font-size: 1.1rem;
}

label {
    display: block;
    margin-bottom: 0.3rem;
    color: var(--muted);
}

button {
    margin-top: 0.5rem;
    padding: 0.5rem 0.9rem;
    border: 1px solid transparent;
    border-radius: 10px;
    font-weight: 600;
    color: #06202c;
    background: var(--accent);
    cursor: pointer;
}

button:hover {
    background: var(--accent-strong);
}

input,
textarea {
    width: 100%;
    padding: 0.55rem 0.7rem;
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text);
    background: var(--surface-alt);
}

.panel {
    margin-top: 0.7rem;
    padding: 0.75rem;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--surface);
    min-height: 2.5rem;
}

.is-hidden {
    display: none;
}

@media (max-width: 900px) {
    .layout-grid {
        grid-template-columns: 1fr;
    }
}
```

</details>


<details>
<summary>Notes</summary>

```text
Frontend Service Port:
80

Container Name:
frontend-service

Backend Service:
enrolment-service

Backend Port:
5001
```

The frontend service contains presentation only.

Business logic, AI integration, prompt loading, and architecture review processing remain inside the `enrolment-service`.

</details>

</details>


### Backend Service (Flask)

<details>
<summary>backend-service description</summary>

The `enrolment-service` is the backend API layer.

Responsibilities:

- Expose REST/HTMX API endpoints
- Call `database-service`
- Load architecture prompt files
- Call Ollama for architecture review tasks
- Return HTML fragments to the frontend

The `enrolment-service` does **not**:

- Render the full frontend page
- Store data directly
- Own CSS or HTMX templates

</details>

<details>
<summary>enrolment-service/Dockerfile</summary>

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY prompts ./prompts

EXPOSE 5001

CMD ["python", "app.py"]
```

</details>


<details>
<summary>enrolment-service/requirements.txt</summary>

```text
flask==3.0.3
flask-cors==4.0.1
requests==2.32.3
openai
python-dotenv
```

</details>


<details>
<summary>enrolment-service/app.py</summary>

```python
from flask import Flask, request
from flask_cors import CORS
from openai import OpenAI
from pathlib import Path

import os
import requests

app = Flask(__name__)
CORS(app)

DATABASE_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL", "http://database-service:5002")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")

PROMPT_DIR = Path("prompts")

client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

def load_prompt(filename):
    return (PROMPT_DIR / filename).read_text(encoding="utf-8").strip()

def format_students_html(students):
    if not students:
        return "<p>No students found.</p>"

    html = "<ul>"
    for student in students:
        html += (
            f"<li>{student['student_id']} - "
            f"{student['student_name']} - {student['subject_code']}</li>"
        )
    html += "</ul>"
    return html

def format_student_html(student):
    return (
        f"<p>ID: {student['student_id']}<br>"
        f"Name: {student['student_name']}<br>"
        f"Subject: {student['subject_code']}</p>"
    )


def call_architecture_agent(system_prompt_file, task_prompt_file, user_input, max_tokens=300):
    system_prompt = load_prompt(system_prompt_file)
    task_prompt = load_prompt(task_prompt_file)

    final_prompt = f"""
{task_prompt}

User Input:

{user_input}
"""

    response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": final_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()

@app.get("/")
def health():
    return "<p>enrolment-service running</p>", 200

@app.get("/students")
def get_students():
    try:
        response = requests.get(f"{DATABASE_SERVICE_URL}/students", timeout=5)
        response.raise_for_status()
        return format_students_html(response.json()), 200
    except requests.RequestException as exc:
        return (
            "<p>Failed to retrieve students from database-service.</p>"
            f"<pre>{exc}</pre>",
            503,
        )

@app.get("/students/by-id")
def get_student_by_id():
    student_id = request.args.get("student_id", "").strip()

    if not student_id:
        return "<p>Student ID is required.</p>", 400

    try:
        response = requests.get(f"{DATABASE_SERVICE_URL}/students/{student_id}", timeout=5)

        if response.status_code == 404:
            return "<p>Student not found.</p>", 404

        if response.status_code == 400:
            return "<p>Student ID must be valid.</p>", 400

        response.raise_for_status()
        return format_student_html(response.json()), 200
    except requests.RequestException as exc:
        return (
            "<p>Failed to retrieve student from database-service.</p>"
            f"<pre>{exc}</pre>",
            503,
        )

@app.get("/students/by-subject")
def get_students_by_subject():
    subject_code = request.args.get("subject_code", "").strip().upper()

    if not subject_code:
        return "<p>Subject code is required.</p>", 400

    try:
        response = requests.get(
            f"{DATABASE_SERVICE_URL}/students/by-subject",
            params={"subject_code": subject_code},
            timeout=5,
        )

        if response.status_code == 404:
            return f"<p>No students found for {subject_code}.</p>", 404

        response.raise_for_status()
        return format_students_html(response.json()), 200
    except requests.RequestException as exc:
        return (
            "<p>Failed to retrieve subject results from database-service.</p>"
            f"<pre>{exc}</pre>",
            503,
        )


@app.post("/ask")
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
                    ),
                },
                {"role": "user", "content": question},
            ],
            max_tokens=200,
            temperature=0.2,
        )
        answer = response.choices[0].message.content
        return f"<p>{answer}</p>", 200
    except Exception as exc:
        return (
            "<p>Local AI agent request failed. "
            "Check that Ollama is running and that qwen2.5:0.5b is installed.</p>"
            f"<pre>{exc}</pre>",
            503,
        )


@app.post("/ask-with-context")
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
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": final_prompt},
            ],
            max_tokens=300,
            temperature=0.2,
        )

        answer = response.choices[0].message.content
        return f"<p>{answer}</p>", 200
    except Exception as exc:
        return (
            "<p>Context-aware request failed.</p>"
            f"<pre>{exc}</pre>",
            503,
        )

@app.post("/architecture-review")
def architecture_review():
    architecture_request = request.form.get("architecture_request", "").strip()

    if not architecture_request:
        return "<p>Architecture request is required.</p>", 400

    try:
        answer = call_architecture_agent(
            "architecture_system_prompt.txt",
            "architecture_task_prompt.txt",
            architecture_request,
        )

        return f"<pre>{answer}</pre>", 200

    except Exception as exc:
        return (
            "<p>Architecture agent request failed.</p>"
            f"<pre>{exc}</pre>",
            503,
        )

@app.post("/pattern-selection")
def pattern_selection():
    architecture_request = request.form.get("architecture_request", "").strip()

    if not architecture_request:
        return "<p>Architecture request is required.</p>", 400

    try:
        answer = call_architecture_agent(
            "architecture_system_prompt.txt",
            "pattern_selection_prompt.txt",
            architecture_request,
        )

        return f"<pre>{answer}</pre>", 200

    except Exception as exc:
        return (
            "<p>Pattern selection request failed.</p>"
            f"<pre>{exc}</pre>",
            503,
        )

@app.post("/adr-review")
def adr_review():
    architecture_request = request.form.get("architecture_request", "").strip()

    if not architecture_request:
        return "<p>ADR text is required.</p>", 400

    try:
        answer = call_architecture_agent(
            "architecture_system_prompt.txt",
            "adr_review_prompt.txt",
            architecture_request,
        )

        return f"<pre>{answer}</pre>", 200

    except Exception as exc:
        return (
            "<p>ADR review request failed.</p>"
            f"<pre>{exc}</pre>",
            503,
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
```

</details>

<details>
<summary>Prompt Specification Files</summary>

<details>
<summary>enrolment-service/prompts/architecture_system_prompt.txt</summary>

```text
You are a senior software architecture assistant.

Your role is to help evaluate and improve the architecture of the Student Enrolment System.

Focus on:

- service boundaries
- deployment boundaries
- ownership boundaries
- architecture trade-offs
- maintainability
- scalability
- reliability

Rules:

- Use only supplied requirements.
- Do not invent services.
- Do not invent deployment environments.
- Do not invent database fields.
- Do not generate implementation code unless explicitly asked.
- Prefer simple architecture decisions over unnecessary complexity.
- Explain trade-offs clearly.

Keep responses concise and evidence-based.
```

</details>


<details>
<summary>enrolment-service/prompts/architecture_task_prompt.txt</summary>

```text
Design or review a target architecture for the Student Enrolment System.

Current State:

- Lab 03 used a single Flask application.
- The application used HTMX, SQLite, and local Ollama models.
- Prompts were externalised into prompt files.

Target State:

- frontend-service
- enrolment-service
- database-service

Return:

1. Service Responsibilities
2. Communication Paths
3. Service Ownership
4. Benefits
5. Risks
6. Trade-Offs

Do not generate source code.

Focus on architecture decisions.
```

</details>


<details>
<summary>enrolment-service/prompts/architecture_review_prompt.txt</summary>

```text
Review the proposed architecture.

Evaluate:

- service boundaries
- deployment boundaries
- ownership boundaries
- coupling
- maintainability
- scalability
- reliability

Identify:

- architecture risks
- unnecessary complexity
- responsibility overlap
- missing evidence

Return exactly:

Risk:
Correction:
Retest:
```

</details>

<details>
<summary>enrolment-service/prompts/pattern_selection_prompt.txt</summary>

```text
Compare the following architecture styles:

- Monolith
- Layered Architecture
- Microservices

Evaluate each using:

- scalability
- maintainability
- deployment complexity
- operational complexity
- team ownership
- future growth

Recommend one architecture style for the Student Enrolment System.

Return exactly:

Architecture:
Reason:
Trade-Offs:
```

</details>

<details>
<summary>enrolment-service/prompts/service_boundary_prompt.txt</summary>

```text
Review the proposed service boundaries.

Services:

- frontend-service
- enrolment-service
- database-service

For each service identify:

1. Responsibilities
2. Data Ownership
3. API Ownership
4. Dependencies

Identify any responsibility overlap.

Return:

Boundary Review:
Risk:
Recommendation:
```

</details>

<details>
<summary>enrolment-service/prompts/adr_generation_prompt.txt</summary>

```text
Generate an Architecture Decision Record for the Student Enrolment System.

Include:

Context:
Decision:
Alternatives:
Trade-Offs:
Consequences:

The ADR must be concise and architecture focused.

Do not include implementation code.
```

</details>

<details>
<summary>enrolment-service/prompts/adr_review_prompt.txt</summary>

```text
Review the Architecture Decision Record.

Validate:

- Context completeness
- Decision clarity
- Alternatives considered
- Trade-Offs identified
- Consequences documented
- Evidence provided

Identify missing evidence.

Return exactly:

Risk:
Correction:
Retest:
```

</details>

</details>

### Database Service

<details>
<summary>database-service description</summary>

The database service owns all student data.

Responsibilities:

- Database creation
- Database seeding
- Data persistence
- Student data APIs

The database service does not:

- Render HTML
- Load prompts
- Call AI models
- Implement business logic

</details>

<details>
<summary>database-service/Dockerfile</summary>

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY init_db.py .

RUN python init_db.py

EXPOSE 5002

CMD ["python", "app.py"]
```

</details>

<details>
<summary>database-service/requirements.txt</summary>

```text
flask==3.0.3
```

</details>


<details>
<summary>database-service/init_db.py</summary>

```python
import os
import sqlite3

DATA_DIR = "/app/data"
DATABASE_NAME = os.path.join(DATA_DIR, "enrolment.db")

os.makedirs(DATA_DIR, exist_ok=True)

conn = sqlite3.connect(
    DATABASE_NAME
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    student_name TEXT NOT NULL,
    subject_code TEXT NOT NULL
)
""")

cursor.execute(
    "DELETE FROM students"
)

students = [
    (1, "John Smith", "ASD101"),
    (2, "Sarah Jones", "ASD101"),
    (3, "Michael Lee", "WEB201"),
    (4, "Emma Brown", "WEB201"),
    (5, "James Wilson", "DBS101"),
    (6, "Olivia White", "DBS101"),
    (7, "Daniel Green", "NET201"),
    (8, "Sophia Hall", "NET201"),
    (9, "Liam King", "SEC301"),
    (10, "Chloe Young", "SEC301"),
]

cursor.executemany(
    """
    INSERT INTO students (
        student_id,
        student_name,
        subject_code
    )
    VALUES (?, ?, ?)
    """,
    students
)

conn.commit()
conn.close()

print(
    "Database initialized with 10 students."
)
```

</details>


<details>
<summary>database-service/app.py</summary>

```python
from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DATABASE_NAME = "/app/data/enrolment.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def health():
    return jsonify({"service": "database-service", "status": "running"})

@app.get("/students")
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        "SELECT student_id, student_name, subject_code FROM students"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in students])

@app.get("/students/<int:student_id>")
def get_student(student_id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT student_id, student_name, subject_code FROM students WHERE student_id = ?",
        (student_id,),
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))

@app.get("/students/by-subject")
def get_students_by_subject():
    subject_code = request.args.get("subject_code", "").strip().upper()

    if not subject_code:
        return jsonify({"error": "subject_code required"}), 400

    conn = get_db_connection()
    students = conn.execute(
        "SELECT student_id, student_name, subject_code FROM students WHERE subject_code = ?",
        (subject_code,),
    ).fetchall()
    conn.close()

    if not students:
        return jsonify({"error": "No students found"}), 404

    return jsonify([dict(row) for row in students])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
```

</details>


###  Docker Compose Architecture

<details>
<summary>docker-compose.yml</summary>

```yaml
services:
    frontend-service:
        build:
            context: ./frontend-service
        container_name: frontend-service
        ports:
            - "8080:80"
        depends_on:
            - enrolment-service
        restart: unless-stopped

    enrolment-service:
        build:
            context: ./enrolment-service
        container_name: enrolment-service
        ports:
            - "5001:5001"
        environment:
            DATABASE_SERVICE_URL: http://database-service:5002
            OLLAMA_BASE_URL: http://host.docker.internal:11434/v1
            OLLAMA_MODEL: qwen2.5:0.5b
        extra_hosts:
            - "host.docker.internal:host-gateway"
        depends_on:
            - database-service
        restart: unless-stopped

    database-service:
        build:
            context: ./database-service
        container_name: database-service
        ports:
            - "5002:5002"
        volumes:
            - database_data:/app/data
        restart: unless-stopped

volumes:
    database_data:
```

</details>

<details>
<summary>Architecture Flow</summary>

```text
Browser
    │
    ▼
frontend-service
(Nginx)
Port 8080
    │
    ▼
enrolment-service
(Flask + Ollama)
Port 5001
    │
    ▼
database-service
(Flask + SQLite)
Port 5002
```
</details>

<details>
<summary>Service Communication</summary>

```text
frontend-service
    ↓ HTTP
enrolment-service

enrolment-service
    ↓ HTTP
database-service

database-service
    ↓
SQLite Database
```
</details>

<details>
<summary>Run Steps</summary>

1. Install

Linux (Ubuntu):

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker
```

Windows PowerShell (Admin):

```powershell
winget install -e --id Docker.DockerDesktop
```

2. Build and run

Linux and Windows PowerShell:

```bash
docker-compose up --build
```

3. Check status

Linux and Windows PowerShell:

```bash
docker-compose ps
```

4. Open app

Linux:

```bash
xdg-open http://localhost:8080
```

Windows PowerShell:

```powershell
Start-Process http://localhost:8080
```

5. Enable AI connection to containers

Linux:

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d && printf "[Service]\nEnvironment=\"OLLAMA_HOST=0.0.0.0:11434\"\n" | sudo tee /etc/systemd/system/ollama.service.d/override.conf >/dev/null && sudo systemctl daemon-reload && sudo systemctl restart ollama
```

Windows PowerShell:

```powershell
setx OLLAMA_HOST "0.0.0.0:11434"
```

Close and reopen Ollama after `setx`.

6. Verify container access to Ollama

Linux and Windows PowerShell:

```bash
docker-compose exec enrolment-service python -c "import requests; print(requests.get('http://host.docker.internal:11434/api/tags', timeout=5).status_code)"
```

Expected: `200`

7. Test AI endpoint

Linux and Windows PowerShell:

```bash
curl -X POST http://localhost:5001/ask -d "question=Say hello in one sentence"
```

8. Stop services

Linux and Windows PowerShell:

```bash
docker-compose down
```

9. Remove stopped containers

Linux and Windows PowerShell:

```bash
docker-compose rm -f
```

10. View logs

Linux and Windows PowerShell:

```bash
docker-compose logs -f
```

11. Rebuild containers

Linux and Windows PowerShell:

```bash
docker-compose up --build --force-recreate
```
</details>

---

## 5. Application Testing

<details>
<summary>Endpoints Testing</summary>

| Function | Browser Validation | API Validation |
|---|---|---|
| Home Page | `http://localhost:8080` | N/A |
| View Students | Use "Show All Students" on `http://localhost:8080` | `curl http://localhost:5001/students` |
| Get Student by ID | Use "Find Student by ID" on `http://localhost:8080` | `curl "http://localhost:5001/students/by-id?student_id=1"` |
| Student Not Found | Use "Find Student by ID" with invalid ID on `http://localhost:8080` | `curl "http://localhost:5001/students/by-id?student_id=9999"` |
| Search by Subject | Use "Find Students by Subject Code" on `http://localhost:8080` | `curl "http://localhost:5001/students/by-subject?subject_code=ASD101"` |
| Subject Not Found | Use "Find Students by Subject Code" with unknown code on `http://localhost:8080` | `curl "http://localhost:5001/students/by-subject?subject_code=ABC999"` |
| AI Assistant | Use "Ask Local AI Agent" on `http://localhost:8080` | `curl -X POST http://localhost:5001/ask -d "question=Test"` |
| Context Assistant | Use "Ask With Context" on `http://localhost:8080` | `curl -X POST http://localhost:5001/ask-with-context -d "question=What endpoints exist?"` |
| Architecture Review | Use "Run Architecture Review" on `http://localhost:8080` | `curl -X POST http://localhost:5001/architecture-review -d "architecture_request=Review service boundaries"` |
| Pattern Selection | N/A | `curl -X POST http://localhost:5001/pattern-selection -d "architecture_request=Select one architecture"` |
| ADR Review | N/A | `curl -X POST http://localhost:5001/adr-review -d "architecture_request=Context:... Decision:..."` |

Expected: all listed browser and API checks return valid responses.

</details>

<details>
<summary>NFR Validation</summary>

The non-functional requirement is:

```text
GET /students/by-subject?subject_code=ASD101 returns within 500 ms.
```

Pass condition:

```text
At least 19 out of 20 requests complete in <= 0.500 seconds.
```

**Linux/macOS:**

```bash
for i in $(seq 1 20); do
    curl -s -o /dev/null -w "%{time_total}\n" \
    "http://localhost:5001/students/by-subject?subject_code=ASD101"
done
```

**Windows PowerShell**

```powershell
1..20 | ForEach-Object {
    curl.exe -s -o NUL -w "%{time_total}`n" `
    "http://localhost:5001/students/by-subject?subject_code=ASD101"
}
```

Record the result in the evidence log.

</details>


---

## 6. Architecture Analysis Activities

<details>
<summary>Pattern Selection</summary>
Evaluate:

- Monolith
- Layered Architecture
- Microservices

Select the most appropriate architecture pattern.
</details>

<details>
<summary>Service Boundary Review</summary>

Validate:

- Responsibilities
- Ownership
- Dependencies
- Coupling

Identify overlap and ownership conflicts.

</details>

<details>
<summary>Architecture Decision Record (ADR)</summary>

Students document:

- Context
- Decision
- Alternatives
- Trade-Offs
- Consequences

</details>

<details>
<summary>Architecture Validation</summary>

Validate:

- Service boundaries
- API ownership
- Database ownership
- Deployment independence
</details>


## 7. Improvement Cycle

<details>
<summary>Quality Attribute Review</summary>

Evaluate:

- Scalability
- Maintainability
- Reliability
- Security
- Observability

Perform Improvements:

- Pattern selection
- Service boundary analysis
- ADR generation
- One architecture improvement

</details>

---

## 8. Evidence Log

<details>
<summary>Record Evidence</summary>

| Check | Expected Result | Actual Result | Pass/Fail |
|---------|---------|---------|---------|
| ADR complete | Yes | | |
| Architecture diagram | Yes | | |
| Service boundaries defined | Yes | | |
| Frontend service created | Yes | | |
| Backend service created | Yes | | |
| Database service created | Yes | | |
| Pattern selected | Yes | | |
| Boundary analysis completed | Yes | | |
| ADR generated | Yes | | |
| Adaptation applied | Yes | | |

</details>

---

## 9. Reflection

<details>
<summary>Answer Briefly:</summary>

1. Why was the selected architecture pattern appropriate?
2. What service boundary decision was most important?
3. What architecture trade-off was hardest to justify?
4. What would change before production deployment?
5. How does this support Lab 05?

</details>

---

## 10. Key Learning Point

<details>
<summary>Learning Outcome</summary>

Architecture is the process of making evidence-based decisions about:

- Boundaries
- Responsibilities
- Communication
- Deployment

before implementation begins.

</details>