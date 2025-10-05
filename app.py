from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)  # allow cross-origin requests

# ------------------ IN-MEMORY DATA ------------------
users = []        # {id,name,email,password,role,extra_info}
jobs = []         # {id,title,description,location,expiryDate,recruiterId}
applications = [] # {id,candidateId,jobId,status}
shortlisted = []  # {id,candidateId,jobId}
messages = []     # {id,fromId,toId,message,date}
interviews = []   # {id,candidateId,jobId,dateTime,status}

# ------------------ HELPER ------------------
def find_user(email, role):
    return next((u for u in users if u['email']==email and u['role']==role), None)

def find_job(job_id):
    return next((j for j in jobs if j['id']==job_id), None)

# ------------------ AUTH ------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if find_user(data['email'], data['role']):
        return jsonify({'message':'User already exists'}), 400
    user = {
        'id': str(uuid.uuid4()),
        'name': data.get('name',''),
        'email': data['email'],
        'password': data['password'],
        'role': data['role'],
        'extra_info': data.get('extra_info',{})
    }
    users.append(user)
    return jsonify({'message':'Registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = find_user(data['email'], data['role'])
    if user and user['password']==data['password']:
        return jsonify({'message':'Login success','user':user}), 200
    return jsonify({'message':'Invalid credentials'}), 401

# ------------------ JOBS ------------------
@app.route('/jobs', methods=['GET','POST'])
def job_handler():
    if request.method=='POST':
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
        return jsonify({'message':'Job posted','job':job}), 201
    # GET
    now = datetime.now().strftime('%Y-%m-%d')
    active_jobs = [j for j in jobs if j['expiryDate']>=now]
    return jsonify(active_jobs)

@app.route('/recruiters/<recruiter_id>/jobs', methods=['GET'])
def recruiter_jobs(recruiter_id):
    recruiter_jobs = [j for j in jobs if j['recruiterId'] == recruiter_id]
    return jsonify(recruiter_jobs)

@app.route('/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    global jobs
    jobs = [j for j in jobs if j['id'] != job_id]
    return jsonify({'message': 'Job deleted'}), 200

# -------------------- APPLICATIONS --------------------
applications = []
messages = []

@app.route('/apply', methods=['POST'])
def apply_job():
    data = request.json
    application = {
        'id': str(uuid.uuid4()),
        'candidateId': data['candidateId'],
        'candidateName': data['candidateName'],
        'jobId': data['jobId'],
        'jobTitle': data['jobTitle'],
        'recruiterId': data['recruiterId'],
        'status': 'applied'
    }
    applications.append(application)
    return jsonify({'message': 'Application submitted', 'application': application}), 201


@app.route('/recruiters/<recruiter_id>/applications', methods=['GET'])
def recruiter_applications(recruiter_id):
    apps = [a for a in applications if a['recruiterId'] == recruiter_id]
    return jsonify(apps)


@app.route('/applications/<app_id>/shortlist', methods=['POST'])
def shortlist_application(app_id):
    for app in applications:
        if app['id'] == app_id:
            app['status'] = 'shortlisted'
            app['interviewDate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return jsonify({'message': 'Applicant shortlisted'}), 200
    return jsonify({'message': 'Application not found'}), 404


@app.route('/applications/<app_id>/reject', methods=['POST'])
def reject_application(app_id):
    for app in applications:
        if app['id'] == app_id:
            app['status'] = 'rejected'
            return jsonify({'message': 'Applicant rejected'}), 200
    return jsonify({'message': 'Application not found'}), 404


@app.route('/recruiters/<recruiter_id>/shortlisted', methods=['GET'])
def shortlisted_applicants(recruiter_id):
    shortlisted = [a for a in applications if a['recruiterId'] == recruiter_id and a['status'] == 'shortlisted']
    return jsonify(shortlisted)


# -------------------- MESSAGES --------------------
@app.route('/messages', methods=['GET', 'POST'])
def handle_messages():
    if request.method == 'POST':
        data = request.json
        message = {
            'id': str(uuid.uuid4()),
            'from': data['from'],
            'to': data['to'],
            'message': data['message'],
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        messages.append(message)
        return jsonify({'message': 'Message sent'}), 201

    # GET
    user_id = request.args.get('userId')
    user_messages = [m for m in messages if m['to'] == user_id or m['from'] == user_id]
    return jsonify({'messages': user_messages})





# ------------------ APPLICATIONS ------------------
@app.route('/applications', methods=['GET','POST'])
def applications_handler():
    if request.method=='POST':
        data = request.json
        applications.append({
            'id': str(uuid.uuid4()),
            'candidateId': data['candidateId'],
            'jobId': data['jobId'],
            'status': 'applied'
        })
        return jsonify({'message':'Applied'}),201
    userId = request.args.get('userId')
    user_apps = []
    for app_ in applications:
        if app_['candidateId']==userId:
            job = find_job(app_['jobId'])
            user_apps.append({
                'jobTitle': job['title'] if job else '',
                'status': app_['status'],
                'recruiterName': next((u['name'] for u in users if u['id']==job['recruiterId']), '') if job else ''
            })
    return jsonify(user_apps)

# ------------------ SHORTLISTED ------------------
@app.route('/shortlisted', methods=['GET','POST'])
def shortlist_handler():
    userId = request.args.get('userId')
    user_short = []
    for s in shortlisted:
        if s['candidateId']==userId:
            job = find_job(s['jobId'])
            user_short.append({
                'jobTitle': job['title'] if job else '',
                'recruiterName': next((u['name'] for u in users if u['id']==job['recruiterId']), '') if job else ''
            })
    return jsonify(user_short)

# ------------------ MESSAGES ------------------
@app.route('/messages', methods=['GET','POST'])
def messages_handler():
    if request.method=='POST':
        data = request.json
        messages.append({
            'id': str(uuid.uuid4()),
            'fromId': data['fromId'],
            'toId': data['toId'],
            'message': data['message'],
            'date': datetime.now().isoformat()
        })
        return jsonify({'message':'Message sent'}),201
    userId = request.args.get('userId')
    user_msgs = [ {**m,'fromName':next((u['name'] for u in users if u['id']==m['fromId']), '')} 
                  for m in messages if m['toId']==userId]
    return jsonify(user_msgs)

# ------------------ INTERVIEWS ------------------
@app.route('/interviews', methods=['POST','GET'])
def interviews_handler():
    if request.method=='POST':
        data = request.json
        interviews.append({
            'id': str(uuid.uuid4()),
            'candidateId': data['candidateId'],
            'jobId': data['jobId'],
            'dateTime': data['dateTime'],
            'status': 'scheduled'
        })
        return jsonify({'message':'Interview scheduled'}),201
    userId = request.args.get('userId')
    user_interviews = [i for i in interviews if i['candidateId']==userId or 
                       any(j['id']==i['jobId'] and j['recruiterId']==userId for j in jobs)]
    return jsonify(user_interviews)

# ------------------ RUN ------------------
if __name__=='__main__':
    app.run(debug=True)
