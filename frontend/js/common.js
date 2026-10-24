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
}

function option(value, label) { return '<option value="' + esc(value) + '">' + esc(label) + "</option>"; }

function formData(form) {
  const data = {};
  new FormData(form).forEach((v, k) => { data[k] = v === "" ? null : v; });
  return data;
}
