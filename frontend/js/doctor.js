const user = requireRole(["doctor", "admin"]);
let medicines = [];

async function loadAppointments() {
  try {
    const list = await api("/appointments");
    document.getElementById("appointments").innerHTML = list.length
      ? "<table><tr><th>When</th><th>Patient</th><th>Reason</th><th>Status</th><th></th></tr>" +
        list.map(a => `<tr><td>${fmt(a.scheduled_at, false)}</td><td>${esc(a.patient_name)}</td><td>${esc(a.reason || "")}</td>
          <td><span class="tag ${a.status === "scheduled" ? "blue" : a.status === "completed" ? "green" : "grey"}">${esc(a.status)}</span></td>
          <td>${a.status === "scheduled" ? `<button class="small green" onclick="setStatus(${a.id},'completed')">Complete</button>
          <button class="small red" onclick="setStatus(${a.id},'cancelled')">Cancel</button>` : ""}</td></tr>`).join("") + "</table>"
      : '<p class="muted">No appointments.</p>';
  } catch (e) { handleError(e); }
}

async function setStatus(id, status) {
  try { await api("/appointments/" + id + "/status", "PATCH", { status }); loadAppointments(); } catch (e) { handleError(e); }
}

async function loadPatients() {
  try {
    const q = encodeURIComponent(document.getElementById("search").value);
    const patients = await api("/patients?q=" + q);
    document.getElementById("patients").innerHTML = "<table>" + patients.map(p =>
      `<tr><td>${esc(p.full_name)}<br><span class="muted">${esc(p.patient_no)}</span></td>
       <td><button class="small" onclick="showPatient(${p.id})">View</button></td></tr>`).join("") + "</table>";
    document.getElementById("rx-patient").innerHTML = patients.map(p => option(p.id, p.full_name + " (" + p.patient_no + ")")).join("");
  } catch (e) { handleError(e); }
}

async function showPatient(id) {
  try {
    const p = await api("/patients/" + id);
    const adm = p.current_admission;
    document.getElementById("detail").innerHTML = `
      <b>${esc(p.full_name)}</b> <span class="muted">${esc(p.patient_no)}</span><br>
      DOB: ${esc(p.date_of_birth || "-")} | Gender: ${esc(p.gender || "-")} | Phone: ${esc(p.phone || "-")}<br>
      Allergies: <b>${esc(p.allergies || "none recorded")}</b><br>
      Condition: ${esc(p.medical_condition || "-")}<br>
      ${p.isolation_status ? '<span class="tag red">ISOLATION</span><br>' : ""}
      Special needs: ${esc(p.special_needs || "-")}<br>
      Admission: ${adm ? esc(adm.building_name + " / " + adm.ward_name + " / Bed " + adm.bed_number) : "not admitted"}<br>
      Guardians: ${p.guardians.length ? p.guardians.map(g => esc(g.full_name + " (" + (g.relationship_type || "") + ") " + (g.phone || ""))).join("; ") : "-"}`;
  } catch (e) { handleError(e); }
}

async function loadMedicines() {
  try {
    medicines = await api("/inventory?category=medicine");
    document.getElementById("rx-item").innerHTML = option("", "-- not linked --") + medicines.map(m => option(m.id, m.name + " (" + m.quantity + " in stock)")).join("");
  } catch (e) { handleError(e); }
}

document.getElementById("rx-item").addEventListener("change", (e) => {
  const item = medicines.find(m => String(m.id) === e.target.value);
  if (item) document.getElementById("rx-name").value = item.name;
});

document.getElementById("rx-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const d = formData(e.target);
  d.patient_id = +d.patient_id;
  d.item_id = d.item_id ? +d.item_id : null;
  try { await api("/prescriptions", "POST", d); toast("Prescription issued"); e.target.reset(); loadPrescriptions(); } catch (err) { handleError(err); }
});

async function loadPrescriptions() {
  try {
    const list = await api("/prescriptions");
    document.getElementById("rx-list").innerHTML = list.length
      ? "<table>" + list.map(r => `<tr><td>${esc(r.patient_name)}</td><td>${esc(r.medicine_name)} ${esc(r.dosage || "")}</td>
          <td><span class="tag ${r.status === "dispensed" ? "green" : "orange"}">${esc(r.status)}</span></td></tr>`).join("") + "</table>"
      : '<p class="muted">None yet.</p>';
  } catch (e) { handleError(e); }
}

document.getElementById("search").addEventListener("input", loadPatients);

if (user) { loadAppointments(); loadPatients(); loadMedicines(); loadPrescriptions(); }
