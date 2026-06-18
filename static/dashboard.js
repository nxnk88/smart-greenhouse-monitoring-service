const grid = document.querySelector("#greenhouse-grid");
const filters = document.querySelectorAll(".filter");
let greenhouses = [];

const formatValue = (value, suffix) => `${value}${suffix}`;

function greenhouseCard(item) {
  const statusLabel = item.status === "optimal" ? "В норме" : "Внимание";
  const irrigation = item.irrigation_enabled ? "вкл." : "выкл.";

  return `
    <article class="greenhouse-card" data-status="${item.status}">
      <div class="card-top">
        <div>
          <h3>${item.name}</h3>
          <p>${item.zone} · ${item.crop}</p>
        </div>
        <span class="status ${item.status}">${statusLabel}</span>
      </div>
      <div class="sensor-row">
        <div class="sensor"><span>Температура</span><strong>${formatValue(item.temperature_c, "°")}</strong></div>
        <div class="sensor"><span>Влажность</span><strong>${formatValue(item.humidity_pct, "%")}</strong></div>
        <div class="sensor"><span>Почва</span><strong>${formatValue(item.soil_moisture_pct, "%")}</strong></div>
        <div class="sensor"><span>Полив</span><strong>${irrigation}</strong></div>
      </div>
    </article>`;
}

function render(filter = "all") {
  const visible = filter === "all"
    ? greenhouses
    : greenhouses.filter((item) => item.status === filter);

  grid.innerHTML = visible.length
    ? visible.map(greenhouseCard).join("")
    : '<p class="loading">Для выбранного фильтра объектов нет.</p>';
}

async function loadDashboard() {
  try {
    const [summaryResponse, greenhousesResponse] = await Promise.all([
      fetch("/summary"),
      fetch("/greenhouses"),
    ]);

    if (!summaryResponse.ok || !greenhousesResponse.ok) {
      throw new Error("API returned an error");
    }

    const summary = await summaryResponse.json();
    const greenhousePayload = await greenhousesResponse.json();
    greenhouses = greenhousePayload.greenhouses;

    document.querySelector("#total-greenhouses").textContent = summary.total_greenhouses;
    document.querySelector("#optimal-greenhouses").textContent = summary.optimal_greenhouses;
    document.querySelector("#attention-required").textContent = summary.attention_required;
    document.querySelector("#average-temperature").textContent = summary.average_temperature_c;
    document.querySelector("#average-humidity").textContent = summary.average_humidity_pct;
    render();
  } catch (error) {
    grid.innerHTML = '<p class="error-message">Не удалось получить телеметрию. Проверьте состояние API.</p>';
    document.querySelector(".live-indicator").lastChild.textContent = " API недоступен";
  }
}

filters.forEach((button) => {
  button.addEventListener("click", () => {
    filters.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    render(button.dataset.filter);
  });
});

loadDashboard();

