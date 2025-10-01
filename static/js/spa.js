const API = "https://your-render-backend.onrender.com"; // change to your Render backend

function showSection(id) {
  document.querySelectorAll(".container > div").forEach(s => s.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
}

// Navbar
document.getElementById("navHome").onclick = () => showSection("landingSection");
document.getElementById("navLogin").onclick = () => showSection("loginSection");
document.getElementById("navCandidateRegister").onclick = () => showSection("candidateRegisterSection");
document.getElementById("navRecruiterRegister").onclick = () => showSection("recruiterRegisterSection");
document.getElementById("navLogout").onclick = () => { localStorage.clear(); location.reload(); };

// Candidate Register
document.getElementById("candidateForm").onsubmit = async e => {
  e.preventDefault();
  const data = { name:c_name.value, email:c_email.value, password:c_password.value, role:"candidate" };
  await fetch(API+"/register", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
  alert("Candidate registered!"); showSection("loginSection");
};

// Recruiter Register
document.getElementById("recruiterForm").onsubmit = async e => {
  e.preventDefault();
  const data = { name:r_name.value, email:r_email.value, password:r_password.value, role:"recruiter" };
  await fetch(API+"/register", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
  alert("Recruiter registered!"); showSection("loginSection");
};

// Login
document.getElementById("loginForm").onsubmit = async e => {
  e.preventDefault();
  const data = { email:loginEmail.value,password:loginPassword.value,role:loginRole.value };
  const res = await fetch(API+"/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
  const out = await res.json();
  if(!out.success){ alert("Invalid login"); return; }
  localStorage.setItem("user", JSON.stringify(out.user));
  document.getElementById("navLogout").classList.remove("hidden");
  if(out.user.role==="candidate"){ candidateName.textContent=out.user.name; loadJobs(); showSection("candidateDashboard"); }
  else if(out.user.role==="recruiter"){ recruiterName.textContent=out.user.name; loadRecruiterJobs(); showSection("recruiterDashboard"); }
  else { loadAdmin(); showSection("adminDashboard"); }
};

// Candidate: Jobs
async function loadJobs(){
  const res=await fetch(API+"/jobs"); const jobs=await res.json(); const user=JSON.parse(localStorage.getItem("user"));
  jobList.innerHTML=jobs.map(j=>`
    <div class="card p-2 mb-2">
      <b>${j.title}</b> - ${j.desc}
      <button class="btn btn-sm btn-primary" onclick="applyJob('${j._id}')">Apply</button>
      <button class="btn btn-sm btn-warning" onclick="saveJob('${j._id}')">Save</button>
    </div>`).join("");
}
async function applyJob(jobId){ const user=JSON.parse(localStorage.getItem("user")); await fetch(API+"/apply",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({candidateId:user._id,jobId})}); loadJobs(); }
async function saveJob(jobId){ const user=JSON.parse(localStorage.getItem("user")); await fetch(API+"/save_job",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({candidateId:user._id,jobId})}); loadJobs(); }

// Recruiter
document.getElementById("jobPostForm").onsubmit=async e=>{
  e.preventDefault();
  const user=JSON.parse(localStorage.getItem("user"));
  const data={title:jobTitle.value,desc:jobDesc.value,recruiterId:user._id};
  await fetch(API+"/post_job",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
  loadRecruiterJobs();
};
async function loadRecruiterJobs(){ const user=JSON.parse(localStorage.getItem("user")); const res=await fetch(API+"/recruiter_jobs/"+user._id); const jobs=await res.json(); recruiterJobs.innerHTML=jobs.map(j=>`<div class="card p-2 mb-2"><b>${j.title}</b></div>`).join(""); }

// Admin
async function loadAdmin(){
  const res=await fetch(API+"/admin_stats"); const stats=await res.json();
  new Chart(document.getElementById("adminChart"),{type:'bar',data:{labels:["Candidates","Recruiters","Jobs","Reports"],datasets:[{data:[stats.candidates,stats.recruiters,stats.jobs,stats.reports],backgroundColor:["blue","green","orange","red"]}]}})
  const res2=await fetch(API+"/users"); const users=await res2.json(); adminUsers.innerHTML=users.map(u=>`<div>${u.role}: ${u.name} (${u.email})</div>`).join("");
}
