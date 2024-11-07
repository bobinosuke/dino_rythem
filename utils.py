import json
import os
from typing import Dict, Any

def load_json(filepath: str) -> Dict:
    """JSONファイルを読み込む"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(filepath: str, data: Dict) -> None:
    """JSONファイルに保存"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def format_time(seconds: float) -> str:
    """秒数を「分:秒」形式にフォーマット"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def ensure_dir_exists(directory: str) -> None:
    """ディレクトリが存在しない場合は作成"""
    if not os.path.exists(directory):
        os.makedirs(directory)
