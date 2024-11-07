import pygame
from screens import TitleScreen, SongSelectScreen, DownloadScreen, OptionsScreen, MenuAction
from game_manager import GameManager

class MenuSystem:
    def __init__(self):
        pygame.init()
        pygame.scrap.init()  # クリップボード機能の初期化
        self.game_manager = GameManager()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("リズムゲーム")
        
        self.screens = {
            'title': TitleScreen(),
            'song_select': SongSelectScreen(self.game_manager.song_library),
            'download': DownloadScreen(),
            'options': OptionsScreen()
        }
        self.current_screen = 'title'
        
    def run(self):
        while True:
            action = self.screens[self.current_screen].update(self.screen)
            if action:
                self.handle_action(action)
            pygame.display.flip()
    
    def handle_action(self, action: MenuAction):
        if action.type == "QUIT":
            pygame.quit()
            exit()
        elif action.type == "CHANGE_SCREEN":
            self.current_screen = action.screen
        elif action.type == "START_GAME":
            try:
                self.game_manager.start_game(action.song_path)
            except Exception as e:
                print(f"ゲーム開始エラー: {str(e)}")
        elif action.type == "DOWNLOAD":
            try:
                print("ダウンロードを開始します...")
                self.game_manager.download_and_analyze_song(
                    action.url,
                    lambda msg, progress: print(f"{msg} - {progress}%完了")
                )
                print("ダウンロード完了")
                self.screens['song_select'].update_song_list()
                self.current_screen = 'song_select'
            except Exception as e:
                print(f"ダウンロードエラー: {str(e)}")
                self.screens['download'].message = "エラーが発生しました"