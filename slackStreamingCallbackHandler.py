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
        self.interval = CHAT_UPDATE_INTERVAL_SEC
        # 投稿を更新した累計回数カウンタ
        self.update_count = 0
        self.app = app

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.message += token
        now = time.time()
        if now - self.last_send_time > self.interval:
            self.last_send_time = now
            self.app.client.chat_update(
                channel=self.channel,
                ts=self.ts,
                text=f"{self.message}..."
            )
            self.update_count += 1
            # update_countが現在の更新間隔 x10 より多くなるたびに更新間隔を 2 倍にする
            if self.update_count / 10 > self.interval:
                self.interval = self.interval * 2

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        self.app.client.chat_update(
            channel=self.channel,
            ts=self.ts,
            text=self.message
        )
