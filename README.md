# Minecraft VibeCoding Bridge (MVB)

MinecraftとAIを安全に連携させるためのブリッジアプリケーションです。
講座用に設計されており、強力なセキュリティ制限（フォルダ隔離、コマンド制限）があります。
ただし、現状のコードは完成していません。問題を多く抱えている状態です。

## セットアップ

1. **前提条件**
    - Python 3.10+
    - Java Runtime Environment (JRE) 17+ (Minecraft Server用)

2. **Server Jarの配置**
    - `server/` フォルダの中に、Minecraftの `server.jar` を配置してください。
    - 推奨バージョン: Pythonアプリの設定 `pack_format` と合わせる必要があります（デフォルトは1.21系の `pack_format: 48`）。

3. **EULAの同意**
    - 初回起動時に `server/eula.txt` が生成されます。
    - テキストエディタで開き、`eula=true` に変更してください。

## 使い方

1. **起動**
    ```bash
    python3 -m app.main
    ```
    GUIが立ち上がります。

2. **Minecraftサーバの起動**
    - GUIの「Start Server」ボタンを押します。
    - 初回はワールド生成に時間がかかります。

3. **実行フロー (講座形式)**
    - GUIの入力欄に「〇〇を作って」と入力します。
    - 「Generate & Run Plan (JSON)」ボタンを押します。
    - `mvb_work/bridge_in/prompt.json` が生成されます。
    - **動画講座の指示に従い、このファイルをAIに渡し、`mvb_work/bridge_out/plan.json` を生成させてください。**
    - `plan.json` が配置されると、MVBが自動的に検知し、データパック生成・実行を行います。

4. **Minecraftでの確認**
    - ゲーム内でマルチプレイから `localhost` に接続します。

## 安全機能

- **フォルダ隔離**: アプリフォルダの外には一切アクセスしません。
- **削除禁止**: ファイルの削除コマンドは無効化されています。
- **コマンド制限**: `say`, `give`, `summon` など、安全なコマンドのみ許可されます。`execute` や `op` はブロックされます。
- **通信制限**: RCONおよびAPIは `localhost` のみに制限されています。
