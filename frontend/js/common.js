const API = "/api";

function getToken() { return localStorage.getItem("token"); }
function currentUser() { try { return JSON.parse(localStorage.getItem("user")); } catch (e) { return null; } }

function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}

async function api(path, method = "GET", body = null) {
  const options = { method, headers: { "Content-Type": "application/json" } };
  if (getToken()) options.headers["Authorization"] = "Bearer " + getToken();
  if (body) options.body = JSON.stringify(body);
  const res = await fetch(API + path, options);
  if (res.status === 401 && !path.startsWith("/auth/login")) { logout(); return; }
  let data = null;
  try { data = await res.json(); } catch (e) { /* empty body */ }
  if (!res.ok) {
    let msg = "Request failed (" + res.status + ")";
    if (data && data.detail) msg = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    throw new Error(msg);
  }
  return data;
}

function esc(value) {
  return String(value === null || value === undefined ? "" : value).replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// Server timestamps are UTC without a "Z". Appointment times are entered as local time, so pass isUtc=false for those.
function fmt(dt, isUtc = true) {
  if (!dt) return "-";
  const text = isUtc && !/Z|[+-]\d\d:\d\d$/.test(dt) ? dt + "Z" : dt;
  return new Date(text).toLocaleString();
}

function toast(message, isError = false) {
  let el = document.getElementById("toast");
  if (!el) { el = document.createElement("div"); el.id = "toast"; document.body.appendChild(el); }
  el.textContent = message;
  el.className = isError ? "error" : "";
  el.style.display = "block";
  clearTimeout(el._timer);
  el._timer = setTimeout(() => { el.style.display = "none"; }, 3500);
}

function handleError(e) { toast(e.message || String(e), true); }

const HOME = { admin: "admin.html", doctor: "doctor.html", nurse: "nurse.html", patient: "patient.html" };

function requireRole(roles) {
  const user = currentUser();
  if (!user || !getToken() || !roles.includes(user.role)) {
    window.location.href = "index.html";
    return null;
  }
  renderNav(user);
  return user;
}

function renderNav(user) {
  const nav = document.getElementById("nav");
  if (!nav) return;
  let links = "";
  if (user.role !== "patient") links += '<a href="' + HOME[user.role] + '">Home</a>';
  if (user.role !== "patient") links += '<a href="inventory.html">Inventory</a>';
  nav.innerHTML = '<span class="brand">Ward Management</span>' + links +
    '<span class="grow"></span><span>' + esc(user.full_name) + " (" + esc(user.role) + ')</span>' +
    '<button class="small grey" onclick="logout()">Logout</button>';
  const sidebarLinks = user.role === "patient"
    ? '<a class="active" href="patient.html">Patient portal</a><a href="#appt-form">Appointments</a><a href="#prescriptions">Medications</a><a class="critical-link" href="#call-card">Request assistance</a>'
    : user.role === "doctor"
      ? '<a class="active" href="doctor.html">Doctor dashboard</a><a href="#appointments">Appointments</a><a href="#patients">Patient roster</a><a href="#rx-form">Prescriptions</a><a href="inventory.html">Inventory &amp; pharmacy</a>'
      : user.role === "admin"
        ? '<a class="active" href="admin.html">Admin dashboard</a><a href="#summary">Operations summary</a><a href="#users">Staff &amp; access</a><a href="#alert-report">Alert reports</a><a href="inventory.html">Inventory &amp; pharmacy</a>'
        : '<a class="active" href="nurse.html">Nurse station</a><a href="#alerts-title">Safety alerts</a><a href="#beds-title">Ward census</a><a href="inventory.html">Inventory &amp; pharmacy</a><a class="critical-link" href="#alerts-title">Emergency protocols</a>';
  const sidebar = document.createElement("aside");
  sidebar.className = "clinical-sidebar";
  sidebar.setAttribute("aria-label", "Clinical navigation");
  sidebar.innerHTML = '<p class="eyebrow">Clinical navigation</p>' + sidebarLinks;
  document.body.prepend(sidebar);
}

function option(value, label) { return '<option value="' + esc(value) + '">' + esc(label) + "</option>"; }

function formData(form) {
  const data = {};
  new FormData(form).forEach((v, k) => { data[k] = v === "" ? null : v; });
  return data;
}
