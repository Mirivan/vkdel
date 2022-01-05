import os, re, time

from PIL import Image

from telethon import events, TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import DocumentAttributeFilename, MessageMediaWebPage, PeerChannel

from vkbottle.tools import PhotoMessageUploader, VoiceMessageUploader

from config import API_ID, API_HASH, TG_CHAT, VK_CHAT
from environment import TGS, VKT

bot = TelegramClient(session=StringSession(TGS), api_id=API_ID, api_hash=API_HASH, auto_reconnect=True)
# ^- Setting up Telegram client via string session

async def me():
    global me
    me = await bot.get_me()
with bot:
    bot.loop.run_until_complete(me())
# ^- Setting up bot information here

nameval = {"tg": 0}

@bot.on(
    events.NewMessage(
        incoming=True,
        func=lambda a: a.is_group and isinstance(a.peer_id, PeerChannel) and a.peer_id.channel_id==TG_CHAT
    )
) # <- Using Telegram wrapper
async def handler(event):
    from .VKontakte import bot as vkbot
    sender = await event.get_sender()

    if sender.id != nameval["tg"]:
        name = "👤 " + (sender.first_name + " " + sender.last_name if sender.last_name else sender.first_name) + "\n"
        nameval["tg"] = sender.id
    else:
        name = ""

    replied = await event.get_reply_message()

    if replied:
        reply = await get_replied_text(replied)
    else:
        reply = ""

    timestamp = int(time.time() * 2)

    # Photo...
    # - - - - - - - - - - - - - - - 
    if event.photo:
        await event.download_media(f"{timestamp}_tgphoto.jpg")
        doc = await PhotoMessageUploader(vkbot.api).upload(
            f"{timestamp}_tgphoto.jpg"
        )
        if name:
            await vkbot.api.messages.send(
                peer_id=VK_CHAT,
                message=f"{name}",
                random_id=0
            )
        await vkbot.api.messages.send(
            peer_id=VK_CHAT,
            attachment=doc,
            text=f"{event.raw_text if event.raw_text else ''}{reply}",
            random_id=0
        )
        os.remove(f"{timestamp}_tgphoto.jpg")
        return
    # Sticker...
    # - - - - - - - - - - - - - - - 
    if event.media:
        if isinstance(event.media, MessageMediaWebPage):
            return
        if "tgsticker" in event.media.document.mime_type:
            emoji = event.media.document.attributes[1].alt
            await vkbot.api.messages.send(
                peer_id=VK_CHAT,
                message=f"{name}{emoji} Стикер{reply}",
                random_id=0
            )
        if "image" in event.media.document.mime_type.split('/'):
            if (DocumentAttributeFilename(file_name='sticker.webp') in event.media.document.attributes):
                await event.client.download_file(event.media.document, f"{timestamp}_sticker.webp")
                im = Image.open(f"{timestamp}_sticker.webp").convert("RGBA")
                im.save(f"{timestamp}_sticker.png","PNG")
                doc = await PhotoMessageUploader(vkbot.api).upload(
                    f"{timestamp}_sticker.png"
                )
                if name:
                    await vkbot.api.messages.send(
                        peer_id=VK_CHAT,
                        message=f"{name}",
                        random_id=0
                    )
                await vkbot.api.messages.send(
                    peer_id=VK_CHAT,
                    attachment=doc,
                    message=f"{reply}",
                    random_id=0
                )
                os.remove(f"{timestamp}_sticker.webp")
                os.remove(f"{timestamp}_sticker.png")
                return
    # Voice message...
    # - - - - - - - - - - - - - - - 
    if event.voice:
        await event.download_media(f"{timestamp}_tgvoice.mp3")
        doc = await VoiceMessageUploader(vkbot.api).upload(
            "voice.mp3", f"{timestamp}_tgvoice.mp3", peer_id=VK_CHAT
        )
        if name:
            await vkbot.api.messages.send(
                peer_id=VK_CHAT,
                message=f"{name}",
                random_id=0
            )
        await vkbot.api.messages.send(
            peer_id=VK_CHAT,
            attachment=doc,
            message=f"{reply}",
            random_id=0
        )
        os.remove(f"{timestamp}_tgvoice.mp3")
        return
    # Text (Default)...
    # - - - - - - - - - - - - - - - 
    if not event.text:
        return
    await vkbot.api.messages.send(
        peer_id=VK_CHAT,
        message=f"{name}{event.raw_text}{reply}",
        random_id=0
    )

async def get_replied_text(message):
    if message.photo:
        text = "🖼️ Фото"
    elif message.sticker:
        text = message.media.document.attributes[1].alt + " Стикер"
    elif message.voice:
        text = "🔊 Голосовое сообщение"
    elif message.media:
        text = "📎 Прикреплённое медиа"
    else:
        text = ""
    if message.text:
        unname = re.match("👤 +(.*)\\n(.*)", message.raw_text)
        unname = unname.group(2) if message.sender.id == me.id and unname and unname.group(2) else message.raw_text
        text = "\n➥ " + (text + ", " if text else "") + (f"{unname[:27]}..." if len(unname) > 27 else unname)
    else:
        text = ("\n➥ " + text) if text else ""
    return text

bot.start()