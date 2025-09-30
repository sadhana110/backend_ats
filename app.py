from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# In-memory storage (reset if backend restarts on Render free tier)
candidates = []
recruiters = []
admins = [{"email": "admin@naukri.com", "password": "admin123"}]
jobs = []
applications = []
messages = []
reports = []

# ===== Registration =====
@app.route("/register_candidate", methods=["POST"])
def register_candidate():
    data = request.json
    data["_id"] = str(len(candidates) + 1)
    data["saved_jobs"] = []
    data["applied_jobs"] = []
    candidates.append(data)
    return jsonify({"success": True, "message": "Candidate registered successfully"})

@app.route("/register_recruiter", methods=["POST"])
def register_recruiter():
    data = request.json
    data["_id"] = str(len(recruiters) + 1)
    recruiters.append(data)
    return jsonify({"success": True, "message": "Recruiter registered successfully"})

# ===== Login =====
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    role = data.get("role")
    email = data.get("email")
    password = data.get("password")

    user = None
    if role == "candidate":
        user = next((c for c in candidates if c["email"] == email and c["password"] == password), None)
    elif role == "recruiter":
        user = next((r for r in recruiters if r["email"] == email and r["password"] == password), None)
    elif role == "admin":
        user = next((a for a in admins if a["email"] == email and a["password"] == password), None)

    if user:
        return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "message": "Invalid credentials"})

# ===== Jobs =====
@app.route("/post_job", methods=["POST"])
def post_job():
    data = request.json
    data["_id"] = str(len(jobs) + 1)
    data["posted"] = datetime.now().isoformat()
    data["status"] = "active"
    jobs.append(data)
    return jsonify({"success": True, "message": "Job posted successfully"})

@app.route("/jobs")
def get_jobs():
    return jsonify([j for j in jobs if j["status"] == "active"])

@app.route("/recruiter_jobs/<rid>")
def recruiter_jobs(rid):
    return jsonify([j for j in jobs if j["recruiterId"] == rid])

@app.route("/delete_job", methods=["POST"])
def delete_job():
    data = request.json
    job = next((j for j in jobs if j["_id"] == data["jobId"]), None)
    if job:
        job["status"] = "deleted"
    return jsonify({"success": True, "message": "Job deleted"})

# ===== Apply / Save Jobs =====
@app.route("/apply", methods=["POST"])
def apply():
    data = request.json
    applications.append({
        "_id": str(len(applications) + 1),
        "candidateId": data["candidateId"],
        "jobId": data["jobId"],
        "status": "applied"
    })
    candidate = next((c for c in candidates if c["_id"] == data["candidateId"]), None)
    if candidate:
        candidate["applied_jobs"].append(data["jobId"])
    return jsonify({"success": True, "message": "Applied successfully"})

@app.route("/save_job", methods=["POST"])
def save_job():
    data = request.json
    candidate = next((c for c in candidates if c["_id"] == data["candidateId"]), None)
    if candidate:
        if data["jobId"] not in candidate["saved_jobs"]:
            candidate["saved_jobs"].append(data["jobId"])
    return jsonify({"success": True, "message": "Job saved successfully"})

@app.route("/applicants/<jobId>")
def applicants(jobId):
    apps = [a for a in applications if a["jobId"] == jobId]
    res = []
    for app_obj in apps:
        candidate = next((c for c in candidates if c["_id"] == app_obj["candidateId"]), None)
        if candidate:
            res.append({"candidate": candidate, "status": app_obj["status"]})
    return jsonify(res)

# ===== Shortlist / Reject =====
@app.route("/shortlist", methods=["POST"])
def shortlist():
    data = request.json
    app_obj = next((a for a in applications if a["candidateId"] == data["candidateId"] and a["jobId"] == data["jobId"]), None)
    if app_obj:
        app_obj["status"] = "shortlisted"
    return jsonify({"success": True, "message": "Candidate shortlisted"})

@app.route("/reject", methods=["POST"])
def reject():
    data = request.json
    app_obj = next((a for a in applications if a["candidateId"] == data["candidateId"] and a["jobId"] == data["jobId"]), None)
    if app_obj:
        app_obj["status"] = "rejected"
    return jsonify({"success": True, "message": "Candidate rejected"})

# ===== Messaging =====
@app.route("/message", methods=["POST"])
def message():
    data = request.json
    data["_id"] = str(len(messages) + 1)
    data["timestamp"] = datetime.now().isoformat()
    messages.append(data)
    return jsonify({"success": True, "message": "Message sent"})

@app.route("/get_messages/<uid>")
def get_messages(uid):
    return jsonify([m for m in messages if m["toId"] == uid or m["fromId"] == uid])

# ===== Reports =====
@app.route("/report", methods=["POST"])
def report():
    data = request.json
    data["_id"] = str(len(reports) + 1)
    data["timestamp"] = datetime.now().isoformat()
    reports.append(data)
    return jsonify({"success": True, "message": "Report submitted"})

@app.route("/reports")
def get_reports():
    return jsonify(reports)

# ===== Admin =====
@app.route("/admin_stats")
def admin_stats():
    return jsonify({
        "candidates": len(candidates),
        "recruiters": len(recruiters),
        "jobs": len(jobs),
        "reports": len(reports)
    })

@app.route("/ban_recruiter", methods=["POST"])
def ban_recruiter():
    data = request.json
    rid = data.get("recruiterId")
    recruiter = next((r for r in recruiters if r["_id"] == rid), None)
    if recruiter:
        recruiters.remove(recruiter)
        # Remove their jobs
        for j in jobs:
            if j["recruiterId"] == rid:
                j["status"] = "banned"
    return jsonify({"success": True, "message": "Recruiter banned"})

# ===== Run =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
