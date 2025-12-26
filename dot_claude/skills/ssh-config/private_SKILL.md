---
name: ssh-config
description: SSH接続時に参照。~/.ssh/configにホスト設定があるはずなので、IPアドレス直打ちではなくホスト名を使用すること。
---

# SSH Configuration Guide

## 基本方針

SSHで接続する際は、IPアドレスを直接指定せず `~/.ssh/config` に定義されたホスト名を使用すること。

```bash
# Good
ssh vp-cl-nmd-01

# Bad
ssh 192.168.40.216
ssh chiyonn@192.168.40.216 -i ~/.ssh/some-key
```

## 接続前の確認

1. `~/.ssh/config` を読んで、対象ホストの設定があるか確認
2. 設定があれば、そのHost名を使って接続
3. 設定がなければ、ユーザーに追加を促す

## 設定がない場合のテンプレート

```
Host {hostname}
    HostName {ip-address}
    User {username}
    IdentityFile ~/.ssh/{key-name}
    IdentitiesOnly yes
```

ユーザーに以下を確認してもらう：
- 接続先のIPアドレス
- 使用するSSH鍵
- ユーザー名
