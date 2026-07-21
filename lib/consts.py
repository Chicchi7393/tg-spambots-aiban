from telegram import Message, User


BOT_DESC_PROMPT = "Sei un bot telegram che ha come compito decretare se, un utente, è un bot o no. Rispondi sempre e solo seguendo lo schema JSON richiesto" \
" Sei in un gruppo inerente all'informatica frequentato da umani, il tuo obiettivo " \
"è restituirmi un numero da 0.00 a 1.00 (\"probability\"), dove 0.00 è assolutamente umano, e 1.00 è assolutamente bot." \
"Inoltre, se hai sospetti sul fatto che sia bot, fornisci una descrizione breve sul perchè (max 40 parole, \"desc\", se non necessaria, stringa vuota)." \
"Se la probabilità è sopra 0.85, verrà bannato ed eliminato il messaggio, se invece tra 0.65 e 0.85, verranno avvisati gli admin" \
"Esempi bot:  - self-promo a servizi, ad esempio, di scommesse, " \
"che siano bot con nomi servizi genuini, " \
"atti a far credere che sia il servizio ufficiale, o complete truffe " \
"(ad esempio, come bot prominenti abbiamo Stake Casino - impersonazione di casino davvero esistente, o BC Game, che è pure esso molto presente - bot truffa, casino scam su telegram)" \
" - Bot mirati a promozione di trading o sorte  - Bot mirati alla diffusione di canali porno.  - Bot mirati alla vendita di sostanze/servizi illegali." \
"Non bannare se non sei ASSOLUTAMENTE certo che sia un bot."

# gatekept for secret info, like the history of bans?
BOT_EXTRA_PROMPT = open("extra_prompt.txt").read()

# corrections
BOT_CORRECTIONS_PROMPT_FILE = open("corrections_prompt.txt", "w")

BOT_JOIN_PROMPT = "Un nuovo membro del gruppo è entrato: come assistente, devi fornirmi, " \
"come ti ho detto prima, una probabilita e, se necessario, una descrizione. Ti fornirò nome, username e id telegram (più basso è il numero, più è vecchio l'account -> meno probabile che sia un bot)."

BOT_MESSAGE_PROMPT = "Un nuovo membro del gruppo ha mandato il suo primo messaggio: come assistente, devi fornirmi, " \
"come ti ho detto prima, una probabilita e, se necessario, una descrizione. Ti fornirò nome, username, messaggio inviato e id telegram (più basso è il numero, più è vecchio l'account -> meno probabile che sia un bot)."


GENERATION_CONFIG = {
                "temperature": 0.0,
                "maxOutputTokens": 1000,
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "probability": {"type": "NUMBER"},
                        "desc": {"type": "STRING"}
                    },
                    "required": ["probability", "desc"]
                }
            }

def alert_staff_ban_message(user: User, message: Message | None, verdict: dict):
    final_msg = ""
    final_msg += f"⚠️ <b>BANNATO BOT</b>\nUtente: {user.full_name} [{user.id}]\nVerdetto:"
    final_msg += f"\n\t- Probabilità: {verdict["probability"]}\n\t- Descrizione: <i>{verdict["desc"]}</i>"
    final_msg += f"\n\nCausato da: "
    if message is not None:
        final_msg += 'Primo messaggio'
        final_msg += f"\nMessaggio (eliminato): {message.text}"
    else:
        final_msg += 'Informazioni utente'
    return final_msg

def alert_group_ban_message(user: User, message: Message | None, verdict: dict):
    return f"⚠️ <b>BANNATO BOT</b>: {user.full_name} \n- Descrizione: <i>{verdict["desc"]}</i>"


def alert_staff_suspicious_message(user: User, message: Message | None, verdict: dict):
    final_msg = ""
    final_msg += f"⁉️ <b>PROBABILE BOT</b>\nUtente: {user.full_name} [{user.id}]\nVerdetto:"
    final_msg += f"\n\t- Probabilità: {verdict["probability"]}\n\t- Descrizione: <i>{verdict["desc"]}</i>"
    final_msg += f"\n\nCausato da: {'Primo messaggio' if message is not None else 'Informazioni utente'}"
    if message is not None:
        final_msg += f"\nMessaggio (eliminato): {message.text}"
    final_msg += "\n\n<b>DECIDERE SE BANNARE O NO</b>"
    
    return final_msg

def correction_subprompt(replyMessage: Message, opinion: str, pos: bool) -> str:
    final_subprompt = ""
    final_subprompt += "CORREZIONE DI ESITO BOT:\n"
    final_subprompt += "MESSAGGIO DI ESITO BOT QUA SOTTO (verrà interrotto da questa sequenza \"{STOP}\"):\n\n"
    assert replyMessage.text is not None
    final_subprompt += replyMessage.text
    final_subprompt += "\n{STOP}\n"
    final_subprompt += f"Correzione di {'de' if not pos else ''}merito: {opinion}\n\n"
    final_subprompt += f"-------- FINE CORREZIONE --------\n\n"
    
    return final_subprompt