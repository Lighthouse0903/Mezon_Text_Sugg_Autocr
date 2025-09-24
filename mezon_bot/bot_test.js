const BASE = "http://localhost:8000";
const API_KEY = "dev-key-123";

(async () => {
    const params = new URLSearchParams({
        context: "Món ăn này được làm",
        prefix: "nh",
        k: "5",
    });

    const r = await fetch(`${BASE}/v1/suggest?${params}`, {
        headers: {"x-api-key": API_KEY},
    });

    if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
    const {candidates} = await r.json();
    console.log("Candidates:", candidates);
})();
