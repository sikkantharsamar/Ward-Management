const user = requireRole(["patient"]);

async function loadProfile() {
  try {
    const p = await api("/patients/me");
    const adm = p.current_admission;
    document.getElementById("profile").innerHTML = `
      <b>${esc(p.full_name)}</b> <span class="muted">${esc(p.patient_no)}</span><br>
      DOB: ${esc(p.date_of_birth || "-")} | Phone: ${esc(p.phone || "-")}<br>
      Allergies: ${esc(p.allergies || "none recorded")}<br>
      Admission: ${adm ? esc(adm.building_name + " / " + adm.ward_name + " / Bed " + adm.bed_number) : "not admitted"}`;
    const card = document.getElementById("call-card");
    if (adm) {
      card.style.display = "block";
      document.getElementById("call-info").textContent = "Your nurses are alerted immediately. You are in " + adm.ward_name + ", bed " + adm.bed_number + ".";
    }
  } catch (e) { handleError(e); }
}

document.getElementById("call-btn").addEventListener("click", async () => {
  try { await api("/alerts/patient", "POST"); toast("Nurses have been alerted. Help is coming."); } catch (e) { handleError(e); }
});

async function loadDoctors() {
  try {
    const doctors = await api("/doctors");
    document.getElementById("appt-doctor").innerHTML = doctors.map(d => option(d.id, d.full_name + (d.specialization ? " - " + d.specialization : ""))).join("");
  } catch (e) { handleError(e); }
}

document.getElementById("appt-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const d = formData(e.target);
  d.doctor_id = +d.doctor_id;
  try { await api("/appointments", "POST", d); toast("Appointment booked"); e.target.reset(); loadAppointments(); } catch (err) { handleError(err); }
});

async function loadAppointments() {
  try {
    const list = await api("/appointments");
    document.getElementById("appointments").innerHTML = list.length
      ? "<table>" + list.map(a => `<tr><td>${fmt(a.scheduled_at, false)}</td><td>${esc(a.doctor_name)}</td>
          <td><span class="tag ${a.status === "scheduled" ? "blue" : a.status === "completed" ? "green" : "grey"}">${esc(a.status)}</span></td>
          <td>${a.status === "scheduled" ? `<button class="small red" onclick="cancelAppt(${a.id})">Cancel</button>` : ""}</td></tr>`).join("") + "</table>"
      : '<p class="muted">No appointments.</p>';
  } catch (e) { handleError(e); }
}

async function cancelAppt(id) {
  try { await api("/appointments/" + id + "/status", "PATCH", { status: "cancelled" }); loadAppointments(); } catch (e) { handleError(e); }
}

async function loadPrescriptions() {
  try {
    const list = await api("/prescriptions");
    document.getElementById("prescriptions").innerHTML = list.length
      ? "<table>" + list.map(r => `<tr><td>${esc(r.medicine_name)}<br><span class="muted">${esc([r.dosage, r.frequency, r.duration].filter(Boolean).join(", "))}</span></td>
          <td><span class="tag ${r.status === "dispensed" ? "green" : "orange"}">${esc(r.status)}</span></td></tr>`).join("") + "</table>"
      : '<p class="muted">No prescriptions.</p>';
  } catch (e) { handleError(e); }
}

if (user) { loadProfile(); loadDoctors(); loadAppointments(); loadPrescriptions(); }
