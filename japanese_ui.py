# japanese_ui_ja.py

# ==============================
# ===公式UI日本語化プラグイン===
# ========CAFFEE-Editor=========
# ==============================


import curses
import datetime
import re
from typing import TYPE_CHECKING, Dict, Any

# 型ヒントのためのインポート（実行時には不要）
if TYPE_CHECKING:
    # 実際にはcafee.pyからインポートできないが、型チェックのために想定
    from caffee import Editor, get_config_dir

# --- 日本語化リソース ---
# {元の英語メッセージ: 翻訳された日本語メッセージ}
# Editor.set_status() / Editor.set_status_message() で使用されるものを中心に定義
STATUS_MESSAGES: Dict[str, str] = {
    "No selection to copy.": "コピーする選択範囲がありません。",
    "Copied {count} lines.": "{count} 行をコピーしました。",
    "Cut line.": "行を切り取りました。",
    "Cut selection.": "選択範囲を切り取りました。",
    "Clipboard empty.": "クリップボードは空です。",
    "Pasted.": "貼り付けました。",
    "Uncommented line.": "行のコメントを解除しました。",
    "Commented line.": "行をコメント化しました。",
    "Deleted line.": "行を削除しました。",
    "Search aborted.": "検索を中止しました。",
    "Invalid Regex: {error}": "無効な正規表現: {error}",
    "Found match.": "一致するものが見つかりました。",
    "No match for '{query}'": "'{query}' に一致するものはありません。",
    "Filename: ": "ファイル名: ",
    "Aborted": "中止しました",
    "Backup warning: {error}": "バックアップ警告: {error}",
    "Saved {line_count} lines to {filename}.": " {line_count} 行を {filename} に保存しました。",
    "Error saving file: {error}": "ファイル保存エラー: {error}",
    "Selection cleared.": "選択を解除しました。",
    "Selected all.": "すべて選択しました。",
    "Goto line: ": "行番号へ移動: ",
    "Goto {line}": "{line} 行目へ移動",
    "Invalid line number.": "無効な行番号です。",
    "Mark Unset": "マーク解除",
    "Mark Set": "マーク設定",
    "Save changes? (y/n/Esc)": "変更を保存しますか？ (y/n/Esc)",
    "Cancelled.": "キャンセルしました。",
    "File changed on disk.": "ファイルがディスク上で変更されました。",
    "Cannot run: No filename provided.": "実行できません: ファイル名が指定されていません。",
    "No build command defined for {ext}": "{ext} に対応するビルドコマンドが定義されていません。",
    "Search (Regex): ": "検索 (正規表現): ",
    "Applied history state {current}/{total}": "履歴状態 {current}/{total} を適用しました",
    "Nothing to undo.": "元に戻す操作はありません。",
    "Nothing to redo.": "やり直し操作はありません。",
    # Start Screen / Settings
    "[^S] Settings      [^P] Plugin Manager      [Any Key] Empty Buffer": "[^S] 設定      [^P] プラグイン管理      [Any Key] 新規ファイルを開く",
    "Press any key to brew...": "任意のキーを押して開始...",
    "Error loading file: {error}": "ファイル読み込みエラー: {error}",
    "Plugin load error ({filename}): {error}": "プラグイン読み込みエラー ({filename}): {error}",
    "Loaded {count} plugins.": "{count} 個のプラグインを読み込みました。",
    "Config load error: {error}": "設定ファイル読み込みエラー: {error}",
    "Config dir error: {error}": "設定ディレクトリエラー: {error}",
    "Restart editor to apply changes.": "エディタを再起動して変更を適用してください。",
    "Error toggling plugin: {error}": "プラグイン切り替えエラー: {error}",
}

# Editor.draw_ui() で使用されるショートカットの定義
SHORTCUT_MAP: Dict[str, str] = {
    "Exit": "終了",
    "Copy": "コピー",
    "Save": "保存",
    "Build": "ビルド/実行",
    "Cut": "切り取り",
    "Paste": "貼り付け",
    "Search": "検索",
    "Undo": "元に戻す",
    "Mark": "マーク",
    "All": "全選択",
    "Goto": "行移動",
    "DelLine": "行削除",
    "Comment": "コメント切替",
    "Explorer": "ファイルツリー",
    "Terminal": "ターミナル",
    "LineEnd": "行末へ",
}

# Header / Pane Focus
PANEL_FOCUS_MAP: Dict[str, str] = {
    'EDT': 'エディタ',
    'EXP': 'ファイルツリー',
    'TRM': 'ターミナル'
}


def translate_status_message(msg: str) -> str:
    """ステータスメッセージを日本語に翻訳する"""
    
    # 履歴メッセージの翻訳
    history_match = re.match(r"Applied history state (\d+)/(\d+)", msg)
    if history_match:
        current, total = history_match.groups()
        return STATUS_MESSAGES["Applied history state {current}/{total}"].format(current=current, total=total)
        
    # 保存メッセージの翻訳
    save_match = re.match(r"Saved (\d+) lines to (.*)\.", msg)
    if save_match:
        line_count, filename = save_match.groups()
        return STATUS_MESSAGES["Saved {line_count} lines to {filename}."].format(line_count=line_count, filename=filename)

    # ロードメッセージの翻訳
    load_match = re.match(r"Error loading file: (.*)", msg)
    if load_match:
        error = load_match.group(1)
        return STATUS_MESSAGES["Error loading file: {error}"].format(error=error)
    
    # プラグインロードメッセージの翻訳
    plugin_load_match = re.match(r"Plugin load error \((.*)\): (.*)", msg)
    if plugin_load_match:
        filename, error = plugin_load_match.groups()
        return STATUS_MESSAGES["Plugin load error ({filename}): {error}"].format(filename=filename, error=error)

    # 読み込み数の翻訳
    loaded_match = re.match(r"Loaded (\d+) plugins\.", msg)
    if loaded_match:
        count = loaded_match.group(1)
        return STATUS_MESSAGES["Loaded {count} plugins."].format(count=count)
    
    # 検索メッセージの翻訳
    no_match = re.match(r"No match for '(.*)'", msg)
    if no_match:
        query = no_match.group(1)
        return STATUS_MESSAGES["No match for '{query}'"].format(query=query)
        
    # その他のシンプルなメッセージの翻訳
    return STATUS_MESSAGES.get(msg, msg)


# --- Editor.draw_ui のオーバーライド ---
# オリジナルの draw_ui を保存しておき、新しい関数でラップする
original_draw_ui = None

def plugin_draw_ui(self):
    """ヘッダーとメニューを日本語化して描画する"""
    if self.active_pane == 'plugin_manager':
        original_draw_ui(self)
        return

    # 1. ヘッダー行の処理 (Header)
    mark_status = "[マーク]" if self.mark_pos else ""
    mod_char = " *" if self.modified else ""
    syntax_name = "テキスト"
    if self.current_syntax_rules:
        ext_list = self.current_syntax_rules.get("extensions", [])
        if ext_list: syntax_name = ext_list[0].upper().replace(".", "") # 拡張子から言語名を推定

    focus_map_internal = {'editor': 'EDT', 'explorer': 'EXP', 'terminal': 'TRM'}
    focus_key = focus_map_internal.get(self.active_pane, '---')
    focus_str_ja = f"[{PANEL_FOCUS_MAP.get(focus_key, '---')}]"

    header = f" {self.config.get('EDITOR_NAME', 'CAFFEE')} v{self.config.get('VERSION', '?.?.?')} | {self.filename or '新規ファイル'} {mod_char} | {syntax_name} | {focus_str_ja} {mark_status}"
    header = header.ljust(self.width)
    self.safe_addstr(0, 0, header, curses.color_pair(1) | curses.A_BOLD)
    self.header_height = 1

    # 2. メニュー行の処理 (Shortcuts)
    shortcuts_en = [
        ("^X", "Exit"), ("^C", "Copy"), ("^O", "Save"), ("^B", "Build"),
        ("^K", "Cut"), ("^U", "Paste"), ("^W", "Search"), ("^Z", "Undo"),
        ("^6", "Mark"), ("^A", "All"), ("^G", "Goto"), ("^Y", "DelLine"),
        ("^/", "Comment"), ("^F", "Explorer"), ("^T", "Terminal"), ("^E", "LineEnd")
    ]
    
    # 日本語のショートカットリストを作成
    shortcuts_ja = []
    for key_str, label_en in shortcuts_en:
        label_ja = SHORTCUT_MAP.get(label_en, label_en)
        shortcuts_ja.append((key_str, label_ja))

    menu_lines = []
    current_line_text = ""
    
    for key_str, label_ja in shortcuts_ja:
        item_str = f"{key_str} {label_ja}  "
        if len(current_line_text) + len(item_str) > self.width:
            menu_lines.append(current_line_text)
            current_line_text = item_str
        else:
            current_line_text += item_str
    if current_line_text:
        menu_lines.append(current_line_text)

    self.menu_height = len(menu_lines)
    self.status_height = 1

    for i, line in enumerate(reversed(menu_lines)):
        y = self.height - 1 - i
        self.safe_addstr(y, 0, line.ljust(self.width), curses.color_pair(1))

    # 3. ステータス行の処理 (Status)
    status_y = self.height - self.menu_height - 1
    now = datetime.datetime.now()
    display_msg = ""
    
    if self.status_message:
        if not self.status_expire_time or now <= self.status_expire_time:
            display_msg = translate_status_message(self.status_message)
        else:
            self.status_message = ""
            self.status_expire_time = None
            
    pos_info = f" {self.cursor_y + 1}行目:{self.cursor_x + 1}桁 " # 座標表示も日本語化
    max_msg_len = self.width - len(pos_info) - 1
    if len(display_msg) > max_msg_len:
        display_msg = display_msg[:max_msg_len]
        
    self.safe_addstr(status_y, 0, " " * self.width, curses.color_pair(2))
    self.safe_addstr(status_y, 0, display_msg, curses.color_pair(2))
    self.safe_addstr(status_y, self.width - len(pos_info), pos_info, curses.color_pair(1))


# --- Editor.show_start_screen のオーバーライド ---
original_show_start_screen = None

def plugin_show_start_screen(self, duration_ms=None, interactive=False):
    """スタート画面のテキストを日本語化して描画する"""
    self.stdscr.clear()
    logo_attr = curses.color_pair(3) | curses.A_BOLD
    
    # ロゴ部分は変更しない
    logo = [
        "                                         　    ) (",
        "                                         　   (   ) )",
        "                                         　    ) ( (",
        "                                         　  _______)",
        f"   _________    ________________________　.-'-------|",
        f"  / ____/   |  / ____/ ____/ ____/ ____/　| CAFFEE  |__",
        f" / /   / /| | / /_  / /_  / __/ / __/   　| v{self.config.get('VERSION', '?.?.?')}  |__)",
        f"/ /___/ ___ |/ __/ / __/ / /___/ /___   　|_________|",
        f"\____/_/  |_/_/   /_/   /_____/_____/   　 `-------'"
    ]
    my = self.height // 2 - 6
    mx = self.width // 2 
    start_x_offset = 28

    for i, l in enumerate(logo):
        if my + i < self.height - 2:
            self.safe_addstr(my + i, max(0, mx - start_x_offset), l.rstrip(), logo_attr)
            
    self.safe_addstr(my + len(logo) + 1, max(0, mx - 12), f"CAFFEE Editor v{self.config.get('VERSION', '?.?.?')}", logo_attr)
    
    # --- 日本語化したインタラクティブモードの表示 ---
    if interactive:
        menu_y = my + len(logo) + 4
        menu_text_ja = STATUS_MESSAGES["[^S] Settings      [^P] Plugin Manager      [Any Key] Empty Buffer"]
        self.safe_addstr(menu_y, max(0, mx - len(menu_text_ja)//2), menu_text_ja, curses.color_pair(3))
    
    # --- 日本語化した通常のメッセージ ---
    elif not duration_ms:
        message_ja = STATUS_MESSAGES["Press any key to brew..."]
        self.safe_addstr(my + len(logo) + 3, max(0, mx - len(message_ja)//2), message_ja, curses.A_DIM | curses.color_pair(3))
    
    self.stdscr.refresh()
    
    if duration_ms:
         curses.napms(duration_ms)
    elif not interactive:
         self.stdscr.getch()


# --- Editor.prompt_user のオーバーライド ---
original_prompt_user = None

def plugin_prompt_user(self, prompt_msg: str, default_value: str = ""):
    """プロンプトメッセージを日本語化して表示する"""
    prompt_msg_ja = translate_status_message(prompt_msg)
    
    # set_status の代わりに直接表示を操作するため、ここでステータスを一時的に設定
    # set_statusがすでにラップされているため、ここではラップされたset_statusを呼び出す
    self.set_status(prompt_msg_ja, timeout=60)
    self.draw_ui() # 日本語プロンプトを表示

    curses.echo()
    result = None
    try:
        status_y = self.height - self.menu_height - 1
        # 日本語プロンプトを再描画
        self.safe_addstr(status_y, 0, prompt_msg_ja.ljust(self.width), curses.color_pair(2))
        
        # 入力開始X座標を計算
        start_x = min(len(prompt_msg_ja), self.width - 1)
        
        # getstrで入力を取得
        inp_bytes = self.stdscr.getstr(status_y, start_x)
        result = inp_bytes.decode('utf-8')
    except Exception:
        result = None
    finally:
        curses.noecho()
        self.status_message = ""
        self.redraw_screen()
    return result

# --- 初期化関数 ---

def init(editor):
    """CAFFEEエディタのUI関連メソッドをオーバーライドし、日本語化する"""
    global original_draw_ui
    global original_show_start_screen
    global original_prompt_user

    # draw_ui の日本語化
    if original_draw_ui is None:
        original_draw_ui = editor.draw_ui
        editor.draw_ui = plugin_draw_ui.__get__(editor) # インスタンスメソッドとしてバインド

    # show_start_screen の日本語化
    if original_show_start_screen is None:
        original_show_start_screen = editor.show_start_screen
        editor.show_start_screen = plugin_show_start_screen.__get__(editor)

    # prompt_user の日本語化 (ユーザー入力プロンプト)
    if original_prompt_user is None:
        original_prompt_user = editor.prompt_user
        editor.prompt_user = plugin_prompt_user.__get__(editor)

    # set_status のラッパー（メッセージを翻訳してからオリジナルを呼び出す）
    original_set_status = editor.set_status
    def plugin_set_status(self, msg, timeout=3):
        msg_ja = translate_status_message(msg)
        # 🌟 修正済み: original_set_status が既にインスタンスにバインドされているため、
        # `self`を引数から削除して呼び出すことでTypeErrorを解消します。
        original_set_status(msg_ja, timeout) 
    editor.set_status = plugin_set_status.__get__(editor)
    
    # ロード成功メッセージ
    editor.set_status("日本語UIプラグインをロードしました。", timeout=2)
