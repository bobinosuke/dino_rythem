from menu_system import MenuSystem
from config import SONGS_DIR, CACHE_DIR, ASSETS_DIR
from utils import ensure_dir_exists

def initialize_directories():
    """必要なディレクトリを初期化"""
    for directory in [SONGS_DIR, CACHE_DIR, ASSETS_DIR]:
        ensure_dir_exists(directory)

def main():
    """ゲームのメインエントリーポイント"""
    initialize_directories()
    menu = MenuSystem()
    menu.run()

if __name__ == "__main__":
    main()

