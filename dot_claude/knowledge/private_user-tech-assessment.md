# User Tech Assessment

Voidによる技術力評価。

## Level Definition
- **Beginner**: 概念知ってる程度。コマンド使えない
- **Intermediate**: 基本操作可。トラブルシュートは弱い
- **Advanced**: 自力で問題解決。他人に教えられる

---

## AdGuard Home #networking #dns
**Level: Intermediate**

Query Log確認、`@@||domain^$important`で許可、API経由確認できる。モグラ叩き問題（1サイト=複数ドメイン依存）を理解。DNSは発信元サイト条件分岐不可と知ってる。

**Gaps**: フィルタリスト管理、一括許可ワークフロー

---

## DNS #linux #networking
**Level: Intermediate**

`dig @server domain +short`、`resolvectl status`、Split DNS概念を理解。

**Gaps**: dig出力詳細、resolved.conf、Split DNS永続化

---

## systemd #linux
**Level: Beginner**

systemctl基本(start/stop/status)、systemd-resolvedの存在は知ってる。

**Learned (2025-12-16)**:
- `journalctl -b -1` で前回ブートのログ確認
- `-b` に負の数を渡して過去ブート指定

**Gaps**: unitファイル、journalctl詳細オプション（--since, --until, -u など）

---

## Nomad #devops #hashicorp
**Level: Intermediate**

job run/status、Job定義構造、Consul連携。NOMAD_ADDRに`http://`と`:4646`必要。自力でヘルプ読んで修正できた。

**Gaps**: トークン管理場所の把握

---

## Consul #devops #hashicorp
**Level: Intermediate**

catalog services、サービスディスカバリ概念、API経由アクセス。

**Gaps**: KV store、ACL

---

## Traefik #devops #networking
**Level: Intermediate**

TLS終端、Static/Dynamic config、File Provider、entryPoints(web=80, websecure=443)、certResolver。

**Gaps**: middleware、複雑なルーティング、dashboard

---

## Shell Basics #linux #shell
**Level: Intermediate**

パイプ、リダイレクト、環境変数。`head -1`、`2>&1`の構文。スペック確認コマンド。

**Gaps**: エラーメッセージ読まない、英語--help読み飛ばす、シェルスクリプト弱い

---

## sway/i3 #linux #desktop
**Level: Intermediate**

swaymsg(get_tree, subscribe)、criteria、mark、scratchpad、`floating enable`が`move position`の前提。

**Gaps**: IPC全般

---

## Wayland/PipeWire #linux #desktop
**Level: Beginner**

xdg-desktop-portal-wlr、縦置きモニター画面共有問題、OBS仮想カメラ回避策。

**Gaps**: PipeWire詳細、portal設定

---

## Package Management #linux #fedora #debian
**Level: Intermediate**

dnf基本、RPM Fusion、akmod。**`ffmpeg-free` vs `ffmpeg`**（パテント制限）を理解。`--allowerasing`でパッケージ置換。Firefoxはシステムコーデック依存、Braveは自前。

**Learned (2025-12-16)**:
- `dpkg -l` のステータス文字: `ii`=installed, `rc`=removed but config remains
- `apt remove` vs `apt purge` の違い

**Gaps**: dnf詳細オプション、rpm直接操作、dpkg詳細

---

## Kernel Modules #linux
**Level: Beginner**

lsmod、modprobe、v4l2loopback用途。

**Gaps**: パラメータ、永続化設定

---

## Firefox Internals #browser
**Level: Beginner**

DoH(`network.trr.mode`: 0=無効, 3=強制, 5=明示無効)、`about:networking#dns`、`--safe-mode`、メディア設定。Firefoxはffmpegに依存。

**Gaps**: about:config詳細、プロファイル管理

---

## LVM #linux #storage
**Level: Intermediate**

PV→VG→LV→FS→mount→fstab のフロー理解。`pvcreate`, `vgcreate`, `lvcreate` 操作可能。`vgmerge`/`vgrename` で VG 統合・リネーム。`lvextend -L +XXX` で拡張。`wipefs` でシグネチャ削除。複数 PV を1つの VG に統合するリスク（1台死亡で LV 道連れ）を理解した上で設計判断できる。

**Learned (2025-12-15)**:
- fdisk は GPT 対応済み、非推奨ではない
- HDD 容量: マーケティング (10^9) vs OS表示 (2^30)
- `lvextend -L 250G` vs `-L +250G` の違い

**Gaps**: LV 縮小 (lvreduce)、スナップショット、thin provisioning

---

## NetworkManager #linux #networking
**Level: Beginner**

`nmcli device status` でデバイス状態確認。NetworkManager への移行は実施済み。

**Learned (2025-12-16)**:
- ifupdown との共存は危険（両方が同じ NIC を管理しようとして競合）
- 移行時は古いネットワーク管理システムを完全に無効化/削除すべき
- dhclient が裏で動いてると DHCP リクエストが競合する

**Gaps**: nmcli 詳細操作、connection profile 管理、VPN 設定

---

## General Observations

### Strengths
- 仮説→検証の姿勢
- 思考過程を言語化できる
- YAGNI判断できる
- ギブアップを言える
- ヘルプ読んで自己修正（`--help | head` で構文確認する習慣）
- 段階的トラブルシュート
- 矛盾を指摘できる
- リスク考慮してから設計判断（「壊れたらどうなる？」を先に聞ける）

### Weaknesses
- **エラーメッセージ読まない**: 最大の課題（改善の兆しあり）
- **英語回避**: ドキュメント読み飛ばす
- **typo常習犯**: 同一セッションで複数回やらかす
- 機密情報管理が曖昧
- chezmoi apply忘れ
- ドキュメント鵜呑み

### Recommendations
1. エラー出たらまず全文読む
2. 英語は翻訳してでも理解
3. 機密情報は一元管理
4. **コマンド打つ前に一呼吸**（typo対策）

---

*Last updated by Void: 2025-12-16*
