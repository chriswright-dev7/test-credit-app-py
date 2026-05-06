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

  signInBtn.addEventListener('click', async function () {
  const username = document.getElementById('popupUsername').value;
  const password = document.getElementById('popupPassword').value;

  popupStatus.textContent = 'Signing in...';

    try {
      const res = await fetch("/config");
      const CONFIG = await res.json();

      console.log('CONFIG loaded:', CONFIG);

      const response = await fetch(
        `http://${CONFIG.HOST}:${CONFIG.SIGNIN_PORT}/signin`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        }
      );

      const data = await response.json();

      if (data.success && data.user) {
        popupStatus.style.color = 'green';
        popupStatus.textContent = 'Sign in successful!';

        const u = data.user;

        if (document.getElementById('firstName'))
          document.getElementById('firstName').value = u.firstName || '';

        if (document.getElementById('middleInitial'))
          document.getElementById('middleInitial').value = u.middleInitial || '';

        if (document.getElementById('lastName'))
          document.getElementById('lastName').value = u.lastName || '';

        if (document.getElementById('SSN'))
          document.getElementById('SSN').value = u.SSN || '';

        if (document.getElementById('DOB'))
          document.getElementById('DOB').value = formatDate(u.DOB) || '';

        if (document.getElementById('email'))
          document.getElementById('email').value = u.email || '';

        if (document.getElementById('phoneNumber'))
          document.getElementById('phoneNumber').value = u.phoneNumber || '';

        if (document.getElementById('address'))
          document.getElementById('address').value = u.address || '';

        if (document.getElementById('city'))
          document.getElementById('city').value = u.city || '';

        if (document.getElementById('state'))
          document.getElementById('state').value = u.state || '';

        if (document.getElementById('zip'))
          document.getElementById('zip').value = u.zip || '';

        if (document.getElementById('annualIncome'))
          document.getElementById('annualIncome').value = u.annualIncome || '';

        setTimeout(() => {
          userPopup.style.display = 'none';
        }, 1000);

      } else {
        popupStatus.style.color = 'red';
        popupStatus.textContent = data.message || 'Sign in failed.';
      }

    } catch (err) {
      popupStatus.style.color = 'red';
      popupStatus.textContent = 'Error signing in.';
      console.error(err);
    }
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
