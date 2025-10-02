from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory storage
users = {'candidate': [], 'recruiter': [], 'admin': []}
jobs = []  # {'id','title','company','description','location','end_date'}
applications = []  # {'job_id','candidate_email','status','shortlist'}
messages = []  # {'from','to','message','timestamp'}
interviews = []  # {'job_id','candidate_email','recruiter_email','date','time','status'}
reports = []  # {'candidate_email','company','job_id','report'}
user_bans = {'candidate': [], 'recruiter': []}
job_id_counter = 1

def find_user(email, role):
    return next((u for u in users[role] if u['email']==email), None)

def auto_remove_expired_jobs():
    global jobs
    today = datetime.today().date()
    jobs[:] = [j for j in jobs if datetime.strptime(j['end_date'],'%Y-%m-%d').date() >= today]

@app.route('/register/<role>', methods=['POST'])
def register(role):
    if role not in ['candidate','recruiter']: return jsonify({'status':'error','message':'Invalid role'})
    data = request.json
    if find_user(data['email'], role): return jsonify({'status':'error','message':'User exists'})
    users[role].append(data)
    return jsonify({'status':'success','message':'Registered'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    role = data.get('role'); email = data.get('email'); password = data.get('password')
    user = find_user(email, role)
    if user and user.get('password')==password: return jsonify({'status':'success','message':'Login successful'})
    return jsonify({'status':'error','message':'Invalid credentials'})

@app.route('/recruiter/job', methods=['POST'])
def post_job():
    global job_id_counter
    auto_remove_expired_jobs()
    data = request.json
    data['id'] = job_id_counter; job_id_counter += 1
    jobs.append(data)
    return jsonify({'status':'success','message':'Job posted'})

@app.route('/candidate/applied_jobs', methods=['GET'])
def applied_jobs():
    email = request.args.get('email')
    res=[]
    for a in applications:
        if a['candidate_email']==email:
            job = next((j for j in jobs if j['id']==a['job_id']), None)
            if job: res.append({'id':job['id'],'title':job['title'],'company':job['company'],'status':a.get('status','Applied')})
    return jsonify(res)

@app.route('/candidate/apply', methods=['POST'])
def apply_job():
    data = request.json
    for a in applications:
        if a['job_id']==data['job_id'] and a['candidate_email']==data['candidate_email']:
            return jsonify({'status':'error','message':'Already applied'})
    applications.append({'job_id':data['job_id'],'candidate_email':data['candidate_email'],'status':'Applied','shortlist':False})
    return jsonify({'status':'success','message':'Applied'})

@app.route('/recruiter/applications/<int:job_id>', methods=['GET'])
def view_applications(job_id):
    job_apps = [a for a in applications if a['job_id']==job_id]
    res=[]
    for a in job_apps:
        candidate = find_user(a['candidate_email'],'candidate')
        res.append({'candidate_email':a['candidate_email'],'status':a['status'],'shortlist':a['shortlist'],'name':candidate.get('name')})
    return jsonify(res)

@app.route('/recruiter/application_action', methods=['POST'])
def application_action():
    data = request.json
    for a in applications:
        if a['job_id']==data['job_id'] and a['candidate_email']==data['candidate_email']:
            a['status']=data['action']
            a['shortlist']=data.get('action')=='Shortlisted'
            return jsonify({'status':'success','message':'Updated'})
    return jsonify({'status':'error','message':'Application not found'})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json; data['timestamp']=str(datetime.now()); messages.append(data)
    return jsonify({'status':'success','message':'Message sent'})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    user = request.args.get('email')
    inbox = [m for m in messages if m['to']==user]
    return jsonify(inbox)

@app.route('/schedule_interview', methods=['POST'])
def schedule_interview():
    data = request.json; data['status']='Scheduled'; interviews.append(data)
    return jsonify({'status':'success','message':'Interview scheduled'})

@app.route('/get_interviews', methods=['GET'])
def get_interviews():
    email = request.args.get('email'); role = request.args.get('role')
    res = [i for i in interviews if (i['candidate_email']==email if role=='candidate' else i['recruiter_email']==email)]
    return jsonify(res)

@app.route('/admin/users/<role>', methods=['GET'])
def admin_view_users(role):
    return jsonify(users.get(role,[]))

@app.route('/admin/ban_user', methods=['POST'])
def ban_user():
    data = request.json; role=data['role']; email=data['email']; user_bans[role].append(email)
    users[role] = [u for u in users[role] if u['email']!=email]
    return jsonify({'status':'success','message':'User banned'})

if __name__=="__main__":
    app.run(debug=True)
