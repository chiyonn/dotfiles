#!/usr/bin/env python3
"""メルカリ出品商品の自動削除スクリプト

更新日が2週間以上前の出品商品を自動削除する。
Playwright CLI のセッションが起動済み＆ログイン済みであることが前提。

Usage:
    python3 ~/.claude/skills/mercari-manage/mercari-cleanup.py
"""

import re
import sys

from base import PlaywrightClient


class MercariCleaner:
    """古い出品を自動検出・削除する。"""

    LISTINGS_URL = "https://jp.mercari.com/mypage/listings"
    EDIT_URL = "https://jp.mercari.com/sell/edit/{item_id}"
    STALE_DAYS = 14

    def __init__(self, client: PlaywrightClient | None = None) -> None:
        self._cli = client or PlaywrightClient(default_timeout=90)

    def run(self) -> None:
        """メインフロー: 古い出品を収集→削除。"""
        print("出品一覧を取得中...")
        items = self._collect_old_items()

        if not items:
            print("削除対象の商品はありません")
            return

        print(f"削除対象: {len(items)}件")
        ok_count = 0
        fail_count = 0

        for i, item_id in enumerate(items, 1):
            print(f"[{i}/{len(items)}] {item_id} ...", end=" ", flush=True)
            if self._delete_item(item_id):
                print("OK")
                ok_count += 1
            else:
                print("FAIL")
                fail_count += 1

        print(f"\n完了: {ok_count}件削除, {fail_count}件失敗")

    def _collect_old_items(self) -> list[str]:
        """出品一覧から2週間以上前の商品IDを収集する（ページネーション対応）。"""
        if not self._cli.goto(self.LISTINGS_URL):
            print("ERROR: 出品一覧ページに遷移できませんでした")
            sys.exit(1)

        self._cli.wait(3)
        seen: set[str] = set()
        all_items: list[str] = []

        while True:
            content = self._cli.snapshot()
            for item_id in self._parse_old_items(content):
                if item_id not in seen:
                    seen.add(item_id)
                    all_items.append(item_id)

            more_ref = self._cli.find_ref(content, r'button "もっと見る"')
            if not more_ref:
                break

            print(f"  ({len(all_items)}件収集済み、もっと見る...)")
            self._cli.click(more_ref)
            self._cli.wait(3)

        return all_items

    def _parse_old_items(self, content: str) -> list[str]:
        """スナップショットから古い商品IDを抽出する。"""
        url_pat = re.compile(r"/url: /item/(m\d+)")
        date_pat = re.compile(r"(\d+)(時間|日|か月)前に更新")

        items: list[str] = []
        current_id: str | None = None

        for line in content.split("\n"):
            url_m = url_pat.search(line)
            if url_m:
                current_id = url_m.group(1)
                continue

            date_m = date_pat.search(line)
            if date_m and current_id:
                num = int(date_m.group(1))
                unit = date_m.group(2)
                is_old = unit == "か月" or (unit == "日" and num >= self.STALE_DAYS)
                if is_old:
                    items.append(current_id)
                current_id = None

        return items

    def _delete_item(self, item_id: str) -> bool:
        """商品を1件削除する。"""
        url = self.EDIT_URL.format(item_id=item_id)
        ok, output = self._cli.run("goto", url, timeout=90)
        if not ok:
            if output == "TIMEOUT":
                print("(タイムアウト)", end=" ")
            return False
        self._cli.wait(4)

        content = self._cli.snapshot()
        delete_ref = self._cli.find_ref(content, r'button "この商品を削除する"')
        if not delete_ref:
            print("(削除ボタン不在)", end=" ")
            return False

        self._cli.click(delete_ref)
        self._cli.wait(1)

        content = self._cli.snapshot()
        confirm_ref = self._cli.find_ref(
            content, r'dialog.*\n.*\n.*\n.*button "削除する"'
        )
        if not confirm_ref:
            confirm_ref = self._cli.find_ref(content, r'button "削除する"')
        if not confirm_ref:
            print("(確認ボタン不在)", end=" ")
            return False

        self._cli.click(confirm_ref)
        self._cli.wait(2)

        content = self._cli.snapshot()
        if "/mypage/listings" in content or "出品した商品" in content:
            return True

        print("(リダイレクト未確認)", end=" ")
        return False


if __name__ == "__main__":
    MercariCleaner().run()
