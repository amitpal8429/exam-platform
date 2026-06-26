#!/usr/bin/env python3
"""
Daily Question Upload Script
Run this daily to automatically update questions
"""

import json
import os
import datetime
import shutil
import random

QUESTIONS_FILE = "questions.json"
BACKUP_DIR = "question_backups"
BANK_FILE = "question_bank.json"


def create_question_bank():
    """Create question bank with daily topics"""
    bank = {
        "monday": [
            {"question": "Python mein list aur tuple mein kya farak hai?", "type": "text", "marks": 10},
            {"question": "Python mein dictionary kya hai?", "type": "text", "marks": 10},
            {"question": "Python mein lambda function kya hota hai?", "type": "text", "marks": 10},
        ],
        "tuesday": [
            {"question": "OOP ke 4 pillars kaunse hain?", "type": "mcq",
             "options": ["Encapsulation, Inheritance, Polymorphism, Abstraction",
                         "Class, Object, Method, Function",
                         "List, Tuple, Dict, Set",
                         "Input, Output, Process, Storage"],
             "correct": 0, "marks": 5},
            {"question": "Inheritance kya hoti hai?", "type": "text", "marks": 10},
            {"question": "Polymorphism ka example do?", "type": "text", "marks": 10},
        ],
        "wednesday": [
            {"question": "Time complexity kya hoti hai?", "type": "text", "marks": 10},
            {"question": "Stack aur queue mein kya farak hai?", "type": "text", "marks": 10},
            {"question": "Binary tree kya hota hai?", "type": "text", "marks": 10},
        ],
        "thursday": [
            {"question": "Python mein decorator kya hota hai?", "type": "mcq",
             "options": ["Function wrapper", "Class variable", "Loop type", "None"],
             "correct": 0, "marks": 5},
            {"question": "Generator kya hota hai?", "type": "text", "marks": 10},
            {"question": "Context manager kya hai?", "type": "text", "marks": 10},
        ],
        "friday": [
            {"question": "SQL aur NoSQL mein kya farak hai?", "type": "text", "marks": 10},
            {"question": "ACID properties kya hain?", "type": "text", "marks": 10},
            {"question": "Normalization kya hai?", "type": "text", "marks": 10},
        ],
        "saturday": [
            {"question": "REST API kya hota hai?", "type": "text", "marks": 10},
            {"question": "HTTP aur HTTPS mein kya farak hai?", "type": "text", "marks": 10},
            {"question": "Flask framework ke advantages kya hain?", "type": "text", "marks": 10},
        ],
        "sunday": [
            {"question": "What is Python?", "type": "text", "marks": 10},
            {"question": "What is OOP?", "type": "text", "marks": 10},
            {"question": "What is Data Structure?", "type": "text", "marks": 10},
        ]
    }

    with open(BANK_FILE, 'w', encoding='utf-8') as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)
    print(f"✅ Question bank created: {BANK_FILE}")
    return bank


def load_question_bank():
    """Load question bank from file or create if not exists"""
    if os.path.exists(BANK_FILE):
        with open(BANK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return create_question_bank()


def get_daily_questions():
    """Get questions for today"""
    today = datetime.datetime.now().strftime("%A").lower()
    bank = load_question_bank()

    # Get questions for today
    day_questions = bank.get(today, bank.get("monday", []))

    # Randomly select 2-3 questions
    num_questions = min(3, len(day_questions))
    selected = random.sample(day_questions, num_questions) if len(day_questions) > num_questions else day_questions

    # Add IDs
    questions = []
    for i, q in enumerate(selected):
        q_copy = q.copy()
        q_copy["id"] = i + 1
        questions.append(q_copy)

    return questions


def daily_upload():
    """Upload daily questions"""
    now = datetime.datetime.now()
    print("=" * 60)
    print(f"  📅 DAILY QUESTION UPLOAD - {now.strftime('%A, %B %d, %Y')}")
    print(f"  Time: {now.strftime('%H:%M:%S')}")
    print("=" * 60)

    # Backup existing questions
    if os.path.exists(QUESTIONS_FILE):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"questions_{timestamp}.json")
        shutil.copy(QUESTIONS_FILE, backup_path)
        print(f"✅ Backup created: {backup_path}")

    # Get today's questions
    questions = get_daily_questions()

    # Save questions
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print(f"✅ Uploaded {len(questions)} questions for today")
    print("\n📝 Questions:")
    for q in questions:
        print(f"   Q{q['id']}: {q['question'][:40]}... ({q['type']})")

    # Log the activity
    with open("upload_log.txt", "a", encoding='utf-8') as log:
        log.write(
            f"{now.strftime('%Y-%m-%d %H:%M:%S')}: Uploaded {len(questions)} questions for {now.strftime('%A')}\n")

    print("\n✅ Daily upload complete!")
    return questions


if __name__ == "__main__":
    daily_upload()