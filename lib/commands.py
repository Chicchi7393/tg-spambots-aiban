import os

from telegram import Update
from telegram.ext import ContextTypes

from lib.consts import BOT_CORRECTIONS_PROMPT_FILE, correction_subprompt

async def _replyChecks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    errorMsg = None
    message = update.message

    try:
        assert message is not None and message.text is not None
        assert update.effective_chat is not None
        assert str(update.effective_chat.id) == os.environ["TG_ALERT_ID"]

        replyMessage = message.reply_to_message

        errorMsg = "Devi rispondere ad un messaggio!"
        assert replyMessage is not None

        errorMsg = "Devi rispondere ad un mio messaggio!"
        assert replyMessage.from_user is not None and replyMessage.from_user.id == context.bot.id

        errorMsg = "Il mio messaggio deve essere di evento."
        assert replyMessage.text is not None and "bot" in replyMessage.text.lower()

        errorMsg = "Il messaggio deve contenere, dopo lo spazio, una tua opinione sul perchè sia giusto/sbagliato"
        assert len(message.text.split(" ")) > 1
    except AssertionError:
        if errorMsg is not None and message is not None:
            await message.reply_text(errorMsg)
        return False
    
    return True

async def goodboy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    passedChecks = await _replyChecks(update, context)

    if not passedChecks:
        return
    
    message = update.message
    assert message is not None and message.text is not None
    reply_to_message = message.reply_to_message
    assert reply_to_message is not None and reply_to_message.text is not None
    opinion = " ".join(message.text.split(" ")[1:])

    BOT_CORRECTIONS_PROMPT_FILE.write(correction_subprompt(reply_to_message, opinion, True))
    BOT_CORRECTIONS_PROMPT_FILE.flush()
    await message.reply_text("Aggiunta nota di merito")
    


async def badboy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    passedChecks = await _replyChecks(update, context)

    if not passedChecks:
        return
    
    message = update.message
    assert message is not None and message.text is not None
    reply_to_message = message.reply_to_message
    assert reply_to_message is not None and reply_to_message.text is not None
    opinion = " ".join(message.text.split(" ")[1:])

    BOT_CORRECTIONS_PROMPT_FILE.write(correction_subprompt(reply_to_message, opinion, False))
    BOT_CORRECTIONS_PROMPT_FILE.flush()

    await message.reply_text("Aggiunta nota di demerito")
