const user = requireRole(["nurse", "admin", "doctor"]);
let audioCtx = null;
let ws = null;
let currentWard = null;

function beep() {
  if (!audioCtx) return;
  for (let i = 0; i < 3; i++) {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain); gain.connect(audioCtx.destination);
    osc.frequency.value = 880; gain.gain.value = 0.2;
    osc.start(audioCtx.currentTime + i * 0.4);
    osc.stop(audioCtx.currentTime + i * 0.4 + 0.25);
  }
}

document.getElementById("sound-btn").addEventListener("click", () => {
  audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
  beep();
  document.getElementById("sound-btn").style.display = "none";
});

function setConn(text, ok) {
  const el = document.getElementById("conn");
  el.textContent = text;
  el.style.background = ok ? "#2E8B57" : "#C0392B";
}

function connectSocket() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(proto + "://" + location.host + "/api/alerts/ws?token=" + getToken());
  ws.onopen = () => setConn("live", true);
  ws.onmessage = (msg) => {
    const data = JSON.parse(msg.data);
    if (data.event === "alert_created" || data.event === "alert_repeat") beep();
    loadAlerts();
    loadBeds();
  };
  ws.onclose = () => { setConn("disconnected - retrying", false); setTimeout(connectSocket, 3000); };
}

async function loadAlerts() {
  try {
    const alerts = await api("/alerts?status=open");
    const box = document.getElementById("alerts");
    const alertCount = document.getElementById("stat-alerts");
    if (alertCount) alertCount.textContent = alerts.length;
    const alertPanel = box.closest(".alert-panel");
    if (!alerts.length) {
      box.innerHTML = '<p class="muted">No active alerts. Continue routine safety checks.</p>';
      if (alertPanel) alertPanel.classList.add("empty");
      return;
    }
    if (alertPanel) alertPanel.classList.remove("empty");
    box.innerHTML = alerts.map(a => `
      <div class="alert-card ${a.status === "active" ? "flash" : "acknowledged"}">
        <b>${esc(a.building_name)} / ${esc(a.ward_name)} / Bed ${esc(a.bed_number)}</b>
        <span class="tag ${a.status === "active" ? "red" : "orange"}">${esc(a.status)}</span>
        <span class="tag blue">${esc(a.source)}</span><br>
        Patient: <b>${esc(a.patient_name || "unknown")}</b>
        ${a.isolation_status ? '<span class="tag red">ISOLATION</span>' : ""}
        ${a.allergies ? " | Allergies: " + esc(a.allergies) : ""}
        ${a.medical_condition ? " | Condition: " + esc(a.medical_condition) : ""}
        ${a.special_needs ? "<br>Special needs: " + esc(a.special_needs) : ""}
        <br><span class="muted">Raised ${fmt(a.created_at)}</span><br>
        <span class="row" style="margin-top:6px">
          ${a.status === "active" ? `<button class="orange small" onclick="ack(${a.id})">Acknowledge</button>` : ""}
          <button class="green small" onclick="resolveAlert(${a.id})">Resolve</button>
        </span>
      </div>`).join("");
  } catch (e) { handleError(e); }
}

async function ack(id) { try { await api("/alerts/" + id + "/acknowledge", "POST"); loadAlerts(); loadBeds(); } catch (e) { handleError(e); } }
async function resolveAlert(id) {
  const notes = prompt("Notes (optional):") || null;
  try { await api("/alerts/" + id + "/resolve", "POST", { notes }); loadAlerts(); loadBeds(); } catch (e) { handleError(e); }
}

async function loadWards() {
  const wards = await api("/wards");
  const select = document.getElementById("ward-select");
  select.innerHTML = wards.map(w => option(w.id, w.building_name + " - " + w.name)).join("");
  if (wards.length) { currentWard = wards[0].id; }
  select.onchange = () => { currentWard = select.value; loadBeds(); };
  loadBeds();
}

async function loadBeds() {
  if (!currentWard) return;
  try {
    const beds = await api("/wards/" + currentWard + "/beds");
    const occupied = beds.filter(b => b.status === "occupied").length;
    const available = beds.filter(b => b.status === "available").length;
    const patients = beds.filter(b => b.patient_name).length;
    const occupiedCount = document.getElementById("stat-occupied");
    const availableCount = document.getElementById("stat-available");
    const patientCount = document.getElementById("stat-patients");
    if (occupiedCount) occupiedCount.textContent = occupied;
    if (availableCount) availableCount.textContent = available;
    if (patientCount) patientCount.textContent = patients;
    document.getElementById("beds").innerHTML = beds.map(b => {
      let cls = b.status;
      if (b.alert_status === "active") cls = "alert-active";
      else if (b.alert_status === "acknowledged") cls = "alert-acknowledged";
      return `<div class="bed ${cls}"><b>${esc(b.bed_number)}</b><br>${esc(b.patient_name || b.status)}
        ${b.isolation_status ? "<br>ISOLATION" : ""}
        ${b.admission_id ? `<br><button class="small grey" onclick="discharge(${b.admission_id})">Discharge</button>` : ""}</div>`;
    }).join("");
    const free = beds.filter(b => b.status === "available");
    document.getElementById("admit-bed").innerHTML = free.map(b => option(b.id, "Bed " + b.bed_number)).join("");
  } catch (e) { handleError(e); }
}

async function discharge(admissionId) {
  if (!confirm("Discharge this patient?")) return;
  try { await api("/admissions/" + admissionId + "/discharge", "POST"); toast("Discharged"); loadBeds(); } catch (e) { handleError(e); }
}

document.getElementById("admit-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const d = formData(e.target);
  const body = { patient_id: +d.patient_id, bed_id: +d.bed_id, doctor_id: d.doctor_id ? +d.doctor_id : null, diagnosis: d.diagnosis };
  try { await api("/admissions", "POST", body); toast("Patient admitted"); loadBeds(); } catch (err) { handleError(err); }
});

async function loadLists() {
  try {
    const patients = await api("/patients");
    document.getElementById("admit-patient").innerHTML = patients.map(p => option(p.id, p.full_name + " (" + p.patient_no + ")")).join("");
    const doctors = await api("/doctors");
    document.getElementById("admit-doctor").innerHTML = option("", "-- none --") + doctors.map(d => option(d.id, d.full_name)).join("");
    const low = await api("/inventory/low-stock");
    document.getElementById("low-stock").innerHTML = low.length
      ? "<table>" + low.map(i => `<tr><td>${esc(i.name)}</td><td><span class="tag red">${i.quantity} left</span></td></tr>`).join("") + "</table>"
      : '<p class="muted">Nothing is low.</p>';
    loadPrescriptions();
  } catch (e) { handleError(e); }
}

async function loadPrescriptions() {
  const rx = await api("/prescriptions?status=issued");
  document.getElementById("rx-list").innerHTML = rx.length
    ? "<table>" + rx.map(r => `<tr><td>${esc(r.patient_name)}<br><span class="muted">${esc(r.medicine_name)} ${esc(r.dosage || "")}</span></td>
        <td><button class="small green" onclick="dispense(${r.id})">Dispense</button></td></tr>`).join("") + "</table>"
    : '<p class="muted">No pending prescriptions.</p>';
}

async function dispense(id) {
  try { await api("/prescriptions/" + id + "/dispense", "POST", { quantity: 1 }); toast("Dispensed"); loadLists(); } catch (e) { handleError(e); }
}

if (user) {
  loadAlerts(); loadWards(); loadLists(); connectSocket();
  // Safety net: poll every 10 s in case the live connection silently drops.
  setInterval(() => { loadAlerts(); loadBeds(); }, 10000);
}
