import requests
from telegram import Message, User
import json
from lib.consts import BOT_DESC_PROMPT, BOT_EXTRA_PROMPT, BOT_JOIN_PROMPT, BOT_MESSAGE_PROMPT, GENERATION_CONFIG


class GeminiAILogic:
    def __init__(self, vertex_proj_id: str, vertex_api_key: str, vertex_model: str) -> None:
        self.vertex_proj_id = vertex_proj_id
        self.vertex_api_key = vertex_api_key
        self.vertex_model = vertex_model

    def _call(self, payload: dict) -> dict:
        req = requests.post(
            f"https://firebasevertexai.googleapis.com/v1beta/projects/{self.vertex_proj_id}" + 
            f"/locations/global/publishers/google/models/{self.vertex_model}:generateContent?key={self.vertex_api_key}",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        return req.json()

    def is_bot_join(self, user: User) -> dict:
        corrections = ""
        with open("corrections_prompt.txt") as c:
            corrections = c.read()

        userPayload = json.dumps(
            user,
            default=lambda o: o.__dict__, 
            sort_keys=True)
        
        payload = {
            "contents": [
                {"role": "assistant", "parts": [
                    {"text": f"User: {userPayload}"}
                ]}
            ],
            "generationConfig": GENERATION_CONFIG,
            "systemInstruction": {
                "role": "system",
                "parts": [{"text": BOT_DESC_PROMPT}, {"text": BOT_JOIN_PROMPT}, {"text": BOT_EXTRA_PROMPT}, {"text": corrections}]
            }
        }
        ai_call = self._call(payload)
        overview = json.loads(ai_call["candidates"][0]["content"]["parts"][0]["text"])
        
        return overview
    

    def is_bot_msg(self, user: User, message: Message) -> dict:
        corrections = ""
        with open("corrections_prompt.txt") as c:
            corrections = c.read()

        messagePayload = json.dumps(
            message,
            default=lambda o: o.__dict__, 
            sort_keys=True)        
        
        userPayload = json.dumps(
            user,
            default=lambda o: o.__dict__, 
            sort_keys=True)
        
        payload = {
            "contents": [
                {"role": "assistant", "parts": [
                    {"text": f"User: {userPayload}, message: {messagePayload}"}
                ]}
            ],
            "generationConfig": GENERATION_CONFIG,
            "systemInstruction": {
                "role": "system",
                "parts": [{"text": BOT_DESC_PROMPT}, {"text": BOT_MESSAGE_PROMPT}, {"text": BOT_EXTRA_PROMPT}, {"text": corrections}]
            }
        }
        ai_call = self._call(payload)
        overview = json.loads(ai_call["candidates"][0]["content"]["parts"][0]["text"])
        
        return overview