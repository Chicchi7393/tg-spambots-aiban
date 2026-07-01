import os

from telegram import ChatMember, ChatMemberUpdated
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


def extract_status_change(chat_member_update: ChatMemberUpdated) -> tuple[bool, bool]:
    """
    Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """

    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return False, False

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)

    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)


    return was_member, is_member

async def alert_staff(text: str, context: ContextTypes.DEFAULT_TYPE):
    if os.environ["TG_ALERT_ID"] == "":
        return
    
    await context.bot.send_message(chat_id=os.environ["TG_ALERT_ID"], text=text, parse_mode=ParseMode.HTML)

async def alert_group(text: str, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=os.environ["TG_GROUP_ID"], text=text, parse_mode=ParseMode.HTML)