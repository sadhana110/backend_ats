from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date
import uuid

app = Flask(__name__)
CORS(app)

# In-memory storage (resets on restart)
applicants = {}   # email -> applicant dict
hrs = {}          # email -> hr dict
jobs = {}         # job_id -> job dict
applications = {} # app_id -> application dict
messages = []     # list of message dicts

# ---------- helper ----------
def now_iso():
    return datetime.utcnow().isoformat()

def job_active(job):
    try:
        end = datetime.strptime(job.get("end_date","9999-12-31"), "%Y-%m-%d").date()
        return end >= date.today()
    except:
        return True

# ---------- Auth & Profiles ----------
@app.route("/register_applicant", methods=["POST"])
def register_applicant():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"status":"error","msg":"Email required"}), 400
    if email in applicants:
        return jsonify({"status":"error","msg":"Already registered"}), 400
    applicants[email] = {
        "email": email,
        "name": data.get("name"),
        "age": data.get("age"),
        "contact": data.get("contact"),
        "password": data.get("password"),
        "current_role": data.get("current_role"),
        "experience": data.get("experience"),
        "degree": data.get("degree"),
        "university": data.get("university"),
        "skills": data.get("skills") or [],
        "resume": data.get("resume"),  # base64 data url or null
        "links": data.get("links"),
        "saved_jobs": []
    }
    return jsonify({"status":"success","msg":"Applicant registered"}), 200

@app.route("/login_applicant", methods=["POST"])
def login_applicant():
    data = request.get_json()
    email = data.get("email")
    pwd = data.get("password")
    if not email or email not in applicants or applicants[email].get("password") != pwd:
        return jsonify({"status":"error","msg":"Invalid credentials"}), 401
    return jsonify({"status":"success","msg":"ok","data": applicants[email]}), 200

@app.route("/get_profile_applicant/<email>", methods=["GET"])
def get_profile_applicant(email):
    p = applicants.get(email)
    if not p: return jsonify({"status":"error","msg":"Not found"}), 404
    return jsonify({"status":"success","data": p}), 200

@app.route("/get_profile_hr/<email>", methods=["GET"])
def get_profile_hr(email):
    p = hrs.get(email)
    if not p: return jsonify({"status":"error","msg":"Not found"}), 404
    return jsonify({"status":"success","data": p}), 200

@app.route("/register_hr", methods=["POST"])
def register_hr():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"status":"error","msg":"Email required"}), 400
    if email in hrs:
        return jsonify({"status":"error","msg":"Already registered"}), 400
    hrs[email] = {
        "email": email,
        "hr_name": data.get("hr_name"),
        "company": data.get("company"),
        "password": data.get("password"),
        "description": data.get("description")
    }
    return jsonify({"status":"success","msg":"HR registered"}), 200

@app.route("/login_hr", methods=["POST"])
def login_hr():
    data = request.get_json()
    email = data.get("email")
    pwd = data.get("password")
    if not email or email not in hrs or hrs[email].get("password") != pwd:
        return jsonify({"status":"error","msg":"Invalid credentials"}), 401
    return jsonify({"status":"success","msg":"ok","data": hrs[email]}), 200

# ---------- Jobs ----------
@app.route("/post_job", methods=["POST"])
def post_job():
    data = request.get_json()
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "title": data.get("title"),
        "location": data.get("location"),
        "experience": int(data.get("experience") or 0),
        "salary": data.get("salary"),
        "skills": data.get("skills") or [],
        "description": data.get("description"),
        "end_date": data.get("end_date"),
        "posted_by": data.get("posted_by"),
        "company": data.get("company") or hrs.get(data.get("posted_by"),{}).get("company"),
        "created_at": now_iso()
    }
    jobs[job_id] = job
    return jsonify({"status":"success","msg":"Job posted","job_id":job_id}), 200

@app.route("/get_jobs", methods=["GET"])
def get_jobs():
    q = request.args.get("q","").lower()
    exp = request.args.get("exp","")
    location = request.args.get("location","").lower()
    result = []
    for job in jobs.values():
        if not job_active(job): continue
        if q and q not in (job.get("title","")+" "+job.get("description","")+" "+(" ".join(job.get("skills",[])))).lower(): continue
        if exp:
            try:
                if int(job.get("experience",0)) > int(exp): continue
            except: pass
        if location and location not in job.get("location","").lower(): continue
        result.append(job)
    # sort by created_at desc
    result.sort(key=lambda x: x.get("created_at",""), reverse=True)
    return jsonify({"status":"success","jobs": result}), 200

@app.route("/get_job/<job_id>", methods=["GET"])
def get_job(job_id):
    job = jobs.get(job_id)
    if not job: return jsonify({"status":"error","msg":"Not found"}), 404
    return jsonify({"status":"success","job": job}), 200

@app.route("/delete_job", methods=["POST"])
def delete_job():
    data = request.get_json()
    job_id = data.get("job_id")
    if job_id in jobs:
        del jobs[job_id]
        # remove related applications
        to_del = [aid for aid,a in applications.items() if a.get("job_id")==job_id]
        for aid in to_del: del applications[aid]
        return jsonify({"status":"success","msg":"Deleted"}), 200
    return jsonify({"status":"error","msg":"Not found"}), 404

# ---------- Apply / Applications ----------
@app.route("/apply_job", methods=["POST"])
def apply_job():
    data = request.get_json()
    job_id = data.get("job_id")
    applicant_email = data.get("applicant_email")
    if not job_id or not applicant_email: return jsonify({"status":"error","msg":"Missing"}), 400
    if job_id not in jobs: return jsonify({"status":"error","msg":"Job not found"}), 404
    app_id = str(uuid.uuid4())
    applications[app_id] = {
        "id": app_id,
        "job_id": job_id,
        "applicant_email": applicant_email,
        "status": "Applied",
        "applied_at": now_iso()
    }
    return jsonify({"status":"success","msg":"Applied","app_id":app_id}), 200

@app.route("/get_applied_jobs/<applicant_email>", methods=["GET"])
def get_applied_jobs(applicant_email):
    res = []
    for a in applications.values():
        if a.get("applicant_email")==applicant_email:
            res.append(a)
    return jsonify({"status":"success","applied": res}), 200

@app.route("/get_applications_for_hr/<hr_email>", methods=["GET"])
def get_applications_for_hr(hr_email):
    # find jobs posted by hr
    hr_jobs = [j['id'] for j in jobs.values() if j.get('posted_by')==hr_email]
    res = []
    for a in applications.values():
        if a.get("job_id") in hr_jobs:
            # attach applicant basic profile
            applicant = applicants.get(a.get("applicant_email"), {})
            res.append({ **a, "applicant": applicant })
    return jsonify({"status":"success","applications": res}), 200

@app.route("/get_applications_for_job/<job_id>", methods=["GET"])
def get_applications_for_job(job_id):
    res=[]
    for a in applications.values():
        if a.get("job_id")==job_id:
            a_c = dict(a)
            a_c['applicant'] = applicants.get(a.get("applicant_email"),{})
            res.append(a_c)
    return jsonify({"status":"success","applications":res}), 200

@app.route("/update_application_status", methods=["POST"])
def update_application_status():
    data = request.get_json()
    app_id = data.get("app_id")
    status = data.get("status")
    if app_id in applications:
        applications[app_id]['status'] = status
        return jsonify({"status":"success","msg":"Updated"}), 200
    return jsonify({"status":"error","msg":"not found"}), 404

# ---------- Save job ----------
@app.route("/save_job", methods=["POST"])
def save_job():
    data = request.get_json()
    email = data.get("applicant_email")
    job_id = data.get("job_id")
    if not email or email not in applicants: return jsonify({"status":"error","msg":"Applicant not found"}), 404
    if job_id not in jobs: return jsonify({"status":"error","msg":"Job not found"}), 404
    if job_id not in applicants[email].get('saved_jobs',[]):
        applicants[email].setdefault('saved_jobs', []).append(job_id)
    return jsonify({"status":"success","msg":"Saved"}), 200

@app.route("/get_saved_jobs/<applicant_email>", methods=["GET"])
def get_saved_jobs(applicant_email):
    user = applicants.get(applicant_email)
    if not user: return jsonify({"status":"error","msg":"Not found"}),404
    job_list = [ jobs[jid] for jid in user.get('saved_jobs',[]) if jid in jobs and job_active(jobs[jid]) ]
    return jsonify({"status":"success","jobs":job_list}), 200

# ---------- Messaging ----------
@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.get_json()
    m = {
        "id": str(uuid.uuid4()),
        "from": data.get("from"),
        "to": data.get("to"),
        "job_id": data.get("job_id"),
        "message": data.get("message"),
        "timestamp": now_iso()
    }
    messages.append(m)
    return jsonify({"status":"success","msg":"sent"}), 200

@app.route("/get_messages", methods=["GET"])
def get_messages():
    u1 = request.args.get("user1")
    u2 = request.args.get("user2")
    job_id = request.args.get("job_id")
    conv = [m for m in messages if ((m['from']==u1 and m['to']==u2) or (m['from']==u2 and m['to']==u1))]
    if job_id:
        conv = [m for m in conv if m.get('job_id')==job_id]
    conv.sort(key=lambda x: x['timestamp'])
    return jsonify({"status":"success","messages":conv}), 200

# ---------- simple health / list ----------
@app.route("/", methods=["GET"])
def hello():
    return jsonify({"status":"ok","msg":"Backend alive"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
