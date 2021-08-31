from asyncio import Lock
from os import remove

from pyrogram import filters
from pyrogram.types import Message

from wbb import app, arq
from wbb.core.decorators.errors import capture_err
from wbb.utils.functions import get_file_id_from_message

__MODULE__ = "Storage"
__HELP__ = """
Upload unlimited files smaller than 100MB
And get a download link
**Usage:**
    /upload [url|Reply to a file]
"""

UPLOAD_LOCK = Lock()


async def upload(m: Message, file: str = None, url: str = None):
    err = "Something went wrong"
    try:
        resp = await arq.upload(file=file, url=url)
    except Exception:
        await m.edit(err)
        if file:
            remove(file)
        return

    if file:
        remove(file)

    if not resp:
        return await m.edit(err)

    if not resp.ok:
        return await m.edit(err)

    await m.edit(
        f"**Download Link:** {resp.result}",
        disable_web_page_preview=True,
    )


@app.on_message(filters.command("upload"))
@capture_err
async def arq_upload(_, message):
    if message.reply_to_message:
        if UPLOAD_LOCK.locked():
            return await message.reply(
                "One upload is already in progress, please try again later"
            )
        async with UPLOAD_LOCK:
            r = message.reply_to_message

            file_id = get_file_id_from_message(r, 100000000, None)
            if not file_id:
                return await message.reply("Unsupported media.")

            m = await message.reply("Downloading...")
            file = await app.download_media(file_id)

            await m.edit("Uploading...")
            return await upload(m, file=file)

    if len(message.command) != 2:
        return await message.reply("Not enough arguments")

    url = message.text.split(None, 1)[1]

    m = await message.reply("Uploading...")
    await upload(m, url=url)
