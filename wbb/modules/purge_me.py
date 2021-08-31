from pyrogram import filters
from pyrogram.types import Message

from wbb import USERBOT_ID, USERBOT_PREFIX, app2

# Yeah i know this should've been in userbot.py,
# But i wrote it here for some obvious reasons.
__MODULE__ = "Userbot"
__HELP__ = """
`.alive`
    Send Alive Message.
`.create (b|s|c) Title`
        create [basic|super]group & channel
`.chatbot [ENABLE|DISABLE]`
        Enable chatbot in a chat.
`.autocorrect [ENABLE|DISABLE]`
        This will autocorrect your messages on the go.
`.purgeme [Number of messages to purge]`
        Purge your own messages.
        Ex: .purgeme 10
`.eval [Lines of code]`
        Execute Python Code.
`.lsTasks`
        List running tasks (eval)
`.cancelTask [ID] or Reply to .eval message`
        Cancel a running task (eval)
`.sh [Some shell code]`
        Execute Shell Code.
`.approve`
        Approve a user to PM you.
`.disapprove`
        Disapprove a user to PM you.
`.block`
        Block a user.
`.unblock`
        Unblock a user.
`.anonymize`
        Change Name/PFP Randomly.
`.impersonate [User_ID|Username|Reply]`
        Clone profile of a user.
`.useradd`
        To add a user in sudoers.
        [Don't use it if you don't know what you're doing]
`.userdel`
        To remove a user from sudoers.
`.sudoers`
        To list sudo users.
`.download [URL or reply to a file]`
        Download a file from TG or URL
`.upload [URL or File Path]`
        Upload a file from local or URL
"""


@app2.on_message(
    filters.command("purgeme", prefixes=USERBOT_PREFIX)
    & filters.user(USERBOT_ID)
)
async def purge_me_func(_, message: Message):
    await message.delete()

    if len(message.command) != 2:
        return

    n = message.text.split(None, 1)[1].strip()
    if not n.isnumeric():
        return

    n = int(n)
    if n < 1:
        return

    chat_id = message.chat.id

    message_ids = [
        m.message_id
        async for m in app2.search_messages(
            chat_id, from_user=USERBOT_ID
        )
    ][
        :n
    ]  # NOTE Don't use limit param here

    if len(message_ids) == 0:
        return

    # A list containing lists of 100 message chunks
    # because we can't delete more than 100 messages at once,
    # we have to do it in chunks of 100, i'll choose 99 just
    # to be safe.
    to_delete = list(
        (
            message_ids[i : i + 99]
            for i in range(0, len(message_ids), 99)
        )
    )

    for hundred_messages_or_less in to_delete:
        await app2.delete_messages(
            chat_id=chat_id,
            message_ids=hundred_messages_or_less,
            revoke=True,
        )
