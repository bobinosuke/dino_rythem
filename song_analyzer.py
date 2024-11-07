import librosa
import numpy as np
import json
import os
from typing import Dict, List, Optional, Tuple

class SongAnalyzer:
    def __init__(self):
        self.jump_speed = 15
        self.gravity = 0.8
        self.obstacle_speed = 5
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def analyze_song(self, file_path: str, progress_callback=None) -> Dict:
        """楽曲を解析してリズムデータを生成"""
        cached_data = self._get_cached_analysis(file_path)
        if cached_data:
            return cached_data

        if progress_callback:
            progress_callback("音楽ファイルを解析中...", 0)

        try:
            y, sr, onset_env, beats, chroma, mfcc = self._analyze_music(file_path)
            
            if progress_callback:
                progress_callback("リズムパターンを生成中...", 50)
            
            rhythm_patterns = self._generate_rhythm_patterns(
                y, sr, onset_env, beats, chroma, mfcc,
                self.jump_speed, self.gravity, self.obstacle_speed
            )

            result = {
                'rhythm_patterns': rhythm_patterns,
                'tempo': float(librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]),
                'duration': float(librosa.get_duration(y=y, sr=sr))
            }

            self._cache_analysis(file_path, result)
            
            if progress_callback:
                progress_callback("解析完了", 100)

            return result

        except Exception as e:
            raise RuntimeError(f"楽曲解析エラー: {str(e)}")

    def _analyze_music(self, file_path: str) -> Tuple[np.ndarray, int, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """音楽ファイルの基本的な特徴量を抽出"""
        y, sr = librosa.load(file_path)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        mfcc = librosa.feature.mfcc(y=y, sr=sr)
        return y, sr, onset_env, beats, chroma, mfcc

    def _generate_rhythm_patterns(
        self, y: np.ndarray, sr: int, onset_env: np.ndarray, 
        beats: np.ndarray, chroma: np.ndarray, mfcc: np.ndarray,
        jump_speed: float, gravity: float, obstacle_speed: float,
        min_interval: float = 0.8
    ) -> List[Dict]:
        """リズムパターンを生成"""
        patterns = []
        apex_time = jump_speed / gravity
        
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
        beat_times = librosa.frames_to_time(beats, sr=sr)
        
        song_duration = librosa.get_duration(y=y, sr=sr)
        target_points = int(song_duration / 2)
        last_obstacle_time = -min_interval
        
        for onset in librosa.frames_to_time(onsets):
            if onset - last_obstacle_time >= min_interval:
                frame = librosa.time_to_frames(onset, sr=sr)
                
                chroma_score = np.max(chroma[:, frame])
                mfcc_score = np.std(mfcc[:, frame])
                beat_score = 1 if np.min(np.abs(beat_times - onset)) < 0.05 else 0
                
                rhythm_strength = (chroma_score + mfcc_score + beat_score) / 3
                jump_time = onset - apex_time
                
                if jump_time > 0:
                    patterns.append({
                        "jump_time": float(jump_time),
                        "obstacle_time": float(onset),
                        "start_time": float(jump_time - 0.2),
                        "end_time": float(jump_time + 0.2),
                        "rhythm_strength": float(rhythm_strength),
                        "variation": "normal"
                    })
                    last_obstacle_time = onset

        self._add_additional_patterns(patterns, target_points, song_duration, apex_time)
        return patterns

    def _add_additional_patterns(
        self, patterns: List[Dict], target_points: int, 
        song_duration: float, apex_time: float
    ) -> None:
        """追加のリズムポイントを挿入"""
        if len(patterns) < target_points:
            additional_points = target_points - len(patterns)
            interval = song_duration / additional_points
            
            for i in range(additional_points):
                time = (len(patterns) + i + 1) * interval
                if time > song_duration:
                    break
                    
                jump_time = time - apex_time
                if jump_time > 0:
                    patterns.append({
                        "jump_time": float(jump_time),
                        "obstacle_time": float(time),
                        "start_time": float(jump_time - 0.2),
                        "end_time": float(jump_time + 0.2),
                        "rhythm_strength": 0.5,
                        "variation": "normal"
                    })

    def _get_cached_analysis(self, file_path: str) -> Optional[Dict]:
        """キャッシュされた解析結果を取得"""
        cache_path = os.path.join(self.cache_dir, f"{hash(file_path)}.json")
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)
        return None

    def _cache_analysis(self, file_path: str, data: Dict) -> None:
        """解析結果をキャッシュ"""
        cache_path = os.path.join(self.cache_dir, f"{hash(file_path)}.json")
        with open(cache_path, 'w') as f:
            json.dump(data, f, indent=2)
