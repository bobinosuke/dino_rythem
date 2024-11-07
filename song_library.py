import yt_dlp
import json
import os
from datetime import datetime
from utils import load_json, save_json
from config import SONGS_DIR

class SongLibrary:
    def __init__(self):
        self.songs_dir = SONGS_DIR
        self.data_file = os.path.join(SONGS_DIR, "song_data.json")
        self.song_data = {}
        self.load_library()
    
    def add_song(self, song_path: str, rhythm_data: dict):
        """新しい楽曲とそのリズムデータを追加"""
        self.song_data[song_path] = {
            'rhythm_data': rhythm_data,
            'added_date': datetime.now().isoformat()
        }
        self.save_library()
    
    def load_library(self):
        """楽曲データをJSONから読み込む"""
        self.song_data = load_json(self.data_file)
    
    def save_library(self):
        """楽曲データをJSONに保存"""
        save_json(self.data_file, self.song_data)
    
    def get_song_list(self) -> list:
        """利用可能な楽曲のリストを返す"""
        return list(self.song_data.keys())
    
    def get_song_details(self, song_path: str) -> dict:
        """特定の楽曲の詳細情報を返す"""
        return self.song_data.get(song_path, {})
    
    def get_rhythm_data(self, song_path: str) -> dict:
        """楽曲のリズムデータを返す"""
        return self.song_data.get(song_path, {}).get('rhythm_data', {})
    
    def download_from_youtube(self, url: str) -> str:
        """YouTubeから楽曲をダウンロード"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'outtmpl': os.path.join(self.songs_dir, '%(title)s.%(ext)s')
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return os.path.join(self.songs_dir, f"{info['title']}.mp3")

