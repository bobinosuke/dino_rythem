from song_analyzer import SongAnalyzer
from song_library import SongLibrary
from game_runner import GameRunner
import os
from typing import Dict, Optional

class GameManager:
    def __init__(self):
        self.song_analyzer = SongAnalyzer()
        self.game_runner = GameRunner()
        self.song_library = SongLibrary()
        
    def download_and_analyze_song(self, youtube_url: str, progress_callback=None) -> str:
        """YouTubeから楽曲をダウンロードして解析"""
        if progress_callback:
            progress_callback("楽曲をダウンロード中...", 0)
            
        song_path = self.song_library.download_from_youtube(youtube_url)
        
        if progress_callback:
            progress_callback("楽曲を解析中...", 50)
            
        rhythm_data = self.song_analyzer.analyze_song(song_path)
        self.song_library.add_song(song_path, rhythm_data)
        
        if progress_callback:
            progress_callback("完了", 100)
            
        return song_path
    
    def start_game(self, song_path):
        print(f"GameManager: ゲーム開始処理 - {song_path}")
        rhythm_data = self.song_library.get_rhythm_data(song_path)
        print(f"GameManager: リズムデータ取得完了")
        self.game_runner.run(song_path, rhythm_data)
    def get_available_songs(self) -> list:
        """利用可能な楽曲リストを取得"""
        return self.song_library.get_song_list()
    
    def get_song_details(self, song_path: str) -> Dict:
        """楽曲の詳細情報を取得"""
        return self.song_library.get_song_details(song_path)
    
    def update_settings(self, settings: Dict) -> None:
        """ゲーム設定を更新"""
        self.game_runner.update_settings(settings)

