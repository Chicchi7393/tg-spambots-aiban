from telegram import Chat, Message, Update, User
from telegram.ext import ContextTypes
import os
from lib.consts import alert_group_ban_message, alert_staff_ban_message, alert_staff_suspicious_message
from lib.tg import alert_group, alert_staff

async def info_change_handler(verdict: dict, user: User, context: ContextTypes.DEFAULT_TYPE, chat: Chat):
    if verdict["probability"] >= 0.85:
        await ban_final_verdict(verdict, None, user, context, chat)
        return
    
    if verdict["probability"] >= 0.65:
        await alert_suspicious_final_verdict(verdict, None, user, context, chat)
        return
    
async def message_handler(verdict: dict, user: User, message: Message, context: ContextTypes.DEFAULT_TYPE, chat: Chat):
    if verdict["probability"] >= 0.85:
        await ban_final_verdict(verdict, message, user, context, chat)
        return
    
    if verdict["probability"] >= 0.65:
        await alert_suspicious_final_verdict(verdict, message, user, context, chat)
        return


async def ban_final_verdict(verdict: dict, message: Message | None, user: User, context: ContextTypes.DEFAULT_TYPE, chat: Chat):
    await chat.ban_member(user.id, revoke_messages=True)

    if message is not None:
        await chat.delete_message(message.id)

    await alert_group(alert_group_ban_message(user, message, verdict), context)
    await alert_staff(alert_staff_ban_message(user, message, verdict), context)

async def alert_suspicious_final_verdict(verdict: dict, message: Message | None, user: User, context: ContextTypes.DEFAULT_TYPE, chat: Chat):
    if message is not None:
        await chat.delete_message(message.id)

    await alert_staff(alert_staff_suspicious_message(user, message, verdict), context)