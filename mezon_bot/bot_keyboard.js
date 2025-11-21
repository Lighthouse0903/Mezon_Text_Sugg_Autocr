require("dotenv").config();
const {
    MezonClient,
    EMessageComponentType,
    EMessageActionType,
} = require("mezon-sdk");

const client = new MezonClient({
    app_id: process.env.APP_ID,
    app_secret: process.env.APP_SECRET,
});

let userInputs = {};

function buildKeyboard(currentText = "") {
    const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
    const rows = [];

    for (let i = 0; i < alphabet.length; i += 7) {
        rows.push(
            alphabet.slice(i, i + 7).map((ch) => ({
                type: EMessageComponentType.BUTTON,
                title: ch,
                action: {type: EMessageActionType.REPLY, value: ch},
            }))
        );
    }

    rows.push([
        {
            type: EMessageComponentType.BUTTON,
            title: "Space",
            action: {type: EMessageActionType.REPLY, value: " "},
        },
        {
            type: EMessageComponentType.BUTTON,
            title: "Delete",
            action: {type: EMessageActionType.REPLY, value: "DELETE"},
        },
        {
            type: EMessageComponentType.BUTTON,
            title: "Enter",
            action: {type: EMessageActionType.REPLY, value: "ENTER"},
        },
    ]);

    return {
        type: "MESSAGE",
        payload: {
            content: `Nhập: ${currentText}`,
            components: rows.map((row) => ({
                type: EMessageComponentType.GRID,
                items: row,
            })),
        },
    };
}

client.on("message", async (msg) => {
    console.log("Sự kiện message:", JSON.stringify(msg, null, 2));

    const text =
        (msg.content && msg.content.text) ||
        (msg.payload && msg.payload.content) ||
        msg.content ||
        "";

    if (text.toLowerCase() === "keyboard") {
        userInputs[msg.from] = "";
        await client.sendMessage(msg.from, buildKeyboard(userInputs[msg.from]));
    } else {
        await client.sendMessage(msg.from, {
            type: "MESSAGE",
            payload: {content: `Bot echo: ${text}`},
        });
    }
});

client.on("action", async (action) => {
    console.log("Sự kiện action:", JSON.stringify(action, null, 2));

    const {from, value} = action;
    if (!(from in userInputs)) userInputs[from] = "";

    if (value === "DELETE") {
        userInputs[from] = userInputs[from].slice(0, -1);
    } else if (value === "ENTER") {
        await client.sendMessage(from, {
            type: "MESSAGE",
            payload: {content: `Bạn đã nhập: ${userInputs[from]}`},
        });
        userInputs[from] = "";
    } else {
        userInputs[from] += value;
    }

    await client.sendMessage(from, buildKeyboard(userInputs[from]));
});

console.log("Bot khởi động (auto-connect MezonClient)");
