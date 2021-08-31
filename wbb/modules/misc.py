import secrets
import string
from asyncio import Lock

import aiohttp
from cryptography.fernet import Fernet
from pyrogram import filters

from wbb import FERNET_ENCRYPTION_KEY, app, arq
from wbb.core.decorators.errors import capture_err
from wbb.utils import random_line
from wbb.utils.http import get
from wbb.utils.json_prettify import json_prettify
from wbb.utils.pastebin import paste

__MODULE__ = "Misc"
__HELP__ = """
/asq
    Ask a question
/commit
    Generate Funny Commit Messages
/runs
    Idk Test Yourself
/id
    Get Chat_ID or User_ID
/random [Length]
    Generate Random Complex Passwords
/encrypt
    Encrypt Text [Can Only Be Decrypted By This Bot]
/decrypt
    Decrypt Text
/cheat [Language] [Query]
    Get Programming Related Help
/tr [LANGUAGE_CODE]
    Translate A Message
    Ex: /tr en
/json [URL]
    Get parsed JSON response from a rest API.
/arq
    Statistics Of ARQ API.
/webss [URL]
    Take A Screenshot Of A Webpage
/reverse
    Reverse search an image.
/carbon
    Make Carbon from code.
/tts
    Convert Text To Speech.
/autocorrect [Reply to a message]
    Autocorrects the text in replied message.
#RTFM - Tell noobs to read the manual
"""

ASQ_LOCK = Lock()


@app.on_message(filters.command("asq") & ~filters.edited)
async def asq(_, message):
    err = "Reply to text message or pass the question as argument"
    if message.reply_to_message:
        if not message.reply_to_message.text:
            return await message.reply(err)
        question = message.reply_to_message.text
    else:
        if len(message.command) < 2:
            return await message.reply(err)
        question = message.text.split(None, 1)[1]
    m = await message.reply("Thinking...")
    async with ASQ_LOCK:
        resp = await arq.asq(question)
        await m.edit(resp.result)


@app.on_message(filters.command("commit") & ~filters.edited)
async def commit(_, message):
    await message.reply_text(
        await get("http://whatthecommit.com/index.txt")
    )


@app.on_message(filters.command("RTFM", "#"))
async def rtfm(_, message):
    await message.delete()
    if not message.reply_to_message:
        return await message.reply_text("Reply To A Message lol")
    await message.reply_to_message.reply_text(
        "Are You Lost? READ THE FUCKING DOCS!"
    )


@app.on_message(filters.command("runs") & ~filters.edited)
async def runs(_, message):
    await message.reply_text(
        (await random_line("wbb/utils/runs.txt"))
    )


@app.on_message(filters.command("id"))
async def getid(_, message):
    chat = message.chat
    your_id = message.from_user.id
    message_id = message.message_id
    reply = message.reply_to_message
    text = f"**[Message ID:]({message.link})** `{message_id}`\n"
    text += f"**[Your ID:](tg://user?id={your_id})** `{your_id}`\n"
    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await app.get_users(split)).id
            text += f"**[User ID:](tg://user?id={user_id})** `{user_id}`\n"
        except Exception:
            return await message.reply_text(
                "This user doesn't exist."
            )
    text += f"**[Chat ID:](https://t.me/{chat.username})** `{chat.id}`\n\n"
    if not getattr(reply, "empty", True):
        text += f"**[Replied Message ID:]({reply.link})** `{reply.message_id}`\n"
        text += f"**[Replied User ID:](tg://user?id={reply.from_user.id})** `{reply.from_user.id}`"
    await message.reply_text(
        text, disable_web_page_preview=True, parse_mode="md"
    )


# Random
@app.on_message(filters.command("random") & ~filters.edited)
@capture_err
async def random(_, message):
    if len(message.command) != 2:
        return await message.reply_text(
            '"/random" Needs An Argurment.' " Ex: `/random 5`"
        )
    length = message.text.split(None, 1)[1]
    try:
        if 1 < int(length) < 1000:
            alphabet = string.ascii_letters + string.digits
            password = "".join(
                secrets.choice(alphabet) for i in range(int(length))
            )
            await message.reply_text(f"`{password}`")
        else:
            await message.reply_text(
                "Specify A Length Between 1-1000"
            )
    except ValueError:
        await message.reply_text(
            "Strings Won't Work!, Pass A Positive Integer Less Than 1000"
        )


# Encrypt
@app.on_message(filters.command("encrypt") & ~filters.edited)
@capture_err
async def encrypt(_, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "Reply To A Message To Encrypt It."
        )
    text = message.reply_to_message.text
    text_in_bytes = bytes(text, "utf-8")
    cipher_suite = Fernet(FERNET_ENCRYPTION_KEY)
    encrypted_text = cipher_suite.encrypt(text_in_bytes)
    bytes_in_text = encrypted_text.decode("utf-8")
    await message.reply_text(bytes_in_text)


# Decrypt
@app.on_message(filters.command("decrypt") & ~filters.edited)
@capture_err
async def decrypt(_, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "Reply To A Message To Decrypt It."
        )
    text = message.reply_to_message.text
    text_in_bytes = bytes(text, "utf-8")
    cipher_suite = Fernet(FERNET_ENCRYPTION_KEY)
    try:
        decoded_text = cipher_suite.decrypt(text_in_bytes)
    except Exception:
        return await message.reply_text("Incorrect token")
    bytes_in_text = decoded_text.decode("utf-8")
    await message.reply_text(bytes_in_text)


async def fetch_text(url):
    async with aiohttp.ClientSession(
        headers={"user-agent": "curl"}
    ) as session:
        async with session.get(url) as resp:
            data = await resp.text()
    return data


# Cheat.sh
@app.on_message(filters.command("cheat") & ~filters.edited)
@capture_err
async def cheat(_, message):
    if len(message.command) < 3:
        return await message.reply_text("/cheat [language] [query]")
    text = message.text.split(None, 2)
    m = await message.reply_text("Searching")
    try:
        language = text[1]
        query = text[2]
        data = await fetch_text(
            f"http://cht.sh/{language}/{query}?QT"
        )
        if not data:
            return await m.edit("Found Literally Nothing!")
        if len(data) > 4090:
            with open("cheat.txt", "w") as f:
                f.write(data)
            return await message.reply_document(data)
        await m.edit(f"`{data}`")
    except Exception as e:
        await m.edit(str(e))
        print(str(e))


# Translate
@app.on_message(filters.command("tr") & ~filters.edited)
@capture_err
async def tr(_, message):
    if len(message.command) != 2:
        return await message.reply_text("/tr [LANGUAGE_CODE]")
    lang = message.text.split(None, 1)[1]
    if not message.reply_to_message or not lang:
        return await message.reply_text(
            "Reply to a message with /tr [language code]"
            + "\nGet supported language list from here -"
            + " https://py-googletrans.readthedocs.io/en"
            + "/latest/#googletrans-languages"
        )
    reply = message.reply_to_message
    text = reply.text or reply.caption
    if not text:
        return await message.reply_text(
            "Reply to a text to translate it"
        )
    result = await arq.translate(text, lang)
    if not result.ok:
        return await message.reply_text(result.result)
    await message.reply_text(result.result.translatedText)


@app.on_message(filters.command("json") & ~filters.edited)
@capture_err
async def json_fetch(_, message):
    if len(message.command) != 2:
        return await message.reply_text("/json [URL]")
    url = message.text.split(None, 1)[1]
    m = await message.reply_text("Fetching")
    try:
        data = await get(url)
        data = await json_prettify(data)
        if len(data) < 4090:
            await m.edit(data)
        else:
            link = await paste(data)
            await m.edit(
                f"[OUTPUT_TOO_LONG]({link})",
                disable_web_page_preview=True,
            )
    except Exception as e:
        await m.edit(str(e))


@app.on_message(filters.command("webss"))
@capture_err
async def take_ss(_, message):
    if len(message.command) != 2:
        return await message.reply_text(
            "Give A Url To Fetch Screenshot."
        )
    url = message.text.split(None, 1)[1]
    m = await message.reply_text("**Uploading**")
    try:
        await app.send_photo(
            message.chat.id,
            photo=f"https://webshot.amanoteam.com/print?q={url}",
        )
    except Exception:
        return await m.edit("No Such Website.")
    await m.delete()


@app.on_message(filters.command(["kickme", "banme"]))
async def kickbanme(_, message):
    await message.reply_text(
        "Haha, it doesn't work that way, You're stuck with everyone here."
    )
