require("dotenv/config");
const {MezonClient} = require("mezon-sdk");

process.on("unhandledRejection", (e) => {
    console.error("UNHANDLED REJECTION:", e?.stack || e);
});
process.on("uncaughtException", (e) => {
    console.error("UNCAUGHT EXCEPTION:", e?.stack || e);
});

function logSendCapabilities(client) {
    const caps = {
        "client.channels?.send": !!(
            client.channels && typeof client.channels.send === "function"
        ),
        "client.channels?.fetch": !!(
            client.channels && typeof client.channels.fetch === "function"
        ),
        "client.sendMessage": typeof client.sendMessage === "function",
        "client.messages?.create": !!(
            client.messages && typeof client.messages.create === "function"
        ),
        "client.api?.post": !!(
            client.api && typeof client.api.post === "function"
        ),
        "client.rest?.post": !!(
            client.rest && typeof client.rest.post === "function"
        ),
        "client.request": typeof client.request === "function",
    };
    console.log("[mezon-sdk send capabilities]", caps);
}

async function sendMessage(client, channelId, payload) {
    if (client.channels && typeof client.channels.send === "function") {
        return client.channels.send(channelId, payload);
    }
    if (client.channels && typeof client.channels.fetch === "function") {
        const ch = await client.channels.fetch(channelId).catch(() => null);
        if (ch && typeof ch.send === "function") return ch.send(payload);
    }
    if (typeof client.sendMessage === "function") {
        return client.sendMessage(channelId, payload);
    }
    if (client.messages && typeof client.messages.create === "function") {
        return client.messages.create(channelId, payload);
    }
    if (client.api && typeof client.api.post === "function") {
        try {
            return await client.api.post(
                `/channels/${channelId}/messages`,
                payload
            );
        } catch {
            return client.api.post(`/channels/${channelId}/messages`, {
                content: payload,
            });
        }
    }
    if (client.rest && typeof client.rest.post === "function") {
        try {
            return await client.rest.post(`/channels/${channelId}/messages`, {
                body: payload,
            });
        } catch {
            return client.rest.post(`/channels/${channelId}/messages`, {
                body: {content: payload},
            });
        }
    }
    if (typeof client.request === "function") {
        try {
            return await client.request({
                method: "POST",
                path: `/channels/${channelId}/messages`,
                body: payload,
            });
        } catch {
            return client.request({
                method: "POST",
                path: `/channels/${channelId}/messages`,
                body: {content: payload},
            });
        }
    }
    throw new Error("No message-sending method found on mezon-sdk client");
}

async function sendWithWebview(client, channelId, text, url) {
    const attType = {type: "webview", title: "Typeahead", url, size: "tall"};
    const attKind = {kind: "webview", title: "Typeahead", url, size: "tall"};

    try {
        await sendMessage(client, channelId, {t: text, attachments: [attType]});
        return;
    } catch (e) {
        console.warn("shape A failed:", e?.message || e);
    }

    try {
        await sendMessage(client, channelId, {
            content: {t: text, attachments: [attType]},
        });
        return;
    } catch (e) {
        console.warn("shape B failed:", e?.message || e);
    }

    try {
        await sendMessage(client, channelId, {t: text, attachments: [attKind]});
        return;
    } catch (e) {
        console.warn("shape C failed:", e?.message || e);
    }

    try {
        await sendMessage(client, channelId, {
            content: {t: text, attachments: [attKind]},
        });
        return;
    } catch (e) {
        console.warn("shape D failed:", e?.message || e);
    }

    await sendMessage(client, channelId, {
        t: text + " (không mở được panel webview)",
    });
}

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
        const token = process.env.MEZON_BOT_TOKEN;
        if (!token) {
            console.error("MEZON_BOT_TOKEN is empty! Check your .env");
            return;
        }
        client.token = token;

        await client.login();
        logSendCapabilities(client);
        const TEST_CH = process.env.MEZON_CHANNEL_ID;
        const BASE = process.env.SUGGEST_API_BASE || "http://localhost:8000";
        const url = `${BASE}/ui/typeahead.html?embed=1`;
        if (TEST_CH) {
            console.log(
                "[self-test] trying to send a webview card to",
                TEST_CH
            );
            await sendWithWebview(
                client,
                TEST_CH,
                "Gợi ý nhập nhanh (mở panel bên dưới):",
                url
            ).catch((e) =>
                console.warn(
                    "[self-test] webview send failed:",
                    e?.message || e
                )
            );
        }

        const MY_BOT_ID = process.env.MEZON_BOT_ID || "";
        client.onChannelMessage(async (e) => {
            try {
                if (MY_BOT_ID && e.sender_id === MY_BOT_ID) return;
                const text = e.content?.t ?? "";
                if (!text.trim()) return;

                const {context, prefix} = splitContextPrefix(text);
                const lead = "Gợi ý nhập nhanh (mở panel bên dưới):";

                const ui = `${BASE}/ui/typeahead.html?embed=1&q=${encodeURIComponent(
                    text
                )}`;
                await sendWithWebview(client, e.channel_id, lead, ui);
            } catch (err) {
                console.error(
                    "onChannelMessage error:",
                    err?.stack || err?.message || err
                );
            }
        });
        setInterval(() => {}, 1 << 30);
    } catch (err) {
        const resp = err?.response;
        if (resp && typeof resp.text === "function") {
            console.error("Login failed:", resp.status, await resp.text());
        } else {
            console.error("Login failed:", err?.stack || err?.message || err);
        }
    }
})();
