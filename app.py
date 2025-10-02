from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# In-memory storage
users = []
jobs = []
applications = []
messages = []
interviews = []
admin_reports = []

# Utility functions
def find_user(email):
    for u in users:
        if u['email'] == email:
            return u
    return None

def find_job(job_id):
    for j in jobs:
        if j['id'] == job_id:
            return j
    return None

def auto_expire_jobs():
    global jobs
    now = datetime.now()
    jobs = [j for j in jobs if j['end_date'] >= now]

# Routes

# Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if find_user(data['email']):
        return jsonify({'status':'fail','message':'Email already exists'})
    user = {
        'id': len(users)+1,
        'role': data['role'],
        'email': data['email'],
        'password': data['password'],
        'details': data['details'], # All candidate/recruiter registration info
    }
    users.append(user)
    return jsonify({'status':'success','message':'Registered successfully'})

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = find_user(data['email'])
    if user and user['password'] == data['password'] and user['role'] == data['role']:
        return jsonify({'status':'success','user': user})
    return jsonify({'status':'fail','message':'Invalid credentials'})

# Post Job (Recruiter)
@app.route('/post_job', methods=['POST'])
def post_job():
    data = request.json
    job = {
        'id': len(jobs)+1,
        'recruiter_email': data['recruiter_email'],
        'title': data['title'],
        'description': data['description'],
        'skills': data['skills'],
        'location': data['location'],
        'end_date': datetime.strptime(data['end_date'], '%Y-%m-%d'),
    }
    jobs.append(job)
    return jsonify({'status':'success','job': job})

# Get all jobs
@app.route('/jobs', methods=['GET'])
def get_jobs():
    auto_expire_jobs()
    return jsonify({'jobs': jobs})

# Apply Job (Candidate)
@app.route('/apply', methods=['POST'])
def apply_job():
    data = request.json
    applications.append({
        'job_id': data['job_id'],
        'candidate_email': data['candidate_email'],
        'status': 'applied'
    })
    return jsonify({'status':'success'})

# Shortlist/Reject
@app.route('/update_application', methods=['POST'])
def update_application():
    data = request.json
    for app_obj in applications:
        if app_obj['job_id'] == data['job_id'] and app_obj['candidate_email'] == data['candidate_email']:
            app_obj['status'] = data['status'] # shortlisted / rejected
            return jsonify({'status':'success'})
    return jsonify({'status':'fail','message':'Application not found'})

# Schedule Interview
@app.route('/schedule_interview', methods=['POST'])
def schedule_interview():
    data = request.json
    interviews.append({
        'job_id': data['job_id'],
        'candidate_email': data['candidate_email'],
        'recruiter_email': data['recruiter_email'],
        'date_time': data['date_time'],
        'venue': data['venue'],
        'status': 'scheduled'
    })
    return jsonify({'status':'success'})

# Messaging
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    messages.append({
        'from': data['from'],
        'to': data['to'],
        'message': data['message'],
        'timestamp': datetime.now().isoformat()
    })
    return jsonify({'status':'success'})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    user_email = request.args.get('email')
    user_msgs = [m for m in messages if m['to'] == user_email or m['from'] == user_email]
    return jsonify({'messages': user_msgs})

# Admin: Ban / Investigate
@app.route('/admin_action', methods=['POST'])
def admin_action():
    data = request.json
    user = find_user(data['email'])
    if not user:
        return jsonify({'status':'fail','message':'User not found'})
    if data['action'] == 'ban':
        users.remove(user)
        # Remove their jobs if recruiter
        global jobs
        jobs = [j for j in jobs if j['recruiter_email'] != data['email']]
    elif data['action'] == 'investigate':
        user['investigating'] = True
    return jsonify({'status':'success'})

# Run server
if __name__ == '__main__':
    app.run(debug=True)
