import mido
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import os

def visualize_midi(midi_path, output_dir, difficulty_names=None):
    """MIDIファイルから譜面を可視化して画像として保存する関数"""
    
    # MIDIファイルを読み込む
    mid = mido.MidiFile(midi_path)
    
    # トラック情報を表示（デバッグ用）
    print(f"Total tracks in MIDI: {len(mid.tracks)}")
    for i, track in enumerate(mid.tracks):
        print(f"Track {i}: {len(track)} messages")
    
    # 難易度名のデフォルト設定（トラック数に合わせる）
    if difficulty_names is None or len(difficulty_names) < len(mid.tracks):
        difficulty_names = [f"Difficulty {i+1}" for i in range(len(mid.tracks))]
    
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    
    # トラック（難易度）ごとに処理
    for track_idx, track in enumerate(mid.tracks):
        # 難易度名の範囲チェック
        if track_idx >= len(difficulty_names):
            diff_name = f"Additional Track {track_idx+1}"
        else:
            diff_name = difficulty_names[track_idx]
        
        # 譜面のレーン数（通常は4レーン）と長さを設定
        lanes = 4
        # 最大時間を見つける（ミリ秒単位）
        max_time = 0
        notes = []
        
        # 絶対時間の計算用
        current_time = 0
        
        # ノートイベントを抽出
        for msg in track:
            current_time += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                # レーン番号（0-3）を取得（MIDIノート番号からマッピング）
                lane = msg.note % lanes
                # 時間情報（ティック）を取得
                time = current_time
                notes.append((time, lane))
                max_time = max(max_time, time)
        
        # ノートがない場合はスキップ
        if not notes:
            print(f"No notes found in track {track_idx}, skipping visualization")
            continue
        
        # グリッドサイズを設定
        time_resolution = 100  # 時間方向の解像度
        grid_height = int(max_time / time_resolution) + 1
        grid_width = lanes
        
        # グリッドを初期化（すべて0）
        grid = np.zeros((grid_height, grid_width))
        
        # ノートをグリッドに配置
        for time, lane in notes:
            row = int(time / time_resolution)
            col = lane
            grid[row, col] = 1
        
        # 可視化
        plt.figure(figsize=(8, 12))
        cmap = ListedColormap(['white', 'red'])
        plt.imshow(grid, cmap=cmap, aspect='auto')
        plt.title(f"{diff_name} - {len(notes)} notes")
        plt.xlabel("Lanes")
        plt.ylabel("Time (descending)")
        plt.xticks(range(lanes), ['Left', 'Down', 'Up', 'Right'])
        plt.gca().invert_yaxis()  # 時間を上から下に流れるように
        
        # 保存
        output_path = os.path.join(output_dir, f"track_{track_idx+1}.png")
        plt.savefig(output_path)
        plt.close()
        
        print(f"Saved visualization for {diff_name} to {output_path}")

# 使用例
midi_path = "/app/data/sample_chart.mid/0.mid"
output_dir = "/app/data/visualizations"
difficulty_names = ["Beginner (10)", "Easy (20)", "Medium (30)", "Hard (40)", "Expert (50)"]

visualize_midi(midi_path, output_dir, difficulty_names)