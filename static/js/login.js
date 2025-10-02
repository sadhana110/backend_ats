const API_URL = "https://backend-ats-z0tb.onrender.com";

// Login form
const loginForm = document.getElementById("loginForm");
if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const role = document.getElementById("role").value;

        try {
            const res = await fetch(`${API_URL}/login`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ email, password, role })
            });
            const data = await res.json();
            if (data.success) {
                localStorage.setItem("user", JSON.stringify(data.user));
                if(role === "candidate") window.location.href = "candidate_dashboard.html";
                else if(role === "recruiter") window.location.href = "recruiter_dashboard.html";
                else window.location.href = "admin_dashboard.html";
            } else {
                alert(data.message);
            }
        } catch(err) {
            console.error(err);
            alert("Login failed");
        }
    });
}

// Candidate registration
const candidateForm = document.getElementById("candidateRegisterForm");
if(candidateForm){
    candidateForm.addEventListener("submit", async (e)=>{
        e.preventDefault();
        const name = document.getElementById("name").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const phone = document.getElementById("phone").value;
        const skills = document.getElementById("skills").value;
        const resume = document.getElementById("resume").value;

        try{
            const res = await fetch(`${API_URL}/register/candidate`, {
                method:"POST",
                headers: {"Content-Type":"application/json"},
                body: JSON.stringify({ name,email,password,phone,skills,resume })
            });
            const data = await res.json();
            if(data.success){
                alert("Registered Successfully");
                window.location.href = "login.html";
            } else alert(data.message);
        } catch(err){ console.error(err); alert("Registration failed"); }
    });
}

// Recruiter registration
const recruiterForm = document.getElementById("recruiterRegisterForm");
if(recruiterForm){
    recruiterForm.addEventListener("submit", async (e)=>{
        e.preventDefault();
        const name = document.getElementById("name").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const company = document.getElementById("company").value;
        const phone = document.getElementById("phone").value;
        const description = document.getElementById("description").value;

        try{
            const res = await fetch(`${API_URL}/register/recruiter`, {
                method:"POST",
                headers: {"Content-Type":"application/json"},
                body: JSON.stringify({ name,email,password,company,phone,description })
            });
            const data = await res.json();
            if(data.success){
                alert("Registered Successfully");
                window.location.href = "login.html";
            } else alert(data.message);
        } catch(err){ console.error(err); alert("Registration failed"); }
    });
}
