const admin = JSON.parse(localStorage.getItem("user"));
if(!admin || admin.role !== "admin") window.location.href="login.html";

function showSection(sectionId){
    document.querySelectorAll(".dashboard-section").forEach(sec=>sec.classList.remove("active"));
    document.getElementById(sectionId).classList.add("active");
}

async function fetchStats(){
    const res = await fetch(`${API_URL}/admin/stats`);
    const stats = await res.json();
    const container = document.getElementById("stats");
    container.innerHTML = `<div class="card">Total Users: ${stats.totalUsers}</div>
    <div class="card">Candidates: ${stats.totalCandidates}</div>
    <div class="card">Recruiters: ${stats.totalRecruiters}</div>`;
}

async function fetchRecruiters(){
    const res = await fetch(`${API_URL}/admin/recruiters`);
    const recruiters = await res.json();
    const container = document.getElementById("recruiters");
    container.innerHTML="";
    recruiters.forEach(r=>{
        const card=document.createElement("div");
        card.className="card";
        card.innerHTML=`<h3>${r.name}</h3><p>Company: ${r.company}</p>
        <button onclick="banUser('${r.id}','recruiter')">Ban</button>
        <button onclick="investigateUser('${r.id}','recruiter')">Investigate</button>`;
        container.appendChild(card);
    });
}

async function fetchCandidates(){
    const res = await fetch(`${API_URL}/admin/candidates`);
    const candidates = await res.json();
    const container = document.getElementById("candidates");
    container.innerHTML="";
    candidates.forEach(c=>{
        const card=document.createElement("div");
        card.className="card";
        card.innerHTML=`<h3>${c.name}</h3><p>Skills: ${c.skills.join(", ")}</p>
        <button onclick="banUser('${c.id}','candidate')">Ban</button>
        <button onclick="investigateUser('${c.id}','candidate')">Investigate</button>`;
        container.appendChild(card);
    });
}

async function banUser(userId,type){
    const res=await fetch(`${API_URL}/admin/ban`,{
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({userId,type})
    });
    const data = await res.json(); alert(data.message);
    fetchRecruiters(); fetchCandidates();
}

async function investigateUser(userId,type){
    const res=await fetch(`${API_URL}/admin/investigate`,{
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({userId,type})
    });
    const data = await res.json(); alert(data.message);
    fetchRecruiters(); fetchCandidates();
}

function logout(){ localStorage.removeItem("user"); window.location.href="login.html"; }

// Initial load
showSection("stats");
fetchStats();
fetchRecruiters();
fetchCandidates();
