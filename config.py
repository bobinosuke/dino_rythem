import os

# ディレクトリ設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SONGS_DIR = os.path.join(BASE_DIR, "songs")
CACHE_DIR = os.path.join(BASE_DIR, "cache")

# ゲーム設定のデフォルト値
DEFAULT_SETTINGS = {
    "volume": 0.7,
    "fullscreen": True,
    "difficulty": "normal",
    "scroll_speed": 5.0,
    "jump_height": 15.0
}

# アセットパス
ASSET_PATHS = {
    "player": os.path.join(ASSETS_DIR, "player.png"),
    "background": os.path.join(ASSETS_DIR, "background.png"),
    "obstacles": os.path.join(ASSETS_DIR, "obstacles")
}

# フォントパスの追加
FONT_DIR = os.path.join(ASSETS_DIR, "fonts")
DEFAULT_FONT = os.path.join(FONT_DIR, "NotoSansJP-Regular.ttf")
