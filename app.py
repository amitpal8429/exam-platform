from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import datetime
import shutil

app = Flask(__name__)

# ===== CONFIGURATION =====
RECORDINGS_DIR = "recordings"
QUESTIONS_FILE = "questions.json"
BACKUP_DIR = "question_backups"
os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# ===== SESSION STORAGE =====
sessions = {}


# ===== DYNAMIC QUESTIONS LOADER =====
def load_questions():
    """Load questions from JSON file or create default"""
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        default = [
            {"id": 1, "question": "Python mein list aur tuple mein kya farak hai?", "type": "text", "marks": 10},
            {"id": 2, "question": "OOP ke 4 pillars kaunse hain?", "type": "mcq",
             "options": ["Encapsulation, Inheritance, Polymorphism, Abstraction",
                         "Class, Object, Method, Function",
                         "List, Tuple, Dict, Set",
                         "Input, Output, Process, Storage"],
             "correct": 0, "marks": 5},
            {"id": 3, "question": "Recursion kya hoti hai? Example ke saath explain karo.", "type": "text",
             "marks": 10},
            {"id": 4, "question": "Python mein decorator kya hota hai?", "type": "mcq",
             "options": ["Ek function jo doosre function ko wrap karta hai",
                         "Ek class ka variable",
                         "Ek loop ka type",
                         "Inme se koi nahi"],
             "correct": 0, "marks": 5},
            {"id": 5, "question": "Time complexity kya hoti hai? Big-O notation explain karo.", "type": "text",
             "marks": 10},
        ]
        save_questions(default)
        return default


def save_questions(questions):
    """Save questions to JSON file with backup"""
    if os.path.exists(QUESTIONS_FILE):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"questions_{timestamp}.json")
        shutil.copy(QUESTIONS_FILE, backup_path)
        print(f"✅ Backup created: {backup_path}")

    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    print(f"✅ Questions saved: {QUESTIONS_FILE}")


QUESTIONS = load_questions()


# ===== ROUTES =====

@app.route("/")
def home():
    return """
    <html>
    <body style='font-family:sans-serif;padding:40px;background:#0d0f18;color:#e2e8f0'>
        <h2>📚 Exam Platform Running</h2>
        <p style='margin-top:12px'>
            <a href='/admin' style='color:#7c6ff7'>Admin Panel</a> | 
            <a href='/admin/questions' style='color:#7c6ff7'>Manage Questions</a> |
            <a href='/admin/reports' style='color:#7c6ff7'>Reports</a> |
            <a href='/generate_links' style='color:#7c6ff7'>Generate Links</a>
        </p>
        <p style='color:#475569;margin-top:20px'>
            Students: <a href='/exam/student_name' style='color:#7c6ff7'>/exam/student_name</a>
        </p>
    </body>
    </html>
    """


@app.route("/exam/<student_id>")
def exam(student_id):
    """Student exam page"""
    current_questions = load_questions()
    if student_id not in sessions:
        sessions[student_id] = {
            "student_id": student_id,
            "start_time": datetime.datetime.now().isoformat(),
            "answers": {},
            "submitted": False,
            "video_saved": False,
            "video_file": None,
            "alerts": [],
            "chunk_count": 0
        }
        print(f"[NEW] Student joined: {student_id}")
    return render_template("exam.html",
                           student_id=student_id,
                           questions=current_questions,
                           submitted=sessions[student_id]["submitted"])


@app.route("/generate_links")
def generate_links():
    """Generate exam links for students"""
    # For Render, use RENDER_EXTERNAL_URL environment variable
    public_url = os.environ.get("RENDER_EXTERNAL_URL", os.environ.get("PUBLIC_URL", "http://localhost:5000"))

    # For local testing
    if os.path.exists("public_url.txt") and public_url == "http://localhost:5000":
        with open("public_url.txt", "r") as f:
            public_url = f.read().strip()

    students = ["rahul", "priya", "amit", "sneha", "vikram", "neha", "raj", "anita"]
    links = []
    for student in students:
        links.append({
            "name": student,
            "url": f"{public_url}/exam/{student}"
        })

    return render_template("generate_links.html", links=links, public_url=public_url)


@app.route("/upload_chunk/<student_id>", methods=["POST"])
def upload_chunk(student_id):
    """Receive video chunks during exam"""
    if "chunk" not in request.files:
        return jsonify({"error": "No chunk"}), 400

    chunk_file = request.files["chunk"]
    chunk_num = request.form.get("chunk_num", "0")
    chunk_type = request.form.get("type", "cam")

    student_dir = os.path.join(RECORDINGS_DIR, student_id)
    os.makedirs(student_dir, exist_ok=True)

    filename = f"{chunk_type}_chunk_{str(chunk_num).zfill(3)}.webm"
    chunk_file.save(os.path.join(student_dir, filename))

    if student_id in sessions:
        sessions[student_id]["chunk_count"] = int(chunk_num)

    print(f"[CHUNK] {student_id} -> {filename}")
    return jsonify({"status": "saved", "chunk": chunk_num})


@app.route("/upload_video/<student_id>", methods=["POST"])
def upload_video(student_id):
    """Receive final video on submission"""
    if "video" not in request.files:
        return jsonify({"error": "No video"}), 400

    video_file = request.files["video"]
    video_type = request.form.get("type", "cam")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{student_id}_{video_type}_{timestamp}_FINAL.webm"
    filepath = os.path.join(RECORDINGS_DIR, filename)
    video_file.save(filepath)
    size_mb = round(os.path.getsize(filepath) / (1024 * 1024), 2)

    print(f"[VIDEO] Saved: {filepath} ({size_mb} MB)")

    if student_id in sessions:
        sessions[student_id]["video_saved"] = True
        sessions[student_id]["video_file"] = filename

        log_path = os.path.join(RECORDINGS_DIR, f"{student_id}_{timestamp}_log.json")
        with open(log_path, "w", encoding='utf-8') as f:
            json.dump({
                "student": student_id,
                "start_time": sessions[student_id]["start_time"],
                "end_time": datetime.datetime.now().isoformat(),
                "video_file": filename,
                "alerts": sessions[student_id]["alerts"],
                "answers": sessions[student_id]["answers"]
            }, f, indent=2, ensure_ascii=False)

    return jsonify({"status": "saved", "file": filename, "size_mb": size_mb})


@app.route("/save_alert/<student_id>", methods=["POST"])
def save_alert(student_id):
    """Save proctoring alerts"""
    data = request.get_json()
    if student_id in sessions:
        sessions[student_id]["alerts"].append({
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "alert": data.get("alert", "")
        })
        print(f"[ALERT] {student_id}: {data.get('alert')}")
    return jsonify({"status": "ok"})


@app.route("/submit/<student_id>", methods=["POST"])
def submit(student_id):
    """Submit exam answers"""
    data = request.get_json()
    if student_id in sessions and not sessions[student_id]["submitted"]:
        sessions[student_id]["answers"] = data.get("answers", {})
        sessions[student_id]["submitted"] = True
        sessions[student_id]["end_time"] = datetime.datetime.now().isoformat()

        ans_path = os.path.join(RECORDINGS_DIR, f"{student_id}_answers.json")
        with open(ans_path, "w", encoding='utf-8') as f:
            json.dump(sessions[student_id], f, indent=2, ensure_ascii=False)
        print(f"[SUBMIT] {student_id} submitted")

    return jsonify({"status": "submitted"})


@app.route("/admin")
def admin():
    """Admin dashboard"""
    files = []
    for fname in os.listdir(RECORDINGS_DIR):
        fpath = os.path.join(RECORDINGS_DIR, fname)
        if os.path.isfile(fpath):
            files.append({
                "name": fname,
                "size_mb": round(os.path.getsize(fpath) / (1024 * 1024), 2)
            })

    folders = []
    for fname in os.listdir(RECORDINGS_DIR):
        fpath = os.path.join(RECORDINGS_DIR, fname)
        if os.path.isdir(fpath):
            folders.append({
                "name": fname,
                "chunks": len(os.listdir(fpath))
            })

    files.sort(key=lambda x: x["name"], reverse=True)

    public_url = os.environ.get("RENDER_EXTERNAL_URL", os.environ.get("PUBLIC_URL", "http://localhost:5000"))
    if os.path.exists("public_url.txt") and public_url == "http://localhost:5000":
        with open("public_url.txt", "r") as f:
            public_url = f.read().strip()

    return render_template("admin.html", sessions=sessions, files=files, folders=folders, public_url=public_url)


@app.route("/admin/questions", methods=['GET', 'POST'])
def manage_questions():
    """Question management page"""
    global QUESTIONS

    if request.method == 'POST':
        try:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                data = request.get_json()
                if 'questions' in data:
                    new_questions = data['questions']
                    save_questions(new_questions)
                    QUESTIONS = new_questions
                    return jsonify({"status": "success", "message": "Questions updated!"})

            new_questions = []
            question_count = int(request.form.get('question_count', 0))

            for i in range(question_count):
                q_type = request.form.get(f'q_{i}_type')
                q_data = {
                    "id": i + 1,
                    "question": request.form.get(f'q_{i}_question'),
                    "type": q_type,
                    "marks": int(request.form.get(f'q_{i}_marks', 5))
                }

                if q_type == 'mcq':
                    options = [
                        request.form.get(f'q_{i}_opt_0', ''),
                        request.form.get(f'q_{i}_opt_1', ''),
                        request.form.get(f'q_{i}_opt_2', ''),
                        request.form.get(f'q_{i}_opt_3', '')
                    ]
                    q_data["options"] = options
                    q_data["correct"] = int(request.form.get(f'q_{i}_correct', 0))

                new_questions.append(q_data)

            save_questions(new_questions)
            QUESTIONS = new_questions

            return jsonify({"status": "success", "message": "Questions updated!"})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    current_questions = load_questions()
    return render_template("manage_questions.html", questions=current_questions)


@app.route("/admin/reports")
def reports():
    """Generate reports"""
    report_data = []
    for fname in os.listdir(RECORDINGS_DIR):
        if fname.endswith("_answers.json"):
            fpath = os.path.join(RECORDINGS_DIR, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                report_data.append({
                    'student': data.get('student_id', 'Unknown'),
                    'submitted': data.get('submitted', False),
                    'answers': len(data.get('answers', {})),
                    'alerts': len(data.get('alerts', [])),
                    'start_time': data.get('start_time', ''),
                    'end_time': data.get('end_time', '')
                })

    return render_template("reports.html", reports=report_data)


@app.route("/recordings/<path:filename>")
def download_file(filename):
    """Download recording files"""
    return send_from_directory(RECORDINGS_DIR, filename, as_attachment=True)


@app.route("/api/questions", methods=['GET'])
def api_get_questions():
    """API endpoint to get current questions"""
    return jsonify(load_questions())


@app.route("/api/upload_questions", methods=['POST'])
def api_upload_questions():
    """API endpoint to upload questions via JSON"""
    global QUESTIONS

    try:
        data = request.get_json()
        if 'questions' not in data:
            return jsonify({"error": "Missing 'questions' field"}), 400

        new_questions = data['questions']
        save_questions(new_questions)
        QUESTIONS = new_questions
        return jsonify({"status": "success", "message": "Questions updated!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ===== API ROUTE FOR DAILY UPLOAD =====
@app.route("/api/daily_upload", methods=['POST'])
def api_daily_upload():
    """API endpoint to run daily upload"""
    global QUESTIONS

    try:
        from daily_upload import daily_upload
        questions = daily_upload()
        QUESTIONS = questions
        return jsonify({
            "status": "success",
            "message": f"Uploaded {len(questions)} questions for today",
            "questions": questions
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


# ===== MAIN =====
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  📚 EXAM PLATFORM STARTING")
    print("=" * 60)

    # Check if running on Render
    is_render = os.environ.get("RENDER", False)

    if is_render:
        print("  🚀 Running on Render.com")
        port = int(os.environ.get("PORT", 5000))
        print(f"  🌐 Port: {port}")
    else:
        print("  💻 Running locally on http://localhost:5000")
        print("  📝 To deploy on Render, push to GitHub and connect")

    print("\n" + "=" * 60)
    print("  💡 TIPS:")
    print("  • Press CTRL+C to stop the server")
    print("  • Use /generate_links to create student links")
    print("  • All recordings are saved locally in 'recordings/'")
    print("=" * 60 + "\n")

    # For Render, use the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=not is_render, host="0.0.0.0", port=port, threaded=True)