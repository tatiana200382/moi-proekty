#!/bin/bash
# ffmpeg.sh — обёртка над локальным ffmpeg 9.0 (вне репозитория).
# Использование: ./tools/ffmpeg.sh -i video.mp4 -vf scale=1080:-2 out.mp4
exec "$HOME/.local/bin/ffmpeg" "$@"
