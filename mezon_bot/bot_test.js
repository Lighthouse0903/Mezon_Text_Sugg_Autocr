require("dotenv/config");
const {
    MezonClient,
    EButtonMessageStyle,
    EMessageComponentType,
} = require("mezon-sdk");

const BOT_TOKEN = process.env.MEZON_BOT_TOKEN;
const CHANNEL_ID = process.env.MEZON_CHANNEL_ID;

(async () => {
    const client = new MezonClient();

    client.on("ready", async () => {
        console.log("Bot is ready!");

        try {
            const channel = await client.channels.fetch(CHANNEL_ID);
            if (!channel) {
                console.error("Không tìm thấy channel");
                return;
            }

            await channel.send({
                t: "Bấm nút bên dưới để mở webview",
                components: [
                    {
                        components: [
                            {
                                type: EMessageComponentType.BUTTON,
                                id: "btn_open_webview",
                                component: {
                                    label: "Mở Webview",
                                    style: EButtonMessageStyle.LINK,
                                    url: "https://unthrobbing-tosha-nonruminatingly.ngrok-free.dev/ui/typeahead.html",
                                },
                            },
                        ],
                    },
                ],
            });

            console.log("Đã gửi interactive message");
        } catch (err) {
            console.error("Lỗi gửi:", err);
        }
    });

    client.token = BOT_TOKEN;
    await client.login();
})();
