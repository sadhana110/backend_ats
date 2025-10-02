// -------------------- BASE URL --------------------
const BASE_URL = "https://backend-ats-z0tb.onrender.com";

// -------------------- AUTH --------------------
async function registerUser() {
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const role = document.getElementById("role").value;

    // You can add extra info like education later
    const extra_info = {};

    try {
        const res = await fetch(`${BASE_URL}/register`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({name, email, password, role, extra_info})
        });

        const data = await res.json();

        if (res.ok) {
            alert(data.message);
            window.location.href = "login.html";
        } else {
            alert("Error: " + data.message);
        }
    } catch (err) {
        console.error(err);
        alert("Server error: Cannot connect to backend");
    }
}

async function loginUser(){
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;
    try{
        const res = await fetch(`${BASE_URL}/login`, {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({email,password,role})
        });
        const result = await res.json();
        if(res.ok){
            localStorage.setItem('user',JSON.stringify(result.user));
            if(role==='candidate') window.location='candidate_dashboard.html';
            else if(role==='recruiter') window.location='recruiter_dashboard.html';
            else if(role==='admin') window.location='admin_dashboard.html';
        } else {
            alert('Login failed: '+result.message);
        }
    } catch(err){
        alert('Server error');
    }
}

function logout(){
    localStorage.removeItem('user');
    window.location='login.html';
}

// -------------------- DASHBOARD TABS --------------------
function showTab(tab){
    const container = document.getElementById('dashboardContent');
    container.innerHTML='<p class="text-center">Loading...</p>';
    if(tab==='profile') loadProfile();
    else if(tab==='jobs') loadJobs();
    else if(tab==='applications') loadApplications();
    else if(tab==='shortlisted') loadShortlisted();
    else if(tab==='messages') loadMessages();
    else if(tab==='postJob') showJobPostForm();
}

// -------------------- PROFILE --------------------
async function loadProfile(){
    const user = JSON.parse(localStorage.getItem('user'));
    document.getElementById('dashboardContent').innerHTML=`
        <div class="card p-3 shadow">
            <h3>${user.name}</h3>
            <p>Email: ${user.email}</p>
            <p>Role: ${user.role}</p>
        </div>`;
}

// -------------------- JOB POSTING --------------------
async function loadPostJobForm(){
    const container = document.getElementById('dashboardContent');
    container.innerHTML=`
    <div class="col-md-12">
        <div class="card p-4 shadow">
            <h4>Post New Job</h4>
            <form id="postJobForm">
                <div class="mb-3"><input type="text" id="title" class="form-control" placeholder="Job Title" required></div>
                <div class="mb-3"><input type="text" id="company" class="form-control" placeholder="Company Name" required></div>
                <div class="mb-3"><input type="text" id="location" class="form-control" placeholder="Location" required></div>
                <div class="mb-3"><input type="text" id="role" class="form-control" placeholder="Role" required></div>
                <div class="mb-3"><textarea id="description" class="form-control" placeholder="Job Description" required></textarea></div>
                <div class="mb-3"><input type="date" id="expiryDate" class="form-control" placeholder="Application End Date" required></div>
                <button type="submit" class="btn btn-primary">Post Job</button>
            </form>
        </div>
    </div>`;

    document.getElementById('postJobForm').addEventListener('submit', async (e)=>{
        e.preventDefault();

        const currentUser = JSON.parse(localStorage.getItem('user'));
        if(!currentUser) return alert("You must be logged in as recruiter!");

        const data={
            title: document.getElementById('title').value,
            company: document.getElementById('company').value,
            location: document.getElementById('location').value,
            role: document.getElementById('role').value,
            description: document.getElementById('description').value,
            expiryDate: document.getElementById('expiryDate').value, // corrected
            recruiterId: currentUser.id
        };

        try {
            const res = await fetch(`${BASE_URL}/jobs`,{
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify(data)
            });

            const result = await res.json();

            if(res.ok){
                alert(result.message || 'Job posted successfully!');
                loadJobs(); // reload job list
            } else {
                alert('Error posting job: ' + (result.message || 'Unknown error'));
            }
        } catch(err){
            console.error(err);
            alert('Server error: Cannot connect to backend');
        }
    });
}


async function loadJobs(){
    const res = await fetch(`${BASE_URL}/jobs`);
    const jobs = await res.json();
    const container = document.getElementById('dashboardContent');
    container.innerHTML='';
    jobs.forEach(job=>{
        const card = document.createElement('div');
        card.className='card p-3 shadow mb-2';
        card.innerHTML=`
            <h4>${job.title}</h4>
            <p>${job.description}</p>
            <p>Location: ${job.location}</p>
            <p>Expiry: ${job.expiryDate}</p>
        `;
        container.appendChild(card);
    });
}

// -------------------- APPLICATIONS --------------------
async function loadApplications(){
    const user = JSON.parse(localStorage.getItem('user'));
    const res = await fetch(`${BASE_URL}/applications?userId=${user.id}`);
    const apps = await res.json();
    const container = document.getElementById('dashboardContent');
    container.innerHTML='';
    apps.forEach(app=>{
        const card = document.createElement('div');
        card.className='card p-3 shadow mb-2';
        card.innerHTML=`
            <h4>${app.jobTitle}</h4>
            <p>Status: ${app.status}</p>
            <p>Recruiter: ${app.recruiterName}</p>
        `;
        container.appendChild(card);
    });
}

// -------------------- SHORTLISTED --------------------
async function loadShortlisted(){
    const user = JSON.parse(localStorage.getItem('user'));
    const res = await fetch(`${BASE_URL}/shortlisted?userId=${user.id}`);
    const apps = await res.json();
    const container = document.getElementById('dashboardContent');
    container.innerHTML='';
    apps.forEach(app=>{
        const card = document.createElement('div');
        card.className='card p-3 shadow mb-2';
        card.innerHTML=`
            <h4>${app.jobTitle}</h4>
            <p>Recruiter: ${app.recruiterName}</p>
        `;
        container.appendChild(card);
    });
}

// -------------------- MESSAGING --------------------
async function loadMessages(){
    const user = JSON.parse(localStorage.getItem('user'));
    const res = await fetch(`${BASE_URL}/messages?userId=${user.id}`);
    const msgs = await res.json();
    const container = document.getElementById('dashboardContent');
    container.innerHTML='';
    msgs.forEach(m=>{
        const card = document.createElement('div');
        card.className='card p-3 shadow mb-2';
        card.innerHTML=`
            <p><strong>From:</strong> ${m.fromName}</p>
            <p>${m.message}</p>
            <small>${new Date(m.date).toLocaleString()}</small>
        `;
        container.appendChild(card);
    });
}

async function sendMessage(toId,message){
    const user = JSON.parse(localStorage.getItem('user'));
    await fetch(`${BASE_URL}/messages`,{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({fromId:user.id,toId,message})
    });
    alert('Message sent');
}

// -------------------- INTERVIEW SCHEDULING --------------------
async function scheduleInterview(candidateId,jobId,dateTime){
    const res = await fetch(`${BASE_URL}/interviews`,{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({candidateId,jobId,dateTime})
    });
    if(res.ok) alert('Interview scheduled');
}

// -------------------- UTILS --------------------
function showError(msg){
    alert(msg);
}
