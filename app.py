from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import datetime

app = Flask(__name__)
CORS(app)

# ===============================
# In-Memory Storage (No Database)
# ===============================
candidates = {}
recruiters = {}
jobs = {}
applications = {}
messages = []
reports = []
admin = {"email": "admin@naukri.com", "password": "admin123"}

# ===============================
# Utility Functions
# ===============================
def generate_id():
    return str(uuid.uuid4())

# ===============================
# Candidate APIs
# ===============================
@app.route("/register_candidate", methods=["POST"])
def register_candidate():
    data = request.json
    cid = generate_id()
    candidates[cid] = data
    candidates[cid]["id"] = cid
    return jsonify({"message": "Candidate registered successfully", "id": cid})

@app.route("/login_candidate", methods=["POST"])
def login_candidate():
    data = request.json
    for cid, c in candidates.items():
        if c["email"] == data["email"] and c["password"] == data["password"]:
            return jsonify({"message": "Login success", "id": cid})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/candidates/<cid>", methods=["GET"])
def get_candidate(cid):
    return jsonify(candidates.get(cid, {}))

# ===============================
# Recruiter APIs
# ===============================
@app.route("/register_recruiter", methods=["POST"])
def register_recruiter():
    data = request.json
    rid = generate_id()
    recruiters[rid] = data
    recruiters[rid]["id"] = rid
    return jsonify({"message": "Recruiter registered successfully", "id": rid})

@app.route("/login_recruiter", methods=["POST"])
def login_recruiter():
    data = request.json
    for rid, r in recruiters.items():
        if r["email"] == data["email"] and r["password"] == data["password"]:
            return jsonify({"message": "Login success", "id": rid})
    return jsonify({"message": "Invalid credentials"}), 401

# ===============================
# Admin APIs
# ===============================
@app.route("/login_admin", methods=["POST"])
def login_admin():
    data = request.json
    if data["email"] == admin["email"] and data["password"] == admin["password"]:
        return jsonify({"message": "Admin login success"})
    return jsonify({"message": "Invalid admin credentials"}), 401

@app.route("/admin_stats", methods=["GET"])
def admin_stats():
    return jsonify({
        "total_candidates": len(candidates),
        "total_recruiters": len(recruiters),
        "total_reports": len(reports)
    })

@app.route("/admin_reports", methods=["GET"])
def admin_reports():
    return jsonify(reports)

@app.route("/admin_ban/<rid>", methods=["POST"])
def admin_ban(rid):
    if rid in recruiters:
        del recruiters[rid]
    # remove jobs
    for jid in list(jobs.keys()):
        if jobs[jid]["recruiter_id"] == rid:
            del jobs[jid]
    return jsonify({"message": "Recruiter banned"})

# ===============================
# Job Posting APIs
# ===============================
@app.route("/post_job", methods=["POST"])
def post_job():
    data = request.json
    jid = generate_id()
    data["id"] = jid
    jobs[jid] = data
    return jsonify({"message": "Job posted", "id": jid})

@app.route("/jobs", methods=["GET"])
def get_jobs():
    return jsonify(list(jobs.values()))

@app.route("/apply_job", methods=["POST"])
def apply_job():
    data = request.json
    aid = generate_id()
    applications[aid] = data
    applications[aid]["id"] = aid
    return jsonify({"message": "Applied successfully", "id": aid})

@app.route("/applications/<jid>", methods=["GET"])
def get_applications(jid):
    return jsonify([a for a in applications.values() if a["job_id"] == jid])

# ===============================
# Messaging & Reports
# ===============================
@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    msg = {
        "from": data["from"],
        "to": data["to"],
        "text": data["text"],
        "timestamp": str(datetime.datetime.now())
    }
    messages.append(msg)
    return jsonify({"message": "Message sent"})

@app.route("/messages/<uid>", methods=["GET"])
def get_messages(uid):
    return jsonify([m for m in messages if m["to"] == uid or m["from"] == uid])

@app.route("/report", methods=["POST"])
def report():
    data = request.json
    data["id"] = generate_id()
    reports.append(data)
    return jsonify({"message": "Report submitted"})

# ===============================
# Run App
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
