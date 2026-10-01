from telegram import Update
from telegram.ext import ApplicationBuilder, ChatMemberHandler, CommandHandler, ContextTypes, filters, MessageHandler
import dotenv
import os
import json

from lib.commands import badboy, goodboy
from lib.gemini_ai import GeminiAILogic
from lib.handlers import info_change_handler, message_handler
from lib.tg import extract_status_change

DEV = False
FIRST_MSGS = 15
dotenv.load_dotenv(".env.dev" if DEV else ".env.prod", override=True)

to_check = {}
checking = []

for key in ["TG_GROUP_ID", "TG_BOT", "AI_BASE_URL", "AI_API_KEY", "AI_MODEL"]:
    try:
        assert os.environ[key] != "" and os.environ[key] != None
    except AssertionError as e:
        e.add_note(f"Missing value in env: {key}")
        raise e

ai = GeminiAILogic(
    base_url = os.environ["AI_BASE_URL"],
    api_key = os.environ["AI_API_KEY"],
    model = os.environ["AI_MODEL"],
)

async def check_userchange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.chat_member is None or str(update.chat_member.chat.id) != os.environ["TG_GROUP_ID"]:
        return
    
    if update.chat_member.new_chat_member.user.id in checking:
        return

    checking.append(update.chat_member.new_chat_member.user.id)

    _, is_member = extract_status_change(update.chat_member)
    # with the from_user == new_chat_member ids check, i just prevent the fact that
    # any other bot could edit permissions on the user
    # and retrigger the check
    if is_member and update.chat_member.from_user.id == update.chat_member.new_chat_member.user.id:

        user = update.chat_member.new_chat_member.user
        chat = update.chat_member.chat

        isBot = ai.is_bot_join(user)
        print(json.dumps(isBot))

        await info_change_handler(isBot, user, context, chat)

        to_check[user.id] = 0
    
    checking.remove(update.chat_member.new_chat_member.user.id)

    
async def check_message_afterchange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or message is None or chat is None or str(chat.id) != os.environ["TG_GROUP_ID"]:
        return
    
    if to_check.get(user.id) is None or to_check[user.id] == -1:
        return
    
    isBot = ai.is_bot_msg(user, message)
    print(json.dumps(isBot))

    await message_handler(isBot, user, message, context, chat)

    to_check[user.id] += 1

    if to_check[user.id] == FIRST_MSGS:
        to_check[user.id] = -1
    


app = ApplicationBuilder().token(os.environ["TG_BOT"]).build()

app.add_handler(ChatMemberHandler(check_userchange, ChatMemberHandler.CHAT_MEMBER))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message_afterchange))
app.add_handler(CommandHandler("goodboy", goodboy))
app.add_handler(CommandHandler("badboy", badboy))

print("Bot started!")
app.run_polling(allowed_updates=Update.ALL_TYPES)