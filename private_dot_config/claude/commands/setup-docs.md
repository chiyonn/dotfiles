---
name: setup-docs
description: PLANNING.mdとTASK.mdを作成してプロジェクトドキュメント体制を整備
---
# プロジェクトドキュメント作成コマンド

技術設計書(PLANNING.md)とタスク管理ファイル(TASK.md)を作成します。

## 実行手順

### 1. 既存ファイル確認
```bash
ls -la PLANNING.md TASK.md 2>/dev/null
```
- 既存ファイルがある場合は上書き確認

### 2. PLANNING.md 作成

以下の構成で作成:

```markdown
# PLANNING.md - 技術設計・運用方針

## Technology Stack

### [技術名]
- **選定理由**: なぜこれを選んだか
- **代替案**: 検討した他の選択肢
- **トレードオフ**: 制約や課題
- **決定日**: YYYY-MM-DD

(既存のプロジェクト構成を分析して記載)

## Architecture Decisions

### [設計決定]
- **背景**: 何の問題を解決するか
- **選択肢**: 検討した手法
- **決定**: 採用した方法と理由

## Deployment Strategy

(CI/CDパイプライン、デプロイフロー等)

## Performance Targets

- 目標値を具体的に記載

## Security Considerations

- セキュリティ上の注意点
```

### 3. TASK.md 作成

以下の構成で作成:

```markdown
# TASK.md - タスク管理

## Status Legend
- [ ] Todo
- [x] Done
- [>] In Progress
- [!] Blocked
- [~] Cancelled

## Active Tasks (優先度高)

(現在進行中のタスクがあれば記載)

## Backlog

### Features
- [ ] #001 [機能名]

### Bugs
- [ ] #050 [バグ内容]

### Refactoring
- [ ] #100 [リファクタリング内容]

## Completed (直近30件)

(過去の完了タスク)
```

## 既存ドキュメントの活用

- CLAUDE.mdが存在する場合、技術スタック情報を参照して初期内容を生成
- README.mdから技術スタックやアーキテクチャ情報を抽出
- package.jsonから依存関係を分析

## 既存ファイルがある場合の対応

### 新規作成モード
- ファイルが存在しない場合、基本構造を作成
- CLAUDE.md/README.md/package.jsonから情報を自動抽出

### 更新モード
- **ファイルが既に存在する場合は上書きせず、セクション単位で追加・更新**
- 既存内容を読み込んで不足しているセクションを提案
- 例1: PLANNING.mdに新しい技術スタックが追加されたら、該当セクションのみ追記
- 例2: TASK.mdに完了したタスクを`## Completed`へ移動
- 例3: git logから新しいタスクを検出してBacklogに追加提案

### 更新の判断基準
- **PLANNING.md**: package.json変更、新しいアーキテクチャ決定があれば追加
- **TASK.md**:
  - Active Tasksのステータス更新(TodoWrite参照)
  - git log未反映のタスクを提案
  - 完了タスクのアーカイブ(100件超えたら別ファイル提案)

### 実行フロー
1. 既存ファイル存在チェック
2. 存在する場合:
   - ファイル内容を読み込み
   - 不足セクション/古い情報を検出
   - 更新内容をユーザーに確認
   - 承認後に該当セクションのみ編集
3. 存在しない場合:
   - 基本構造を作成
   - 他のドキュメントから情報抽出

## 注意事項

- CLAUDE.mdとの重複を避ける(役割分担を意識)
- 完璧を目指さず、8割の精度でスタート
- ユーザー確認なしで上書きしない
