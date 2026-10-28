// ===== 結果ボードカスタムの 絵（App Store版・第4.91版）：ぺたっとした 色の かわいい 馬（SVG の 文字列）=====
//   bcx.js が 使う。形は すべて 一から 作った オリジナル。色は 毛の 色（PAL）と テーマの アクセント色（CSS の 変数 --bcA）
//   front（前から 見た 頭）・side（横から 見た 体：走る・立つ・ねる）・hoof（ひづめ）・小物（旗・花・クラッカー・メダル・トロフィー・王冠・札束 など）
(function (root) {
  'use strict';
  // 毛の 色：b＝体・s＝かげ・m＝鼻先・n＝たてがみ・nh＝たてがみの 明るい 所・e＝耳の 中・k＝蹄・o＝鼻の 穴と 口
  const PAL = {
    chestnut: { b: '#C9773D', s: '#A65C29', m: '#F7DDC1', n: '#5B3018', nh: '#8A4E2A', e: '#F2A08A', k: '#4B3A33', o: '#7A4128' },
    bay: { b: '#8E5430', s: '#6C3B1E', m: '#EBCBA9', n: '#22160F', nh: '#4A3023', e: '#E59B85', k: '#2E2622', o: '#5A2E18' },
    gray: { b: '#C3CAD3', s: '#9AA3AF', m: '#F1F3F6', n: '#5E6672', nh: '#848C98', e: '#F2AFBE', k: '#4F4A52', o: '#6B6470' },
    white: { b: '#FBF7EF', s: '#DCD1C0', m: '#FFFFFF', n: '#D9C397', nh: '#EEDDB8', e: '#F7B2B5', k: '#8C7B6B', o: '#B07A70' },
    black: { b: '#3F3845', s: '#29232E', m: '#9A8B91', n: '#151117', nh: '#3A3140', e: '#D08E9A', k: '#1E1A20', o: '#2A2228' },
    palomino: { b: '#E6B35B', s: '#C68F38', m: '#FFF1D6', n: '#FFF6E2', nh: '#FFFFFF', e: '#F4A48A', k: '#6A5340', o: '#9A5E2E' },
    foal: { b: '#DFA06A', s: '#BE7F4C', m: '#FBE6CF', n: '#7A4425', nh: '#A86B42', e: '#F6AE96', k: '#5A463A', o: '#8C5234' }
  };
  const EYE = '#2A1A12';
  const f = n => (Math.round(n * 100) / 100).toString();

  // ---------- 前から 見た 頭（0〜100 の 箱・頭の てっぺん y≈14・鼻先 y≈97）----------
  //  o.expr：smile（にっこり）・happy（目を 細めて 口を あける）・wink・sleep（ねむる）・cheer（大きく 口を あける）・oh（びっくり）・bite（口を 横に 広げて くわえる）・sad
  //  o.neck：首を 下へ（のぞく・見る 馬）・o.blink：まばたきの クラス（.bcbl）を 目に つける・o.tilt：頭の かたむき（度）
  function front(c, o) {
    o = o || {};
    const ex = o.expr || 'smile';
    let s = '';
    if (o.neck) {
      s += `<path d="M30 66 C29 80 27 94 25 ${o.neckTo || 112} L75 ${o.neckTo || 112} C73 94 71 80 70 66 Z" fill="${c.b}"/>`
        + `<path d="M58 70 C63 84 66 98 67 ${o.neckTo || 112} L75 ${o.neckTo || 112} C73 94 71 80 70 66 Z" fill="${c.s}" opacity=".5"/>`
        + `<path d="M37 72 C41 84 44 98 45 ${o.neckTo || 112} L52 ${o.neckTo || 112} C50 96 46 82 42 70 Z" fill="${c.n}" opacity=".0"/>`;
    }
    // 耳（うしろ）
    const ear = side => {
      const m = x => side > 0 ? 100 - x : x;
      return `<path d="M${m(31)} 30 C${m(24)} 21 ${m(22)} 10 ${m(25)} 2 C${m(34)} 6 ${m(42)} 14 ${m(45)} 24 Z" fill="${c.b}"/>`
        + `<path d="M${m(31.5)} 25.5 C${m(28)} 19 ${m(27)} 12 ${m(28.2)} 7.5 C${m(33.5)} 11 ${m(38.5)} 16.5 ${m(40.5)} 22 Z" fill="${c.e}"/>`;
    };
    s += ear(-1) + ear(1);
    // たてがみ（耳の あいだの 房）
    s += `<path d="M41 22 C42 13 47 7 53 6 C52 10 53.5 14 57 17 C60 13 63 12 66 13 C63 16 62 20 61 24 Z" fill="${c.n}"/>`;
    // 頭
    s += `<path d="M50 15 C69 15 80 28 80 45 C80 54 77.5 60 75 65 C73 71 74 78 72 85 C69.5 93.5 60.5 98 50 98 C39.5 98 30.5 93.5 28 85 C26 78 27 71 25 65 C22.5 60 20 54 20 45 C20 28 31 15 50 15 Z" fill="${c.b}"/>`;
    // ほおの かげ（右）
    s += `<path d="M73 52 C76 60 73 66 72.5 74 C72 80 71 86 68 91 C72 84 75 74 76 64 C77 59 76 55 73 52 Z" fill="${c.s}" opacity=".55"/>`;
    // 鼻先
    s += `<path d="M50 60 C63 60 72 67 72 78 C72 90 62 97 50 97 C38 97 28 90 28 78 C28 67 37 60 50 60 Z" fill="${c.m}"/>`;
    // 前髪
    s += `<path d="M38 19 C44 11 56 10 62 16 C64 19 63 24 58 28 C55 31 50 34 44 36 C47 31 47 27 45 24 C43 22 41 21 38 19 Z" fill="${c.n}"/>`
      + `<path d="M46 17 C51 14 56 14 59 17" fill="none" stroke="${c.nh}" stroke-width="1.6" stroke-linecap="round" opacity=".8"/>`;
    // ほお紅
    s += `<ellipse cx="29.5" cy="62" rx="5" ry="3" fill="#FF7E86" opacity=".42"/><ellipse cx="70.5" cy="62" rx="5" ry="3" fill="#FF7E86" opacity=".42"/>`;
    // 目
    const eyeOpen = (x, y) => `<g class="${o.blink ? 'bcbl' : ''}" style="transform-origin:${x}px ${y}px"><ellipse cx="${x}" cy="${y}" rx="6.2" ry="7.6" fill="${EYE}"/>`
      + `<circle cx="${x + 2.1}" cy="${y - 2.7}" r="2.4" fill="#FFFFFF"/><circle cx="${x - 2}" cy="${y + 3}" r="1.15" fill="#FFFFFF" opacity=".9"/></g>`;
    const eyeArc = (x, y, up) => `<path d="M${x - 6} ${y + (up ? 2 : -1)} Q${x} ${y + (up ? -5 : 5)} ${x + 6} ${y + (up ? 2 : -1)}" fill="none" stroke="${EYE}" stroke-width="2.6" stroke-linecap="round"/>`;
    if (ex === 'happy' || ex === 'cheer') s += eyeArc(37.5, 47, true) + eyeArc(62.5, 47, true);
    else if (ex === 'sleep') s += eyeArc(37.5, 48, false) + eyeArc(62.5, 48, false);
    else if (ex === 'wink') s += eyeOpen(37.5, 47) + eyeArc(62.5, 47, true);
    else if (ex === 'sad') s += eyeOpen(37.5, 48) + eyeOpen(62.5, 48) + `<path d="M30.5 40.5 L41.5 37 M69.5 40.5 L58.5 37" stroke="${EYE}" stroke-width="1.8" stroke-linecap="round"/>`;
    else s += eyeOpen(37.5, 47) + eyeOpen(62.5, 47);
    // 鼻の 穴
    s += `<ellipse cx="41.5" cy="74" rx="2.6" ry="3.5" transform="rotate(-18 41.5 74)" fill="${c.o}"/><ellipse cx="58.5" cy="74" rx="2.6" ry="3.5" transform="rotate(18 58.5 74)" fill="${c.o}"/>`;
    // 口
    if (ex === 'cheer') s += `<path d="M41 82 C44 92 56 92 59 82 Z" fill="#8E2E2A"/><path d="M45 87.5 C48 85.5 52 85.5 55 87.5 C53 90 47 90 45 87.5 Z" fill="#F07A7A"/>`;
    else if (ex === 'happy') s += `<path d="M43 83 C46 89 54 89 57 83 Z" fill="#8E2E2A"/><path d="M46.5 86.5 C49 85.3 51 85.3 53.5 86.5 C52 88 48 88 46.5 86.5 Z" fill="#F07A7A"/>`;
    else if (ex === 'oh') s += `<ellipse cx="50" cy="86" rx="3.6" ry="4.4" fill="#8E2E2A"/>`;
    else if (ex === 'bite') s += `<path d="M36 84 C42 88 58 88 64 84" fill="none" stroke="${c.o}" stroke-width="2.2" stroke-linecap="round"/>`;
    else if (ex === 'sad') s += `<path d="M44 87 Q50 83 56 87" fill="none" stroke="${c.o}" stroke-width="2" stroke-linecap="round"/>`;
    else s += `<path d="M43.5 84 Q50 89 56.5 84" fill="none" stroke="${c.o}" stroke-width="2" stroke-linecap="round"/>`;
    return o.tilt ? `<g transform="rotate(${o.tilt} 50 60)">${s}</g>` : s;
  }

  // ---------- 前足（前から）：ひざから下の 足と ひづめ。(x, y)＝ひづめの 先・a＝かたむき（度）・L＝足の 長さ ----------
  function hoof(c, x, y, a, L, w) {
    L = L || 18; w = w || 11;
    return `<g transform="translate(${f(x)} ${f(y)}) rotate(${f(a || 0)})">`
      + `<path d="M${-w / 2} ${-L} L${w / 2} ${-L} L${w / 2 + .3} -5 L${-w / 2 - .3} -5 Z" fill="${c.b}"/>`
      + `<path d="M${-w / 2 - .6} -6 L${w / 2 + .6} -6 C${w / 2 + 1.2} -2 ${w / 2 + 1} 1.5 ${w / 2 - 1} 2.5 L${-w / 2 + 1} 2.5 C${-w / 2 - 1} 1.5 ${-w / 2 - 1.2} -2 ${-w / 2 - .6} -6 Z" fill="${c.k}"/>`
      + `<path d="M${-w / 2 + 1.5} -4.6 L${w / 2 - 1.5} -4.6" stroke="#FFFFFF" stroke-opacity=".28" stroke-width="1.2" stroke-linecap="round"/></g>`;
  }

  // ---------- 横から 見た 馬（右向き・0〜140 × 0〜100：地面 y≈96）----------
  //  o.pose：run（走る：足は .bcL1〜4 の クラスで 動く）・stand（立つ）・lie（ねそべる）
  //  o.cloth：鞍の 下の 布（アクセント色）と 番号・o.expr：smile・sleep・happy
  function side(c, o) {
    o = o || {};
    const pose = o.pose || 'run', lie = pose === 'lie';
    let s = '';
    const dy = lie ? 18 : 0;               // ねそべる：体を 下へ
    // しっぽ
    s += `<g class="bcTl" style="transform-origin:31px ${44 + dy}px"><path d="M31 ${43 + dy} C20 ${40 + dy} 11 ${46 + dy} 7 ${56 + dy} C5 ${62 + dy} 7 ${69 + dy} 10 ${73 + dy} C11 ${66 + dy} 14 ${60 + dy} 19 ${57 + dy} C16 ${63 + dy} 16 ${69 + dy} 19 ${74 + dy} C20 ${66 + dy} 24 ${58 + dy} 32 ${53 + dy} Z" fill="${c.n}"/>`
      + `<path d="M26 ${47 + dy} C19 ${49 + dy} 14 ${54 + dy} 12 ${60 + dy}" fill="none" stroke="${c.nh}" stroke-width="1.6" stroke-linecap="round" opacity=".7"/></g>`;
    // 足（奥 → 手前）。run は 2つの 関節（もも・すね）
    const leg = (cls, px, py, far, fold) => {
      const col = far ? c.s : c.b;
      if (lie) {
        // ねそべる：足を 体の 下に たたむ
        return `<g class="${cls}"><path d="M${px - 4} ${py + dy - 4} C${px - 2} ${py + dy + 6} ${px + (fold || 10)} ${py + dy + 8} ${px + (fold || 10) + 8} ${py + dy + 7} L${px + (fold || 10) + 8} ${py + dy + 1} C${px + 8} ${py + dy + 2} ${px + 4} ${py + dy - 2} ${px + 5} ${py + dy - 6} Z" fill="${col}"/>`
          + `<path d="M${px + (fold || 10) + 6} ${py + dy + 1} L${px + (fold || 10) + 11} ${py + dy + 1.5} C${px + (fold || 10) + 13} ${py + dy + 3} ${px + (fold || 10) + 13} ${py + dy + 6} ${px + (fold || 10) + 11} ${py + dy + 7.5} L${px + (fold || 10) + 6} ${py + dy + 7.5} Z" fill="${c.k}"/></g>`;
      }
      return `<g class="${cls}" style="transform-origin:${px}px ${py}px">`
        + `<path d="M${px - 5.5} ${py - 4} L${px + 5.5} ${py - 4} L${px + 4.2} ${py + 15} L${px - 4.2} ${py + 15} Z" fill="${col}"/>`
        + `<g class="bcK" style="transform-origin:${px}px ${py + 14}px">`
        + `<path d="M${px - 4.2} ${py + 13} L${px + 4.2} ${py + 13} L${px + 3.6} ${py + 27} L${px - 3.6} ${py + 27} Z" fill="${col}"/>`
        + `<path d="M${px - 4.4} ${py + 26} L${px + 4.4} ${py + 26} C${px + 5} ${py + 29} ${px + 4.8} ${py + 31} ${px + 3.4} ${py + 32} L${px - 3.6} ${py + 32} C${px - 4.9} ${py + 31} ${px - 5.1} ${py + 29} ${px - 4.4} ${py + 26} Z" fill="${c.k}"/></g></g>`;
    };
    s += leg('bcL bcL3', 44, 62, true, 12) + leg('bcL bcL1', 92, 62, true, 4);
    // 体
    s += `<path d="M30 ${50 + dy} C29 ${38 + dy} 40 ${33 + dy} 55 ${34 + dy} C68 ${32 + dy} 84 ${31 + dy} 96 ${35 + dy} C106 ${39 + dy} 109 ${51 + dy} 103 ${60 + dy} C97 ${68 + dy} 84 ${70 + dy} 66 ${70 + dy} C50 ${71 + dy} 38 ${69 + dy} 33 ${62 + dy} C31 ${58 + dy} 30 ${54 + dy} 30 ${50 + dy} Z" fill="${c.b}"/>`
      + `<path d="M36 ${64 + dy} C46 ${70 + dy} 66 ${71 + dy} 84 ${69 + dy} C95 ${68 + dy} 101 ${64 + dy} 103 ${60 + dy} C99 ${66 + dy} 90 ${71 + dy} 70 ${71.5 + dy} C54 ${72 + dy} 42 ${70 + dy} 36 ${64 + dy} Z" fill="${c.s}" opacity=".6"/>`;
    // 布（アクセント色）と 番号
    if (o.cloth) {
      s += `<path d="M52 ${35 + dy} C60 ${33 + dy} 70 ${32.5 + dy} 79 ${33.5 + dy} L81 ${55 + dy} C72 ${57 + dy} 60 ${57 + dy} 51 ${55 + dy} Z" fill="var(--bcA,#E2A23B)"/>`
        + `<path d="M51.5 ${52 + dy} C60 ${54 + dy} 72 ${54 + dy} 80.6 ${52 + dy}" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity=".9"/>`
        + `<text x="66" y="${48.5 + dy}" text-anchor="middle" font-family="'BIZ UDPGothic',sans-serif" font-weight="800" font-size="12" fill="#FFFFFF">${o.num || 1}</text>`
        + `<path d="M58 ${33.5 + dy} C64 ${29 + dy} 72 ${29 + dy} 77 ${33 + dy} Z" fill="#3A2A22"/>`;
    }
    s += leg('bcL bcL4', 50, 64, false, 10) + leg('bcL bcL2', 98, 63, false, 2);
    // 首と 頭（頭の グループは .bcH：うなずき）
    const hy = lie ? 22 : 0, hx = lie ? 6 : 0;
    s += `<path d="M86 ${37 + dy} C90 ${24 + hy} 98 ${14 + hy} 106 ${11 + hy} L118 ${22 + hy} C112 ${30 + hy} 106 ${42 + dy} 104 ${52 + dy} C99 ${50 + dy} 92 ${44 + dy} 86 ${37 + dy} Z" fill="${c.b}"/>`;
    s += `<g class="bcH" style="transform-origin:${106 + hx}px ${22 + hy}px">`;
    // たてがみ（首の 上）
    s += `<path d="M84 ${36 + dy} C86 ${24 + hy} 94 ${12 + hy} 104 ${7 + hy} C102 ${11 + hy} 102 ${14 + hy} 104 ${16 + hy} C98 ${18 + hy} 95 ${24 + hy} 94 ${30 + hy} C92 ${27 + hy} 89 ${28 + hy} 88 ${32 + hy} C88 ${35 + dy} 86 ${38 + dy} 84 ${36 + dy} Z" fill="${c.n}"/>`;
    // 耳
    s += `<path d="M104 ${9 + hy} C102 ${2 + hy} 104 ${-3 + hy} 108 ${-6 + hy} C111 ${-1 + hy} 112 ${5 + hy} 110 ${11 + hy} Z" fill="${c.b}"/><path d="M105.6 ${7.5 + hy} C104.8 ${3 + hy} 105.8 ${-.5 + hy} 107.8 ${-2.5 + hy} C109.3 ${0.5 + hy} 109.7 ${4.5 + hy} 108.6 ${8.5 + hy} Z" fill="${c.e}"/>`;
    // 頭（大きめ：かわいく）
    s += `<path d="M100 ${16 + hy} C104 ${6 + hy} 118 ${4 + hy} 126 ${12 + hy} C132 ${18 + hy} 137 ${26 + hy} 136 ${33 + hy} C135 ${40 + hy} 128 ${43 + hy} 121 ${41 + hy} C115 ${40 + hy} 110 ${37 + hy} 106 ${33 + hy} C100 ${28 + hy} 98 ${22 + hy} 100 ${16 + hy} Z" fill="${c.b}"/>`;
    s += `<path d="M122 ${24 + hy} C130 ${23 + hy} 137 ${28 + hy} 136 ${34 + hy} C135 ${40 + hy} 128 ${43 + hy} 121 ${41 + hy} C117 ${40 + hy} 115 ${36 + hy} 116 ${31 + hy} C117 ${27 + hy} 119 ${24.5 + hy} 122 ${24 + hy} Z" fill="${c.m}"/>`;
    // 前髪
    s += `<path d="M104 ${8 + hy} C110 ${4 + hy} 117 ${6 + hy} 119 ${11 + hy} C114 ${11 + hy} 110 ${14 + hy} 108 ${19 + hy} C107 ${15 + hy} 105 ${12 + hy} 104 ${8 + hy} Z" fill="${c.n}"/>`;
    // 目
    const ex = o.expr || 'smile';
    if (ex === 'sleep') s += `<path d="M110 ${21 + hy} Q114.5 ${25 + hy} 119 ${21 + hy}" fill="none" stroke="${EYE}" stroke-width="2.2" stroke-linecap="round"/>`;
    else if (ex === 'happy') s += `<path d="M110 ${22 + hy} Q114.5 ${17 + hy} 119 ${22 + hy}" fill="none" stroke="${EYE}" stroke-width="2.2" stroke-linecap="round"/>`;
    else s += `<g class="${o.blink ? 'bcbl' : ''}" style="transform-origin:114.5px ${20 + hy}px"><ellipse cx="114.5" cy="${20 + hy}" rx="4.4" ry="5.4" fill="${EYE}"/><circle cx="116" cy="${18 + hy}" r="1.7" fill="#FFFFFF"/><circle cx="113.2" cy="${22.4 + hy}" r=".8" fill="#FFFFFF" opacity=".9"/></g>`;
    s += `<ellipse cx="111" cy="${28 + hy}" rx="3.6" ry="2.2" fill="#FF7E86" opacity=".42"/>`;
    s += `<ellipse cx="131.5" cy="${30 + hy}" rx="1.7" ry="2.4" transform="rotate(20 131.5 ${30 + hy})" fill="${c.o}"/>`;
    s += `<path d="M125 ${37 + hy} Q128.5 ${39.5 + hy} 132 ${37 + hy}" fill="none" stroke="${c.o}" stroke-width="1.6" stroke-linecap="round"/>`;
    s += '</g>';
    return s;
  }

  // ---------- 前から 見た 体（胸と 前足）：頭の 下に 置く。0〜100 の 箱（頭と 同じ）の y＝88〜150。
  //  o.arm：'up'（右の 前足を 上げる）・'stick'（右の 前足で 棒を 持つ：棒の 先は o.stick＝[x, y]）・'wave'（右の 前足を ふる：.bcWv）
  function chest(c, o) {
    o = o || {};
    let s = '';
    // 胸
    s += `<path d="M27 86 C22 100 22 122 28 138 C34 146 66 146 72 138 C78 122 78 100 73 86 Z" fill="${c.b}"/>`
      + `<path d="M60 92 C68 104 70 122 66 140 C70 139 72 138 72 138 C78 122 78 100 73 86 Z" fill="${c.s}" opacity=".5"/>`;
    // 左の 前足（下へ。o.arm＝'stick'：左の 前足を 左上へ 上げて 自撮り棒を 持つ：棒の 先は o.stick＝[x, y]）
    if (o.arm === 'stick') {
      const [sx, sy] = o.stick || [-30, -10];
      s += `<path d="M38 116 C32 108 24 100 16 94 L10 102 C18 108 26 116 30 122 Z" fill="${c.b}"/>`;
      s += `<path d="M12 97 L${sx} ${sy}" stroke="#2F3440" stroke-width="2.8" stroke-linecap="round"/><path d="M12 97 L${sx} ${sy}" stroke="#9AA3B0" stroke-width=".9" stroke-linecap="round" opacity=".8"/>`;
      s += hoof(c, 9, 99, 128, 8, 11.5);
    } else s += `<path d="M30 128 L42 128 L41.5 150 L30.5 150 Z" fill="${c.b}"/>` + hoof(c, 36, 156, 0, 10, 11.5);
    // 右の 前足
    if (o.arm === 'up' || o.arm === 'wave') {
      s += `<g class="${o.arm === 'wave' ? 'bcWv' : 'bcUp'}" style="transform-origin:66px 112px"><path d="M60 116 C64 104 70 92 76 80 L86 85 C80 97 74 109 70 121 Z" fill="${c.b}"/>` + hoof(c, 83, 78, 205, 10, 11.5) + '</g>';
    } else {
      s += `<path d="M58 128 L70 128 L69.5 150 L58.5 150 Z" fill="${c.b}"/>` + hoof(c, 64, 156, 0, 10, 11.5);
    }
    return s;
  }

  // ---------- 横断幕：前から 見た 立った 馬が 両方の 前足を 上げて、頭の 上の ボードを ひづめで 持つ（-5〜105 × -42〜182：ひづめの 先 y≈-34.5・地面 y≈177）----------
  //  うしろ足は .bcR1・.bcR2（走る）。o.flip＝左右 反対（しっぽの 向き）
  function carrier(c, o) {
    o = o || {};
    let s = '';
    // しっぽ（体の うしろ）
    s += `<g class="bcTl" style="transform-origin:66px 128px"><path d="M64 124 C78 124 88 134 91 150 C84 145 77 143 70 145 C74 139 72 132 64 129 Z" fill="${c.n}"/>`
      + `<path d="M70 128 C78 131 84 137 86 144" fill="none" stroke="${c.nh}" stroke-width="1.5" stroke-linecap="round" opacity=".7"/></g>`;
    // うしろ足（走る）
    s += `<g class="bcR1" style="transform-origin:39px 136px"><path d="M32 132 L46 132 L45 166 L33.5 166 Z" fill="${c.s}"/>${hoof(c, 39.3, 173, 0, 9, 12.5)}</g>`;
    s += `<g class="bcR2" style="transform-origin:61px 136px"><path d="M54 132 L68 132 L66.5 166 L55 166 Z" fill="${c.b}"/>${hoof(c, 60.7, 173, 0, 9, 12.5)}</g>`;
    // 前足（両方 上へ：頭の 横を とおって ひづめで 持つ）
    s += `<path d="M25 106 C18 72 12 30 9.5 -24 L21.5 -24 C23 28 29 68 37 100 Z" fill="${c.s}"/>` + hoof(c, 15.5, -32, 180, 10, 12.5);
    s += `<path d="M75 106 C82 72 88 30 90.5 -24 L78.5 -24 C77 28 71 68 63 100 Z" fill="${c.b}"/>` + hoof(c, 84.5, -32, 180, 10, 12.5);
    // 胸と おなか
    s += `<path d="M27 86 C21 102 22 126 29 140 C36 148 64 148 71 140 C78 126 79 102 73 86 Z" fill="${c.b}"/>`
      + `<path d="M60 92 C68 106 70 124 66 144 C69 143 71 141 71 140 C78 126 79 102 73 86 Z" fill="${c.s}" opacity=".5"/>`
      + `<path d="M38 108 C44 112 56 112 62 108" fill="none" stroke="${c.s}" stroke-width="1.6" stroke-linecap="round" opacity=".6"/>`;
    // 頭
    s += front(c, { expr: o.expr || 'happy', blink: true });
    return o.flip ? `<g transform="translate(100 0) scale(-1 1)">${s}</g>` : s;
  }

  // ---------- 子馬が ぶら下がる（前から）：0〜100 × 0〜150。ひづめの 先（ボードの ふち）は y≈6 ----------
  function foal(c) {
    let s = '';
    // しっぽ（体の うしろ）
    s += `<g class="bcTl" style="transform-origin:57px 116px"><path d="M55 114 C67 116 75 124 77 136 C71 132 65 130 59 130 C63 126 61 120 55 118 Z" fill="${c.n}"/></g>`;
    // 前足（上へ：ボードの ふちを つかむ）
    s += `<path d="M30 70 C28 52 27 30 29 10 L39 10 C39 30 40 52 42 70 Z" fill="${c.b}"/><path d="M70 70 C72 52 73 30 71 10 L61 10 C61 30 60 52 58 70 Z" fill="${c.s}"/>`;
    s += hoof(c, 34, 4, 180, 8, 11) + hoof(c, 66, 4, 180, 8, 11);
    // うしろ足（ぱたぱた）
    s += `<g class="bcPd1" style="transform-origin:43px 114px"><path d="M38 112 L48 112 L47 134 L39 134 Z" fill="${c.s}"/>${hoof(c, 43, 140, 0, 8, 10)}</g>`;
    s += `<g class="bcPd2" style="transform-origin:57px 114px"><path d="M52 112 L62 112 L61 134 L53 134 Z" fill="${c.b}"/>${hoof(c, 57, 140, 0, 8, 10)}</g>`;
    // 体
    s += `<ellipse cx="50" cy="98" rx="17" ry="19" fill="${c.b}"/><path d="M57 82 C65 90 67 104 61 116 C65 114 69 106 67 94 C66 88 62 84 57 82 Z" fill="${c.s}" opacity=".5"/>`;
    // 頭（大きめ）
    s += `<g transform="translate(13 10) scale(.74)">${front(c, { expr: 'oh', blink: true })}</g>`;
    // 汗
    s += `<path d="M86 34 C88 38 90 41 88 44 C86 46 83 45 83 42 C83 39 85 36 86 34 Z" fill="#9FDCFF" stroke="#FFFFFF" stroke-width=".8"/>`;
    return s;
  }

  // ---------- 小物 ----------
  // 吹き出し（w×h・しっぽの 向き：'l'＝左下・'r'＝右下・'u'＝上）
  function bubble(w, h, tail, txt, fs) {
    const r = Math.min(14, h / 2);
    let t = '';
    if (tail === 'l') t = `<path d="M${w * .18} ${h - 2} L${w * .06} ${h + 12} L${w * .32} ${h - 2} Z" fill="#FFFFFF" stroke="var(--bcA,#E2A23B)" stroke-width="2.4" stroke-linejoin="round"/>`;
    else if (tail === 'r') t = `<path d="M${w * .68} ${h - 2} L${w * .92} ${h + 12} L${w * .82} ${h - 2} Z" fill="#FFFFFF" stroke="var(--bcA,#E2A23B)" stroke-width="2.4" stroke-linejoin="round"/>`;
    else if (tail === 'u') t = `<path d="M${w * .3} 2 L${w * .22} -12 L${w * .46} 2 Z" fill="#FFFFFF" stroke="var(--bcA,#E2A23B)" stroke-width="2.4" stroke-linejoin="round"/>`;
    return `<svg viewBox="-4 -14 ${w + 8} ${h + 30}" width="${w + 8}" height="${h + 30}" aria-hidden="true">${t}<rect x="0" y="0" width="${w}" height="${h}" rx="${r}" fill="#FFFFFF" stroke="var(--bcA,#E2A23B)" stroke-width="2.4"/>`
      + (tail === 'l' ? `<path d="M${w * .19} ${h - 3.4} L${w * .31} ${h - 3.4}" stroke="#FFFFFF" stroke-width="3"/>` : tail === 'r' ? `<path d="M${w * .69} ${h - 3.4} L${w * .81} ${h - 3.4}" stroke="#FFFFFF" stroke-width="3"/>` : tail === 'u' ? `<path d="M${w * .29} 3.4 L${w * .45} 3.4" stroke="#FFFFFF" stroke-width="3"/>` : '')
      + `<text x="${w / 2}" y="${h / 2 + fs * .36}" text-anchor="middle" font-family="'Dela Gothic One','BIZ UDPGothic',sans-serif" font-size="${fs}" fill="#2A1F18">${txt}</text></svg>`;
  }
  // 花（5まいの 花びら）：まん中 (0,0)・r＝花の 半径・col＝花びら・cc＝まん中
  function flower(r, col, cc) {
    let s = '';
    for (let i = 0; i < 5; i++) {
      const a = i * 72 - 90;
      s += `<ellipse cx="${f(Math.cos(a * Math.PI / 180) * r * .52)}" cy="${f(Math.sin(a * Math.PI / 180) * r * .52)}" rx="${f(r * .5)}" ry="${f(r * .36)}" transform="rotate(${a} ${f(Math.cos(a * Math.PI / 180) * r * .52)} ${f(Math.sin(a * Math.PI / 180) * r * .52)})" fill="${col}"/>`;
    }
    return s + `<circle r="${f(r * .3)}" fill="${cc}"/><circle cx="${f(-r * .08)}" cy="${f(-r * .09)}" r="${f(r * .1)}" fill="#FFFFFF" opacity=".7"/>`;
  }
  // 茎と 葉（下 (0,0) から 上へ h）
  function stem(h, bend) {
    const b = bend || 0;
    return `<path d="M0 0 C${f(b * .5)} ${f(-h * .4)} ${f(b)} ${f(-h * .7)} ${f(b)} ${f(-h)}" fill="none" stroke="#3F9A4B" stroke-width="2.4" stroke-linecap="round"/>`
      + `<path d="M${f(b * .25)} ${f(-h * .35)} C${f(b * .25 + 8)} ${f(-h * .35 - 7)} ${f(b * .25 + 13)} ${f(-h * .35 - 2)} ${f(b * .25 + 14)} ${f(-h * .35 + 2)} C${f(b * .25 + 8)} ${f(-h * .35 + 3)} ${f(b * .25 + 3)} ${f(-h * .35 + 2)} ${f(b * .25)} ${f(-h * .35)} Z" fill="#5BBF5E"/>`;
  }
  // ゴール板（ポールと 丸い 板）：下 (0,0)・高さ h
  function goalPost(h) {
    return `<rect x="-2.4" y="${-h}" width="4.8" height="${h}" rx="2" fill="#FFFFFF" stroke="#3A3A44" stroke-width="1.2"/>`
      + `<circle cx="0" cy="${-h - 8}" r="11" fill="#FFFFFF" stroke="#3A3A44" stroke-width="1.4"/><circle cx="0" cy="${-h - 8}" r="7.2" fill="none" stroke="#E2323A" stroke-width="3.2"/>`;
  }
  // スマホ（うら：カメラの レンズ）・w×h
  function phone(w, h) {
    return `<rect x="0" y="0" width="${w}" height="${h}" rx="${f(w * .2)}" fill="#2F3440" stroke="#FFFFFF" stroke-width="1.2"/><rect x="${f(w * .12)}" y="${f(h * .06)}" width="${f(w * .5)}" height="${f(w * .5)}" rx="${f(w * .14)}" fill="#1B1E26"/>`
      + `<circle cx="${f(w * .27)}" cy="${f(h * .06 + w * .14)}" r="${f(w * .09)}" fill="#5E7CC9"/><circle cx="${f(w * .47)}" cy="${f(h * .06 + w * .36)}" r="${f(w * .08)}" fill="#5E7CC9"/><circle cx="${f(w * .27)}" cy="${f(h * .06 + w * .14)}" r="${f(w * .035)}" fill="#FFFFFF" opacity=".8"/>`;
  }
  // 「的中」の ハンコ（まん中 (0,0)・半径 r・色 ink）：二重の 輪・上に 蹄鉄・まん中に 的中
  function stamp(r, ink) {
    return `<g fill="none" stroke="${ink}"><circle r="${f(r)}" stroke-width="${f(r * .1)}"/><circle r="${f(r * .8)}" stroke-width="${f(r * .045)}"/></g>`
      + `<path d="M${f(-r * .34)} ${f(-r * .3)} C${f(-r * .38)} ${f(-r * .62)} ${f(r * .38)} ${f(-r * .62)} ${f(r * .34)} ${f(-r * .3)}" fill="none" stroke="${ink}" stroke-width="${f(r * .12)}" stroke-linecap="round"/>`
      + `<text x="0" y="${f(r * .34)}" text-anchor="middle" font-family="'Dela Gothic One','BIZ UDPGothic',sans-serif" font-size="${f(r * .66)}" fill="${ink}" letter-spacing="-1">的中</text>`;
  }
  // 蹄（大きい：ハンコを 押す 足）：上から 下へ。(0,0)＝ひづめの 先。長さ L
  function bigLeg(c, L) {
    return `<path d="M-12 ${-L} L12 ${-L} L11 -16 L-11 -16 Z" fill="${c.b}"/><path d="M-12 ${-L} L-4 ${-L} L-5 -16 L-11 -16 Z" fill="${c.s}" opacity=".5"/>`
      + `<path d="M-13 -18 L13 -18 C14.5 -10 14 -2 11 2 L-11 2 C-14 -2 -14.5 -10 -13 -18 Z" fill="${c.k}"/><path d="M-9 -14 L9 -14" stroke="#FFFFFF" stroke-opacity=".3" stroke-width="2" stroke-linecap="round"/>`;
  }
  // クラッカー（円すい）：先 (0,0)・向き a 度
  function cracker(a, col) {
    return `<g transform="rotate(${a})"><path d="M0 0 L-9 34 C-4 37 4 37 9 34 Z" fill="${col}"/><path d="M-3 12 L3 12 M-5.5 22 L5.5 22" stroke="#FFFFFF" stroke-width="2.4" opacity=".85"/><ellipse cx="0" cy="34.5" rx="9" ry="3" fill="#FFD966"/></g>`;
  }
  // 花束（下 (0,0)）
  function bouquet() {
    let s = `<path d="M-6 0 L6 0 L18 -30 L-18 -30 Z" fill="#FFF6E8" stroke="#E7D3B5" stroke-width="1"/>`;
    const fl = [[-12, -38, '#FF7FA8'], [0, -44, '#FFD34D'], [12, -38, '#FF8A6B'], [-6, -50, '#FFFFFF'], [7, -52, '#FF7FA8'], [-16, -48, '#B9A2FF'], [16, -49, '#FFFFFF']];
    fl.forEach(p => { s += `<g transform="translate(${p[0]} ${p[1]})">${flower(8.5, p[2], p[2] === '#FFFFFF' ? '#FFC93C' : '#FFF1B8')}</g>`; });
    s += `<path d="M-14 -28 L14 -28 L6 -16 L-6 -16 Z" fill="#FFF6E8"/>`
      + `<path d="M0 -14 C-6 -22 -16 -20 -14 -13 C-12 -8 -5 -10 0 -14 Z M0 -14 C6 -22 16 -20 14 -13 C12 -8 5 -10 0 -14 Z" fill="var(--bcA,#E2A23B)"/>`
      + `<path d="M-1 -13 L-7 0 L-3 -1 L0 -11 L3 -1 L7 0 L1 -13 Z" fill="var(--bcA,#E2A23B)"/><circle cx="0" cy="-14" r="3" fill="var(--bcA,#E2A23B)" stroke="#FFFFFF" stroke-width=".8"/>`;
    return s;
  }
  // 金メダル（リボンの 上 (0,0)・金の 円の 半径 r）
  function medal(r) {
    return `<path d="M-14 0 L-4 ${f(r * 1.4)} L4 ${f(r * 1.4)} L14 0 L6 0 L0 ${f(r * .9)} L-6 0 Z" fill="var(--bcA,#E2323A)"/><path d="M-6 0 L0 ${f(r * .9)} L6 0" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity=".7"/>`
      + `<circle cx="0" cy="${f(r * 1.4 + r)}" r="${f(r)}" fill="#F2B632"/><circle cx="0" cy="${f(r * 1.4 + r)}" r="${f(r * .78)}" fill="#FFD34D" stroke="#E09A1A" stroke-width="1.2"/>`
      + `<path d="M${f(-r * .34)} ${f(r * 1.4 + r * 1.2)} C${f(-r * .42)} ${f(r * 1.4 + r * .55)} ${f(r * .42)} ${f(r * 1.4 + r * .55)} ${f(r * .34)} ${f(r * 1.4 + r * 1.2)}" fill="none" stroke="#B87A12" stroke-width="${f(r * .17)}" stroke-linecap="round"/>`
      + `<path d="M${f(-r * .5)} ${f(r * 1.4 + r * .5)} C${f(-r * .3)} ${f(r * 1.4 + r * .2)} ${f(r * .1)} ${f(r * 1.4 + r * .15)} ${f(r * .35)} ${f(r * 1.4 + r * .3)}" fill="none" stroke="#FFFFFF" stroke-width="1.4" opacity=".7" stroke-linecap="round"/>`;
  }
  // トロフィー（下 (0,0)・高さ h）
  function trophy(h) {
    const k = h / 64;
    return `<g transform="scale(${f(k)})"><rect x="-17" y="-8" width="34" height="8" rx="2" fill="#6B4A2A"/><rect x="-12" y="-14" width="24" height="7" rx="1.5" fill="#E09A1A"/>`
      + `<path d="M-4 -14 L4 -14 L3 -24 L-3 -24 Z" fill="#E09A1A"/>`
      + `<path d="M-18 -60 L18 -60 C18 -40 10 -27 0 -25 C-10 -27 -18 -40 -18 -60 Z" fill="#FFC93C" stroke="#E09A1A" stroke-width="1.4"/>`
      + `<path d="M-18 -55 C-28 -55 -29 -40 -16 -37 M18 -55 C28 -55 29 -40 16 -37" fill="none" stroke="#FFC93C" stroke-width="4" stroke-linecap="round"/>`
      + `<path d="M-11 -56 C-11 -44 -7 -35 -2 -31" fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round" opacity=".7"/>`
      + `<path d="M-6 -48 C-6 -54 6 -54 6 -48" fill="none" stroke="#B87A12" stroke-width="2.6" stroke-linecap="round"/><circle cx="0" cy="-42" r="2.2" fill="#B87A12"/></g>`;
  }
  // 黄金の どでかい 冠（下の まん中 (0,0)・はば w）
  function crown(w) {
    const k = w / 120;
    return `<g transform="scale(${f(k)})"><path d="M-56 0 L-60 -52 L-36 -26 L-18 -66 L0 -32 L18 -66 L36 -26 L60 -52 L56 0 Z" fill="#FFC93C" stroke="#D18A10" stroke-width="2.4" stroke-linejoin="round"/>`
      + `<path d="M-56 0 L56 0 L57 -12 L-57 -12 Z" fill="#F2A81E" stroke="#D18A10" stroke-width="2"/>`
      + `<path d="M-48 -18 L-50 -40 M-14 -30 L-17 -52 M44 -20 L48 -40" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity=".55"/>`
      + [[-60, -52, '#E2323A'], [-18, -66, '#2F7BFF'], [18, -66, '#2FBF71'], [60, -52, '#B34CFF']].map(p => `<circle cx="${p[0]}" cy="${p[1]}" r="6.2" fill="#FFE27A" stroke="#D18A10" stroke-width="1.6"/><circle cx="${p[0]}" cy="${p[1]}" r="3.2" fill="${p[2]}"/>`).join('')
      + [[-34, -6, '#E2323A'], [0, -6, '#2F7BFF'], [34, -6, '#2FBF71']].map(p => `<rect x="${p[0] - 5}" y="${p[1] - 4}" width="10" height="8" rx="2" fill="${p[2]}" stroke="#FFF4C8" stroke-width="1.2"/>`).join('')
      + `<path d="M0 -30 L5 -24 L0 -18 L-5 -24 Z" fill="#E2323A" stroke="#FFF4C8" stroke-width="1"/></g>`;
  }
  // 金で できた 札束（まん中 (0,0)・はば w・かたむき a）
  function bills(w, a) {
    const h = w * .48;
    return `<g transform="rotate(${a || 0})"><rect x="${f(-w / 2)}" y="${f(-h / 2 + 3)}" width="${f(w)}" height="${f(h)}" rx="2" fill="#C98A16"/>`
      + `<rect x="${f(-w / 2)}" y="${f(-h / 2)}" width="${f(w)}" height="${f(h)}" rx="2" fill="#FFD24A" stroke="#D18A10" stroke-width="1"/>`
      + `<rect x="${f(-w / 2 + 3)}" y="${f(-h / 2 + 3)}" width="${f(w - 6)}" height="${f(h - 6)}" rx="1.5" fill="none" stroke="#E2A31E" stroke-width="1"/>`
      + `<circle cx="${f(-w * .22)}" cy="0" r="${f(h * .26)}" fill="none" stroke="#D18A10" stroke-width="1.2"/><text x="${f(-w * .22)}" y="${f(h * .14)}" text-anchor="middle" font-family="'BIZ UDPGothic',sans-serif" font-weight="800" font-size="${f(h * .38)}" fill="#B87A12">金</text>`
      + `<rect x="${f(w * .08)}" y="${f(-h / 2 - 1)}" width="${f(w * .2)}" height="${f(h + 2)}" fill="#FFFFFF" opacity=".92"/><rect x="${f(w * .08)}" y="${f(-h / 2 - 1)}" width="${f(w * .2)}" height="${f(h + 2)}" fill="none" stroke="#E2A31E" stroke-width=".8"/>`
      + `<path d="M${f(-w / 2 + 4)} ${f(-h / 2 + 2)} L${f(-w * .2)} ${f(-h / 2 + 2)}" stroke="#FFFFFF" stroke-width="1.4" opacity=".6"/></g>`;
  }
  // きらめき（4本の 光）
  function spark(r, col) {
    return `<path d="M0 ${f(-r)} C${f(r * .12)} ${f(-r * .12)} ${f(r * .12)} ${f(-r * .12)} ${f(r)} 0 C${f(r * .12)} ${f(r * .12)} ${f(r * .12)} ${f(r * .12)} 0 ${f(r)} C${f(-r * .12)} ${f(r * .12)} ${f(-r * .12)} ${f(r * .12)} ${f(-r)} 0 C${f(-r * .12)} ${f(-r * .12)} ${f(-r * .12)} ${f(-r * .12)} 0 ${f(-r)} Z" fill="${col}"/>`;
  }
  // 土けむり（ぽわっ）
  function puff(r, col) {
    return `<g fill="${col || '#FFFFFF'}"><circle cx="0" cy="0" r="${f(r)}"/><circle cx="${f(r * .9)}" cy="${f(r * .25)}" r="${f(r * .75)}"/><circle cx="${f(-r * .9)}" cy="${f(r * .25)}" r="${f(r * .7)}"/></g>`;
  }

  root.TengelBoardArt = { PAL: PAL, front: front, hoof: hoof, side: side, chest: chest, carrier: carrier, foal: foal, bubble: bubble, flower: flower, stem: stem, goalPost: goalPost, phone: phone,
    stamp: stamp, bigLeg: bigLeg, cracker: cracker, bouquet: bouquet, medal: medal, trophy: trophy, crown: crown, bills: bills, spark: spark, puff: puff, f: f };
})(typeof window !== 'undefined' ? window : globalThis);
