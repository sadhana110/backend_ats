from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

# ---- In-memory storage ----
users = []
jobs = []

# ---- User Routes ----
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data.get('email') or not data.get('password') or not data.get('role'):
        return jsonify({'error': 'Missing fields'}), 400
    if any(u['email'] == data['email'] for u in users):
        return jsonify({'error': 'Email already exists'}), 400
    users.append(data)
    return jsonify({'message': 'Registered successfully', 'user': data})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = next((u for u in users if u['email'] == data.get('email') 
                 and u['password'] == data.get('password') 
                 and u['role'] == data.get('role')), None)
    if user:
        return jsonify({'message': 'Login successful', 'user': user})
    return jsonify({'error': 'Invalid credentials'}), 401

# ---- Job Routes ----
@app.route('/jobs', methods=['GET'])
def get_jobs():
    return jsonify(jobs)

@app.route('/jobs', methods=['POST'])
def post_job():
    data = request.json
    job = {
        'id': str(len(jobs) + 1),
        'title': data.get('title'),
        'company': data.get('company'),
        'location': data.get('location'),
        'experience': data.get('experience'),
        'type': data.get('type'),
        'salary': data.get('salary'),
        'description': data.get('description'),
        'applied': []
    }
    jobs.append(job)
    return jsonify({'message': 'Job posted', 'job': job})

@app.route('/jobs/<job_id>/apply', methods=['POST'])
def apply_job(job_id):
    data = request.json
    email = data.get('email')
    user = next((u for u in users if u['email'] == email and u['role'] == 'applicant'), None)
    if not user:
        return jsonify({'error': 'Applicant not found'}), 404
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    if email in job['applied']:
        return jsonify({'message': 'Already applied'})
    job['applied'].append(email)
    return jsonify({'message': 'Applied successfully', 'job': job})

# ---- Run Server ----
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Dynamic port for Render
    app.run(host='0.0.0.0', port=port)
