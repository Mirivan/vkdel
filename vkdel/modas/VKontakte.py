import os, re, requests, time

from PIL import Image

from vkbottle.bot import Bot, Message

from config import TG_CHAT, VK_CHAT
from environment import TGS, VKT

bot = Bot(token=VKT) # <- Setting up vkontakte via token

me = requests.get(
    "https://api.vk.com/method/groups.getById?" \
    f"access_token={VKT}&v=5.131"
).json()
me = int(f"-{me['response'][0]['id']}")
# ^- Setting up bot information here

nameval = {"vk": 0}

TG_CHAT = int(f"-100{TG_CHAT}")

# https://vkbottle.readthedocs.io/ru/latest/tutorial/first-bot/
@bot.on.message(
    func=lambda a: a.peer_id==VK_CHAT and not str(a.from_id).startswith("-")
) # <- Using vk wrapper
async def handler(message: Message):
    from .Telegram import bot as tgbot
    sender = (await bot.api.users.get(message.from_id))[0]

    if sender.id != nameval["vk"]:
        name = "👤 " + (sender.first_name + " " + sender.last_name if sender.last_name else sender.first_name) + "\n"
        nameval["vk"] = sender.id
    else:
        name = ""

    replied = message.reply_message

    if replied:
        reply = await get_replied_text(replied)
    else:
        reply = ""

    timestamp = int(time.time() * 2)

    attachments = message.attachments
    if attachments:
        # Photo...
        # - - - - - - - - - - - - - - - 
        if attachments[0].photo:
            content = requests.get(f"{get_max_size(attachments[0].photo.sizes)}").content
            open(f"./downloads/photo_{timestamp}.jpg", "+wb").write(content)
            if name:
                await tgbot.send_message(
                    TG_CHAT,
                    f"{name}"
                )
            await tgbot.send_file(
                TG_CHAT,
                f"./downloads/photo_{timestamp}.jpg",
                caption=f"{message.text if message.text else ''}{reply}", 
            )
            os.remove(f"./downloads/photo_{timestamp}.jpg")
        # Voice message...
        # - - - - - - - - - - - - - - - 
        if attachments[0].audio_message:
            content = requests.get(f"{attachments[0].audio_message.link_ogg}").content
            open(f"./downloads/voice_{timestamp}.ogg", "+wb").write(content)
            if name:
                await tgbot.send_message(
                    TG_CHAT,
                    f"{name}"
                )
            await tgbot.send_file(
                TG_CHAT,
                f"./downloads/voice_{timestamp}.ogg",
                caption=f"{reply}",
                voice_note=True
            )
            os.remove(f"./downloads/voice_{timestamp}.ogg")
            return
        # Sticker...
        # - - - - - - - - - - - - - - - 
        if attachments[0].sticker:
            if attachments[0].sticker.animation_url:
                content = requests.get(f"{attachments[0].sticker.animation_url}").content
                open(f"./downloads/animated_sticker_{timestamp}.json", "+wb").write(content)
                os.system(f"lottie_convert.py ./downloads/animated_sticker_{timestamp}.json ./downloads/animated_sticker_{timestamp}.tgs")
                if name:
                    await tgbot.send_message(
                        TG_CHAT,
                        f"{name}"
                    )
                x = await tgbot.send_file(
                    TG_CHAT,
                    f"./downloads/animated_sticker_{timestamp}.tgs",
                    caption=f"{reply}"
                )
                if "x-bad-tgsticker" in x.media.document.mime_type:
                    await x.edit("**Телеграм не удалось отрисовать стикер.**" + reply)
                os.remove(f"./downloads/animated_sticker_{timestamp}.json")
                os.remove(f"./downloads/animated_sticker_{timestamp}.tgs")
                return
            content = requests.get(f"{attachments[0].sticker.images[4].url}").content
            open(f"./downloads/sticker_{timestamp}.png", "+wb").write(content)
            im = Image.open(f"./downloads/sticker_{timestamp}.png").convert("RGBA")
            im.save(f"./downloads/sticker_{timestamp}.webp","WEBP")
            if name:
                await tgbot.send_message(
                    TG_CHAT,
                    f"{name}"
                )
            await tgbot.send_file(
                TG_CHAT,
                f"./downloads/sticker_{timestamp}.webp",
                caption=f"{reply}"
            )
            os.remove(f"./downloads/sticker_{timestamp}.png")
            os.remove(f"./downloads/sticker_{timestamp}.webp")
            return
        if attachments[0].graffiti:
            content = requests.get(f"{attachments[0].graffiti.url}").content
            open(f"./downloads/graffiti_{timestamp}.png", "+wb").write(content)
            im = Image.open(f"./downloads/graffiti_{timestamp}.png").convert("RGBA")
            im.save(f"./downloads/graffiti_{timestamp}.webp","WEBP")
            if name:
                await tgbot.send_message(
                    TG_CHAT,
                    f"{name}"
                )
            await tgbot.send_file(
                TG_CHAT,
                f"./downloads/graffiti_{timestamp}.webp",
                caption=f"{reply}"
            )
            os.remove(f"./downloads/graffiti_{timestamp}.png")
            os.remove(f"./downloads/graffiti_{timestamp}.webp")
            return

    # Text (Default)...
    # - - - - - - - - - - - - - - - 
    if not message.text:
        return
    await tgbot.send_message(
        TG_CHAT,
        f"{name}" \
        f"{message.text}{reply}"
   )

def get_max_size(sizes: list):
    if getattr(sizes[0], "type", None):
        size_values = list("opqrsmxklyzcwid")
        max_size = sorted(sizes, key=lambda x: size_values.index(x.type.value))[-1]
    else:
        max_size = sorted(sizes, key=lambda x: x.width + x.height)[-1]
    return getattr(max_size, "url", None) or getattr(max_size, "src", None)

async def get_replied_text(message):
    attachments = message.attachments
    if attachments:
        if attachments[0].photo:
            text = "🖼️ Фото"
        elif attachments[0].sticker or attachments[0].graffiti:
            text = "Стикер"
        elif attachments[0].audio_message:
            text = "🔊 Голосовое сообщение"
        else:
            text = "📎 Прикреплённое медиа"
    else:
        text = ""
    if message.text:
        unname = re.match("👤 +(.*)\\n(.*)", message.text)
        unname = unname.group(2) if message.from_id == me and unname and unname.group(2) else message.text
        text = "\n➥ " + (text + ", " if text else "") + (f"{unname[:27]}..." if len(unname) > 27 else unname)
    else:
        text = ("\n➥ " + text) if text else ""
    return text
