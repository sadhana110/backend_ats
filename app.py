from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

candidates, recruiters, admins, jobs, applications, reports = [], [], [{"email":"admin@naukri.com","password":"admin123","role":"admin"}], [], [], []

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    data["_id"] = str(len(candidates)+len(recruiters)+len(admins)+1)
    if data["role"]=="candidate": candidates.append(data)
    elif data["role"]=="recruiter": recruiters.append(data)
    return jsonify({"success":True,"user":data})

@app.route("/login", methods=["POST"])
def login():
    data=request.json
    role,email,password=data["role"],data["email"],data["password"]
    user=None
    if role=="candidate": user=next((c for c in candidates if c["email"]==email and c["password"]==password),None)
    elif role=="recruiter": user=next((r for r in recruiters if r["email"]==email and r["password"]==password),None)
    elif role=="admin": user=next((a for a in admins if a["email"]==email and a["password"]==password),None)
    return jsonify({"success":bool(user),"user":user})

@app.route("/post_job", methods=["POST"])
def post_job():
    data=request.json
    data["_id"]=str(len(jobs)+1)
    data["posted"]=datetime.now().isoformat()
    jobs.append(data)
    return jsonify({"success":True})

@app.route("/jobs") def get_jobs(): return jsonify(jobs)
@app.route("/recruiter_jobs/<rid>") def recruiter_jobs(rid): return jsonify([j for j in jobs if j["recruiterId"]==rid])

@app.route("/apply", methods=["POST"])
def apply():
    data=request.json
    applications.append({"candidateId":data["candidateId"],"jobId":data["jobId"],"status":"applied"})
    return jsonify({"success":True})

@app.route("/save_job", methods=["POST"])
def save_job():
    return jsonify({"success":True})

@app.route("/admin_stats")
def admin_stats():
    return jsonify({"candidates":len(candidates),"recruiters":len(recruiters),"jobs":len(jobs),"reports":len(reports)})

@app.route("/users")
def users(): return jsonify(candidates+recruiters+admins)

if __name__=="__main__": app.run(host="0.0.0.0",port=5000)
