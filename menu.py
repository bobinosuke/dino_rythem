import pygame
import sys
from screens import TitleScreen, SongSelectScreen, DownloadScreen, OptionsScreen
from game_manager import GameManager

class MenuSystem:
    def __init__(self):
        pygame.init()
        self.game_manager = GameManager()
        self.screens = {
            'title': TitleScreen(),
            'song_select': SongSelectScreen(),
            'download': DownloadScreen(),
            'options': OptionsScreen()
        }
        self.current_screen = 'title'
    
    def run(self):
        while True:
            screen = self.screens[self.current_screen]
            action = screen.update()
            self.handle_action(action)

    def handle_action(self, action):
        if action.type == 'CHANGE_SCREEN':
            self.current_screen = action.screen
        elif action.type == 'START_GAME':
            self.game_manager.start_game(action.song_path)
