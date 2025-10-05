from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

users = []
jobs = []
applications = []
messages = []
interviews = []

# ---------- Helper ----------
def find_user(email, role):
    return next((u for u in users if u["email"] == email and u["role"] == role), None)

def find_job(job_id):
    return next((j for j in jobs if j["id"] == job_id), None)

# ---------- Register/Login ----------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if find_user(data["email"], data["role"]):
        return jsonify({"message": "User already exists"}), 400

    user = {
        "id": str(uuid.uuid4()),
        "name": data.get("name", ""),
        "email": data["email"],
        "password": data["password"],
        "role": data["role"],
        "extra_info": data.get("extra_info", {}),
    }
    users.append(user)
    return jsonify({"message": "Registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = find_user(data["email"], data["role"])
    if user and user["password"] == data["password"]:
        return jsonify({"message": "Login success", "user": user}), 200
    return jsonify({"message": "Invalid credentials"}), 401

# ---------- Jobs ----------
@app.route("/jobs", methods=["GET", "POST"])
def job_handler():
    if request.method == "POST":
        data = request.json
        job = {
            "id": str(uuid.uuid4()),
            "title": data["title"],
            "description": data["description"],
            "location": data["location"],
            "expiryDate": data["expiryDate"],
            "recruiterId": data["recruiterId"],
        }
        jobs.append(job)
        return jsonify({"message": "Job posted", "job": job}), 201

    now = datetime.now().strftime("%Y-%m-%d")
    active_jobs = [j for j in jobs if j["expiryDate"] >= now]
    return jsonify(active_jobs)

@app.route("/recruiters/<recruiter_id>/jobs", methods=["GET"])
def recruiter_jobs(recruiter_id):
    recruiter_jobs = [j for j in jobs if j["recruiterId"] == recruiter_id]
    return jsonify(recruiter_jobs)

# ---------- Applications ----------
@app.route("/apply", methods=["POST"])
def apply_job():
    data = request.json
    # Prevent duplicate applications
    existing = next((a for a in applications if a["candidateId"] == data["candidateId"] and a["jobId"] == data["jobId"]), None)
    if existing:
        return jsonify({"message": "You already applied for this job"}), 400

    application = {
        "id": str(uuid.uuid4()),
        "candidateId": data["candidateId"],
        "candidateName": data["candidateName"],
        "jobId": data["jobId"],
        "jobTitle": data["jobTitle"],
        "recruiterId": data["recruiterId"],
        "status": "applied",
        "appliedOn": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    applications.append(application)
    return jsonify({"message": "Applied successfully", "application": application}), 201


@app.route("/candidates/<candidate_id>/applications", methods=["GET"])
def candidate_applications(candidate_id):
    apps = [a for a in applications if a["candidateId"] == candidate_id]
    return jsonify(apps), 200


@app.route("/candidates/<candidate_id>/shortlisted", methods=["GET"])
def candidate_shortlisted(candidate_id):
    shortlisted = [a for a in applications if a["candidateId"] == candidate_id and a["status"] == "shortlisted"]
    return jsonify(shortlisted), 200


@app.route("/applications/<app_id>/shortlist", methods=["POST"])
def shortlist_application(app_id):
    for app_ in applications:
        if app_["id"] == app_id:
            app_["status"] = "shortlisted"
            app_["interviewDate"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return jsonify({"message": "Applicant shortlisted"}), 200
    return jsonify({"message": "Application not found"}), 404


@app.route("/applications/<app_id>/reject", methods=["POST"])
def reject_application(app_id):
    for app_ in applications:
        if app_["id"] == app_id:
            app_["status"] = "rejected"
            return jsonify({"message": "Applicant rejected"}), 200
    return jsonify({"message": "Application not found"}), 404

# ---------- Messages ----------
@app.route("/messages", methods=["GET", "POST"])
def handle_messages():
    if request.method == "POST":
        data = request.json
        message = {
            "id": str(uuid.uuid4()),
            "fromId": data["fromId"],
            "toId": data["toId"],
            "message": data["message"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        messages.append(message)
        return jsonify({"message": "Message sent"}), 201

    userId = request.args.get("userId")
    user_msgs = [
        {**m, "fromName": next((u["name"] for u in users if u["id"] == m["fromId"]), "")}
        for m in messages
        if m["toId"] == userId or m["fromId"] == userId
    ]
    return jsonify({"messages": user_msgs}), 200

# ---------- Interviews ----------
@app.route("/interviews", methods=["POST", "GET"])
def interviews_handler():
    if request.method == "POST":
        data = request.json
        interviews.append({
            "id": str(uuid.uuid4()),
            "candidateId": data["candidateId"],
            "jobId": data["jobId"],
            "dateTime": data["dateTime"],
            "status": "scheduled"
        })
        return jsonify({"message": "Interview scheduled"}), 201

    userId = request.args.get("userId")
    user_interviews = [i for i in interviews if i["candidateId"] == userId or
                       any(j["id"] == i["jobId"] and j["recruiterId"] == userId for j in jobs)]
    return jsonify(user_interviews), 200

if __name__ == "__main__":
    app.run(debug=True)
