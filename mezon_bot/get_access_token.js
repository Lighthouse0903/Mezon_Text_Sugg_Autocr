require("dotenv/config");

const CLIENT_ID = process.env.MEZON_CLIENT_ID;
const CLIENT_SECRET = process.env.MEZON_CLIENT_SECRET;

const URL = "https://gw.mezon.ai/v2/apps/authenticate/token";

(async () => {
    const res = await fetch(URL, {
        method: "POST",
        headers: {"content-type": "application/json"},
        body: JSON.stringify({
            client_id: CLIENT_ID,
            client_secret: CLIENT_SECRET,
        }),
    });

    const text = await res.text();
    let data;
    try {
        data = JSON.parse(text);
    } catch {}

    console.log("Status:", res.status);
    console.log("Body  :", data ?? text);

    if (res.ok && data?.access_token) {
        console.log("\nACCESS TOKEN:", data.access_token);
    }
})();
