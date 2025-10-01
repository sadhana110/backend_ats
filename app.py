from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

users = []
jobs = []

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    users.append(data)
    return jsonify({"success": True})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    for u in users:
        if u["email"] == data["email"] and u["password"] == data["password"] and u["role"] == data["role"]:
            return jsonify({"success": True, "user": u})
    return jsonify({"success": False})

@app.route("/postjob", methods=["POST"])
def postjob():
    jobs.append(request.json)
    return jsonify({"success": True})

@app.route("/jobs", methods=["GET"])
def get_jobs():
    return jsonify(jobs)

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
