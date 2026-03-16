#!/usr/bin/env python3
"""メルカリ自動出品スクリプト

Google SheetsのCSVから在庫情報を取得し、有効な商品を1品ずつ出品する。
Playwright CLI のセッションが起動済み＆ログイン済みであることが前提。

Usage:
    python3 -u ~/.claude/skills/mercari-manage/mercari-listing.py
"""

import csv
import io
import os
import re
import sys
import urllib.request
from dataclasses import dataclass

from base import PlaywrightClient

SPREADSHEET_ID = os.environ.get("MERCARI_SPREADSHEET_ID", "")
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
ASSETS_DIR = os.path.expanduser("~/.claude/skills/mercari-manage/assets")
ASSETS_SYMLINK_NAME = ".mercari-assets"

SHIPPING_METHOD_MAP = {
    "郵便（定型、定形外、書留など）": "郵便(定形、定形外、書留など)",
}


@dataclass
class Product:
    asin: str
    name: str
    category: str
    brand: str
    condition: str
    description: str
    shipping_fee: str
    shipping_method: str
    ship_from: str
    ship_days: str
    price: str
    stock: str
    notes: str


class MercariLister:
    """Google SheetsのCSVから商品を自動出品する。"""

    CREATE_URL = "https://jp.mercari.com/sell/create"

    def __init__(self, client: PlaywrightClient | None = None) -> None:
        self._cli = client or PlaywrightClient()

    # ------------------------------------------------------------------
    # 在庫CSV
    # ------------------------------------------------------------------

    def fetch_inventory(self) -> list[Product]:
        """Google SheetsからCSVを取得し、有効な商品リストを返す。"""
        print("在庫CSVを取得中...")
        response = urllib.request.urlopen(CSV_URL)
        content = response.read().decode("utf-8")
        reader = csv.reader(io.StringIO(content))
        next(reader)  # skip header

        products = []
        for row in reader:
            if len(row) < 12:
                continue
            p = Product(
                asin=row[0].strip(),
                name=row[1].strip(),
                category=row[2].strip(),
                brand=row[3].strip(),
                condition=row[4].strip(),
                description=row[5].strip(),
                shipping_fee=row[6].strip(),
                shipping_method=row[7].strip(),
                ship_from=row[8].strip(),
                ship_days=row[9].strip(),
                price=row[10].strip(),
                stock=row[11].strip(),
                notes=row[12].strip() if len(row) > 12 else "",
            )
            if self._is_valid(p):
                products.append(p)
        return products

    @staticmethod
    def _is_valid(p: Product) -> bool:
        if not p.name or not p.description or not p.price or not p.category:
            return False
        try:
            return int(p.stock) > 0
        except (ValueError, TypeError):
            return False

    # ------------------------------------------------------------------
    # 画像
    # ------------------------------------------------------------------

    @staticmethod
    def _image_dir_id(product: Product) -> str:
        if product.asin:
            return product.asin
        return re.sub(r"[\W]", "_", product.name[:20]).strip("_")

    def _get_image_paths(self, product: Product) -> list[str]:
        asset_dir = os.path.join(ASSETS_DIR, self._image_dir_id(product))
        if not os.path.isdir(asset_dir):
            return []
        images = sorted(
            f
            for f in os.listdir(asset_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
        )
        return [os.path.join(asset_dir, img) for img in images]

    @staticmethod
    def _ensure_assets_symlink() -> str:
        symlink_path = os.path.join(os.getcwd(), ASSETS_SYMLINK_NAME)
        if not os.path.exists(symlink_path):
            os.symlink(ASSETS_DIR, symlink_path)
        return symlink_path

    def _upload_images(self, image_paths: list[str]) -> bool:
        symlink_path = self._ensure_assets_symlink()

        for path in image_paths:
            upload_path = path.replace(ASSETS_DIR, symlink_path)

            snap = self._cli.snapshot()
            ref = self._cli.find_ref(snap, r"button.*画像を選択する")
            if not ref:
                print("    画像選択ボタンが見つからない")
                return False

            if not self._cli.click(ref):
                print(f"    画像選択ボタンのクリック失敗")
                return False
            self._cli.wait(0.5)

            if not self._cli.upload(upload_path):
                print(f"    upload fail: {os.path.basename(path)}")
                return False
            self._cli.wait(1)

            # AI出品サポートのモーダルが出ていたらDOMごと削除
            snap = self._cli.snapshot()
            if "dialog" in snap.lower() and "出品画像" in snap:
                self._cli.run(
                    "eval",
                    "() => (document.getElementById('ds-portal-wrapper')"
                    " || document.querySelector('[role=dialog]')"
                    "?.closest('[id*=portal], [class*=portal], [class*=overlay]')"
                    " || document.querySelector('[role=dialog]'))?.remove()",
                )
                self._cli.wait(0.5)
        return True

    # ------------------------------------------------------------------
    # フォーム入力ヘルパー
    # ------------------------------------------------------------------

    def _select_category(self, category_str: str) -> bool:
        parts = [p.strip() for p in category_str.split(">")]

        snap = self._cli.snapshot()
        ref = self._cli.find_ref(snap, r'link "カテゴリーを選択')
        if not ref:
            cat_section = re.search(
                r'カテゴリー.*?link "変更する".*?\[ref=(\w+)\]', snap, re.DOTALL
            )
            if cat_section:
                ref = cat_section.group(1)
        if not ref:
            print("  WARN: カテゴリーリンクが見つからない")
            return False
        if not self._cli.click(ref):
            return False
        self._cli.wait(1)

        for part in parts:
            snap = self._cli.snapshot()
            ref = None
            for match_text, match_ref in self._cli.find_all_refs(snap, r'link "'):
                link_match = re.search(r'link "([^"]+)"', match_text)
                if link_match and link_match.group(1).strip() == part.strip():
                    ref = match_ref
                    break
            if not ref:
                escaped = re.escape(part.strip())
                ref = self._cli.find_ref(snap, rf'link "{escaped}')
            if not ref:
                print(f"  WARN: カテゴリ '{part}' が見つからない")
                return False
            if not self._cli.click(ref):
                print(f"  WARN: カテゴリ '{part}' のクリック失敗")
                return False
            self._cli.wait(0.5)

        return True

    def _select_condition(self, condition: str) -> bool:
        snap = self._cli.snapshot()

        # パネルが既に開いている場合（heading "商品の状態" がある）
        panel_open = 'heading "商品の状態"' in snap

        if not panel_open:
            ref = self._cli.find_ref(snap, r'link "商品の状態を選択')
            if not ref:
                cond_section = re.search(
                    r'商品の状態.*?link "変更する".*?\[ref=(\w+)\]', snap, re.DOTALL
                )
                if cond_section:
                    ref = cond_section.group(1)
            if not ref:
                print("  WARN: 商品状態リンクが見つからない")
                return False
            if not self._cli.click(ref):
                return False
            self._cli.wait(1)
            snap = self._cli.snapshot()

        escaped = re.escape(condition)
        ref = self._cli.find_ref(snap, rf'link "{escaped}')
        if not ref:
            ref = self._cli.find_ref(snap, rf'link ".*{escaped}')
        if not ref:
            print(f"  WARN: 商品状態 '{condition}' が見つからない")
            return False
        return self._cli.click(ref)

    def _select_shipping_method(self, method: str) -> bool:
        form_method = SHIPPING_METHOD_MAP.get(method, method)
        snap = self._cli.snapshot()

        # すでに正しい配送方法が選択済みならスキップ
        if form_method in snap or method in snap:
            ship_section = re.search(
                r"配送の方法.*?(?:変更する|選択する)", snap, re.DOTALL
            )
            if ship_section and (
                form_method in ship_section.group() or method in ship_section.group()
            ):
                return True

        ref = self._cli.find_ref(snap, r'link "配送の方法を選択')
        if not ref:
            ship_section = re.search(
                r'配送の方法.*?link "変更する".*?\[ref=(\w+)\]', snap, re.DOTALL
            )
            if ship_section:
                ref = ship_section.group(1)
        if not ref:
            print("  WARN: 配送方法リンクが見つからない")
            return False
        if not self._cli.click(ref):
            return False
        self._cli.wait(1)

        # 「その他」展開ボタン
        snap = self._cli.snapshot()
        ref = self._cli.find_ref(snap, r"button.*その他")
        if ref:
            self._cli.click(ref)
            self._cli.wait(0.5)
            snap = self._cli.snapshot()

        escaped = re.escape(form_method)
        ref = self._cli.find_ref(snap, rf'radio "{escaped}')
        if not ref:
            ref = self._cli.find_ref(snap, rf'radio ".*{escaped}')
        if not ref:
            ref = self._cli.find_ref(snap, rf'link ".*{escaped}')
        if not ref:
            print(f"  WARN: 配送方法 '{form_method}' が見つからない")
            return False

        if not self._cli.click(ref):
            return False
        self._cli.wait(0.5)

        snap = self._cli.snapshot()
        ref = self._cli.find_ref(snap, r'button "更新する"')
        if ref:
            if not self._cli.click(ref):
                return False

        return True

    # ------------------------------------------------------------------
    # 出品フロー
    # ------------------------------------------------------------------

    def _list_one(self, product: Product) -> bool:
        """商品を1件出品する。"""
        print("  [1/9] 出品ページ遷移...", flush=True)
        if not self._cli.goto(self.CREATE_URL):
            print("  FAIL: 出品ページ遷移")
            return False
        self._cli.wait(3)

        # AI出品サポートをOFFにする
        print("  [2/9] AI出品サポートOFF...", flush=True)
        snap = self._cli.snapshot()
        if "dialog" in snap and "AI出品サポート" in snap:
            close_ref = self._cli.find_ref(snap, r'button "閉じる"')
            if close_ref:
                self._cli.click(close_ref)
                self._cli.wait(0.5)
                snap = self._cli.snapshot()

        switch_match = re.search(
            r'switch ".*?自動入力.*?"(.*?)\[ref=(\w+)\]', snap
        )
        if switch_match:
            attrs = switch_match.group(1)
            switch_ref = switch_match.group(2)
            if "[checked]" in attrs and "[disabled]" not in attrs:
                self._cli.click(switch_ref)
                self._cli.wait(0.5)

        # 画像アップロード
        print("  [3/9] 画像アップロード...", flush=True)
        self._cli.press("Home")
        self._cli.wait(0.3)
        images = self._get_image_paths(product)
        if not images:
            print(f"  SKIP: 画像なし ({self._image_dir_id(product)})")
            return False
        if not self._upload_images(images):
            print("  FAIL: 画像アップロード")
            return False
        self._cli.wait(2)

        # 商品名 (40文字制限)
        print("  [4/9] 商品名入力...", flush=True)
        snap = self._cli.snapshot()
        name_section = re.search(
            r'heading "商品名".*?textbox.*?\[ref=(\w+)\]', snap, re.DOTALL
        )
        ref = name_section.group(1) if name_section else None
        if not ref:
            ref = self._cli.find_ref(snap, r"textbox.*\[ref=")
        if not ref:
            print("  FAIL: 商品名テキストボックスが見つからない")
            return False
        if not self._cli.fill(ref, product.name[:40]):
            print("  FAIL: 商品名入力")
            return False

        # カテゴリ
        print("  [5/9] カテゴリ選択...", flush=True)
        self._cli.press("Home")
        self._cli.wait(0.3)
        if not self._select_category(product.category):
            print("  FAIL: カテゴリ選択")
            return False
        self._cli.wait(1)

        # 商品の状態
        print("  [6/9] 商品状態選択...", flush=True)
        if not self._select_condition(product.condition):
            print("  FAIL: 商品状態選択")
            return False
        self._cli.wait(1)

        # 説明
        print("  [7/9] 説明入力...", flush=True)
        snap = self._cli.snapshot()
        desc_ref = self._cli.find_ref(snap, r'textbox "商品の説明')
        if not desc_ref:
            print("  FAIL: 説明テキストボックスが見つからない")
            return False
        if not self._cli.fill(desc_ref, product.description):
            print("  FAIL: 説明入力")
            return False

        # 配送方法
        print("  [8/9] 配送方法選択...", flush=True)
        if not self._select_shipping_method(product.shipping_method):
            print("  FAIL: 配送方法選択")
            return False
        self._cli.wait(1)

        # 発送元の地域
        print("  [9/9] 価格・発送設定...", flush=True)
        snap = self._cli.snapshot()
        ref = self._cli.find_ref(snap, r'combobox "発送元の地域"')
        if ref:
            self._cli.select(ref, product.ship_from or "東京都")

        # 発送までの日数
        snap = self._cli.snapshot()
        ref = self._cli.find_ref(snap, r'combobox "発送までの日数"')
        if ref:
            self._cli.select(ref, product.ship_days)

        # 価格
        snap = self._cli.snapshot()
        price_ref = self._cli.find_ref(snap, r'textbox "300~"')
        if not price_ref:
            price_section = re.search(
                r"開始価格.*?textbox.*?\[ref=(\w+)\]", snap, re.DOTALL
            )
            if price_section:
                price_ref = price_section.group(1)
        if not price_ref:
            print("  FAIL: 価格テキストボックスが見つからない")
            return False
        if not self._cli.fill(price_ref, product.price):
            print("  FAIL: 価格入力")
            return False
        self._cli.wait(1)

        # 出品ボタン
        snap = self._cli.snapshot()
        ref = self._cli.find_ref(snap, r'button "出品する"')
        if not ref:
            print("  FAIL: 出品ボタンが見つからない")
            return False
        if not self._cli.click(ref):
            print("  FAIL: 出品ボタンクリック")
            return False

        # 出品完了確認
        self._cli.wait(5)
        snap = self._cli.snapshot()

        if "出品が完了" in snap or "出品しました" in snap:
            return True

        url_match = re.search(r"Page URL: (.*)", snap)
        if url_match and "/sell/create" not in url_match.group(1):
            return True

        for err_pattern in [r"選択してください", r"入力してください", r"必須"]:
            err_match = re.search(rf"({err_pattern}[^\n]*)", snap)
            if err_match:
                print(f"  WARN: バリデーションエラー: {err_match.group(1)[:60]}")

        print("  WARN: 出品完了を確認できず")
        return False

    def run(self) -> None:
        """メインフロー: CSV取得→商品を順次出品。"""
        products = self.fetch_inventory()
        if not products:
            print("出品可能な商品はありません")
            return

        print(f"出品候補: {len(products)}種")
        for p in products:
            print(f"  - {p.name[:30]}... (¥{p.price}, 在庫{p.stock})")

        ok_count = 0
        fail_count = 0
        skip_count = 0

        for i, product in enumerate(products, 1):
            print(f"\n[{i}/{len(products)}] {product.name[:30]}...")
            images = self._get_image_paths(product)
            if not images:
                print("  SKIP: 画像なし")
                skip_count += 1
                continue

            if self._list_one(product):
                print("  OK")
                ok_count += 1
            else:
                print("  FAIL — 中断します")
                sys.exit(1)

        print(f"\n完了: {ok_count}件出品, {skip_count}件スキップ")


if __name__ == "__main__":
    MercariLister().run()
