import os
import re
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain_openai import ChatOpenAI

load_dotenv()

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化する
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.event("app_mention")
def handler_mention(event, say):
    user = event["user"]
    thread_ts = event["ts"]
    message = re.sub("<@.*>", "", event["text"])

    llm = ChatOpenAI(
        model_name=os.environ.get("OPENAI_API_MODEL"),
        temperature=os.environ.get("OPENAI_API_TEMPERATURE")
    )
    response = llm.predict(message)

    say(thread_ts=thread_ts, text=response)


# ソケットモードハンドラーを使ってアプリを起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
