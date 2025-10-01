const API = "https://your-render-backend.onrender.com"; // change to your backend URL

// Utility to switch sections
function showSection(id) {
  document.querySelectorAll(".container > div").forEach(s => s.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
}

// Navbar
document.getElementById("navHome").onclick = () => showSection("landingSection");
document.getElementById("navLogin").onclick = () => showSection("loginSection");
document.getElementById("navCandidateRegister").onclick = () => showSection("candidateRegisterSection");
document.getElementById("navRecruiterRegister").onclick = () => showSection("recruiterRegisterSection");
document.getElementById("navLogout").onclick = () => {
  localStorage.clear();
  showSection("landingSection");
  document.getElementById("navLogout").classList.add("hidden");
};

// Candidate Register
document.getElementById("candidateForm").onsubmit = async e => {
  e.preventDefault();
  const data = {
    name: c_name.value,
    email: c_email.value,
    password: c_password.value,
    role: "candidate"
  };
  await fetch(API + "/register", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });
  alert("Candidate registered!");
  showSection("loginSection");
};

// Recruiter Register
document.getElementById("recruiterForm").onsubmit = async e => {
  e.preventDefault();
  const data = {
    name: r_name.value,
    email: r_email.value,
    password: r_password.value,
    role: "recruiter"
  };
  await fetch(API + "/register", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });
  alert("Recruiter registered!");
  showSection("loginSection");
};

// Login
document.getElementById("loginForm").onsubmit = async e => {
  e.preventDefault();
  const data = {
    email: loginEmail.value,
    password: loginPassword.value,
    role: loginRole.value
  };
  const res = await fetch(API + "/login", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });
  const out = await res.json();
  if (!out.success) { alert("Invalid login"); return; }
  localStorage.setItem("user", JSON.stringify(out.user));
  document.getElementById("navLogout").classList.remove("hidden");
  if (out.user.role === "candidate") {
    candidateName.textContent = out.user.name;
    loadJobs();
    showSection("candidateDashboard");
  } else if (out.user.role === "recruiter") {
    recruiterName.textContent = out.user.name;
    loadRecruiterJobs();
    showSection("recruiterDashboard");
  } else {
    loadAdmin();
    showSection("adminDashboard");
  }
};

// Candidate: Load Jobs
async function loadJobs() {
  const res = await fetch(API + "/jobs");
  const jobs = await res.json();
  jobList.innerHTML = jobs.map(j => `<div class="card p-2 mb-2"><b>${j.title}</b> - ${j.desc}</div>`).join("");
}

// Recruiter: Post Job
document.getElementById("jobPostForm").onsubmit = async e => {
  e.preventDefault();
  const user = JSON.parse(localStorage.getItem("user"));
  const data = { title: jobTitle.value, desc: jobDesc.value, postedBy: user.email };
  await fetch(API + "/postjob", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });
  jobTitle.value = ""; jobDesc.value = "";
  loadRecruiterJobs();
};

// Recruiter: Load Posted Jobs
async function loadRecruiterJobs() {
  const user = JSON.parse(localStorage.getItem("user"));
  const res = await fetch(API + "/jobs");
  const jobs = await res.json();
  recruiterJobs.innerHTML = jobs.filter(j => j.postedBy === user.email)
    .map(j => `<div class="card p-2 mb-2"><b>${j.title}</b> - ${j.desc}</div>`).join("");
}

// Admin
async function loadAdmin() {
  const res = await fetch(API + "/users");
  const users = await res.json();
  adminContent.innerHTML = users.map(u => `<div>${u.role}: ${u.name} (${u.email})</div>`).join("");
}
