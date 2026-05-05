// Add popup sign-in logic and autofill form if match found
(function() {
  // Get User popup logic
  const getUserBtn = document.getElementById('getUserBtn');
  const userPopup = document.getElementById('userPopup');
  const closePopupBtn = document.getElementById('closePopupBtn');
  const signInBtn = document.getElementById('signInBtn');
  const popupStatus = document.getElementById('popupStatus');

  document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("secureForm");

    form.addEventListener("submit", () => {
      const submitBtn = form.querySelector('button[type="submit"]');

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Submitting...";
      }

      // lock fields without breaking submission
      setTimeout(() => {
        const inputs = form.querySelectorAll("input, select, textarea");
        inputs.forEach(el => el.readOnly = true);
      }, 0);
    });
  });

  getUserBtn.addEventListener('click', function() {
    userPopup.style.display = 'block';
    popupStatus.textContent = '';
    document.getElementById('popupUsername').value = '';
    document.getElementById('popupPassword').value = '';
  });

  closePopupBtn.addEventListener('click', function() {
    userPopup.style.display = 'none';
  });

  signInBtn.addEventListener('click', function() {
    const username = document.getElementById('popupUsername').value;
    const password = document.getElementById('popupPassword').value;
    console.log('Attempting sign in with:', { username, password });
    popupStatus.textContent = 'Signing in...';
    fetch('http://localhost:5001/signin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.user) {
          popupStatus.style.color = 'green';
          popupStatus.textContent = 'Sign in successful!';
          // Autofill form fields
          const u = data.user;
          if(document.getElementById('firstName')) document.getElementById('firstName').value = u.firstName || '';
          if(document.getElementById('middleInitial')) document.getElementById('middleInitial').value = u.middleInitial || '';
          if(document.getElementById('lastName')) document.getElementById('lastName').value = u.lastName || '';
          if(document.getElementById('SSN')) document.getElementById('SSN').value = u.SSN || '';
          if(document.getElementById('DOB')) document.getElementById('DOB').value = formatDate(u.DOB) || '';
          if(document.getElementById('email')) document.getElementById('email').value = u.email || '';
          if(document.getElementById('phoneNumber')) document.getElementById('phoneNumber').value = u.phoneNumber || '';
          if(document.getElementById('address')) document.getElementById('address').value = u.address || '';
          if(document.getElementById('city')) document.getElementById('city').value = u.city || '';
          if(document.getElementById('state')) document.getElementById('state').value = u.state || '';
          if(document.getElementById('zip')) document.getElementById('zip').value = u.zip || '';
          if(document.getElementById('annualIncome')) document.getElementById('annualIncome').value = u.annualIncome || '';
          setTimeout(() => { userPopup.style.display = 'none'; }, 1000);
        } else {
          popupStatus.style.color = 'red';
          popupStatus.textContent = data.message || 'Sign in failed.';
        }
      })
      .catch(() => {
        popupStatus.style.color = 'red';
        popupStatus.textContent = 'Error signing in.';
      });
  });

  // Helper function to format date for input[type="date"]
  function formatDate(dateStr) {
    if (!dateStr) return "";

    const d = new Date(dateStr);
    if (isNaN(d)) return "";

    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const year = d.getFullYear();

    return `${month}/${day}/${year}`;
  }

  document.getElementById("secureForm").addEventListener("submit", async function(e) {
    e.preventDefault(); // STOP normal form submit

    const overlay = document.getElementById("loadingOverlay");
    overlay.style.display = "flex";

    const form = e.target;
    const formData = new FormData(form);

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: formData
      });

      // Option A: redirect after success
      if (response.ok) {
        window.location.href = "/result?status=success";
      } else {
        overlay.style.display = "none";
        alert("Submission failed");
      }

    } catch (err) {
      overlay.style.display = "none";
      alert("Network error");
    }
  });
})();

//  // function to handle form submission result display
//   function renderResult(success, message) {
//   const app = document.getElementById("app");
//   // app.style.opacity = 0;
//   // setTimeout(() => app.style.opacity = 1, 50);

//   app.innerHTML = ""; // clear everything

//   const box = document.createElement("div");
//   box.style.textAlign = "center";
//   box.style.marginTop = "100px";

//   const title = document.createElement("h1");
//   title.textContent = success
//     ? "✅ Transmission Successful"
//     : "❌ Transmission Failed";

//   title.style.color = success ? "green" : "red";

//   const msg = document.createElement("p");
//   msg.textContent = message || "";

//   // const btn = document.createElement("button");
//   // btn.textContent = "Return to Form";
//   // btn.onclick = () => window.location.reload();

//   box.appendChild(title);
//   box.appendChild(msg);
//   box.appendChild(btn);

//   app.appendChild(box);
// }


//   document.addEventListener("DOMContentLoaded", function () {
//     document.getElementById('secureForm').addEventListener('submit', function (e) {
//     e.preventDefault();

//     document.getElementById("status").textContent = "Transmitting securely...";

//     const form = document.getElementById("secureForm");

//     form.addEventListener("submit", () => {
//     const elements = form.querySelectorAll("input, select, button, textarea");

//       elements.forEach(el => {
//         el.disabled = true;
//       });

//       const submitBtn = form.querySelector('button[type="submit"]');
//       if (submitBtn) {
//         submitBtn.textContent = "Submitting...";
//       }
//     });
    
//     fetch('http://localhost:5005/app', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify(Object.fromEntries(new FormData(e.target)))
//     })
//     .then(res => res.json())
//     .then(data => {
//       renderResult(data.success, data.message);

//       return fetch('http://localhost:5005/app', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(data)
//       });
//     })
//     .then(res => res.json())
//     .then(appResponse => {
//       console.log("App service response:", appResponse);
//     })
//     .catch(() => {
//       renderResult(false, "Network or server error");
//     });
//   });
// });

