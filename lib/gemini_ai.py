import requests
from telegram import Message, User
import json
from lib.consts import BOT_CORRECTIONS_PROMPT_FILE, BOT_DESC_PROMPT, BOT_EXTRA_PROMPT, BOT_JOIN_PROMPT, BOT_MESSAGE_PROMPT, GENERATION_CONFIG


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
        payload = {
            "contents": [
                {"role": "assistant", "parts": [
                    {"text": f"Nome dell'utente: {user.full_name}, username: {user.username}, id: {user.id}"}
                ]}
            ],
            "generationConfig": GENERATION_CONFIG,
            "systemInstruction": {
                "role": "system",
                "parts": [{"text": BOT_DESC_PROMPT}, {"text": BOT_JOIN_PROMPT}, {"text": BOT_EXTRA_PROMPT}, {"text": BOT_CORRECTIONS_PROMPT_FILE.read()}]
            }
        }
        ai_call = self._call(payload)
        overview = json.loads(ai_call["candidates"][0]["content"]["parts"][0]["text"])
        
        return overview
    

    def is_bot_msg(self, user: User, message: Message) -> dict:
        payload = {
            "contents": [
                {"role": "assistant", "parts": [
                    {"text": f"Nome dell'utente: {user.full_name}, username: {user.username}, id: {user.id}, messaggio: {message.text}"}
                ]}
            ],
            "generationConfig": GENERATION_CONFIG,
            "systemInstruction": {
                "role": "system",
                "parts": [{"text": BOT_DESC_PROMPT}, {"text": BOT_MESSAGE_PROMPT}, {"text": BOT_EXTRA_PROMPT}}, {"text": BOT_CORRECTIONS_PROMPT_FILE.read()}]
            }
        }
        ai_call = self._call(payload)
        overview = json.loads(ai_call["candidates"][0]["content"]["parts"][0]["text"])
        
        return overview