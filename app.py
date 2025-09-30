from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os
import uuid
from datetime import date

app = Flask(__name__)
CORS(app)

# JSON file storage
DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({
            "users": [
                {"email": "admin@naukri.com", "password": "admin123", "role": "admin"}
            ],
            "jobs": [],
            "applications": [],
            "messages": [],
            "reports": []
        }, f, indent=2)

def read_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def write_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------------- Register ----------------
@app.route("/register", methods=["POST"])
def register():
    data = read_data()
    user = request.json
    if any(u["email"] == user["email"] for u in data["users"]):
        return jsonify({"error": "User already exists"}), 400

    if user["role"] == "candidate":
        new_user = {
            "name": user["name"], "email": user["email"], "password": user["password"],
            "phone": user["phone"], "role": "candidate", "skills": user.get("skills",""),
            "resume": user.get("resume",""), "education": user.get("education",""),
            "certifications": user.get("certifications",""), "applied_jobs": []
        }
    elif user["role"] == "recruiter":
        new_user = {
            "name": user["name"], "email": user["email"], "password": user["password"],
            "phone": user["phone"], "role": "recruiter", "company": user.get("company",""),
            "designation": user.get("designation",""), "experience": user.get("experience",""),
            "posted_jobs": []
        }
    else:
        return jsonify({"error":"Invalid role"}), 400

    data["users"].append(new_user)
    write_data(data)
    return jsonify({"message":"Registered successfully"}), 201

# ---------------- Login ----------------
@app.route("/login", methods=["POST"])
def login():
    creds = request.json
    data = read_data()
    for u in data["users"]:
        if u["email"] == creds["email"] and u["password"] == creds["password"]:
            return jsonify({"message":"Login success", "role": u["role"], "user": u})
    return jsonify({"error":"Invalid credentials"}), 401

# ---------------- Post Job (Recruiter) ----------------
@app.route("/post_job", methods=["POST"])
def post_job():
    job = request.json
    job["id"] = str(uuid.uuid4())
    job["applications"] = []
    data = read_data()
    data["jobs"].append(job)
    # Add job to recruiter
    for u in data["users"]:
        if u["email"] == job.get("recruiter_email"):
            u.setdefault("posted_jobs", []).append(job["id"])
    write_data(data)
    return jsonify({"message":"Job posted"}), 201

# ---------------- Get All Jobs ----------------
@app.route("/jobs", methods=["GET"])
def get_jobs():
    data = read_data()
    today = str(date.today())
    # Only return jobs not expired
    active_jobs = [j for j in data["jobs"] if j.get("end_date","") >= today]
    return jsonify(active_jobs)

# ---------------- Apply Job ----------------
@app.route("/apply_job", methods=["POST"])
def apply_job():
    data = read_data()
    application = request.json  # candidate email + jobId
    job = next((j for j in data["jobs"] if j["id"]==application["jobId"]), None)
    if not job: return jsonify({"error":"Job not found"}), 404

    # Check duplicate
    if any(a["candidate"]==application["candidate"] and a["jobId"]==application["jobId"] for a in data["applications"]):
        return jsonify({"error":"Already applied"}), 400

    # Add to applications
    application["status"] = "Applied"
    data["applications"].append(application)
    # Update candidate profile
    for u in data["users"]:
        if u["email"]==application["candidate"]:
            u.setdefault("applied_jobs",[]).append(application["jobId"])
    write_data(data)
    return jsonify({"message":"Applied successfully"}), 201

# ---------------- Get Applications (Candidate / Recruiter) ----------------
@app.route("/applications/<email>", methods=["GET"])
def get_applications(email):
    data = read_data()
    user = next((u for u in data["users"] if u["email"]==email), None)
    if not user: return jsonify([])

    if user["role"]=="candidate":
        apps = [a for a in data["applications"] if a["candidate"]==email]
    elif user["role"]=="recruiter":
        # Only jobs posted by recruiter
        recruiter_jobs = user.get("posted_jobs",[])
        apps = [a for a in data["applications"] if a["jobId"] in recruiter_jobs]
    else:
        apps = data["applications"]
    return jsonify(apps)

# ---------------- Update Application Status (Shortlist / Reject) ----------------
@app.route("/application_status", methods=["POST"])
def application_status():
    payload = request.json  # jobId, candidate, status
    data = read_data()
    for a in data["applications"]:
        if a["jobId"]==payload["jobId"] and a["candidate"]==payload["candidate"]:
            a["status"] = payload["status"]
            # send message to candidate
            data["messages"].append({
                "from": a.get("recruiter_email","HR"),
                "to": a["candidate"],
                "message": f"Your application for job {payload['jobId']} is {payload['status']}"
            })
    write_data(data)
    return jsonify({"message":"Status updated"}), 200

# ---------------- Messaging ----------------
@app.route("/messages", methods=["POST"])
def send_message():
    msg = request.json  # from, to, message
    data = read_data()
    data["messages"].append(msg)
    write_data(data)
    return jsonify({"message":"Message sent"}),201

@app.route("/messages/<email>", methods=["GET"])
def get_messages(email):
    data = read_data()
    msgs = [m for m in data["messages"] if m["from"]==email or m["to"]==email]
    return jsonify(msgs)

# ---------------- Reports ----------------
@app.route("/report", methods=["POST"])
def report():
    rep = request.json
    data = read_data()
    data["reports"].append(rep)
    write_data(data)
    return jsonify({"message":"Report submitted"}),201

@app.route("/reports", methods=["GET"])
def get_reports():
    data = read_data()
    return jsonify(data["reports"])

# ---------------- Admin Actions ----------------
@app.route("/ban_user", methods=["POST"])
def ban_user():
    payload = request.json  # email
    data = read_data()
    # Remove user and their jobs
    data["users"] = [u for u in data["users"] if u["email"] != payload["email"]]
    data["jobs"] = [j for j in data["jobs"] if j.get("recruiter_email")!=payload["email"]]
    write_data(data)
    return jsonify({"message":"User banned"}),200

@app.route("/investigate_job", methods=["POST"])
def investigate_job():
    payload = request.json  # jobId
    data = read_data()
    for j in data["jobs"]:
        if j["id"]==payload["jobId"]:
            j["investigation"]=True
    write_data(data)
    return jsonify({"message":"Job under investigation"}),200

# ---------------- Update Profile ----------------
@app.route("/update_profile", methods=["POST"])
def update_profile():
    payload = request.json  # email + fields
    data = read_data()
    for u in data["users"]:
        if u["email"]==payload["email"]:
            for k,v in payload.items():
                if k!="email": u[k]=v
    write_data(data)
    return jsonify({"message":"Profile updated"}),200

if __name__=="__main__":
    app.run(debug=True)
