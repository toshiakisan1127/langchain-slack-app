import os
import re
import time
from typing import Any
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
from slackStreamingCallbackHandler import SlackStreamCallbackHandler

load_dotenv()

app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN"),
    process_before_response=True
)

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化する
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.event("app_mention")
def handler_mention(event, say):
    channel = event["channel"]
    thread_ts = event["ts"]
    message = re.sub("<@.*>", "", event["text"])

    result = say("\n\nTyping...", thread_ts=thread_ts)
    ts = result["ts"]

    callback = SlackStreamCallbackHandler(channel=channel, ts=ts, app=app)
    llm = ChatOpenAI(
        model_name=os.environ.get("OPENAI_API_MODEL"),
        temperature=os.environ.get("OPENAI_API_TEMPERATURE"),
        streaming=True,
        callbacks=[callback]
    )
    response = llm.predict(message)

    say(thread_ts=thread_ts, text=response)


# ソケットモードハンドラーを使ってアプリを起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
