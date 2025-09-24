require("dotenv/config");
const {MezonClient} = require("mezon-sdk");

const MY_BOT_ID = process.env.MEZON_BOT_ID || "";

function splitContextPrefix(text) {
    const t = (text || "").trim();
    if (!t) return {context: "", prefix: ""};
    const parts = t.split(/\s+/);
    const prefix = parts.pop() || "";
    const context = parts.join(" ");
    return {context, prefix};
}

async function getSuggest(context, prefix, k = 5) {
    const base = process.env.SUGGEST_API_BASE || "http://localhost:8000";
    const apikey = process.env.SUGGEST_API_KEY || "";
    const qs = new URLSearchParams({
        context,
        ...(prefix ? {prefix} : {}),
        k: String(k),
    });
    const r = await fetch(`${base}/v1/suggest?${qs}`, {
        headers: apikey ? {"x-api-key": apikey} : {},
    });
    if (!r.ok) throw new Error(`Suggest API ${r.status}: ${await r.text()}`);
    const {candidates = []} = await r.json();
    return candidates;
}

(async () => {
    const client = new MezonClient();
    client.on("ready", () => console.log("Bot is ready!"));
    client.on("error", (e) => console.error("SDK Error:", e?.message || e));

    try {
        client.token = process.env.MEZON_BOT_TOKEN;
        await client.login();

        client.onChannelMessage(async (e) => {
            console.log(
                "onChannelMessage event = :",
                JSON.stringify(e, null, 2)
            );
            try {
                if (MY_BOT_ID && e.sender_id === MY_BOT_ID) return;

                const text = e.content?.t ?? "";
                if (!text.trim()) return;
                if (text.startsWith("Suggestions: ")) return;

                const {context, prefix} = splitContextPrefix(text);
                if (!prefix /* || prefix.length < 2 */) return;

                let cands = [];
                try {
                    cands = await getSuggest(context, prefix, 5);
                } catch (apiErr) {
                    console.error(
                        "getSuggest error:",
                        apiErr?.message || apiErr
                    );
                    return;
                }
                if (!cands.length) return;

                const payload = {t: `Suggestions: ${cands.join(", ")}`};

                if (typeof client.channels?.send === "function") {
                    await client.channels.send(e.channel_id, payload);
                    return;
                }

                const channel = await client.channels?.fetch?.(e.channel_id);
                if (!channel) {
                    console.warn("Channel not found:", e.channel_id);
                    return;
                }
                await channel.send(payload);
            } catch (err) {
                console.error(
                    "onChannelMessage error:",
                    err?.stack || err?.message || err
                );
            }
        });
    } catch (err) {
        const resp = err?.response;
        if (resp && typeof resp.text === "function") {
            console.error("Login failed:", resp.status, await resp.text());
        } else {
            console.error("Login failed:", err?.message || err);
        }
        process.exit(1);
    }
})();
