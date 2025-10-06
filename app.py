from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)  # allow cross-origin requests

# ------------------ IN-MEMORY DATA ------------------
users = []          # {id,name,email,password,role,extra_info}
jobs = []           # {id,title,description,location,expiryDate,recruiterId}
applications = []   # {id,candidateId,jobId,status,jobTitle,recruiterId}
shortlisted = []    # {id,candidateId,jobId}
messages = []       # {id,fromId,toId,message,date}
interviews = []     # {id,candidateId,jobId,dateTime,status}

# ------------------ HELPER FUNCTIONS ------------------
def find_user(email, role):
    return next((u for u in users if u['email'] == email and u['role'] == role), None)

def find_job(job_id):
    return next((j for j in jobs if j['id'] == job_id), None)

# ------------------ AUTH ------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if find_user(data['email'], data['role']):
        return jsonify({'message': 'User already exists'}), 400

    user = {
        'id': str(uuid.uuid4()),
        'name': data.get('name', ''),
        'email': data['email'],
        'password': data['password'],
        'role': data['role'],
        'extra_info': data.get('extra_info', {})
    }
    users.append(user)
    return jsonify({'message': 'Registered successfully', 'user': user}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = find_user(data['email'], data['role'])
    if user and user['password'] == data['password']:
        return jsonify({'message': 'Login success', 'user': user}), 200
    return jsonify({'message': 'Invalid credentials'}), 401


# ------------------ JOBS ------------------
@app.route('/jobs', methods=['GET', 'POST'])
def job_handler():
    if request.method == 'POST':
        data = request.json
        job = {
            'id': str(uuid.uuid4()),
            'title': data['title'],
            'description': data['description'],
            'location': data['location'],
            'expiryDate': data['expiryDate'],
            'recruiterId': data['recruiterId']
        }
        jobs.append(job)
        return jsonify({'message': 'Job posted', 'job': job}), 201

    # GET
    now = datetime.now().strftime('%Y-%m-%d')
    active_jobs = [j for j in jobs if j['expiryDate'] >= now]
    return jsonify(active_jobs)


@app.route('/recruiters/<recruiter_id>/jobs', methods=['GET'])
def recruiter_jobs(recruiter_id):
    rec_jobs = [j for j in jobs if j['recruiterId'] == recruiter_id]
    return jsonify(rec_jobs)


@app.route('/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    global jobs
    jobs = [j for j in jobs if j['id'] != job_id]
    return jsonify({'message': 'Job deleted'}), 200


# ------------------ APPLICATIONS ------------------
# -------------------- APPLY JOB --------------------
@app.route('/apply', methods=['POST'])
def apply_job():
    data = request.json
    app_entry = {
        "id": str(uuid.uuid4()),
        "candidateId": data['candidateId'],
        "candidateName": data['candidateName'],
        "jobId": data['jobId'],
        "jobTitle": data['jobTitle'],
        "recruiterId": data['recruiterId'],
        "status": "applied",
        "appliedDate": datetime.now().isoformat()
    }
    applications.append(app_entry)
    return jsonify({"message": "Application submitted successfully!"}), 201


# -------------------- CANDIDATE APPLICATIONS --------------------
@app.route('/candidates/<candidate_id>/applications')
def candidate_applications(candidate_id):
    user_apps = [a for a in applications if a['candidateId'] == candidate_id]
    return jsonify(user_apps)


# -------------------- CANDIDATE SHORTLISTED JOBS --------------------
@app.route('/candidates/<candidate_id>/shortlisted')
def candidate_shortlisted(candidate_id):
    shortlisted = [a for a in applications if a['candidateId'] == candidate_id and a['status'] == 'shortlisted']
    return jsonify(shortlisted)


# -------------------- RECRUITER APPLICATIONS --------------------
@app.route('/recruiters/<recruiter_id>/applications')
def recruiter_applications(recruiter_id):
    recruiter_apps = [a for a in applications if a['recruiterId'] == recruiter_id]
    return jsonify(recruiter_apps)


# -------------------- SHORTLIST / REJECT --------------------
@app.route('/applications/<app_id>/shortlist', methods=['POST'])
def shortlist_application(app_id):
    for app in applications:
        if app['id'] == app_id:
            app['status'] = 'shortlisted'
            app['interviewDate'] = datetime.now().isoformat()
            return jsonify({'message': 'Applicant shortlisted successfully'}), 200
    return jsonify({'message': 'Application not found'}), 404


@app.route('/applications/<app_id>/reject', methods=['POST'])
def reject_application(app_id):
    for app in applications:
        if app['id'] == app_id:
            app['status'] = 'rejected'
            return jsonify({'message': 'Applicant rejected successfully'}), 200
    return jsonify({'message': 'Application not found'}), 404



# -------------------- RECRUITER SHORTLISTED VIEW --------------------
@app.route('/recruiters/<recruiter_id>/shortlisted')
def recruiter_shortlisted(recruiter_id):
    recruiter_apps = [a for a in applications if a['recruiterId'] == recruiter_id and a['status'] == 'shortlisted']
    return jsonify(recruiter_apps)

# ------------------ MESSAGES ------------------
# Update application schema to include approval status
# status: applied / shortlisted / rejected
# approval: pending / approved / blocked
applications = []   # existing
messages = []       # existing

# Approve or block candidate
@app.route('/applications/<app_id>/approve', methods=['POST'])
def approve_candidate(app_id):
    for app in applications:
        if app['id'] == app_id and app['status'] == 'shortlisted':
            data = request.json
            app['approval'] = 'approved' if data.get('approve') else 'blocked'
            return jsonify({'message': f"Candidate {app['approval']} successfully"}), 200
    return jsonify({'message': 'Application not found or not shortlisted'}), 404

# Send message
@app.route('/messages', methods=['POST', 'GET'])
def messages_handler():
    if request.method == 'POST':
        data = request.json
        # Only allow messaging if candidate is approved
        app_entry = next((a for a in applications if a['candidateId'] == data['toId'] and a['recruiterId'] == data['fromId']), None)
        if not app_entry or app_entry.get('approval') != 'approved':
            return jsonify({'message': 'Cannot send message: Candidate not approved'}), 403

        msg = {
            'id': str(uuid.uuid4()),
            'fromId': data['fromId'],
            'toId': data['toId'],
            'message': data['message'],
            'date': datetime.now().isoformat()
        }
        messages.append(msg)
        return jsonify({'message': 'Message sent successfully'}), 201

    # GET: fetch all messages for a user
    user_id = request.args.get('userId')
    user_msgs = [m for m in messages if m['toId'] == user_id or m['fromId'] == user_id]
    return jsonify({'messages': user_msgs})

# -------------------- RECRUITER MESSAGE HANDLER --------------------
@app.route('/recruiter/messages', methods=['GET', 'POST'])
def recruiter_messages():
    """
    GET: Fetch all messages for this recruiter (optionally filtered by candidateId)
    POST: Send a message from recruiter to candidate (only if approved).
    """
    if request.method == 'POST':
        data = request.get_json()

        # Verify approval before allowing recruiter to message candidate
        app_entry = next(
            (
                a for a in applications
                if a['candidateId'] == data['toId']
                and a['recruiterId'] == data['fromId']
                and a.get('status') == 'shortlisted'
                and a.get('approval') == 'approved'
            ),
            None
        )
        if not app_entry:
            return jsonify({'message': 'Cannot send message: Candidate not approved yet'}), 403

        # Create message
        msg = {
            'id': str(uuid.uuid4()),
            'fromId': data['fromId'],
            'fromName': data.get('fromName', ''),
            'fromEmail': data.get('fromEmail', ''),
            'toId': data['toId'],
            'toName': data.get('toName', ''),
            'message': data['message'],
            'date': datetime.now().isoformat()
        }
        messages.append(msg)
        return jsonify({'message': 'Message sent successfully'}), 201

    # -------------------- GET Messages --------------------
    recruiter_id = request.args.get('recruiterId')
    candidate_id = request.args.get('candidateId')

    recruiter_msgs = [
        m for m in messages
        if recruiter_id in (m['fromId'], m['toId'])
    ]

    # If candidateId is provided → show conversation between both
    if candidate_id:
        recruiter_msgs = [
            m for m in recruiter_msgs
            if candidate_id in (m['fromId'], m['toId'])
        ]

    # Sort by date for proper chat order
    recruiter_msgs.sort(key=lambda x: x['date'])
    return jsonify({'messages': recruiter_msgs})


# -------------------- CANDIDATE MESSAGES --------------------
@app.route('/candidate/messages', methods=['GET', 'POST'])
def candidate_messages():
    """
    GET: Fetch all messages for this candidate.
    POST: Send message from candidate to a recruiter (only if approved).
    """
    if request.method == 'POST':
        data = request.json
        # Check if candidate is approved for this recruiter
        app_entry = next(
            (a for a in applications
             if a['candidateId'] == data['fromId'] and a['recruiterId'] == data['toId']
             and a.get('status') == 'shortlisted'),
            None
        )
        if not app_entry:
            return jsonify({'message': 'Cannot send message: Not approved or not shortlisted'}), 403

        msg = {
            'id': str(uuid.uuid4()),
            'fromId': data['fromId'],
            'fromName': data.get('fromName'),
            'fromEmail': data.get('fromEmail'),
            'toId': data['toId'],
            'toName': data.get('toName', ''),
            'message': data['message'],
            'date': datetime.now().isoformat()
        }
        messages.append(msg)
        return jsonify({'message': 'Message sent successfully'}), 201

    # GET messages for candidate
    candidate_id = request.args.get('candidateId')
    candidate_msgs = [m for m in messages if m['toId'] == candidate_id or m['fromId'] == candidate_id]
    return jsonify({'messages': candidate_msgs})



# ------------------ INTERVIEWS ------------------
@app.route('/interviews', methods=['POST', 'GET'])
def interviews_handler():
    if request.method == 'POST':
        data = request.json
        interviews.append({
            'id': str(uuid.uuid4()),
            'candidateId': data['candidateId'],
            'jobId': data['jobId'],
            'dateTime': data['dateTime'],
            'status': 'scheduled'
        })
        return jsonify({'message': 'Interview scheduled'}), 201

    userId = request.args.get('userId')
    user_interviews = [i for i in interviews if i['candidateId'] == userId or
                       any(j['id'] == i['jobId'] and j['recruiterId'] == userId for j in jobs)]
    return jsonify(user_interviews)


# ------------------ ROOT ------------------
@app.route('/')
def home():
    return jsonify({'message': 'Backend ATS Running Successfully ✅'})


# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(debug=True)
