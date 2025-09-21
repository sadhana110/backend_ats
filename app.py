from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uvicorn

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory databases
users = []
jobs = []
applications = []
messages = []  # ✅ NEW
job_id_counter = 1

class RegisterUser(BaseModel):
    name: str
    email: str
    password: str
    role: str
    education: str | None = None
    skills: str | None = None
    company: str | None = None
    age: int | None = None
    phone: str | None = None

class LoginUser(BaseModel):
    email: str
    password: str
    role: str

class Job(BaseModel):
    title: str
    role: str
    experience: int
    salary: str
    skills: str
    end_date: str

class ApplyJob(BaseModel):
    job_id: int
    applicant: str

class Message(BaseModel):  # ✅ NEW
    sender: str
    receiver: str
    text: str

@app.post("/register")
def register(user: RegisterUser):
    users.append(user.dict())
    return {"success": True}

@app.post("/login")
def login(user: LoginUser):
    for u in users:
        if u["email"] == user.email and u["password"] == user.password and u["role"] == user.role:
            return {"success": True}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/jobs")
def post_job(job: Job):
    global job_id_counter
    job_dict = job.dict()
    job_dict["id"] = job_id_counter
    job_dict["posted"] = str(datetime.now())
    jobs.append(job_dict)
    job_id_counter += 1
    return {"success": True, "job": job_dict}

@app.get("/jobs")
def get_jobs():
    now = datetime.now()
    valid_jobs = []
    for j in jobs:
        if datetime.strptime(j["end_date"], "%Y-%m-%d") >= now:
            valid_jobs.append(j)
    return valid_jobs

@app.post("/apply")
def apply(apply: ApplyJob):
    applications.append({"job_id": apply.job_id, "applicant": apply.applicant, "status": "Applied"})
    return {"success": True}

@app.get("/applications/{applicant}")
def get_applications(applicant: str):
    return [a for a in applications if a["applicant"] == applicant]

@app.post("/applications/{applicant}/{job_id}/{status}")
def update_application(applicant: str, job_id: int, status: str):
    for a in applications:
        if a["applicant"] == applicant and a["job_id"] == job_id:
            a["status"] = status
            return {"success": True}
    raise HTTPException(status_code=404, detail="Application not found")

# ✅ Messaging
@app.post("/message/send")
def send_message(msg: Message):
    messages.append({
        "sender": msg.sender,
        "receiver": msg.receiver,
        "text": msg.text,
        "time": str(datetime.now())
    })
    return {"success": True}

@app.get("/message/{user}")
def get_messages(user: str):
    user_msgs = [m for m in messages if m["sender"] == user or m["receiver"] == user]
    return user_msgs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
