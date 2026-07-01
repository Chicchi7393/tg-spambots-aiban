from telegram import Update
from telegram.ext import ApplicationBuilder, ChatMemberHandler, CommandHandler, ContextTypes, filters, MessageHandler
import dotenv
import os
import json

from lib.gemini_ai import GeminiAILogic
from lib.handlers import info_change_handler, message_handler
from lib.tg import extract_status_change

DEV = False
FIRST_MSGS = 15
dotenv.load_dotenv(".env.dev" if DEV else ".env.prod", override=True)

to_check = {}

for key in ["TG_GROUP_ID", "TG_BOT", "VERTEX_MODEL", "VERTEX_API_KEY", "VERTEX_PROJ_ID"]:
    try:
        assert os.environ[key] != "" and os.environ[key] != None
    except AssertionError as e:
        e.add_note(f"Missing value in env: {key}")
        raise e
    
ai = GeminiAILogic(
    vertex_api_key = os.environ["VERTEX_API_KEY"],
    vertex_model = os.environ["VERTEX_MODEL"],
    vertex_proj_id = os.environ["VERTEX_PROJ_ID"]
)

async def check_userchange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.chat_member is None or str(update.chat_member.chat.id) != os.environ["TG_GROUP_ID"]:
        return
    
    _, is_member = extract_status_change(update.chat_member)
    if is_member:

        user = update.chat_member.new_chat_member.user
        chat = update.chat_member.chat

        isBot = ai.is_bot_join(user)
        print(json.dumps(isBot))

        await info_change_handler(isBot, user, context, chat)

        to_check[user.id] = 0
    
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
print("Bot started!")
app.run_polling(allowed_updates=Update.ALL_TYPES)