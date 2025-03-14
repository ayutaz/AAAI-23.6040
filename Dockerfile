FROM python:3.7-slim

WORKDIR /app

# 必要なパッケージをインストール（curlとその他のツールを追加）
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    git \
    bash \
    curl \
    unzip \
    dos2unix \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 環境変数の設定
ENV PYTHONPATH=/app

# 必要なPythonパッケージのインストール
RUN pip install --no-cache-dir \
    numpy==1.18.1 \
    scikit-learn==0.22.1 \
    scipy==1.4.1 \
    soundfile==0.10.3.post1 \
    librosa==0.8.1 \
    torch==1.7.1 \
    torchvision==0.8.2 \
    torchaudio==0.7.2 \
    pandas==0.25.3 \
    tensorboard==2.1.1 \
    mir_eval==0.6 \
    matplotlib==3.3.4 \
    pytorch-ignite==0.3.0 \
    pytest==5.3.5 \
    pytest-mock==3.1.0 \
    mido==1.2.9 \
    protobuf==3.20.3

# ソースコードのコピー
COPY . .

# 必要なディレクトリを作成
RUN mkdir -p /app/data/midi_out

COPY sample_audio/*.mp3 /app/data/

# ヘルパースクリプトの作成
RUN echo '#!/bin/bash' > /app/run_genelive.sh && \
    echo '' >> /app/run_genelive.sh && \
    echo 'if [ "$1" = "fetch" ]; then' >> /app/run_genelive.sh && \
    echo '  bash scripts/fetch.sh ${2:-data}' >> /app/run_genelive.sh && \
    echo 'elif [ "$1" = "preprocess" ]; then' >> /app/run_genelive.sh && \
    echo '  bash scripts/preprocess.sh ${2:-data}' >> /app/run_genelive.sh && \
    echo 'elif [ "$1" = "train" ]; then' >> /app/run_genelive.sh && \
    echo '  python scripts/onsets_train.py "$@"' >> /app/run_genelive.sh && \
    echo 'elif [ "$1" = "test" ]; then' >> /app/run_genelive.sh && \
    echo '  python scripts/model_test.py "$@"' >> /app/run_genelive.sh && \
    echo 'elif [ "$1" = "generate" ]; then' >> /app/run_genelive.sh && \
    echo '  python scripts/prediction_stepmania.py "$@"' >> /app/run_genelive.sh && \
    echo 'else' >> /app/run_genelive.sh && \
    echo '  echo "Usage: $0 [fetch|preprocess|train|test|generate] [options]"' >> /app/run_genelive.sh && \
    echo '  echo "Example: $0 generate --onset_model_path=pretrained_model/model.pth --audio_path=/app/data/song.mp3 --midi_save_path=/app/data/output.mid --bpm_info=\"[(180.0,600,4)]\" "' >> /app/run_genelive.sh && \
    echo 'fi' >> /app/run_genelive.sh && \
    chmod +x /app/run_genelive.sh

# 実行例のスクリプトを追加（自動的に譜面生成を試すためのもの）
RUN echo '#!/bin/bash' > /app/generate_example.sh && \
    echo 'echo "Generating chart for sample audio..."' >> /app/generate_example.sh && \
    echo 'python scripts/prediction_stepmania.py \\' >> /app/generate_example.sh && \
    echo '  --onset_model_path=pretrained_model/model.pth \\' >> /app/generate_example.sh && \
    echo '  --audio_path=/app/data/sample.mp3 \\' >> /app/generate_example.sh && \
    echo '  --midi_save_path=/app/data/sample_chart.mid \\' >> /app/generate_example.sh && \
    echo '  --bpm_info="[(128.0,500,1)]"' >> /app/generate_example.sh && \
    chmod +x /app/generate_example.sh

# デフォルトのコマンド
CMD ["bash"]