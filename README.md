# Dotfiles

chezmoiで管理してる個人用dotfiles。

## `.chezmoiignore`について

一部のファイルはchezmoiの管理対象から除外してる。理由は以下：

### `.config/claude/settings.json`
Claude CLIが実行時に自動的に設定を書き換えるため、chezmoi管理すると常に差分が出て警告がウザい。
他端末との設定共有は諦めて、アプリ側の自動更新に任せる方針。

必要に応じて手動で設定を揃えるか、初回セットアップ時だけコピーすればOK。
