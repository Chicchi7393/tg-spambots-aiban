import requests
from telegram import Message, User
import json
from lib.consts import BOT_DESC_PROMPT, BOT_EXTRA_PROMPT, BOT_JOIN_PROMPT, BOT_MESSAGE_PROMPT, RESPONSE_SCHEMA


class GeminiAILogic:
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def _call(self, system_parts: list[str], user_text: str) -> dict:
        payload = {
            "model": self.model,
            "instructions": "\n\n".join(p for p in system_parts if p),
            "input": user_text,
            "temperature": 0.0,
            "max_output_tokens": 1000,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "bot_verdict",
                    "schema": RESPONSE_SCHEMA,
                    "strict": True,
                }
            },
        }
        req = requests.post(
            f"{self.base_url}/responses",
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        data = req.json()
        if "error" in data and data["error"] is not None:
            raise RuntimeError(f"AI call failed: {data['error']}")
        for item in data.get("output", []):
            if item.get("type") != "message":
                continue
            for part in item.get("content", []):
                if part.get("type") == "output_text" and part.get("text"):
                    return json.loads(part["text"])
        raise RuntimeError(f"AI call returned no text output: {data}")

    def _read_corrections(self) -> str:
        with open("corrections_prompt.txt") as c:
            return c.read()

    def is_bot_join(self, user: User) -> dict:
        userDict = user._get_attrs()
        userDict["api_kwargs"] = {}
        userPayload = json.dumps(userDict, skipkeys=True, default=None)

        return self._call(
            system_parts=[BOT_DESC_PROMPT, BOT_JOIN_PROMPT, BOT_EXTRA_PROMPT, self._read_corrections()],
            user_text=f"User: {userPayload}",
        )

    def is_bot_msg(self, user: User, message: Message) -> dict:
        messageDict = message._get_attrs()
        messageDict["api_kwargs"] = {}
        messageDict["from_user"] = message.from_user.id
        messageDict["chat"] = message.chat.id
        messageDict["date"] = message.date.timestamp()
        messagePayload = json.dumps(messageDict, skipkeys=True, default=None)

        userDict = user._get_attrs()
        userDict["api_kwargs"] = {}
        userPayload = json.dumps(userDict, skipkeys=True, default=None)

        return self._call(
            system_parts=[BOT_DESC_PROMPT, BOT_MESSAGE_PROMPT, BOT_EXTRA_PROMPT, self._read_corrections()],
            user_text=f"User: {userPayload}, message: {messagePayload}",
        )
