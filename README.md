# GitHub Commit Checker

LINE を通じて GitHub のコミット数を通知するボット

## 設定方法

1. **必要な環境変数を`.env`ファイルに設定:**

```plaintext
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_github_username
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret
```

2.**必要なパッケージのインストール:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3.**アプリケーションの実行:**

```bash
python3 main.py
```

4.**requirements.txt の作成**

```bash
pip freeze > requirements.txt
```
