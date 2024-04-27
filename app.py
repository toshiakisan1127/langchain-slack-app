import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化する
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.event("app_mention")
def handler_mention(event, say):
    user = event["user"]
    thread_ts = event["ts"]
    say(thread_ts=thread_ts, text=f"Hello <@{user}>!")


# ソケットモードハンドラーを使ってアプリを起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
