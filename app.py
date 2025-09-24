from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Session storage (in-memory, resets on reload)
applicants = {}
hrs = {}
jobs = {}
applications = {}
messages = {}

# ---------- Routes ----------

# Applicant Registration
@app.route("/register_applicant", methods=["POST"])
def register_applicant():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"status": "error", "msg": "Email required"}), 400
    applicants[email] = data
    return jsonify({"status": "success", "msg": "Applicant registered"}), 200

# Applicant Login
@app.route("/login_applicant", methods=["POST"])
def login_applicant():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if email in applicants and applicants[email]["password"] == password:
        return jsonify({"status": "success", "msg": "Logged in", "data": applicants[email]}), 200
    return jsonify({"status": "error", "msg": "Invalid credentials"}), 401

# HR Registration
@app.route("/register_hr", methods=["POST"])
def register_hr():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"status": "error", "msg": "Email required"}), 400
    hrs[email] = data
    return jsonify({"status": "success", "msg": "HR registered"}), 200

# HR Login
@app.route("/login_hr", methods=["POST"])
def login_hr():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if email in hrs and hrs[email]["password"] == password:
        return jsonify({"status": "success", "msg": "Logged in", "data": hrs[email]}), 200
    return jsonify({"status": "error", "msg": "Invalid credentials"}), 401

# Post Job
@app.route("/post_job", methods=["POST"])
def post_job():
    data = request.json
    job_id = str(datetime.now().timestamp()).replace(".", "")
    data["id"] = job_id
    data["posted_by"] = data.get("hr_email")
    jobs[job_id] = data
    return jsonify({"status": "success", "msg": "Job posted", "job_id": job_id}), 200

# Get Jobs (All active jobs)
@app.route("/get_jobs", methods=["GET"])
def get_jobs():
    now = datetime.now().date()
    active_jobs = [job for job in jobs.values() if datetime.strptime(job["endDate"], "%Y-%m-%d").date() >= now]
    return jsonify({"status": "success", "jobs": active_jobs}), 200

# Apply Job
@app.route("/apply_job", methods=["POST"])
def apply_job():
    data = request.json
    job_id = data.get("job_id")
    applicant_email = data.get("applicant_email")
    if not job_id or not applicant_email:
        return jsonify({"status": "error", "msg": "Missing job_id or applicant_email"}), 400
    app_id = str(datetime.now().timestamp()).replace(".", "")
    applications[app_id] = {
        "id": app_id,
        "job_id": job_id,
        "applicant_email": applicant_email,
        "status": "Viewed"
    }
    return jsonify({"status": "success", "msg": "Applied successfully"}), 200

# Get Applied Jobs for Applicant
@app.route("/get_applied_jobs/<applicant_email>", methods=["GET"])
def get_applied_jobs(applicant_email):
    applied = [app for app in applications.values() if app["applicant_email"]==applicant_email]
    return jsonify({"status": "success", "applied_jobs": applied}), 200

# Get Applications for HR
@app.route("/get_applications/<hr_email>", methods=["GET"])
def get_applications(hr_email):
    hr_jobs = [job for job in jobs.values() if job.get("hr_email") == hr_email]
    hr_applications = []
    for app_id, app in applications.items():
        if app["job_id"] in [job["id"] for job in hr_jobs]:
            hr_applications.append(app)
    return jsonify({"status": "success", "applications": hr_applications}), 200

# Update Application Status (Shortlist / Reject / Viewed)
@app.route("/update_status", methods=["POST"])
def update_status():
    data = request.json
    app_id = data.get("app_id")
    status = data.get("status")
    if app_id in applications:
        applications[app_id]["status"] = status
        return jsonify({"status": "success", "msg": "Status updated"}), 200
    return jsonify({"status": "error", "msg": "Application not found"}), 404

# Messaging
@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    key = f"{data.get('from_email')}_{data.get('to_email')}"
    if key not in messages:
        messages[key] = []
    messages[key].append({
        "from": data.get("from_email"),
        "to": data.get("to_email"),
        "message": data.get("message"),
        "timestamp": str(datetime.now())
    })
    return jsonify({"status": "success", "msg": "Message sent"}), 200

# Get Messages between two users
@app.route("/get_messages", methods=["GET"])
def get_messages():
    from_email = request.args.get("from_email")
    to_email = request.args.get("to_email")
    key1 = f"{from_email}_{to_email}"
    key2 = f"{to_email}_{from_email}"
    conv = messages.get(key1, []) + messages.get(key2, [])
    conv = sorted(conv, key=lambda x: x["timestamp"])
    return jsonify({"status": "success", "messages": conv}), 200

# Delete Job
@app.route("/delete_job", methods=["POST"])
def delete_job():
    job_id = request.json.get("job_id")
    if job_id in jobs:
        del jobs[job_id]
        # Remove related applications
        for app_id in list(applications.keys()):
            if applications[app_id]["job_id"] == job_id:
                del applications[app_id]
        return jsonify({"status": "success", "msg": "Job deleted"}), 200
    return jsonify({"status": "error", "msg": "Job not found"}), 404

# Edit Job
@app.route("/edit_job", methods=["POST"])
def edit_job():
    data = request.json
    job_id = data.get("job_id")
    if job_id in jobs:
        jobs[job_id].update(data.get("update_data", {}))
        return jsonify({"status": "success", "msg": "Job updated"}), 200
    return jsonify({"status": "error", "msg": "Job not found"}), 404

# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
