document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = formData(e.target);
  try {
    const res = await api("/auth/login", "POST", body);
    localStorage.setItem("token", res.access_token);
    localStorage.setItem("user", JSON.stringify(res.user));
    window.location.href = HOME[res.user.role];
  } catch (err) { handleError(err); }
});

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/auth/register", "POST", formData(e.target));
    toast("Registered. You can log in now.");
    e.target.reset();
  } catch (err) { handleError(err); }
});

if (getToken() && currentUser()) { window.location.href = HOME[currentUser().role]; }
