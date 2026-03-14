#!/usr/bin/env python3
"""メルカリ自動出品スクリプト

Google SheetsのCSVから在庫情報を取得し、有効な商品を1品ずつ出品する。
Playwright CLI のセッションが起動済み＆ログイン済みであることが前提。

重要: eval コマンドは page.evaluate() (ブラウザJS) にマッピングされるため
Playwright API (getByRole等) は使えない。すべて snapshot → ref → CLI コマンドで操作する。

Usage:
    # 事前にブラウザを起動してログイン状態にしておく
    # npx @playwright/cli open --browser firefox --headed
    # npx @playwright/cli state-load mercari
    python3 -u ~/.claude/skills/mercari-manage/mercari-listing.py
"""

import csv
import glob
import io
import os
import re
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass

SPREADSHEET_ID = "1ob4criiPkC-MItr9T08sKFuDVcxmA4NHNbAO2juOxvw"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
ASSETS_DIR = os.path.expanduser("~/.claude/skills/mercari-manage/assets")
# Playwright CLIはCWDをallowed rootにする。CWD配下にsymlinkを作る。
ASSETS_SYMLINK_NAME = ".mercari-assets"

# 配送方法のCSV値 → フォーム操作のマッピング
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


def run_cli(*args: str, timeout: int = 30) -> tuple[bool, str]:
    """Playwright CLIコマンドを実行する。

    exit codeは信頼できない（エラーでも0を返す場合がある）ため、
    出力に "Error" が含まれるかどうかでも判定する。
    """
    result = subprocess.run(
        ["npx", "@playwright/cli", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output = result.stdout + result.stderr
    # exit code + 出力内容の両方で判定
    has_error = result.returncode != 0 or "### Error" in output
    return not has_error, output


def snapshot() -> str:
    """スナップショットを取得して内容を返す（CLI出力 + YAMLファイル）"""
    _, output = run_cli("snapshot")
    snapshots = sorted(glob.glob(".playwright-cli/page-*.yml"))
    if not snapshots:
        return output
    with open(snapshots[-1], "r") as f:
        return output + "\n" + f.read()


def find_ref(content: str, pattern: str) -> str | None:
    """スナップショットからパターンにマッチする要素のrefを返す"""
    match = re.search(rf'{pattern}.*?\[ref=(\w+)\]', content)
    return match.group(1) if match else None


def find_all_refs(content: str, pattern: str) -> list[tuple[str, str]]:
    """パターンにマッチする全要素の (マッチテキスト, ref) を返す"""
    return re.findall(rf'({pattern}[^\n]*?)\[ref=(\w+)\]', content)


def fetch_inventory() -> list[Product]:
    """Google SheetsからCSVを取得し、有効な商品リストを返す"""
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
        if is_valid(p):
            products.append(p)

    return products


def is_valid(p: Product) -> bool:
    """出品可能な商品かどうか判定する"""
    if not p.name or not p.description or not p.price or not p.category:
        return False
    try:
        return int(p.stock) > 0
    except (ValueError, TypeError):
        return False


def _image_dir_id(product: Product) -> str:
    """画像ディレクトリのIDを返す（ASIN or サニタイズ商品名）"""
    if product.asin:
        return product.asin
    return re.sub(r"[\W]", "_", product.name[:20]).strip("_")


def get_image_paths(product: Product) -> list[str]:
    """assets/{id}/ 配下の画像パスを返す"""
    asset_dir = os.path.join(ASSETS_DIR, _image_dir_id(product))
    if not os.path.isdir(asset_dir):
        return []
    images = sorted(
        f
        for f in os.listdir(asset_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    )
    return [os.path.join(asset_dir, img) for img in images]


def _ensure_assets_symlink() -> str:
    """CWD配下にsymlinkを作成し、そのパスを返す"""
    symlink_path = os.path.join(os.getcwd(), ASSETS_SYMLINK_NAME)
    if not os.path.exists(symlink_path):
        os.symlink(ASSETS_DIR, symlink_path)
    return symlink_path


def upload_images(image_paths: list[str]) -> bool:
    """商品画像をアップロードする

    snapshot → 「画像を選択する」ボタンの ref → click → upload を繰り返す。
    """
    symlink_path = _ensure_assets_symlink()

    for path in image_paths:
        upload_path = path.replace(ASSETS_DIR, symlink_path)

        # snapshot → ボタン ref を取得 → click
        snap = snapshot()
        ref = find_ref(snap, r'button.*画像を選択する')
        if not ref:
            print("    画像選択ボタンが見つからない")
            return False

        ok, output = run_cli("click", ref)
        if not ok:
            print(f"    画像選択ボタンのクリック失敗: {output[:80]}")
            return False
        time.sleep(0.5)

        ok, output = run_cli("upload", upload_path)
        if not ok:
            print(f"    upload fail: {os.path.basename(path)}: {output[:80]}")
            return False
        time.sleep(1)

        # AI出品サポートのモーダルが出ていたらDOMごと削除
        # Close→保存せずに戻るはフォームリセットされるため使わない
        snap = snapshot()
        if 'dialog' in snap.lower() and '出品画像' in snap:
            run_cli("eval", "() => (document.getElementById('ds-portal-wrapper') || document.querySelector('[role=dialog]')?.closest('[id*=portal], [class*=portal], [class*=overlay]') || document.querySelector('[role=dialog]'))?.remove()")
            time.sleep(0.5)
    return True


def select_category(category_str: str) -> bool:
    """カテゴリを階層的に選択する

    category_str: "車・バイク・自転車 > 車 > アクセサリー > その他"
    """
    parts = [p.strip() for p in category_str.split(">")]

    # snapshot → 「カテゴリーを選択」または「変更する」リンクの ref → click
    snap = snapshot()
    ref = find_ref(snap, r'link "カテゴリーを選択')
    if not ref:
        # 選択済みの場合は「変更する」リンク
        cat_section = re.search(r'カテゴリー.*?link "変更する".*?\[ref=(\w+)\]', snap, re.DOTALL)
        if cat_section:
            ref = cat_section.group(1)
    if not ref:
        print("  WARN: カテゴリーリンクが見つからない")
        return False
    ok, _ = run_cli("click", ref)
    if not ok:
        return False
    time.sleep(1)

    for part in parts:
        snap = snapshot()
        # 完全一致でリンクを探す
        ref = None
        for match_text, match_ref in find_all_refs(snap, r'link "'):
            # link "テキスト" からテキスト部分を抽出
            link_match = re.search(r'link "([^"]+)"', match_text)
            if link_match and link_match.group(1).strip() == part.strip():
                ref = match_ref
                break

        if not ref:
            # 部分一致フォールバック
            escaped = re.escape(part.strip())
            ref = find_ref(snap, rf'link "{escaped}')

        if not ref:
            print(f"  WARN: カテゴリ '{part}' が見つからない")
            return False

        ok, _ = run_cli("click", ref)
        if not ok:
            print(f"  WARN: カテゴリ '{part}' のクリック失敗")
            return False
        time.sleep(0.5)

    return True


def select_condition(condition: str) -> bool:
    """商品の状態を選択する"""
    snap = snapshot()
    # 「選択する」または「変更する」のリンクを探す
    ref = find_ref(snap, r'link "商品の状態を選択')
    if not ref:
        ref = find_ref(snap, r'商品の状態.*?link "変更する".*?\[ref=(\w+)\]')
        if not ref:
            # 商品の状態セクションの「変更する」を探す
            cond_section = re.search(r'商品の状態.*?link "変更する".*?\[ref=(\w+)\]', snap, re.DOTALL)
            if cond_section:
                ref = cond_section.group(1)
    if not ref:
        print(f"  WARN: 商品状態リンクが見つからない")
        return False
    ok, _ = run_cli("click", ref)
    if not ok:
        return False
    time.sleep(1)

    snap = snapshot()
    # 商品状態のリンクを探す（前方一致）
    escaped = re.escape(condition)
    ref = find_ref(snap, rf'link "{escaped}')
    if not ref:
        # 部分一致
        ref = find_ref(snap, rf'link ".*{escaped}')
    if not ref:
        print(f"  WARN: 商品状態 '{condition}' が見つからない")
        return False

    ok, _ = run_cli("click", ref)
    return ok


def select_shipping_method(method: str) -> bool:
    """配送方法を選択する"""
    form_method = SHIPPING_METHOD_MAP.get(method, method)

    snap = snapshot()

    # すでに正しい配送方法が選択済みならスキップ
    if form_method in snap or method in snap:
        # "郵便（定型、定形外、書留など）" がsnapshotに表示されていればOK
        ship_section = re.search(r'配送の方法.*?(?:変更する|選択する)', snap, re.DOTALL)
        if ship_section and (form_method in ship_section.group() or method in ship_section.group()):
            return True

    ref = find_ref(snap, r'link "配送の方法を選択')
    if not ref:
        # 「変更する」リンクを探す
        ship_section = re.search(r'配送の方法.*?link "変更する".*?\[ref=(\w+)\]', snap, re.DOTALL)
        if ship_section:
            ref = ship_section.group(1)
    if not ref:
        print(f"  WARN: 配送方法リンクが見つからない")
        return False
    ok, _ = run_cli("click", ref)
    if not ok:
        return False
    time.sleep(1)

    # 「その他」展開ボタンを探す
    snap = snapshot()
    ref = find_ref(snap, r'button.*その他')
    if not ref:
        # testIdでも探す
        ref = find_ref(snap, r'shipping-service-trigger-button')
    if ref:
        run_cli("click", ref)
        time.sleep(0.5)
        snap = snapshot()

    # 配送方法のradioを探す
    escaped = re.escape(form_method)
    ref = find_ref(snap, rf'radio "{escaped}')
    if not ref:
        ref = find_ref(snap, rf'radio ".*{escaped}')
    if not ref:
        # リンクとしても探す
        ref = find_ref(snap, rf'link ".*{escaped}')
    if not ref:
        print(f"  WARN: 配送方法 '{form_method}' が見つからない")
        return False

    ok, _ = run_cli("click", ref)
    if not ok:
        return False
    time.sleep(0.5)

    # 「更新する」ボタンがあればクリック
    snap = snapshot()
    ref = find_ref(snap, r'button "更新する"')
    if ref:
        ok, _ = run_cli("click", ref)
        if not ok:
            return False

    return True


def list_one(product: Product) -> bool:
    """商品を1件出品する"""
    # 出品フォームに直接遷移
    ok, _ = run_cli("goto", "https://jp.mercari.com/sell/create", timeout=60)
    if not ok:
        return False
    time.sleep(3)

    # AI出品サポートをOFFにする
    # ONだと画像アップ後にAIダイアログが出てフォーム操作をブロックする
    snap = snapshot()

    # ダイアログが出ていたら先に閉じる
    if 'dialog' in snap and 'AI出品サポート' in snap:
        close_ref = find_ref(snap, r'button "閉じる"')
        if close_ref:
            run_cli("click", close_ref)
            time.sleep(0.5)
            snap = snapshot()

    # switchがON(checked)かつ操作可能(disabledでない)ならOFFにする
    switch_match = re.search(r'switch ".*?自動入力.*?"(.*?)\[ref=(\w+)\]', snap)
    if switch_match:
        attrs = switch_match.group(1)
        switch_ref = switch_match.group(2)
        if '[checked]' in attrs and '[disabled]' not in attrs:
            run_cli("click", switch_ref)
            time.sleep(0.5)

    # --- 画像アップロード ---
    run_cli("press", "Home")
    time.sleep(0.3)
    images = get_image_paths(product)
    if not images:
        print(f"  SKIP: 画像なし ({_image_dir_id(product)})")
        return False
    if not upload_images(images):
        print("  FAIL: 画像アップロード")
        return False
    time.sleep(2)

    # --- 商品名 (40文字制限) ---
    title = product.name[:40]
    snap = snapshot()
    ref = find_ref(snap, r'textbox.*\[ref=')
    # input-name のtextboxを探す
    name_ref = find_ref(snap, r'heading "商品名"')
    if name_ref:
        # 商品名見出しの近くにあるtextboxを探す
        # スナップショットの構造上、input-name配下のtextbox
        name_section = re.search(rf'heading "商品名".*?textbox.*?\[ref=(\w+)\]', snap, re.DOTALL)
        if name_section:
            ref = name_section.group(1)
    if not ref:
        print("  FAIL: 商品名テキストボックスが見つからない")
        return False

    ok, _ = run_cli("fill", ref, title)
    if not ok:
        print("  FAIL: 商品名入力")
        return False

    # --- カテゴリ ---
    run_cli("press", "Home")
    time.sleep(0.3)
    if not select_category(product.category):
        print("  FAIL: カテゴリ選択")
        return False
    time.sleep(1)

    # --- 商品の状態 ---
    if not select_condition(product.condition):
        print("  FAIL: 商品状態選択")
        return False
    time.sleep(1)

    # --- 商品の説明 ---
    snap = snapshot()
    desc_ref = find_ref(snap, r'textbox "商品の説明')
    if not desc_ref:
        print("  FAIL: 説明テキストボックスが見つからない")
        return False
    ok, _ = run_cli("fill", desc_ref, product.description)
    if not ok:
        print("  FAIL: 説明入力")
        return False

    # --- 配送の方法 ---
    if not select_shipping_method(product.shipping_method):
        print("  FAIL: 配送方法選択")
        return False
    time.sleep(1)

    # --- 発送元の地域 ---
    snap = snapshot()
    ref = find_ref(snap, r'combobox "発送元の地域"')
    if ref:
        region = product.ship_from if product.ship_from else "東京都"
        run_cli("select", ref, region)

    # --- 発送までの日数 ---
    snap = snapshot()
    ref = find_ref(snap, r'combobox "発送までの日数"')
    if ref:
        run_cli("select", ref, product.ship_days)

    # --- 価格 ---
    snap = snapshot()
    price_ref = find_ref(snap, r'textbox "300~"')
    if not price_ref:
        # 開始価格テキストボックスを探す
        price_ref = find_ref(snap, r'paragraph "開始価格".*?textbox.*?\[ref=')
        if not price_ref:
            price_section = re.search(r'開始価格.*?textbox.*?\[ref=(\w+)\]', snap, re.DOTALL)
            if price_section:
                price_ref = price_section.group(1)
    if not price_ref:
        print("  FAIL: 価格テキストボックスが見つからない")
        return False
    ok, _ = run_cli("fill", price_ref, product.price)
    if not ok:
        print("  FAIL: 価格入力")
        return False

    time.sleep(1)

    # --- 出品 ---
    snap = snapshot()
    ref = find_ref(snap, r'button "出品する"')
    if not ref:
        print("  FAIL: 出品ボタンが見つからない")
        return False
    ok, _ = run_cli("click", ref)
    if not ok:
        print("  FAIL: 出品ボタンクリック")
        return False

    # 出品完了を確認
    time.sleep(5)
    snap = snapshot()

    # 「出品が完了しました」ダイアログが出ていればOK
    if "出品が完了" in snap or "出品しました" in snap:
        return True

    # URLが /sell (not /sell/create) に変わっていればOK
    url_match = re.search(r'Page URL: (.*)', snap)
    if url_match:
        url = url_match.group(1)
        if "/sell/create" not in url:
            return True

    # まだ /sell/create にいる場合はバリデーションエラー
    # エラーメッセージを探す
    for err_pattern in [r'選択してください', r'入力してください', r'必須']:
        err_match = re.search(rf'({err_pattern}[^\n]*)', snap)
        if err_match:
            print(f"  WARN: バリデーションエラー: {err_match.group(1)[:60]}")

    print("  WARN: 出品完了を確認できず")
    return False


def main():
    products = fetch_inventory()
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

        images = get_image_paths(product)
        if not images:
            print(f"  SKIP: 画像なし")
            skip_count += 1
            continue

        if list_one(product):
            print("  OK")
            ok_count += 1
        else:
            print("  FAIL")
            fail_count += 1

    print(f"\n完了: {ok_count}件出品, {fail_count}件失敗, {skip_count}件スキップ")


if __name__ == "__main__":
    main()
