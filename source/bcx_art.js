// ===== 結果ボードカスタムの 絵（App Store版・第4.91版）：ぺたっとした 色の かわいい 馬（SVG の 文字列）=====
//   bcx.js が 使う。形は すべて 一から 作った オリジナル。色は 毛の 色（PAL）と テーマの アクセント色（CSS の 変数 --bcA）
//   第4.113版：飾りは 16「ボードを持つ馬」だけに なった ので、その 絵が ない とき（CI）の SVG の 馬に 使う front（前から 見た 頭）・hoof（ひづめ）・puff（鼻の 息）だけ 残した
//   （横から 見た 馬・子馬・小物 などは 1〜21 と いっしょに 消した）
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

  // 土けむり（ぽわっ）
  function puff(r, col) {
    return `<g fill="${col || '#FFFFFF'}"><circle cx="0" cy="0" r="${f(r)}"/><circle cx="${f(r * .9)}" cy="${f(r * .25)}" r="${f(r * .75)}"/><circle cx="${f(-r * .9)}" cy="${f(r * .25)}" r="${f(r * .7)}"/></g>`;
  }

  root.TengelBoardArt = { PAL: PAL, front: front, hoof: hoof, puff: puff, f: f };
})(typeof window !== 'undefined' ? window : globalThis);
