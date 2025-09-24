require("dotenv/config");

const URL = "https://gw.mezon.ai/v2/apps/authenticate/token";
const TOKEN = process.env.MEZON_BOT_TOKEN;
if (!TOKEN) {
    console.error("Thiếu MEZON_BOT_TOKEN trong .env");
    process.exit(1);
}

async function hit(name, headerValue) {
    const r = await fetch(URL, {
        method: "POST",
        headers: {Authorization: headerValue},
    });
    const text = await r.text();
    console.log(`\n=== ${name} ===`);
    console.log("status =", r.status);
    console.log("body   =", text);
}

(async () => {
    await hit("Authorization: Bot <token>", `Bot ${TOKEN}`);
    await hit("Authorization: Bearer <token>", `Bearer ${TOKEN}`);
})();
