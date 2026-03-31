# Shift_JIS / CP932 Tools MCP Server

## 日本語

CP932（Shift_JIS）またはUTF-8でエンコードされたファイルの読み取り、書き込み、編集、検索ツールを提供するMCPサーバーです。Claude Codeで日本語ソースコードを扱うために設計されています。

### ツール

日本語ファイルを操作するための以下のツールを提供します：

- ReadCP932
- EditCP932
- WriteCP932
- GrepCP932

各ツールはCP932またはUTF-8エンコーディングのファイルを自動検出し、書き戻し時に元のエンコーディングを保持します。主な用途はWindows上のShift_JIS（CP932）エンコーディングの日本語ソースコードですが、エンコーディングが混在している場合のUTF-8ファイルにも対応しています。

### 必要環境

- Python >= 3.10
- `mcp` パッケージ

### Claude Codeへのインストール

以下のコマンドでClaude Codeの設定にサーバーを追加します：

```bash
claude mcp add cp932-tools -- uv run /path/to/cp932_server.py
```

追加されたことを確認するには：

```bash
claude mcp list
```

削除する場合：

```bash
claude mcp remove cp932-tools
```

---

## English

An MCP server that provides tools for reading, writing, editing, and searching files encoded in CP932 (Shift_JIS) or UTF-8. Designed for working with Japanese-language source code while using Claude Code.

### Tools

Provides the following tools for interacting with Japanese language files:

- ReadCP932
- EditCP932
- WriteCP932
- GrepCP932

Each tool can read, write, edit, or search files in either CP932 or UTF-8 encoding, with automatic detection and while preserving the original encoding when writing back to the files. The primary use case is for working with Japanese source code files on Windows in Shift_JIS (CP932) encoding, but it can also handle UTF-8 files for the case where the user has files with mixed encodings.

### Requirements

- Python >= 3.10
- `mcp` package

### Installation in Claude Code

Add the server to your Claude Code settings by running:

```bash
claude mcp add cp932-tools -- uv run /path/to/cp932_server.py
```

To verify it was added:

```bash
claude mcp list
```

To remove it later:

```bash
claude mcp remove cp932-tools
```
