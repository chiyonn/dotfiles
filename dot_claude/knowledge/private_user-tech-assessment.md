# User Tech Assessment

Voidによる技術力評価。セッションごとに更新。

## Level Definition

- **Beginner**: 概念を聞いたことある程度。コマンド存在は知ってるが使えない
- **Intermediate**: 基本操作はできる。オプションやトラブルシュートは弱い
- **Advanced**: 自力で問題解決できる。設定ファイルいじれる。他人に教えられる

---

## DNS #linux #networking

**Level: Beginner → Intermediate (進行中)**

### Knows
- `dig` コマンドの存在と基本的な使い方
- DNSの基本概念（名前解決）
- AdGuard Homeの存在と役割

### Learned (2024-12-13)
- `dig @server domain` で特定のDNSサーバーに問い合わせ
- `dig +short` で結果だけ表示
- `NXDOMAIN` = ドメイン存在しない
- `resolvectl status` でsystemd-resolvedの状態確認
- Split DNS の概念（ドメインごとにDNSサーバーを分ける）

### Gaps
- digの出力形式の詳細な読み方
- systemd-resolved の設定ファイル（resolved.conf）
- Split DNS の永続化設定
- 英語のドキュメントを読み飛ばす癖あり（resolv.confに書いてあったのに見逃した）

---

## systemd #linux

**Level: Beginner**

### Knows
- systemdがサービス管理してることは知ってる
- systemctl の基本（start, stop, status）

### Learned (2024-12-13)
- systemd-resolved がDNS解決を担当
- resolvectl コマンドの存在

### Gaps
- systemd全般の理解が浅い
- unitファイルの書き方
- journalctl の使いこなし

---

## Nomad #devops #hashicorp

**Level: Intermediate**

### Knows
- nomad job status, run などの基本コマンド
- Job定義ファイルの構造（このリポジトリで使ってる）
- Consulとの連携

### Learned (2024-12-13)
- NOMAD_ADDR は `http://` プロトコルと `:4646` ポートが必要
- ACL有効時は NOMAD_TOKEN が必要

### Gaps
- エラーメッセージを最初ちゃんと読めてなかった（"unsupported protocol scheme"）
- ACL設定したことを忘れてた（TASK.mdとの乖離）
- 機密情報（トークン）の管理場所を把握してなかった

---

## Consul #devops #hashicorp

**Level: Intermediate**

### Knows
- consul catalog services の使い方
- Consul のサービスディスカバリ概念
- API経由でのアクセス（curl）

### Learned (2024-12-13)
- CONSUL_HTTP_ADDR 環境変数の設定

### Gaps
- ポート番号typo（5800 vs 8500）→ 注意力の問題
- Consul の詳細な機能（KV store, ACL等）

---

## Shell Basics #linux #shell

**Level: Intermediate**

### Knows
- 基本的なコマンド操作
- パイプ、リダイレクト
- 環境変数の設定（export）

### Learned (2024-12-13)
- `:` (コロン) コマンドで出力なしコメント
- nmcli con mod でネットワーク設定変更

### Gaps
- エラーメッセージを丁寧に読む習慣が弱い
- manページや--helpの英語を読み飛ばす傾向

---

## General Observations

### Strengths
- 仮説を立てて検証する姿勢がある
- 自分の思考過程を言語化できる（: コマンドでコメント残してた）
- 「これ前にやったはず」という記憶はある（実行はできてないが）

### Weaknesses
- **エラーメッセージを読まない**: 最大の課題。情報は目の前にあるのに見てない
- **英語回避傾向**: ドキュメントに答えが書いてあっても読み飛ばす
- **機密情報管理**: トークンの保存場所を忘れる。chezmoiでの管理方針が曖昧

### Recommendations
1. エラー出たら、まず全文読んでから行動
2. 英語のエラーメッセージは翻訳してでも理解する
3. 機密情報は一元管理する場所を決める（Vault? パスワードマネージャー?）
4. TASK.md / PLANNING.md を実態と同期させる習慣

---

*Last updated: 2024-12-13 by Void*
