#!/usr/bin/env python3
"""メルカリ出品商品の自動削除スクリプト

更新日が2週間以上前の出品商品を自動削除する。
Playwright CLI のセッションが起動済み＆ログイン済みであることが前提。

Usage:
    # 事前にブラウザを起動してログイン状態にしておく
    # npx @playwright/cli open --browser firefox --headed
    # npx @playwright/cli state-load mercari
    python3 ~/Documents/mercari-cleanup.py
"""

import re
import subprocess
import sys
import time


def run_cli(*args: str) -> tuple[bool, str]:
    result = subprocess.run(
        ["npx", "@playwright/cli", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = result.stdout + result.stderr
    return result.returncode == 0, output


def collect_old_items() -> list[str]:
    """出品一覧ページから2週間以上前の商品IDを収集する"""
    ok, _ = run_cli("goto", "https://jp.mercari.com/mypage/listings")
    if not ok:
        print("ERROR: 出品一覧ページに遷移できませんでした")
        sys.exit(1)

    time.sleep(2)
    ok, _ = run_cli("snapshot")
    if not ok:
        print("ERROR: スナップショット取得に失敗しました")
        sys.exit(1)

    # 最新のスナップショットファイルを取得
    import glob
    snapshots = sorted(glob.glob(".playwright-cli/page-*.yml"))
    if not snapshots:
        print("ERROR: スナップショットファイルが見つかりません")
        sys.exit(1)

    with open(snapshots[-1], "r") as f:
        content = f.read()

    # item URL と更新日のペアを抽出
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
            elif unit == "日" and num >= 14:
                is_old = True

            if is_old:
                items.append(current_item_id)
            current_item_id = None

    return items


def delete_item(item_id: str) -> bool:
    """商品を1件削除する"""
    ok, _ = run_cli("goto", f"https://jp.mercari.com/sell/edit/{item_id}")
    if not ok:
        return False
    time.sleep(1)

    run_cli("snapshot")

    # 「この商品を削除する」をクリック
    ok, _ = run_cli(
        "eval",
        "await page.getByRole('button', { name: 'この商品を削除する' }).click()",
    )
    if not ok:
        return False
    time.sleep(0.5)

    run_cli("snapshot")

    # 確認ダイアログで「削除する」をクリック
    ok, _ = run_cli(
        "eval",
        "await page.getByRole('dialog').getByRole('button', { name: '削除する' }).click()",
    )
    if not ok:
        return False

    time.sleep(1)
    return True


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
