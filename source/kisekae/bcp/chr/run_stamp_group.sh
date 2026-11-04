#!/bin/bash
# 的中⑤ スタンプ（2〜4連勝）：馬・腕・ひづめ・ハンコを 1つの キャラに 切りぬく（1連勝と 同じ 印・同じ 置き方）
set -e
cd /home/claude/work/bcpic/chr
for p in "2 d5_2" "3 d5" "4 d5_4"; do
  set -- $p; N=$1; D=/home/claude/work/bcpic/$2; O=/home/claude/work/bcpic/chr/stamp${N}g
  mkdir -p $O
  python3 seg.py $D/src.png 430,0,1000,560 $O/mask_h.png
  python3 seg.py $D/src.png 60,80,480,520 $O/mask_s.png
  python3 - "$N" "$D" "$O" <<'PY'
import json, sys
N, D, O = sys.argv[1:4]
c = json.load(open('/home/claude/work/bcpic/chr/stamp1g/cfg.json'))
c['clean'] = D + '/clean.png'; c['out'] = O; c['masks'] = [O + '/mask_h.png', O + '/mask_s.png']
json.dump(c, open(O + '/cfg.json', 'w'), ensure_ascii=False, indent=1)
PY
  python3 chr_split.py $O/cfg.json | tail -2
done
