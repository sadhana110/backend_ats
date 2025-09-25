from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

applicants = {}
hrs = {}
jobs = {}
applications = {}

@app.route("/")
def home():
    return "Backend is running"

# Applicant Register
@app.route("/register/applicant", methods=["POST"])
def register_applicant():
    data = request.json
    email = data.get("email")
    if email in applicants:
        return jsonify({"error": "Applicant already exists"}), 400
    applicants[email] = data
    return jsonify({"message": "Applicant registered"})

# HR Register
@app.route("/register/hr", methods=["POST"])
def register_hr():
    data = request.json
    email = data.get("email")
    if email in hrs:
        return jsonify({"error": "HR already exists"}), 400
    hrs[email] = data
    return jsonify({"message": "HR registered"})

# Applicant Login
@app.route("/login/applicant", methods=["POST"])
def login_applicant():
    data = request.json
    email, password = data.get("email"), data.get("password")
    if email in applicants and applicants[email]["password"] == password:
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401

# HR Login
@app.route("/login/hr", methods=["POST"])
def login_hr():
    data = request.json
    email, password = data.get("email"), data.get("password")
    if email in hrs and hrs[email]["password"] == password:
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401

# Post Job
@app.route("/jobs", methods=["POST"])
def post_job():
    data = request.json
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"id": job_id, **data}
    return jsonify({"message": "Job posted", "id": job_id})

# Get Jobs
@app.route("/jobs", methods=["GET"])
def get_jobs():
    return jsonify(list(jobs.values()))

# Apply Job
@app.route("/apply", methods=["POST"])
def apply_job():
    data = request.json
    job_id, email = data.get("job_id"), data.get("email")
    if (job_id, email) in applications:
        return jsonify({"error": "Already applied"}), 400
    applications[(job_id, email)] = data
    return jsonify({"message": "Applied successfully"})

# View Applied Jobs
@app.route("/applied/<email>", methods=["GET"])
def view_applied(email):
    result = [v for (jid, em), v in applications.items() if em == email]
    return jsonify(result)

# View Applicants for HR
@app.route("/applicants/<job_id>", methods=["GET"])
def view_applicants(job_id):
    result = [v for (jid, em), v in applications.items() if jid == job_id]
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
