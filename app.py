from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///naukri_clone.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------- Models --------------------
class User(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))  # candidate, recruiter, admin
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    skills = db.Column(db.String(500))
    resume = db.Column(db.Text)
    description = db.Column(db.Text)
    banned = db.Column(db.Boolean, default=False)
    investigated = db.Column(db.Boolean, default=False)

class Job(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100))
    recruiter_id = db.Column(db.String)
    skills = db.Column(db.String(500))
    last_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Application(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = db.Column(db.String)
    job_id = db.Column(db.String)
    status = db.Column(db.String(20), default='applied')  # applied, shortlisted, rejected
    interview_date = db.Column(db.DateTime)

class Message(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = db.Column(db.String)
    receiver_id = db.Column(db.String)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    reporter_id = db.Column(db.String)
    reported_id = db.Column(db.String)
    job_id = db.Column(db.String)
    content = db.Column(db.Text)

db.create_all()

# -------------------- Auth --------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message":"Email already exists"}), 400
    user = User(
        name=data['name'],
        email=data['email'],
        password=data['password'],
        role=data['role'],
        phone=data.get('phone',''),
        company=data.get('company',''),
        skills=','.join(data.get('skills',[])),
        resume=data.get('resume',''),
        description=data.get('description','')
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message":"Registered successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if not user:
        return jsonify({"message":"Invalid credentials"}), 401
    if user.banned:
        return jsonify({"message":"You are banned"}), 403
    return jsonify({
        "id": user.id,
        "name": user.name,
        "role": user.role
    })

# -------------------- Jobs --------------------
@app.route('/job/post', methods=['POST'])
def post_job():
    data = request.json
    job = Job(
        title=data['title'],
        recruiter_id=data['recruiterId'],
        skills=','.join(data.get('skills',[])),
        last_date=datetime.strptime(data['lastDate'], '%Y-%m-%d').date()
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({"message":"Job posted successfully"})

@app.route('/recruiter/<recruiter_id>/jobs')
def recruiter_jobs(recruiter_id):
    jobs = Job.query.filter_by(recruiter_id=recruiter_id).all()
    return jsonify([{
        "id": j.id,
        "title": j.title,
        "skills": j.skills.split(","),
        "last_date": j.last_date.isoformat()
    } for j in jobs])

@app.route('/job/delete', methods=['POST'])
def delete_job():
    data = request.json
    job = Job.query.get(data['jobId'])
    if job:
        db.session.delete(job)
        db.session.commit()
        return jsonify({"message":"Job deleted"})
    return jsonify({"message":"Job not found"}), 404

@app.route('/jobs')
def all_jobs():
    jobs = Job.query.all()
    result = []
    today = datetime.utcnow().date()
    for j in jobs:
        if j.last_date < today:
            db.session.delete(j)
        else:
            result.append({
                "id": j.id,
                "title": j.title,
                "skills": j.skills.split(",")
            })
    db.session.commit()
    return jsonify(result)

# -------------------- Applications --------------------
@app.route('/apply', methods=['POST'])
def apply_job():
    data = request.json
    if Application.query.filter_by(candidate_id=data['candidateId'], job_id=data['jobId']).first():
        return jsonify({"message":"Already applied"}), 400
    app_job = Application(candidate_id=data['candidateId'], job_id=data['jobId'])
    db.session.add(app_job)
    db.session.commit()
    return jsonify({"message":"Applied successfully"})

@app.route('/applications/<recruiter_id>')
def recruiter_applications(recruiter_id):
    jobs = Job.query.filter_by(recruiter_id=recruiter_id).all()
    job_ids = [j.id for j in jobs]
    apps = Application.query.filter(Application.job_id.in_(job_ids)).all()
    result = []
    for a in apps:
        candidate = User.query.get(a.candidate_id)
        job = Job.query.get(a.job_id)
        result.append({
            "applicationId": a.id,
            "candidateName": candidate.name,
            "jobTitle": job.title,
            "status": a.status
        })
    return jsonify(result)

@app.route('/application/update', methods=['POST'])
def update_application():
    data = request.json
    app_job = Application.query.get(data['applicationId'])
    if not app_job:
        return jsonify({"message":"Application not found"}), 404
    app_job.status = data['status']
    db.session.commit()
    return jsonify({"message":"Application updated"})

# -------------------- Messages --------------------
@app.route('/message/send', methods=['POST'])
def send_message():
    data = request.json
    msg = Message(sender_id=data['senderId'], receiver_id=data['receiverId'], content=data['content'])
    db.session.add(msg)
    db.session.commit()
    return jsonify({"message":"Message sent"})

@app.route('/messages/<user_id>')
def get_messages(user_id):
    msgs = Message.query.filter((Message.sender_id==user_id)|(Message.receiver_id==user_id)).all()
    return jsonify([{
        "id": m.id,
        "senderId": m.sender_id,
        "receiverId": m.receiver_id,
        "content": m.content,
        "created_at": m.created_at.isoformat()
    } for m in msgs])

# -------------------- Admin --------------------
@app.route('/admin/stats')
def admin_stats():
    total = User.query.count()
    candidates = User.query.filter_by(role='candidate').count()
    recruiters = User.query.filter_by(role='recruiter').count()
    return jsonify({"totalUsers": total, "totalCandidates": candidates, "totalRecruiters": recruiters})

@app.route('/admin/recruiters')
def admin_recruiters():
    users = User.query.filter_by(role='recruiter').all()
    return jsonify([{"id":u.id,"name":u.name,"company":u.company} for u in users])

@app.route('/admin/candidates')
def admin_candidates():
    users = User.query.filter_by(role='candidate').all()
    return jsonify([{"id":u.id,"name":u.name,"skills":u.skills.split(",")} for u in users])

@app.route('/admin/ban', methods=['POST'])
def admin_ban():
    data = request.json
    user = User.query.get(data['userId'])
    if user:
        user.banned = True
        db.session.commit()
        return jsonify({"message":"User banned"})
    return jsonify({"message":"User not found"}), 404

@app.route('/admin/investigate', methods=['POST'])
def admin_investigate():
    data = request.json
    user = User.query.get(data['userId'])
    if user:
        user.investigated = True
        db.session.commit()
        return jsonify({"message":"User under investigation"})
    return jsonify({"message":"User not found"}), 404

# -------------------- Run --------------------
if __name__ == "__main__":
    app.run(debug=True)
