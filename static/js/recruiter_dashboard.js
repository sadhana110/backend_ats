const recruiter = JSON.parse(localStorage.getItem("user"));
if(!recruiter || recruiter.role !== "recruiter") window.location.href = "login.html";

function showSection(sectionId){
    document.querySelectorAll(".dashboard-section").forEach(sec=>sec.classList.remove("active"));
    document.getElementById(sectionId).classList.add("active");
}

async function postJob(){
    const title = prompt("Job Title");
    const skills = prompt("Skills (comma separated)").split(",");
    const lastDate = prompt("Application End Date (YYYY-MM-DD)");
    const res = await fetch(`${API_URL}/job/post`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({ recruiterId:recruiter.id, title, skills, lastDate })
    });
    const data = await res.json();
    alert(data.message);
}

async function fetchJobs(){
    const res = await fetch(`${API_URL}/recruiter/${recruiter.id}/jobs`);
    const jobs = await res.json();
    const container = document.getElementById("manageJob");
    container.innerHTML="";
    jobs.forEach(job=>{
        const card = document.createElement("div");
        card.className="card";
        card.innerHTML=`<h3>${job.title}</h3><p>Skills: ${job.skills.join(", ")}</p>
        <button onclick="editJob('${job.id}')">Edit</button>
        <button onclick="deleteJob('${job.id}')">Delete</button>`;
        container.appendChild(card);
    });
}

async function editJob(jobId){ alert("Edit job - implement modal or form"); }
async function deleteJob(jobId){
    const res = await fetch(`${API_URL}/job/delete`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({ jobId })
    });
    const data = await res.json();
    alert(data.message);
    fetchJobs();
}

function logout(){ localStorage.removeItem("user"); window.location.href="login.html"; }

// Initial load
showSection("profile");
fetchJobs();
