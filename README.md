# Shift_JIS / CP932 Tools MCP Server

[English](README.en.md)

Claude CodeでShift_JIS（CP932）エンコーディングの日本語ファイルを読み書き・編集・検索するためのMCPサーバーです。

## セットアップ

### 1. uvのインストール

`uv`がインストールされていない場合は、以下の手順に従ってください：
https://docs.astral.sh/uv/getting-started/installation/

### 2. サーバースクリプトのダウンロード

**Bash:**

```bash
mkdir -p ~/.claude/mcp-servers
curl -o ~/.claude/mcp-servers/cp932_server.py https://raw.githubusercontent.com/maubrey/claude-mcp-servers/main/cp932_server.py
```

**PowerShell:**

```powershell
New-Item -ItemType Directory -Force -Path ~/.claude/mcp-servers
Invoke-WebRequest -Uri https://raw.githubusercontent.com/maubrey/claude-mcp-servers/main/cp932_server.py -OutFile ~/.claude/mcp-servers/cp932_server.py
```

### 3. Claude Codeにサーバーを登録

```
claude mcp add cp932-tools -- uv run ~/.claude/mcp-servers/cp932_server.py
```

### 4. 確認

```
claude mcp list
```

出力に`cp932-tools`が表示されていれば成功です。次回Claude Codeを起動すると、`ReadCP932`、`EditCP932`、`WriteCP932`、`GrepCP932`のツールが使えるようになります。

## アンインストール

```
claude mcp remove cp932-tools
```

## ツール

日本語ファイルを操作するための以下のツールを提供します：

- **ReadCP932** — CP932またはUTF-8のファイルを自動検出して読み取ります。行オフセットと行数制限のパラメータに対応しています。
- **EditCP932** — ファイル内のテキストを検索・置換します。元のエンコーディングと改行コードを保持します。CP932に存在しないUnicode文字（全角引用符、emダッシュ、省略記号など）は自動的に置換されます。
- **WriteCP932** — CP932またはUTF-8エンコーディングでファイルを新規作成または上書きします。
- **GrepCP932** — ディレクトリを再帰的に検索し、正規表現パターンでファイルを検索します。globフィルタリングやコンテキスト行の表示に対応しています。

各ツールはファイルがCP932かUTF-8かを自動検出し、書き戻し時に元のエンコーディングを保持します。主な用途はWindows上のShift_JIS（CP932）エンコーディングの日本語ソースコードですが、エンコーディングが混在しているプロジェクトのUTF-8ファイルにも対応しています。
