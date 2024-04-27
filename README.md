# langchain-slack-app
langchainでslackアプリを作ってみるリポジトリ

### ローカルでの起動方法
1. 仮想環境の起動

```
pyenv local 3.10.1  
python -m venv .venv
 . .venv/bin/activate   
```

2. envファイルの設定
```
SLACK_SIGNING_SECRET=
SLACK_BOT_TOKEN=
SLACK_APP_TOKEN=
OPENAI_API_KEY=
OPENAI_API_MODEL=
OPENAI_API_TEMPERATURE=
MOMENTO_AUTH_TOKEN=
MOMENTO_CACHE=
MOMENTO_TTL=1
```

3. requirements.txtに書いてあるpackageのinstall
4. app.pyの実行
```
python app.py       
```