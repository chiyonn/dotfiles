#!/usr/bin/env python3
"""メルカリ既存出品から商品画像をダウンロードするスクリプト

既存出品ページから画像URLを取得し、assets/{asin}/ に保存する。
Playwright CLI のセッションが起動済み＆ログイン済みであることが前提。

画像URLパターン: https://static.mercdn.net/item/detail/orig/photos/{item_id}_{n}.jpg

Usage:
    python3 ~/.claude/skills/mercari-manage/fetch-images.py
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

SPREADSHEET_ID = "1ob4criiPkC-MItr9T08sKFuDVcxmA4NHNbAO2juOxvw"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
ASSETS_DIR = os.path.expanduser("~/.claude/skills/mercari-manage/assets")


def run_cli(*args: str, timeout: int = 30) -> tuple[bool, str]:
    result = subprocess.run(
        ["npx", "@playwright/cli", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode == 0, result.stdout + result.stderr


def fetch_csv_products() -> dict[str, str]:
    """CSVから商品名 → ASIN のマッピングを取得"""
    response = urllib.request.urlopen(CSV_URL)
    content = response.read().decode("utf-8")
    reader = csv.reader(io.StringIO(content))
    next(reader)  # skip header

    name_to_asin = {}
    for row in reader:
        if len(row) < 2:
            continue
        asin = row[0].strip()
        name = row[1].strip()
        if name:
            # ASINがない場合は商品名の先頭20文字をサニタイズしてIDにする
            product_id = asin if asin else re.sub(r"[^\w]", "_", name[:20]).strip("_")
            name_to_asin[name] = product_id
    return name_to_asin


def collect_listing_items() -> list[tuple[str, str]]:
    """出品一覧から (item_id, title) のリストを収集する"""
    ok, _ = run_cli("goto", "https://jp.mercari.com/mypage/listings")
    if not ok:
        print("ERROR: 出品一覧に遷移できません")
        sys.exit(1)

    time.sleep(2)
    run_cli("snapshot")

    snapshots = sorted(glob.glob(".playwright-cli/page-*.yml"))
    if not snapshots:
        print("ERROR: スナップショットが見つかりません")
        sys.exit(1)

    with open(snapshots[-1]) as f:
        content = f.read()

    # linkテキストからitem_idとタイトルを抽出
    # パターン: link "タイトルのサムネイル undefined タイトル ¥ ..."
    #   /url: /item/m12345678901
    pattern = re.compile(
        r'link "(.+?)のサムネイル.*?" \[ref=\w+\].*?\n\s+- /url: /item/(m\d+)'
    )

    items = []
    seen_ids = set()
    for match in pattern.finditer(content):
        title = match.group(1)
        item_id = match.group(2)
        if item_id not in seen_ids:
            items.append((item_id, title))
            seen_ids.add(item_id)

    return items


def _normalize(s: str) -> str:
    """空白・全角半角を正規化して比較しやすくする"""
    import unicodedata
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", "", s).lower()


def match_title_to_asin(title: str, name_to_asin: dict[str, str]) -> str | None:
    """出品タイトルをCSVの商品名にマッチさせてASINを返す"""
    # 完全一致
    if title in name_to_asin:
        return name_to_asin[title]

    norm_title = _normalize(title)

    # 正規化後の完全一致
    for csv_name, asin in name_to_asin.items():
        if _normalize(csv_name) == norm_title:
            return asin

    # 正規化後の部分一致（先頭8文字→15文字段階的）
    for prefix_len in (8, 15):
        for csv_name, asin in name_to_asin.items():
            norm_csv = _normalize(csv_name)
            if norm_title[:prefix_len] in norm_csv or norm_csv[:prefix_len] in norm_title:
                return asin

    # タイトルの重要キーワードで一致（3語以上マッチ）
    title_words = set(re.findall(r"[\w]+", norm_title))
    best_match = None
    best_count = 0
    for csv_name, asin in name_to_asin.items():
        csv_words = set(re.findall(r"[\w]+", _normalize(csv_name)))
        common = title_words & csv_words
        if len(common) > best_count and len(common) >= 3:
            best_count = len(common)
            best_match = asin

    return best_match


def get_image_urls(item_id: str) -> list[str]:
    """商品ページから画像URLを取得する"""
    ok, _ = run_cli("goto", f"https://jp.mercari.com/item/{item_id}", timeout=60)
    if not ok:
        return []
    time.sleep(2)

    # item_idをハードコードしたJSで画像URLを抽出
    js_expr = (
        f"document.querySelector('meta[property=\"og:image\"]')?.content || 'NONE'"
    )
    ok, output = run_cli("eval", js_expr)

    # og:imageからベースURLを取得（{item_id}_1.jpg?ts）
    # 次に連番で存在チェック
    og_url = None
    for line in output.split("\n"):
        if "static.mercdn" in line:
            og_url = line.strip().strip('"')
            break

    if not og_url:
        return []

    # og:imageは _1.jpg のURL。_1 ~ _10 まで試す
    import re as _re

    base_match = _re.match(r"(https://static\.mercdn\.net/item/detail/orig/photos/" + item_id + r"_)\d+(\.jpg)", og_url)
    if not base_match:
        return [og_url]  # パース失敗でもog:imageだけ返す

    base = base_match.group(1)
    ext = base_match.group(2)

    urls = []
    for n in range(1, 11):
        url = f"{base}{n}{ext}"
        try:
            req = urllib.request.Request(url, method="HEAD", headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0",
                "Referer": "https://jp.mercari.com/",
            })
            resp = urllib.request.urlopen(req, timeout=5)
            if resp.status == 200:
                urls.append(url)
        except Exception:
            break  # 連番が途切れたら終了

    return urls if urls else [og_url]


def download_images(urls: list[str], asin: str) -> int:
    """画像をダウンロードする"""
    asset_dir = os.path.join(ASSETS_DIR, asin)
    os.makedirs(asset_dir, exist_ok=True)

    count = 0
    for i, url in enumerate(urls, 1):
        dest = os.path.join(asset_dir, f"{i}.jpg")
        if os.path.exists(dest):
            print(f"    skip {i}.jpg (exists)")
            count += 1
            continue
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0",
                "Referer": "https://jp.mercari.com/",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                with open(dest, "wb") as f:
                    f.write(resp.read())
            print(f"    saved {i}.jpg")
            count += 1
        except Exception as e:
            print(f"    FAIL {i}.jpg: {e}")

    return count


def main():
    print("CSVから商品情報を取得中...")
    name_to_asin = fetch_csv_products()
    print(f"  CSV商品数: {len(name_to_asin)}")

    print("出品一覧を取得中...")
    listings = collect_listing_items()
    print(f"  出品数: {len(listings)}")

    # ASINごとに1つの出品からだけ画像を取得
    asin_done = set()
    # 既にダウンロード済みのASINをスキップ
    if os.path.isdir(ASSETS_DIR):
        for d in os.listdir(ASSETS_DIR):
            asset_path = os.path.join(ASSETS_DIR, d)
            if os.path.isdir(asset_path) and any(
                f.endswith(".jpg") for f in os.listdir(asset_path)
            ):
                asin_done.add(d)
                print(f"  skip {d} (already downloaded)")

    asin_attempted = set(asin_done)  # 試行済み（成功含む）を追跡

    for item_id, title in listings:
        asin = match_title_to_asin(title, name_to_asin)
        if not asin:
            continue  # ASIN不明は静かにスキップ
        if asin in asin_attempted:
            continue
        asin_attempted.add(asin)

        print(f"  [{asin}] {title[:30]}...")
        urls = get_image_urls(item_id)
        if not urls:
            print(f"    画像URL取得失敗")
            continue

        count = download_images(urls, asin)
        print(f"    {count}枚保存")
        asin_done.add(asin)

    print(f"\n完了: {len(asin_done)}商品の画像を取得済み")


if __name__ == "__main__":
    main()
