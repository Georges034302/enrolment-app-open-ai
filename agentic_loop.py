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