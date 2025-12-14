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

### Learned (2024-12-14)
- **初めて自力で `nomad job run` 実行成功**
- `nomad job exec` と間違えたが、ヘルプ読んで自己修正
- NOMAD_ADDR の `http://` 忘れ → 今回は自力で思い出せた

### Gaps
- 機密情報（トークン）の管理場所を把握してなかった → まだ改善の余地あり（SSHでMac探しに行った）

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

## Traefik #devops #networking

**Level: Beginner → Intermediate (進行中)**

### Knows
- Traefikがリバースプロキシであること
- Consulタグベースルーティングの存在

### Learned (2024-12-14)
- **TLS終端**の概念（TraefikでHTTPS受けて、バックエンドにはHTTP転送）
- Static config vs Dynamic config の違い
- **File Provider**: Nomad外サービスをTraefikに教える静的設定
- entryPoints: `web`=80, `websecure`=443
- `certResolver: letsencrypt` でTLS証明書自動取得
- traefik.nomad内でFile Provider設定がtemplate blockで書かれてる構造
- ルーティング設定の書き方（rule, service, entryPoints, tls）

### Gaps
- Traefik middlewareの活用（redirect-to-https等）
- 複雑なルーティングルール
- Traefik dashboard の見方

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

### Learned (2024-12-14)
- `head -1` のハイフン必要性（`head 1`はエラー）
- `2>&1` の正しい順番（`2&>1`ではない）
- `-yq` vs `-y -q` はコマンド側が解釈（shell関係なし）
- zshでの `$(...)` はエスケープ不要（変にいじると壊れる）
- `/proc/cpuinfo`, `free -h`, `lspci` でスペック確認

### Gaps
- エラーメッセージを丁寧に読む習慣が弱い
- manページや--helpの英語を読み飛ばす傾向
- シェルスクリプト書く力が弱い（今回ギブアップ）

---

## sway/i3 Window Manager #linux #desktop

**Level: Beginner → Intermediate (進行中)**

### Knows
- swayの基本操作、keybinds設定
- workspaceの概念

### Learned (2024-12-14)
- `swaymsg -t get_tree` でウィンドウツリー確認
- `swaymsg -t subscribe '["window"]'` でイベント監視
- criteriaの使い方 (`[app_id="..."]`, `[con_mark="..."]`)
- markの概念（ウィンドウに名札をつける）
- scratchpadの運用方法
- `floating enable` が `move position` の前提条件
- `exec` vs `exec_always` の違い
- 複数ウィンドウでcriteria衝突する問題とmark回避策

### Gaps
- swaymsg のその他のメッセージタイプ
- IPC全般の理解

---

## Wayland/PipeWire #linux #desktop

**Level: Beginner**

### Knows
- Waylandがディスプレイサーバーであること
- PipeWireが音声/映像のルーティングすること

### Learned (2024-12-14)
- xdg-desktop-portal-wlrの役割（画面共有の仲介）
- PipeWireのtransform情報（回転情報のメタデータ）
- 縦置きモニターの画面共有問題（ブラウザ側未対応）
- OBS仮想カメラ (v4l2loopback) での回避策

### Gaps
- PipeWireの詳細な仕組み
- xdg-desktop-portalの設定

---

## Package Management (dnf/rpm) #linux #fedora

**Level: Beginner → Intermediate (進行中)**

### Knows
- `dnf install`, `dnf search` の基本

### Learned (2024-12-14)
- `-y` (自動yes), `-q` (quiet) オプション
- RPM Fusionリポジトリの追加方法
- `akmod` の役割（カーネル更新時に自動ビルド）
- `akmods --force` でビルドトリガー
- カーネルバージョンとkernel-develの対応問題

### Gaps
- dnfの詳細オプション
- rpm直接操作

---

## Kernel Modules #linux

**Level: Beginner**

### Knows
- カーネルモジュールという概念がある

### Learned (2024-12-14)
- `lsmod` でロード済みモジュール確認
- `modprobe` でモジュールロード
- v4l2loopbackの用途（仮想カメラデバイス）

### Gaps
- モジュールパラメータ
- 永続化設定 (/etc/modules-load.d/)

---

## General Observations

### Strengths
- 仮説を立てて検証する姿勢がある
- 自分の思考過程を言語化できる（: コマンドでコメント残してた）
- 「これ前にやったはず」という記憶はある（実行はできてないが）
- **YAGNIの判断ができる**: 「退避機能は使用頻度低い」と削った (2024-12-14)
- **ギブアップを言える**: 無理なものは無理と正直に言える (2024-12-14)
- **エラーから学べた**: `floating enable`必要と自分で理解 (2024-12-14)
- **ヘルプを読んで自己修正**: `nomad job exec` → ヘルプ確認 → `run` を発見 (2024-12-14)
- **段階的トラブルシュート**: ping → ポート確認 → HTTP vs HTTPS問題発見、と順序立てて調査できた (2024-12-14)

### Weaknesses
- **エラーメッセージを読まない**: 最大の課題。情報は目の前にあるのに見てない → ただし改善の兆し！
- **英語回避傾向**: ドキュメントに答えが書いてあっても読み飛ばす
- **機密情報管理**: トークンの保存場所を忘れる。chezmoiでの管理方針が曖昧
- **chezmoi apply忘れ**: 編集したけど反映されてなかった (2024-12-14)
- **構文の細かいミス**: `head -1`, `2>&1` など (2024-12-14)
- **ドキュメント鵜呑み問題**: CLAUDE.mdに「3000番」と書いてあったのを信じてた（実際は80番） (2024-12-14)

### Recommendations
1. エラー出たら、まず全文読んでから行動
2. 英語のエラーメッセージは翻訳してでも理解する
3. 機密情報は一元管理する場所を決める（Vault? パスワードマネージャー?）
4. TASK.md / PLANNING.md を実態と同期させる習慣
5. chezmoi編集後は `chezmoi apply` を習慣化する
6. ドキュメントに書いてあっても実機で確認する習慣をつける

---

*Last updated: 2024-12-14 by Void*
