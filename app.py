from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory SQLite DB (replace with PostgreSQL/MySQL later)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///naukri_clone.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------- MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50))  # candidate, recruiter, admin
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    banned = db.Column(db.Boolean, default=False)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default="open")  # open/closed

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    candidate_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default="applied")  # applied/shortlisted/rejected

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# -------------------- AUTH --------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 400

    new_user = User(
        role=data["role"],
        username=data["username"],
        password=data["password"],  # ⚠️ hash later
        email=data["email"]
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"], password=data["password"]).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    if user.banned:
        return jsonify({"error": "User banned by admin"}), 403
    return jsonify({"id": user.id, "role": user.role, "username": user.username})

# -------------------- JOBS --------------------
@app.route("/jobs", methods=["POST"])
def post_job():
    data = request.json
    job = Job(title=data["title"], description=data["description"], recruiter_id=data["recruiter_id"])
    db.session.add(job)
    db.session.commit()
    return jsonify({"message": "Job posted successfully"}), 201

@app.route("/jobs", methods=["GET"])
def list_jobs():
    jobs = Job.query.filter_by(status="open").all()
    return jsonify([{"id": j.id, "title": j.title, "description": j.description, "recruiter_id": j.recruiter_id} for j in jobs])

# -------------------- APPLICATIONS --------------------
@app.route("/apply", methods=["POST"])
def apply_job():
    data = request.json
    existing = Application.query.filter_by(job_id=data["job_id"], candidate_id=data["candidate_id"]).first()
    if existing:
        return jsonify({"error": "Already applied"}), 400
    appn = Application(job_id=data["job_id"], candidate_id=data["candidate_id"])
    db.session.add(appn)
    db.session.commit()
    return jsonify({"message": "Applied successfully"}), 201

@app.route("/applications/<int:job_id>", methods=["GET"])
def view_applicants(job_id):
    apps = Application.query.filter_by(job_id=job_id).all()
    return jsonify([{"id": a.id, "candidate_id": a.candidate_id, "status": a.status} for a in apps])

@app.route("/myapplications/<int:candidate_id>", methods=["GET"])
def my_applications(candidate_id):
    apps = Application.query.filter_by(candidate_id=candidate_id).all()
    return jsonify([{"job_id": a.job_id, "status": a.status} for a in apps])

# -------------------- MESSAGING --------------------
@app.route("/messages", methods=["POST"])
def send_message():
    data = request.json
    msg = Message(sender_id=data["sender_id"], receiver_id=data["receiver_id"], content=data["content"])
    db.session.add(msg)
    db.session.commit()
    return jsonify({"message": "Message sent"}), 201

@app.route("/messages/<int:user1>/<int:user2>", methods=["GET"])
def get_messages(user1, user2):
    msgs = Message.query.filter(
        ((Message.sender_id == user1) & (Message.receiver_id == user2)) |
        ((Message.sender_id == user2) & (Message.receiver_id == user1))
    ).order_by(Message.timestamp.asc()).all()

    return jsonify([{"sender": m.sender_id, "receiver": m.receiver_id, "content": m.content, "timestamp": m.timestamp} for m in msgs])

# -------------------- ADMIN --------------------
@app.route("/admin/users", methods=["GET"])
def admin_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "role": u.role, "banned": u.banned} for u in users])

@app.route("/admin/ban/<int:user_id>", methods=["POST"])
def admin_ban(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.banned = True
    db.session.commit()
    return jsonify({"message": "User banned"}), 200

# -------------------- INIT --------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # ensures tables exist
    app.run(host="0.0.0.0", port=5000, debug=True)

