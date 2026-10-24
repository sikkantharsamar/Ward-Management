const user = requireRole(["admin", "nurse", "doctor"]);
const canManage = user && (user.role === "admin" || user.role === "nurse");

async function loadItems() {
  try {
    const items = await api("/inventory?category=" + document.getElementById("filter").value);
    document.getElementById("items").innerHTML =
      "<table><tr><th>Item</th><th>Category</th><th>Quantity</th><th>Reorder at</th><th>Expiry</th><th></th></tr>" +
      items.map(i => `<tr><td>${esc(i.name)}</td><td>${esc(i.category)}</td>
        <td>${i.quantity} ${esc(i.unit)}</td><td>${i.reorder_level}</td><td>${esc(i.expiry_date || "-")}</td>
        <td>${i.is_low ? '<span class="tag red">LOW</span>' : '<span class="tag green">OK</span>'}</td></tr>`).join("") + "</table>";
    document.getElementById("adjust-item").innerHTML = items.map(i => option(i.id, i.name)).join("");
  } catch (e) { handleError(e); }
}

document.getElementById("filter").addEventListener("change", loadItems);

document.getElementById("add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const d = formData(e.target);
  d.quantity = +d.quantity; d.reorder_level = +d.reorder_level;
  try { await api("/inventory", "POST", d); toast("Item added"); e.target.reset(); loadItems(); } catch (err) { handleError(err); }
});

document.getElementById("adjust-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const d = formData(e.target);
  try {
    await api("/inventory/" + d.item_id + "/adjust", "POST", { change: +d.change, reason: d.reason });
    toast("Stock updated"); e.target.reset(); loadItems();
  } catch (err) { handleError(err); }
});

if (user) {
  if (canManage) document.getElementById("manage").style.display = "grid";
  loadItems();
}
