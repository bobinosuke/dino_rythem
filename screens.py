import pygame
import pyperclip
import os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class MenuAction:
    type: str
    screen: Optional[str] = None
    song_path: Optional[str] = None
    url: Optional[str] = None

class Screen:
    def __init__(self):
        font_path = os.path.join('assets', 'fonts', 'NotoSansJP-Regular.ttf')
        if os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, 36)
        else:
            self.font = pygame.font.SysFont(None, 36)
        self.selected_index = 0

    def draw_text(self, surface: pygame.Surface, text: str, pos: Tuple[int, int], selected: bool = False):
        color = (255, 255, 0) if selected else (255, 255, 255)
        max_width = surface.get_width() - 100
        
        text_surface = self.font.render(text, True, color)
        if text_surface.get_width() > max_width:
            while text_surface.get_width() > max_width:
                text = text[:-1] + "..."
                text_surface = self.font.render(text, True, color)
        
        rect = text_surface.get_rect(center=pos)
        surface.blit(text_surface, rect)

class TitleScreen(Screen):
    def __init__(self):
        super().__init__()
        self.menu_items = ["曲を選ぶ", "曲をダウンロード", "設定", "終了"]
        
    def update(self, surface: pygame.Surface) -> Optional[MenuAction]:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                elif event.key == pygame.K_RETURN:
                    if self.menu_items[self.selected_index] == "曲を選ぶ":
                        return MenuAction("CHANGE_SCREEN", screen="song_select")
                    elif self.menu_items[self.selected_index] == "曲をダウンロード":
                        return MenuAction("CHANGE_SCREEN", screen="download")
                    elif self.menu_items[self.selected_index] == "設定":
                        return MenuAction("CHANGE_SCREEN", screen="options")
                    elif self.menu_items[self.selected_index] == "終了":
                        return MenuAction("QUIT")
        
        surface.fill((0, 0, 0))
        title_pos = surface.get_width() // 2, 100
        self.draw_text(surface, "リズムゲーム", title_pos)
        
        start_y = 250
        for i, item in enumerate(self.menu_items):
            pos = (surface.get_width() // 2, start_y + i * 50)
            self.draw_text(surface, item, pos, i == self.selected_index)
        
        return None

class DownloadScreen(Screen):
    def __init__(self):
        super().__init__()
        self.input_text = ""
        self.message = ""
    
    def update(self, surface: pygame.Surface) -> Optional[MenuAction]:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MenuAction("CHANGE_SCREEN", screen="title")
                elif event.key == pygame.K_RETURN and self.input_text:
                    return MenuAction("DOWNLOAD", url=self.input_text)
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_META:
                    try:
                        self.input_text += pyperclip.paste()
                    except Exception as e:
                        print(f"クリップボードエラー: {e}")
                else:
                    self.input_text += event.unicode
        
        surface.fill((0, 0, 0))
        self.draw_text(surface, "YouTubeのURLを入力:", (surface.get_width() // 2, 150))
        self.draw_text(surface, self.input_text, (surface.get_width() // 2, 200))
        if self.message:
            self.draw_text(surface, self.message, (surface.get_width() // 2, 300))
        return None

class SongSelectScreen(Screen):
    def __init__(self, song_library):
        super().__init__()
        self.song_library = song_library
        self.songs = []
        self.update_song_list()
    
    def update_song_list(self):
        self.songs = self.song_library.get_song_list()
    
    def update(self, surface: pygame.Surface) -> Optional[MenuAction]:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MenuAction("CHANGE_SCREEN", screen="title")
                elif event.key == pygame.K_UP and self.songs:
                    self.selected_index = (self.selected_index - 1) % len(self.songs)
                elif event.key == pygame.K_DOWN and self.songs:
                    self.selected_index = (self.selected_index + 1) % len(self.songs)
                elif event.key == pygame.K_RETURN and self.songs:
                    return MenuAction("START_GAME", song_path=self.songs[self.selected_index])
        
        surface.fill((0, 0, 0))
        if not self.songs:
            self.draw_text(surface, "曲が見つかりません", (surface.get_width() // 2, 200))
            return None
        
        start_y = 150
        for i, song in enumerate(self.songs):
            pos = (surface.get_width() // 2, start_y + i * 50)
            self.draw_text(surface, os.path.basename(song), pos, i == self.selected_index)
        return None

class OptionsScreen(Screen):
    def __init__(self):
        super().__init__()
        self.options = {
            "音量": 100,
            "難易度": "普通",
            "フルスクリーン": True
        }
        self.selected_index = 0
    
    def update(self, surface: pygame.Surface) -> Optional[MenuAction]:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MenuAction("CHANGE_SCREEN", screen="title")
        
        surface.fill((0, 0, 0))
        self.draw_text(surface, "設定", (surface.get_width() // 2, 100))
        
        start_y = 200
        for i, (key, value) in enumerate(self.options.items()):
            pos = (surface.get_width() // 2, start_y + i * 50)
            self.draw_text(surface, f"{key}: {value}", pos, i == self.selected_index)
        return None
