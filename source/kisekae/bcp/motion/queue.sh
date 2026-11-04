#!/bin/bash
# 前の 撮影が おわるのを まってから つぎを 撮る：./queue.sh <まつ ログの 文字> <batch_cap.sh の 引数…>
M=/tmp/claude-0/-home-claude/5cf5eba2-63a4-523b-8a91-64c54d2d6b4b/scratchpad/mo
W=$1; shift
while ! grep -q "$W" $M/batch*.log 2>/dev/null; do sleep 15; done
cd $M && ./batch_cap.sh "$@"
