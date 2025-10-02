const user = JSON.parse(localStorage.getItem("user"));
if(!user || user.role !== "candidate") window.location.href = "login.html";

function showSection(sectionId){
    document.querySelectorAll(".dashboard-section").forEach(sec=>{
        sec.classList.remove("active");
    });
    document.getElementById(sectionId).classList.add("active");
}

async function fetchJobs(){
    const res = await fetch(`${API_URL}/jobs`);
    const jobs = await res.json();
    const jobsContainer = document.getElementById("jobs");
    jobsContainer.innerHTML = "";
    jobs.forEach(job=>{
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
            <h3>${job.title}</h3>
            <p>${job.company}</p>
            <p>Skills: ${job.skills.join(", ")}</p>
            <button onclick="applyJob('${job.id}')">Apply</button>
        `;
        jobsContainer.appendChild(card);
    });
}

async function applyJob(jobId){
    const res = await fetch(`${API_URL}/apply`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ candidateId:user.id, jobId })
    });
    const data = await res.json();
    alert(data.message);
}

async function fetchAppliedJobs(){
    const res = await fetch(`${API_URL}/candidate/${user.id}/applied`);
    const jobs = await res.json();
    const container = document.getElementById("applied");
    container.innerHTML = "";
    jobs.forEach(job=>{
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `<h3>${job.title}</h3><p>${job.company}</p><p>Status: ${job.status}</p>`;
        container.appendChild(card);
    });
}

async function fetchShortlistedJobs(){
    const res = await fetch(`${API_URL}/candidate/${user.id}/shortlisted`);
    const jobs = await res.json();
    const container = document.getElementById("shortlisted");
    container.innerHTML = "";
    jobs.forEach(job=>{
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `<h3>${job.title}</h3><p>${job.company}</p>`;
        container.appendChild(card);
    });
}

async function fetchMessages(){
    const res = await fetch(`${API_URL}/messages/${user.id}`);
    const msgs = await res.json();
    const container = document.getElementById("messages");
    container.innerHTML = "";
    msgs.forEach(msg=>{
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `<p><b>From:</b> ${msg.from}<br>${msg.text}</p>`;
        container.appendChild(card);
    });
}

function logout(){
    localStorage.removeItem("user");
    window.location.href="login.html";
}

// Initial load
showSection("jobs");
fetchJobs();
fetchAppliedJobs();
fetchShortlistedJobs();
fetchMessages();
