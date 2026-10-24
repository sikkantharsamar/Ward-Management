const user = requireRole(["admin"]);

async function loadSummary() {
  try {
    const s = await api("/reports/summary");
    const labels = {
      patients_admitted: "Admitted patients", beds_occupied: "Beds occupied", beds_available: "Beds available",
      alerts_active: "Active alerts", alerts_today: "Alerts today", low_stock_items: "Low stock items", appointments_today: "Appointments today"
    };
    document.getElementById("summary").innerHTML = Object.keys(labels).map(k =>
      `<div class="card" style="margin:0;text-align:center;min-width:120px"><div style="font-size:26px;font-weight:bold">${s[k]}</div><div class="muted">${labels[k]}</div></div>`).join("");
  } catch (e) { handleError(e); }
}

async function loadWards() {
  try {
    const wards = await api("/wards");
    const buildings = await api("/buildings");
    document.getElementById("ward-building").innerHTML = buildings.map(b => option(b.id, b.name)).join("");
    document.getElementById("bed-ward").innerHTML = wards.map(w => option(w.id, w.building_name + " - " + w.name)).join("");
    document.getElementById("user-ward").innerHTML = option("", "-- none --") + wards.map(w => option(w.id, w.building_name + " - " + w.name)).join("");
    let html = "";
    for (const w of wards) {
      const beds = await api("/wards/" + w.id + "/beds");
      html += `<h3>${esc(w.building_name)} - ${esc(w.name)} <span class="muted">(${w.occupied_count}/${w.bed_count} occupied)</span></h3>
        <table><tr><th>Bed</th><th>Status</th><th>Device key</th></tr>` +
        beds.map(b => `<tr><td>${esc(b.bed_number)}</td><td>${esc(b.status)}</td><td><code>${esc(b.device_key || "")}</code></td></tr>`).join("") + "</table>";
    }
    document.getElementById("wards").innerHTML = html || '<p class="muted">No wards yet.</p>';
  } catch (e) { handleError(e); }
}

async function loadUsers() {
  try {
    const users = await api("/users");
    document.getElementById("users").innerHTML = "<table><tr><th>Name</th><th>Email</th><th>Role</th><th>Active</th><th></th></tr>" +
      users.map(u => `<tr><td>${esc(u.full_name)}</td><td>${esc(u.email)}</td><td>${esc(u.role)}</td>
        <td>${u.is_active ? "yes" : "no"}</td>
        <td><button class="small ${u.is_active ? "red" : "green"}" onclick="toggleUser(${u.id}, ${!u.is_active})">${u.is_active ? "Disable" : "Enable"}</button></td></tr>`).join("") + "</table>";
  } catch (e) { handleError(e); }
}

async function toggleUser(id, active) {
  try { await api("/users/" + id + "/active", "PATCH", { is_active: active }); loadUsers(); } catch (e) { handleError(e); }
}

async function loadAlertReport() {
  try {
    const r = await api("/reports/alerts");
    document.getElementById("alert-stats").textContent =
      "Total: " + r.stats.total + " | Average response: " + (r.stats.avg_response_seconds ?? "-") + " s | Slowest: " + (r.stats.max_response_seconds ?? "-") + " s";
    document.getElementById("alert-report").innerHTML = "<table><tr><th>Raised</th><th>Location</th><th>Patient</th><th>Source</th><th>Status</th><th>Response (s)</th></tr>" +
      r.alerts.slice(0, 50).map(a => `<tr><td>${fmt(a.created_at)}</td><td>${esc(a.ward_name)} / ${esc(a.bed_number)}</td><td>${esc(a.patient_name || "-")}</td>
        <td>${esc(a.source)}</td><td>${esc(a.status)}</td><td>${a.response_seconds ?? "-"}</td></tr>`).join("") + "</table>";
  } catch (e) { handleError(e); }
}

document.getElementById("csv-btn").addEventListener("click", async () => {
  try {
    const res = await fetch(API + "/reports/alerts.csv", { headers: { Authorization: "Bearer " + getToken() } });
    if (!res.ok) throw new Error("Could not download the report");
    const url = URL.createObjectURL(await res.blob());
    const a = document.createElement("a"); a.href = url; a.download = "alerts_report.csv"; a.click();
    URL.revokeObjectURL(url);
  } catch (e) { handleError(e); }
});

async function loadAudit() {
  try {
    const rows = await api("/reports/audit");
    document.getElementById("audit").innerHTML = "<table><tr><th>Time</th><th>User</th><th>Action</th><th>Detail</th></tr>" +
      rows.slice(0, 40).map(r => `<tr><td>${fmt(r.created_at)}</td><td>${r.user_id ?? "-"}</td><td>${esc(r.action)}</td><td>${esc(r.detail || "")}</td></tr>`).join("") + "</table>";
  } catch (e) { handleError(e); }
}

function reloadAll() { loadSummary(); loadWards(); loadUsers(); loadAlertReport(); loadAudit(); }

document.getElementById("user-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const d = formData(e.target);
  d.ward_id = d.ward_id ? +d.ward_id : null;
  try { await api("/users", "POST", d); toast("User created"); e.target.reset(); reloadAll(); } catch (err) { handleError(err); }
});
document.getElementById("building-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try { await api("/buildings", "POST", formData(e.target)); toast("Building added"); e.target.reset(); reloadAll(); } catch (err) { handleError(err); }
});
document.getElementById("ward-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const d = formData(e.target);
  d.building_id = +d.building_id; d.ward_type = d.ward_type || "general";
  try { await api("/wards", "POST", d); toast("Ward added"); e.target.reset(); reloadAll(); } catch (err) { handleError(err); }
});
document.getElementById("bed-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const d = formData(e.target);
  d.ward_id = +d.ward_id;
  try { await api("/beds", "POST", d); toast("Bed added"); e.target.reset(); reloadAll(); } catch (err) { handleError(err); }
});

if (user) reloadAll();
