#!/bin/bash
# いくつかの デザインを 順に 写して、点めつを しらべて、動画に して、コマを けす
M=/tmp/claude-0/-home-claude/5cf5eba2-63a4-523b-8a91-64c54d2d6b4b/scratchpad/mo
cd $M
while [ $# -gt 0 ]; do
  CL=$1; TITLE=$2; shift 2
  NAMES=$(python3 -c "import json;print(','.join(c['name'] for c in json.load(open('$M/$CL'))))")
  FR=$M/fr_${CL%.json}; rm -rf $FR
  echo "== $CL $(date +%H:%M:%S)"
  EXP=bcp_chr_exp2.js CHRCFG=${SNAP:-$M/stage_snapshot.json} DPR=2 python3 shots_chr.py $FR $CL 2>&1 | tail -6
  for n in ${NAMES//,/ }; do echo -n "flash $n: "; (cd /home/claude/tengel/source && AREA=.1 python3 kisekae/flash_px.py $FR/$n 0 2>&1 | tail -1); done
  python3 make_video.py $FR "$M/$TITLE" $NAMES 2>&1 | tail -1
  rm -rf $FR
  echo "done $TITLE $(date +%H:%M:%S)"
done
