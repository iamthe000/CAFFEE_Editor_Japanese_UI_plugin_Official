# ==============================
# ===公式UI日本語化プラグイン===
# ========CAFFEE-Editor=========
# ==============================

import curses
import datetime
import sys
import re

TRANSLATIONS = {
    "Exit": "終了",
    "Copy": "コピー",
    "Save": "保存",
    "Cut": "切り取り",
    "Paste": "貼り付け",
    "Search": "検索",
    "Undo": "元に戻す",
    "Redo": "やり直し",
    "Mark": "選択開始",
    "All": "全選択",
    "Goto": "行移動",
    "DelLine": "行削除",
    "Comment": "コメント",
    
    "Filename: ": "保存ファイル名: ",
    "Search (Regex): ": "検索 (正規表現): ",
    "Goto line: ": "移動先の行番号: ",
    "Save changes? (y/n/Esc)": "変更を保存しますか？ (y:はい/n:いいえ/Esc:取消)",
    
    "Mark Unset": "選択解除",
    "Mark Set": "選択開始位置を設定",
    "Cancelled.": "キャンセルしました。",
    "No selection to copy.": "コピーする選択範囲がありません。",
    "Clipboard empty.": "クリップボードは空です。",
    "Pasted.": "貼り付けました。",
    "Uncommented line.": "コメント解除",
    "Commented line.": "コメント化",
    "Deleted line.": "行削除",
    "Search aborted.": "検索を中止しました。",
    "Found match.": "見つかりました。",
    "Selection cleared.": "選択を解除しました。",
    "Selected all.": "すべて選択しました。",
    "Nothing to undo.": "元に戻す操作はありません。",
    "Nothing to redo.": "やり直す操作はありません。",
    "Invalid line number.": "無効な行番号です。",
    "Cut line.": "行を切り取りました。",
    "Cut selection.": "選択範囲を切り取りました。",
    "File changed on disk.": "ディスク上のファイルが変更されました。",
    "Aborted": "中止しました"
}

def translate_dynamic(text):
    if not isinstance(text, str):
        return text
        
    if text in TRANSLATIONS:
        return TRANSLATIONS[text]
    
    if text.startswith("Copied") and "lines" in text:
        return text.replace("Copied", "コピー完了:").replace("lines", "行")
    if text.startswith("Saved") and "lines to" in text:
        m = re.match(r"Saved (\d+) lines to (.+)\.$", text)
        if m:
            return f"{m.group(2)} に {m.group(1)} 行を保存しました。"
    if text.startswith("No match for"):
        return text.replace("No match for", "見つかりません: ")
    if text.startswith("Goto"):
        return text.replace("Goto", "移動:")
    if text.startswith("Applied history state"):
        return "履歴を適用しました"
        
    return text

def init(editor):

    original_draw_ui = editor.draw_ui

    def draw_ui_jp():
        version = "1.3"
        editor_name = "CAFFEE"
        
        mark_status = "[選択中]" if editor.mark_pos else ""
        mod_char = " (変更あり)" if editor.modified else ""
        fname = editor.filename if editor.filename else "新規バッファ"
        
        header = f" {editor_name} v{version} | {fname}{mod_char}   {mark_status}"
        header = header.ljust(editor.width)
        
        # ヘッダー描画
        editor.safe_addstr(0, 0, header, curses.color_pair(1) | curses.A_BOLD)
        editor.header_height = 1

        # メニューバーの日本語化定義
        shortcuts = [
            ("  ^X", "終了"), ("^C", "コピー"), ("^O", "保存"), ("^K", "切り取り"),
            ("^U", "貼付"), ("^W", "検索"), ("^Z", "戻す"), ("^R", "進める"),
            ("^6", "選択"), ("^A", "全選択"), ("^G", "移動"), ("^Y", "行削除"),
            ("^/", "コメント")
        ]

        menu_lines = []
        current_line_text = ""
        
        for key_str, label in shortcuts:
            item_str = f"{key_str} {label}  "
            # 画面幅チェック
            if len(current_line_text) + len(item_str) > editor.width:
                menu_lines.append(current_line_text)
                current_line_text = item_str
            else:
                current_line_text += item_str
        if current_line_text:
            menu_lines.append(current_line_text)

        editor.menu_height = len(menu_lines)
        editor.status_height = 1

        # メニューの描画
        for i, line in enumerate(reversed(menu_lines)):
            y = editor.height - 1 - i
            editor.safe_addstr(y, 0, line.ljust(editor.width), curses.color_pair(1))

        # ステータスバーの描画 (ロジックは元のまま、日本語対応)
        status_y = editor.height - editor.menu_height - 1
        now = datetime.datetime.now()
        display_msg = ""
        
        if editor.status_message:
            if not editor.status_expire_time or now <= editor.status_expire_time:
                # ここでメッセージを翻訳して表示
                display_msg = translate_dynamic(editor.status_message)
            else:
                editor.status_message = ""
                editor.status_expire_time = None
        
        pos_info = f" 行:{editor.cursor_y + 1} 列:{editor.cursor_x + 1} "
        max_msg_len = editor.width - len(pos_info) - 1
        

        if len(display_msg) > max_msg_len:
            display_msg = display_msg[:max_msg_len]
            
        editor.safe_addstr(status_y, 0, " " * editor.width, curses.color_pair(2))
        editor.safe_addstr(status_y, 0, display_msg, curses.color_pair(2))
        editor.safe_addstr(status_y, editor.width - len(pos_info), pos_info, curses.color_pair(1))

    # draw_uiを差し替え
    editor.draw_ui = draw_ui_jp

    # -------------------------------------------------
    # 2. スタート画面 (show_start_screen) のオーバーライド
    # -------------------------------------------------
    def show_start_screen_jp():
        editor.stdscr.clear()
        logo = [
            "      )  (  ",
            "     (   ) )",
            "      ) ( ( ",
            "    _______)",
            f" .-'-------|",
            f" | CAFFEE  |__",
            f" |  v1.2     |__)",
            f" |_________|",
            "  `-------' "
        ]
        my = editor.height // 2 - 6
        mx = editor.width // 2
        for i, l in enumerate(logo):
            if my + i < editor.height - 2:
                editor.safe_addstr(my + i, max(0, mx - 10), l)
        
        editor.safe_addstr(my + len(logo) + 1, max(0, mx - 12), f"CAFFEE Editor v1.2", curses.A_BOLD)
        jp_msg = "何かキーを押して開始..."
        editor.safe_addstr(my + len(logo) + 3, max(0, mx - len(jp_msg)), jp_msg, curses.A_DIM)
        editor.stdscr.refresh()
        editor.stdscr.getch()

    editor.show_start_screen = show_start_screen_jp
    original_prompt_user = editor.prompt_user
    
    def prompt_user_jp(prompt_msg, default_value=""):
        translated_msg = translate_dynamic(prompt_msg)
        return original_prompt_user(translated_msg, default_value)
        
    editor.prompt_user = prompt_user_jp

    editor.set_status("日本語プラグインをロードしました。", timeout=3)
