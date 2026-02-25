/**
 * WebNesk – main.js
 * Kleine Hilfsfunktionen für die Frontend-UI
 */

// ---------------------------------------------------------------
// Echtzeit-Uhr im Footer
// ---------------------------------------------------------------
function updateClock() {
  const el = document.getElementById("clock");
  if (!el) return;
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  el.textContent =
    `${pad(now.getDate())}.${pad(now.getMonth() + 1)}.${now.getFullYear()} ` +
    `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
}

updateClock();
setInterval(updateClock, 1000);

// ---------------------------------------------------------------
// Auto-Dismiss für Flash-Meldungen nach 5 Sekunden
// ---------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".alert.alert-success, .alert.alert-info").forEach((alert) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });
});

// ---------------------------------------------------------------
// Bestätigungsdialog für Lösch-Formulare (als Fallback)
// ---------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      if (!confirm(form.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });
});
