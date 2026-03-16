"""Playwright CLI ラッパー — メルカリ自動化スクリプトの共通基盤"""

import os
import re
import subprocess
import time


class PlaywrightClient:
    """Playwright CLI を操作する薄いラッパー。

    snapshot取得、ref検索、ページ遷移など共通操作をまとめる。
    """

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, default_timeout: int = 30) -> None:
        self._default_timeout = default_timeout

    def run(self, *args: str, timeout: int | None = None) -> tuple[bool, str]:
        """Playwright CLIコマンドを実行する。

        exit codeと出力内容の両方でエラー判定する。
        """
        try:
            result = subprocess.run(
                ["npx", "@playwright/cli", *args],
                capture_output=True,
                text=True,
                timeout=timeout or self._default_timeout,
            )
            output = result.stdout + result.stderr
            has_error = result.returncode != 0 or "### Error" in output
            return not has_error, output
        except subprocess.TimeoutExpired:
            return False, "TIMEOUT"

    def snapshot(self) -> str:
        """スナップショットを取得してYAML内容を返す。"""
        _, output = self.run("snapshot")
        match = re.search(r"\[Snapshot\]\(([^)]+\.yml)\)", output)
        if match:
            yml_path = match.group(1)
            if not os.path.isabs(yml_path):
                # Playwright CLIはCWD基準でYAMLを書く
                yml_path = os.path.normpath(os.path.join(os.getcwd(), yml_path))
            if os.path.exists(yml_path):
                with open(yml_path) as f:
                    return f.read()
        return output

    def goto(self, url: str, timeout: int = 60) -> bool:
        """指定URLに遷移する。"""
        ok, _ = self.run("goto", url, timeout=timeout)
        return ok

    def click(self, ref: str) -> bool:
        """ref IDの要素をクリックする。"""
        ok, _ = self.run("click", ref)
        return ok

    def fill(self, ref: str, value: str) -> bool:
        """ref IDの要素にテキストを入力する。"""
        ok, _ = self.run("fill", ref, value)
        return ok

    def select(self, ref: str, value: str) -> bool:
        """ref IDのselectboxで値を選択する。"""
        ok, _ = self.run("select", ref, value)
        return ok

    def press(self, key: str) -> bool:
        """キーを押す。"""
        ok, _ = self.run("press", key)
        return ok

    def upload(self, path: str) -> bool:
        """ファイルをアップロードする。"""
        ok, _ = self.run("upload", path)
        return ok

    @staticmethod
    def find_ref(content: str, pattern: str) -> str | None:
        """スナップショットからパターンにマッチする要素のrefを返す。"""
        match = re.search(rf"{pattern}.*?\[ref=(\w+)\]", content)
        return match.group(1) if match else None

    @staticmethod
    def find_all_refs(content: str, pattern: str) -> list[tuple[str, str]]:
        """パターンにマッチする全要素の (マッチテキスト, ref) を返す。"""
        return re.findall(rf"({pattern}[^\n]*?)\[ref=(\w+)\]", content)

    def wait(self, seconds: float = 1) -> None:
        """指定秒数待機する。"""
        time.sleep(seconds)
