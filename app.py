import uvicorn
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import uuid, datetime

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change later to GitHub Pages URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stores
applicants = {}
hrs = {}
jobs = {}
applications = {}  # {job_id: [{applicant_email, status, messages:[]}]}

# ---------- Applicant ----------
@app.post("/applicant/register")
async def applicant_register(
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    education: str = Form(...),
    specialization: str = Form(...),
    university: str = Form(...),
    year: int = Form(...),
    skills: str = Form(...),
    experience: Optional[int] = Form(0),
    photo: UploadFile = File(None),
    resume: UploadFile = File(None),
):
    if email in applicants:
        raise HTTPException(status_code=400, detail="Applicant already registered")

    applicants[email] = {
        "id": str(uuid.uuid4()),
        "name": name,
        "age": age,
        "gender": gender,
        "email": email,
        "phone": phone,
        "password": password,
        "education": education,
        "specialization": specialization,
        "university": university,
        "year": year,
        "skills": skills.split(","),
        "experience": experience,
        "photo": photo.filename if photo else None,
        "resume": resume.filename if resume else None,
        "messages": []
    }
    return {"message": "Applicant registered successfully", "applicant": applicants[email]}


@app.post("/applicant/login")
async def applicant_login(email: str = Form(...), password: str = Form(...)):
    if email not in applicants or applicants[email]["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "applicant": applicants[email]}


@app.post("/applicant/update")
async def applicant_update(
    email: str = Form(...),
    name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    skills: Optional[str] = Form(None),
    experience: Optional[int] = Form(None),
):
    if email not in applicants:
        raise HTTPException(status_code=404, detail="Applicant not found")

    if name: applicants[email]["name"] = name
    if phone: applicants[email]["phone"] = phone
    if skills: applicants[email]["skills"] = skills.split(",")
    if experience is not None: applicants[email]["experience"] = experience

    return {"message": "Profile updated", "applicant": applicants[email]}


@app.get("/applicant/applied-jobs/{email}")
async def get_applied_jobs(email: str):
    applied = []
    for job_id, apps in applications.items():
        for app in apps:
            if app["applicant_email"] == email:
                job_info = jobs[job_id].copy()
                job_info["status"] = app["status"]
                applied.append(job_info)
    return {"applied_jobs": applied}


@app.get("/applicant/messages/{email}")
async def get_messages(email: str):
    if email not in applicants:
        raise HTTPException(status_code=404, detail="Applicant not found")
    return {"messages": applicants[email]["messages"]}

# ---------- HR ----------
@app.post("/hr/register")
async def hr_register(
    company: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    designation: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    photo: UploadFile = File(None),
):
    if email in hrs:
        raise HTTPException(status_code=400, detail="HR already registered")

    hrs[email] = {
        "id": str(uuid.uuid4()),
        "company": company,
        "name": name,
        "age": age,
        "email": email,
        "phone": phone,
        "password": password,
        "designation": designation,
        "industry": industry,
        "address": address,
        "photo": photo.filename if photo else None,
    }
    return {"message": "HR registered successfully", "hr": hrs[email]}


@app.post("/hr/login")
async def hr_login(email: str = Form(...), password: str = Form(...)):
    if email not in hrs or hrs[email]["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "hr": hrs[email]}


# ---------- Jobs ----------
@app.post("/hr/post-job")
async def post_job(
    hr_email: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    salary: str = Form(...),
    skills_required: str = Form(...),
    experience_required: int = Form(...),
    end_date: str = Form(...),  # format YYYY-MM-DD
):
    if hr_email not in hrs:
        raise HTTPException(status_code=403, detail="Invalid HR")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "id": job_id,
        "title": title,
        "description": description,
        "location": location,
        "salary": salary,
        "skills_required": skills_required.split(","),
        "experience_required": experience_required,
        "end_date": end_date,
        "posted_by": hr_email,
    }
    return {"message": "Job posted successfully", "job": jobs[job_id]}


@app.post("/hr/edit-job")
async def edit_job(job_id: str = Form(...), title: Optional[str] = Form(None), salary: Optional[str] = Form(None)):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    if title: jobs[job_id]["title"] = title
    if salary: jobs[job_id]["salary"] = salary

    return {"message": "Job updated", "job": jobs[job_id]}


@app.post("/hr/delete-job")
async def delete_job(job_id: str = Form(...)):
    if job_id in jobs:
        del jobs[job_id]
        applications.pop(job_id, None)
        return {"message": "Job deleted"}
    raise HTTPException(status_code=404, detail="Job not found")


@app.get("/jobs")
async def get_jobs():
    today = datetime.date.today()
    active_jobs = []
    for job in jobs.values():
        try:
            if datetime.date.fromisoformat(job["end_date"]) >= today:
                active_jobs.append(job)
        except:
            active_jobs.append(job)  # if invalid date keep it
    return {"jobs": active_jobs}


# ---------- Applications ----------
@app.post("/apply-job")
async def apply_job(applicant_email: str = Form(...), job_id: str = Form(...)):
    if applicant_email not in applicants:
        raise HTTPException(status_code=403, detail="Invalid applicant")
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    applicant = applicants[applicant_email]

    # Requirement check
    if applicant["experience"] < job["experience_required"]:
        return {"error": "You cannot apply, experience not matching"}

    if not set(job["skills_required"]).issubset(set(applicant["skills"])):
        return {"error": "You cannot apply, skills not matching"}

    if job_id not in applications:
        applications[job_id] = []

    # Prevent duplicate
    for app in applications[job_id]:
        if app["applicant_email"] == applicant_email:
            return {"message": "Already applied"}

    applications[job_id].append({
        "applicant_email": applicant_email,
        "status": "Applied",
        "messages": []
    })
    return {"message": "Applied successfully"}


@app.get("/applications/{job_id}")
async def get_applications(job_id: str):
    if job_id not in applications:
        return {"applications": []}
    return {"applications": applications[job_id]}


@app.post("/hr/update-status")
async def update_status(job_id: str = Form(...), applicant_email: str = Form(...), status: str = Form(...)):
    if job_id not in applications:
        raise HTTPException(status_code=404, detail="No applications for this job")

    for app in applications[job_id]:
        if app["applicant_email"] == applicant_email:
            app["status"] = status
            return {"message": f"Status updated to {status}"}
    raise HTTPException(status_code=404, detail="Application not found")


@app.post("/hr/message")
async def send_message(job_id: str = Form(...), applicant_email: str = Form(...), hr_email: str = Form(...), message: str = Form(...)):
    if applicant_email not in applicants:
        raise HTTPException(status_code=404, detail="Applicant not found")

    msg = {"from": hr_email, "job_id": job_id, "message": message}
    applicants[applicant_email]["messages"].append(msg)

    # also track inside application
    for app in applications.get(job_id, []):
        if app["applicant_email"] == applicant_email:
            app["messages"].append(msg)

    return {"message": "Message sent"}
    

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
