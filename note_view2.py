import mido
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
import os

def visualize_stepmania_chart(midi_path, output_dir, difficulty_names=None):
    """MIDIファイルからStepManiaスタイルの譜面を可視化する関数"""
    
    # MIDIファイルを読み込む
    mid = mido.MidiFile(midi_path)
    
    # 難易度名のデフォルト設定
    if difficulty_names is None:
        difficulty_names = [f"Difficulty {i+1}" for i in range(len(mid.tracks))]
    
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    
    # トラック（難易度）ごとに処理
    for track_idx, track in enumerate(mid.tracks[1:], 1):  # 最初のトラックはしばしばメタデータ
        if track_idx > len(difficulty_names):
            break
            
        # 譜面のレーン数と色を設定
        lanes = 4
        lane_colors = ['red', 'blue', 'green', 'purple']
        lane_width = 1.0
        lane_spacing = 0.2
        
        # ノートを抽出
        notes = []
        current_time = 0
        
        for msg in track:
            current_time += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                # レーンとタイミング情報を取得
                lane = msg.note % lanes
                notes.append((current_time, lane))
        
        if not notes:
            print(f"No notes found in track {track_idx}")
            continue
            
        # 時間範囲を決定
        min_time = 0
        max_time = max(note[0] for note in notes)
        
        # 図を作成
        fig, ax = plt.subplots(figsize=(10, 15))
        
        # 背景と図の範囲を設定
        ax.set_xlim(-1, lanes * (lane_width + lane_spacing))
        ax.set_ylim(max_time * 1.05, min_time - max_time * 0.05)  # 上下反転
        
        # レーンの背景を描画
        for i in range(lanes):
            x_pos = i * (lane_width + lane_spacing)
            rect = patches.Rectangle(
                (x_pos, min_time - max_time * 0.05),
                lane_width,
                max_time * 1.1,
                linewidth=1,
                edgecolor='gray',
                facecolor='lightgray',
                alpha=0.3
            )
            ax.add_patch(rect)
        
        # 小節線を描画（簡易的に一定間隔で）
        beat_interval = 480  # 一般的なMIDIの4分音符のティック数
        for beat in range(0, int(max_time) + beat_interval, beat_interval):
            ax.axhline(y=beat, color='black', linestyle='-', alpha=0.3, linewidth=0.5)
        
        # ノートを描画
        note_height = 50  # ノートの高さ
        for time, lane in notes:
            x_pos = lane * (lane_width + lane_spacing)
            rect = patches.Rectangle(
                (x_pos, time - note_height/2),
                lane_width,
                note_height,
                linewidth=1,
                edgecolor='black',
                facecolor=lane_colors[lane],
                alpha=0.8
            )
            ax.add_patch(rect)
        
        # ラベルなどを設定
        ax.set_title(f"{difficulty_names[track_idx-1]} - {len(notes)} notes", fontsize=16)
        ax.set_xlabel("Lanes", fontsize=14)
        ax.set_ylabel("Time (ticks)", fontsize=14)
        ax.set_xticks([i * (lane_width + lane_spacing) + lane_width/2 for i in range(lanes)])
        ax.set_xticklabels(['Left', 'Down', 'Up', 'Right'])
        ax.grid(False)
        
        # 保存
        output_path = os.path.join(output_dir, f"chart_{track_idx}_detailed.png")
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
        
        print(f"Saved detailed visualization for {difficulty_names[track_idx-1]} to {output_path}")

# 使用例
midi_path = "/app/data/sample_chart.mid/0.mid"
output_dir = "/app/data/visualizations"
difficulty_names = ["Beginner (10)", "Easy (20)", "Medium (30)", "Hard (40)", "Expert (50)"]

visualize_stepmania_chart(midi_path, output_dir, difficulty_names)