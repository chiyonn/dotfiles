# TODO

## NFS マウント移行

### 目標
SMBの代わりにNFSを使ってmacOSとLinux間でNASマウントポイントを統一する。

### 現状
- **macOS**: `/Volumes/notes` (SMBマウント)
- **目標**: `/mnt/nas/notes` (NFSマウント、macOS/Linux間で統一)

### タスク
- [ ] NASでNFSサーバーをセットアップ
- [ ] macOSで `/mnt/nas/notes` マウントポイントを作成
- [ ] macOSでNFSマウントを設定 (`/etc/fstab` または automount経由)
- [ ] macOSでNFSマウントをテスト
- [ ] exports.zshの `ZK_NOTEBOOK_DIR` を `/Volumes/notes` から `/mnt/nas/notes` に更新
- [ ] 新規Linuxマシンセットアップ時にNFSマウントを設定
- [ ] 必要に応じて既存データを `/Volumes/notes` から新しいマウントポイントに移行

### メモ
- クロスプラットフォームの互換性向上のためNFSを使用
- 設定管理をシンプルにするため、macOSとLinuxで同じマウントポイントパスを使う
