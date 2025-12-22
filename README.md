# Dotfiles

chezmoiで管理してる個人用dotfiles。

## Zsh設定の使い分け

### `exports.zsh.tmpl` (chezmoi管理)
- 全デバイスで共通の環境変数
- OS差分はtemplateで吸収（例: ZK_NOTEBOOK_DIR）
- 秘密情報ではないが、環境によって異なる設定

### `.zshenv` (chezmoi ignore、手動管理)
- 秘密情報（トークン、パスワードなど）
- 完全にマシン固有の設定
- `.zshenv.example` をコピーして使う

**初回セットアップ:**
```bash
cp ~/.zshenv.example ~/.zshenv
# 実際の値を記入
vim ~/.zshenv
```

## `.chezmoiignore`について

一部のファイルはchezmoiの管理対象から除外してる。理由は以下：

### `.config/claude/settings.json`
Claude CLIが実行時に自動的に設定を書き換えるため、chezmoi管理すると常に差分が出て警告がウザい。
他端末との設定共有は諦めて、アプリ側の自動更新に任せる方針。

必要に応じて手動で設定を揃えるか、初回セットアップ時だけコピーすればOK。
