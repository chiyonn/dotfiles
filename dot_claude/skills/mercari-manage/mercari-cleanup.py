#!/usr/bin/env python3
"""メルカリ出品商品の自動削除スクリプト

更新日が2週間以上前の出品商品を自動削除する。
Playwright CLI のセッションが起動済み＆ログイン済みであることが前提。

Usage:
    # 事前にブラウザを起動してログイン状態にしておく
    # npx @playwright/cli open --browser firefox --headed
    # npx @playwright/cli state-load mercari
    python3 ~/.claude/skills/mercari-manage/mercari-cleanup.py
"""

import glob
import os
import re
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_cli(*args: str, timeout: int = 90) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["npx", "@playwright/cli", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"


def snapshot_content() -> str:
    """最新のスナップショットを取得して内容を返す"""
    _, output = run_cli("snapshot")
    # CLI出力からYAMLファイルパスを動的に取得
    match = re.search(r'\[Snapshot\]\(([^)]+\.yml)\)', output)
    if match:
        yml_path = match.group(1)
        if not os.path.isabs(yml_path):
            yml_path = os.path.normpath(os.path.join(os.getcwd(), yml_path))
        if os.path.exists(yml_path):
            with open(yml_path, "r") as f:
                return f.read()
    return output


def find_ref(content: str, pattern: str) -> str | None:
    """スナップショットからパターンにマッチする要素のrefを返す"""
    match = re.search(rf'{pattern}.*?\[ref=(\w+)\]', content)
    return match.group(1) if match else None


def collect_old_items() -> list[str]:
    """出品一覧ページから2週間以上前の商品IDを収集する（ページネーション対応）"""
    ok, _ = run_cli("goto", "https://jp.mercari.com/mypage/listings")
    if not ok:
        print("ERROR: 出品一覧ページに遷移できませんでした")
        sys.exit(1)

    time.sleep(3)
    seen: set[str] = set()
    all_items: list[str] = []

    while True:
        content = snapshot_content()
        items = _parse_old_items(content)
        for item_id in items:
            if item_id not in seen:
                seen.add(item_id)
                all_items.append(item_id)

        # 「もっと見る」ボタンがあればクリックして続行
        more_ref = find_ref(content, r'button "もっと見る"')
        if not more_ref:
            break

        print(f"  ({len(all_items)}件収集済み、もっと見る...)")
        run_cli("click", more_ref)
        time.sleep(3)

    return all_items


def _parse_old_items(content: str) -> list[str]:
    """スナップショットから2週間以上前の商品IDを抽出する"""
    url_pattern = re.compile(r"/url: /item/(m\d+)")
    date_pattern = re.compile(r"(\d+)(時間|日|か月)前に更新")

    lines = content.split("\n")
    items: list[str] = []
    current_item_id = None

    for line in lines:
        url_match = url_pattern.search(line)
        if url_match:
            current_item_id = url_match.group(1)
            continue

        date_match = date_pattern.search(line)
        if date_match and current_item_id:
            num = int(date_match.group(1))
            unit = date_match.group(2)

            is_old = False
            if unit == "か月":
                is_old = True
            elif unit == "日" and num >= 7:
                is_old = True

            if is_old:
                items.append(current_item_id)
            current_item_id = None

    return items


def delete_item(item_id: str) -> bool:
    """商品を1件削除する"""
    ok, output = run_cli("goto", f"https://jp.mercari.com/sell/edit/{item_id}")
    if not ok:
        if output == "TIMEOUT":
            print("(タイムアウト)", end=" ")
        return False
    time.sleep(4)

    # スナップショットから「この商品を削除する」ボタンのrefを取得
    content = snapshot_content()
    delete_ref = find_ref(content, r'button "この商品を削除する"')
    if not delete_ref:
        print("(削除ボタン不在)", end=" ")
        return False

    run_cli("click", delete_ref)
    time.sleep(1)

    # 確認ダイアログから「削除する」ボタンのrefを取得
    # 「この商品を削除する」ではなく、確認ダイアログ内の「削除する」だけのボタン
    content = snapshot_content()
    # find_all_refsで全マッチを取得し、完全一致の「削除する」を探す
    all_matches = re.findall(r'button "(.*?削除.*?)"[^\n]*?\[ref=(\w+)\]', content)
    confirm_ref = None
    for label, ref in all_matches:
        if label == "削除する":
            confirm_ref = ref
            break
    if not confirm_ref:
        print("(確認ボタン不在)", end=" ")
        return False

    run_cli("click", confirm_ref)
    time.sleep(2)

    # 削除成功の検証: Page URLが編集ページから離れていればOK
    _, output = run_cli("snapshot")
    url_match = re.search(r'Page URL:\s*(\S+)', output)
    if url_match and f"/sell/edit/{item_id}" not in url_match.group(1):
        return True

    print("(リダイレクト未確認)", end=" ")
    return False


def main():
    print("出品一覧を取得中...")
    items = collect_old_items()

    if not items:
        print("削除対象の商品はありません")
        return

    print(f"削除対象: {len(items)}件")

    ok_count = 0
    fail_count = 0

    for i, item_id in enumerate(items, 1):
        print(f"[{i}/{len(items)}] {item_id} ...", end=" ", flush=True)
        if delete_item(item_id):
            print("OK")
            ok_count += 1
        else:
            print("FAIL")
            fail_count += 1

    print(f"\n完了: {ok_count}件削除, {fail_count}件失敗")


if __name__ == "__main__":
    main()
