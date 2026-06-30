const URL =
  "https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/signals.json";

async function loadSignals() {
  try {
    const res = await fetch(URL + "?t=" + Date.now());
    const data = await res.json();

    const feed = document.getElementById("feed");

    if (!Array.isArray(data)) return;

    feed.innerHTML = "";

    data.slice().reverse().forEach(sig => {
      const div = document.createElement("div");

      const cls = sig.side === "LONG" ? "long" : "short";

      div.className = "line " + cls;

      div.innerHTML = `
        <span>[${sig.time}]</span>
        <b>${sig.side}</b>
        <span>${sig.symbol}</span>
        <span>MACD: ${sig.value.toFixed(6)}</span>
      `;

      feed.appendChild(div);
    });

  } catch (e) {
    console.log("feed error", e);
  }
}

loadSignals();
setInterval(loadSignals, 8000);
