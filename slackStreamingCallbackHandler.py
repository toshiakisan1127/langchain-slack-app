from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
from typing import Any
from slack_bolt import App
import time

CHAT_UPDATE_INTERVAL_SEC = 1


class SlackStreamCallbackHandler(BaseCallbackHandler):
    last_send_time = time.time()
    message = ""

    def __init__(self, channel, ts, app: App):
        self.channel = channel
        self.ts = ts
        self.app = app

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.message += token
        now = time.time()
        if now - self.last_send_time > CHAT_UPDATE_INTERVAL_SEC:
            self.last_send_time = now
            self.app.client.chat_update(
                channel=self.channel,
                ts=self.ts,
                text=f"{self.message}..."
            )

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        self.app.client.chat_update(
            channel=self.channel,
            ts=self.ts,
            text=self.message
        )
