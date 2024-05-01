import os
import re
import time
import logging
import json
from typing import Any
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
from slackStreamingCallbackHandler import SlackStreamCallbackHandler
from datetime import timedelta
from langchain.memory import MomentoChatMessageHistory
from langchain.schema import HumanMessage, LLMResult, SystemMessage

load_dotenv()
SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def handler(event, context):
    logger.info("handler called")
    header = event["headers"]
    logger.info(json.dumps(header))

    if "x-slack-retry-num" in header:
        logger.info("SKIP > x-slack-retry-num: %s",
                    header["x-slack-retry-num"])
        return 200

    # AWS Lambda環境のリクエスト情報を app が処理できるように変換してくれるアダプター
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)

def just_ack(ack):
    ack()

def handler_mention(event, say):
    channel = event["channel"]
    thread_ts = event["ts"]
    message = re.sub("<@.*>", "", event["text"])

    # 投稿のキー：初回 → event["ts"], 2回目以降 → event["thread_ts"]
    id_ts = event["ts"]
    if "thread_ts" in event:
        id_ts = event["thread_ts"]
    result = say("\n\nTyping...", thread_ts=thread_ts)
    ts = result["ts"]

    logger.info(f"debug: momento id: {id_ts}")
    history = MomentoChatMessageHistory.from_client_params(
        id_ts,
        os.environ["MOMENTO_CACHE"],
        timedelta(hours=int(os.environ["MOMENTO_TTL"]))
    )

    messages = [SystemMessage(content="You are a good assistant.")]
    messages.extend(history.messages)
    messages.append(HumanMessage(content=message))

    history.add_user_message(message)

    callback = SlackStreamCallbackHandler(channel=channel, ts=ts, app=app)
    llm = ChatOpenAI(
        model_name=os.environ.get("OPENAI_API_MODEL"),
        temperature=os.environ.get("OPENAI_API_TEMPERATURE"),
        streaming=True,
        callbacks=[callback]
    )

    ai_message = llm(messages)
    history.add_message(ai_message)


# ボットトークンとソケットモードハンドラーを使ってアプリを初期化する
app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN"),
    process_before_response=True
)
app.event("app_mention")(ack=just_ack, lazy=[handler_mention])

# ソケットモードハンドラーを使ってアプリを起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
