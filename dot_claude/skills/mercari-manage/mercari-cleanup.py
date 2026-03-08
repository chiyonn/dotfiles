#!/usr/bin/env python3
"""メルカリ出品商品の自動削除スクリプト

更新日が2週間以上前の出品商品を自動削除する。
Playwright CLI のセッションが起動済み＆ログイン済みであることが前提。

重要: eval コマンドは page.evaluate() (ブラウザJS) にマッピングされるため
Playwright API は使えない。すべて snapshot → ref → CLI コマンドで操作する。

Usage:
    # 事前にブラウザを起動してログイン状態にしておく
    # npx @playwright/cli open --browser firefox --headed
    # npx @playwright/cli state-load mercari
    python3 -u ~/.claude/skills/mercari-manage/mercari-cleanup.py
"""

import glob
import re
import subprocess
import sys
import time


def run_cli(*args: str, timeout: int = 30) -> tuple[bool, str]:
    result = subprocess.run(
        ["npx", "@playwright/cli", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output = result.stdout + result.stderr
    has_error = result.returncode != 0 or "### Error" in output
    return not has_error, output


def snapshot() -> str:
    """スナップショットを取得して内容を返す"""
    _, output = run_cli("snapshot")
    snapshots = sorted(glob.glob(".playwright-cli/page-*.yml"))
    if not snapshots:
        return output
    with open(snapshots[-1], "r") as f:
        return output + "\n" + f.read()


def find_ref(content: str, pattern: str) -> str | None:
    match = re.search(rf'{pattern}.*?\[ref=(\w+)\]', content)
    return match.group(1) if match else None


def collect_old_items() -> list[str]:
    """出品一覧ページから2週間以上前の商品IDを収集する。
    「もっと見る」ボタンがあれば全件読み込むまでクリックを繰り返す。
    """
    ok, _ = run_cli("goto", "https://jp.mercari.com/mypage/listings", timeout=60)
    if not ok:
        print("ERROR: 出品一覧ページに遷移できませんでした")
        sys.exit(1)
    time.sleep(3)

    all_items: list[str] = []

    while True:
        snap = snapshot()
        items = _extract_old_items(snap)
        for item_id in items:
            if item_id not in all_items:
                all_items.append(item_id)

        # 「もっと見る」ボタンを探す
        more_ref = find_ref(snap, r'button "もっと見る"')
        if not more_ref:
            break

        print(f"  ({len(all_items)}件収集済み、もっと見る...)")
        ok, _ = run_cli("click", more_ref)
        if not ok:
            break
        time.sleep(2)

    return all_items


def _extract_old_items(content: str) -> list[str]:
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
            elif unit == "日" and num >= 14:
                is_old = True

            if is_old:
                items.append(current_item_id)
            current_item_id = None

    return items


def delete_item(item_id: str) -> bool:
    """商品を1件削除する"""
    ok, _ = run_cli("goto", f"https://jp.mercari.com/sell/edit/{item_id}", timeout=60)
    if not ok:
        return False
    time.sleep(2)

    # 「この商品を削除する」ボタンを探してクリック
    snap = snapshot()
    ref = find_ref(snap, r'button "この商品を削除する"')
    if not ref:
        print("(削除ボタンなし)", end=" ")
        return False
    ok, _ = run_cli("click", ref)
    if not ok:
        return False
    time.sleep(1)

    # 確認ダイアログの「削除する」ボタンをクリック
    snap = snapshot()
    # dialog 配下の「削除する」ボタンを探す
    dialog_match = re.search(
        r'dialog.*?button "削除する".*?\[ref=(\w+)\]', snap, re.DOTALL
    )
    ref = dialog_match.group(1) if dialog_match else None
    if not ref:
        ref = find_ref(snap, r'button "削除する"')
    if not ref:
        print("(確認ダイアログなし)", end=" ")
        return False
    ok, _ = run_cli("click", ref)
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
