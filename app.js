const URL =
  "https://raw.githubusercontent.com/Wuao8/Olimpia-Crypto/main/signals.json";

const MAX_AGE_HOURS = 24;

function isRecent(timeStr) {
  const t = new Date(timeStr).getTime();
  const now = Date.now();
  return now - t < MAX_AGE_HOURS * 60 * 60 * 1000;
}

async function loadSignals() {
  try {
    const res = await fetch(URL + "?t=" + Date.now());
    const data = await res.json();

    const feed = document.getElementById("feed");

    if (!Array.isArray(data)) return;

    // 🔥 filtro ultime 24h
    const filtered = data.filter(sig => sig.time && isRecent(sig.time));

    // ordina dal più recente
    filtered.sort((a, b) => new Date(b.time) - new Date(a.time));

    feed.innerHTML = "";

    filtered.forEach(sig => {
      const div = document.createElement("div");

      const cls = sig.side === "LONG" ? "long" : "short";

      div.className = "line " + cls;

      div.innerHTML = `
        <span>[${sig.time}]</span>
        <b>${sig.side}</b>
        <span>${sig.symbol}</span>
        <span>MACD: ${Number(sig.value).toFixed(6)}</span>
      `;

      feed.appendChild(div);
    });

  } catch (e) {
    console.log("feed error", e);
  }
}

loadSignals();
setInterval(loadSignals, 10000);
