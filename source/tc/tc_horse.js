// トレーニングセンターの 馬（3D）：フィールドの 上を ランダムに 歩いたり 止まったり（止まる 方が 多い）・30回に 1回 朝と 夕方は 1周 走る／夜は 1分 寝る
//   折り紙の 継ぎ目を 関節に（まさちゃん 11/08 09:45）：頭と 首・首の つけ根・足の つけ根・ひざ・足首・しっぽの つけ根
//   データ：tc_horse_<色>.json（骨・数）＋ .bin（位置・法線・色・骨・三角）。座標は y 上・x 前（頭）・z 右・地面 y=0・高さ 約 2.15
//   描き方：フィールドの 絵の 上に「少し 上から 見た」3D（正射影・見下ろし 28°）で、立って いる 場所の 奥行きで 大きさを かえる
(function () {
  'use strict';
  const TAU = Math.PI * 2;
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const smooth = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
  const lerp = (a, b, t) => a + (b - a) * t;
  const angDiff = (a, b) => { let d = (b - a) % TAU; if (d > Math.PI) d -= TAU; if (d < -Math.PI) d += TAU; return d; };

  // ---------- 行列（4x4・列 優先＝WebGL と 同じ） ----------
  const M = {
    id: () => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    mul: (a, b) => { const o = new Array(16); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) { let s = 0; for (let k = 0; k < 4; k++) s += a[k * 4 + r] * b[c * 4 + k]; o[c * 4 + r] = s; } return o; },
    tr: (x, y, z) => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, x, y, z, 1],
    rz: a => { const c = Math.cos(a), s = Math.sin(a); return [c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]; },
    ry: a => { const c = Math.cos(a), s = Math.sin(a); return [c, 0, -s, 0, 0, 1, 0, 0, s, 0, c, 0, 0, 0, 0, 1]; },
    rx: a => { const c = Math.cos(a), s = Math.sin(a); return [1, 0, 0, 0, 0, c, s, 0, 0, -s, c, 0, 0, 0, 0, 1]; },
    sc: (x, y, z) => [x, 0, 0, 0, 0, y, 0, 0, 0, 0, z, 0, 0, 0, 0, 1],
  };

  const VS = [
    'attribute vec3 aPos,aCol;attribute vec4 aNrm;attribute float aBone,aBone2,aBw,aCv;attribute vec2 aUV;uniform float uBlend;',       // aNrm：xyz なめらかな 法線・w 影の なじみ（AO：bake_ao.py）       // aBone2・aBw：関節の 近くは となりの 骨も まぜる（なめらかに 曲がる）
    'uniform mat4 uB[18];uniform mat4 uV;uniform mat3 uR;uniform vec4 uP;uniform vec4 uEm;',     // uV：体 → 見る 向き（向き・見下ろし・大きさ）・uR：その 回転だけ（法線 用）・uP：画面の 場所（clip x,y）と 深さの 倍率・uEm：両目の まん中（xyz）と 頭の 骨の 番号（w）
    'varying vec3 vN,vC;varying vec3 vW;varying vec2 vUV;varying vec3 vR0,vR1,vR2;varying vec4 vP;varying float vAo,vCv,vB;',
    'void main(){float bw=aBw*uBlend;mat4 B=uB[int(aBone+0.5)]*(1.0-bw)+uB[int(aBone2+0.5)]*bw;vec4 w=B*vec4(aPos,1.0);vec4 q=uV*w;mat3 RB=uR*mat3(B);',
    '  gl_Position=vec4(uP.x+q.x,uP.y+q.y,0.5-q.z*uP.z,1.0);vN=RB*aNrm.xyz;vAo=aNrm.w;vCv=aCv*2.0-1.0;vB=aBone;vC=aCol;vW=w.xyz;vUV=aUV;vR0=RB[0];vR1=RB[1];vR2=RB[2];vP=vec4(aPos-uEm.xyz,abs(aBone-uEm.w)<0.5?1.0:0.0);}'].join('\n');
  const FS = [
    'precision highp float;varying vec3 vN,vC;varying vec3 vW;varying vec2 vUV;varying vec3 vR0,vR1,vR2;varying vec4 vP;varying float vAo,vCv,vB;',
    'uniform vec3 uSun,uSunC,uAmb,uFill;uniform float uA,uTexOn,uNrmOn,uLift;uniform sampler2D uTex,uNrm;',
    'uniform vec3 uSky,uGnd;uniform float uAoOn,uSm,uGrain,uCv,uDbg;',      // 空と 地面の 色（背景の 絵から）・AO・面の グラデーション・紙の ざらざら
    'uniform vec3 uE0,uE1,uGc;uniform vec2 uGr;',       // 光る 目：目の 場所（両目の まん中から）・色・（半径, 強さ）
    'float h(vec3 p){return fract(sin(dot(p,vec3(12.9898,78.233,37.719)))*43758.5453);}',
    'float vn3(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);',       // なめらかな ざらざら（紙の 繊維・むら）
    '  return mix(mix(mix(h(i),h(i+vec3(1.0,0.0,0.0)),f.x),mix(h(i+vec3(0.0,1.0,0.0)),h(i+vec3(1.0,1.0,0.0)),f.x),f.y),',
    '    mix(mix(h(i+vec3(0.0,0.0,1.0)),h(i+vec3(1.0,0.0,1.0)),f.x),mix(h(i+vec3(0.0,1.0,1.0)),h(i+vec3(1.0,1.0,1.0)),f.x),f.y),f.z);}',
    'void main(){vec3 n=normalize(vN);',
    '  if(uNrmOn>0.5){vec3 nm=normalize(mat3(vR0,vR1,vR2)*(texture2D(uNrm,vUV).xyz*2.0-1.0));',     // 焼きこんだ 法線（紙の ふち・折り目）
    '    float sl=length(vN);vec3 ns=vN/max(sl,0.0001);n=normalize(mix(nm,ns,uSm*step(0.5,sl)*smoothstep(0.0,0.35,dot(nm,ns))));}',      // なめらかな 法線を 少し まぜる：紙の 面の 中に やわらかい グラデーション（背景の 絵の ような 光り方）
    '  else if(!gl_FrontFacing)n=-n;',
    '  float ds=dot(n,uSun);float d=mix(max(ds,0.0),max((ds+0.3)/1.3,0.0),0.55);',       // 少し まわりこむ やわらかい 光
    '  float ao=uAoOn>0.5?mix(1.0,clamp(vAo,0.0,1.0),0.55):1.0;float gc=mix(0.8,1.0,smoothstep(0.0,0.42,vW.y));',      // AO（足の 付け根・首の 下・たてがみの 下）・地面の 近くは 少し 暗く
    '  vec3 hemi=mix(uGnd,uSky,0.5+0.5*n.y);',      // 上は 空の 色・下は 地面の 照りかえし（背景の 絵の 色）
    '  float rim=uTexOn>0.5?pow(1.0-abs(n.z),3.0)*0.16:pow(1.0-abs(n.z),2.0)*0.12;',
    '  vec3 hv=normalize(uSun+vec3(0.0,0.0,1.0));float sp=uTexOn>0.5?pow(max(dot(n,hv),0.0),24.0)*0.14:0.0;',      // 紙の つや（少しだけ）
    '  vec3 base=uTexOn>0.5?texture2D(uTex,vUV).rgb:vC;',     // テクスチャ（紙の 模様・折り目）
    '  float g=uTexOn>0.5?1.0+uGrain*((vn3(vP.xyz*38.0)-0.5)+0.7*(vn3(vP.xyz*8.0+7.0)-0.5)):0.97+0.06*h(floor(vW*90.0));',   // 紙の ざらざら・むら（体に くっついて 動く）
    '  vec3 fd=normalize(vec3(-uSun.x,0.25,0.65));float fl=uTexOn>0.5?max(dot(n,fd),0.0)*0.22:0.0;',      // 反対がわから 弱い 光（かげの 面が 黒く つぶれない）
    '  float kk=uTexOn>0.5?1.12:1.0;',
    '  vec3 tn=uTexOn>0.5?mix(vec3(1.0),base/max(max(base.r,base.g),max(base.b,0.04)),0.65):vec3(1.0);',      // ふちの 光・つやは 紙の 色で（白い 光を 足すと 赤い マントが 白っぽく なる：11/08 16:26）
    '  float cr=max(vCv,0.0),cc=max(-vCv,0.0);float fold=1.0+uCv*(0.55*cr*(0.45+0.55*d)-0.25*cc);',      // 折り目：山は 光を うけて 明るく・谷は 暗く（背景の 紙の 絵と 同じ）
    '  vec3 hv2=normalize(uSun+vec3(0.0,0.0,1.0));float sh=uTexOn>0.5?pow(max(dot(n,hv2),0.0),6.0)*0.07*uSm:0.0;',      // 紙の やわらかい つや（広く うすく）
    '  vec3 c=base*(hemi*ao*gc+uSunC*d*kk*mix(1.0,ao,0.3)*gc+fl*uFill*ao+uLift)*g*fold+(rim*0.5+sp+sh)*uSunC*tn*ao;',      // uLift：かげも 明るく（神様馬：白い 紙が 灰色に 見えない）
    '  if(uTexOn>0.5){float mx=max(c.r,max(c.g,c.b));if(mx>0.8)c*=(0.8+0.2*(1.0-exp((0.8-mx)*5.0)))/mx;}',      // 明るい 所は 色の わりあいを 保って おさえる（白く とばない：クリーム色・金色が 残る）
    '  if(uGr.y>0.0){float e=min(length(vP.xyz-uE0),length(vP.xyz-uE1))/uGr.x;',       // 光る 目（まん中は 白っぽく・まわりへ じんわり）
    '    float gg=(1.0-smoothstep(0.55,1.35,e))*vP.w*uGr.y;float co=1.0-smoothstep(0.0,0.6,e);',
    '    c=mix(c,mix(uGc,vec3(1.0,0.98,0.94),co*0.6),clamp(gg,0.0,1.0));}',
    '  if(uDbg>0.5)c=vec3(fract(vB*0.37+0.1),fract(vB*0.61+0.3),fract(vB*0.83+0.5));',      // 骨ごとの 色（しらべる 用）
    '  gl_FragColor=vec4(c*uA,uA);}'].join('\n');
  const SVS = 'attribute vec2 p;uniform vec4 uE;varying vec2 v;void main(){v=p;gl_Position=vec4(uE.x+p.x*uE.z,uE.y+p.y*uE.w,0.0,1.0);}';
  const SFS = 'precision mediump float;varying vec2 v;uniform float uO;void main(){float r=length(v);float a=uO*(1.0-smoothstep(0.35,1.0,r));gl_FragColor=vec4(0.0,0.0,0.0,a);}';
  const GFS = 'precision mediump float;varying vec2 v;uniform vec3 uGc;uniform float uGk;void main(){float r=length(v);float a=exp(-r*r*5.0)*(1.0-smoothstep(0.75,1.0,r));float co=exp(-r*r*45.0);' +
    'vec3 c=uGc*a*1.15+vec3(1.0,0.97,0.92)*co*0.7;gl_FragColor=vec4(c*uGk,a*uGk*0.4);}';
  // 光る 目の 色（幻の馬：むらさき・神様馬：金色）
  // うんちの 絵（地面に 立てた 絵）
  const PFS = 'precision mediump float;varying vec2 v;uniform sampler2D uT;uniform vec3 uTint;void main(){vec4 c=texture2D(uT,vec2(v.x*0.5+0.5,0.5-v.y*0.5));gl_FragColor=vec4(c.rgb*uTint*c.a,c.a);}';
  const EYE_GLOW = { purple: [0.78, 0.36, 1.0], gold: [1.0, 0.78, 0.25] };

  function prog(gl, vs, fs) {
    const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
    const p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    return p;
  }

  // ---------- 歩き方（足 1本の 角度：つけ根・ひざ・足首）----------
  //   ph：その 足の 時間（0〜1）・g：歩き方（st＝地面に ついて いる 割合・A＝ふる 角度・K＝ひざ・F＝足首）・amp：歩はばの 大きさ
  //   どの 角度も「位置」だけで なく「速さ」も つなぎ目で そろえる（11/08 13:30 まさちゃん「カクカクじゃなく滑らかに」）
  const bump = (x, p) => Math.pow(Math.max(0, Math.sin(Math.PI * clamp(x, 0, 1))), p);     // 0→1→0（はじめと おわりは 速さ 0）
  function legAngles(ph, g, front, amp) {
    ph = ((ph % 1) + 1) % 1; amp = amp == null ? 1 : amp;
    const A = g.A * amp, lift = 0.4 + 0.6 * Math.min(1, amp);
    let u, k, f;
    if (ph < g.st) {                                  // 地面に ついて いる 間：一定の 速さで 後ろへ（ひづめが すべらない）
      const x = ph / g.st;
      u = A - 2 * A * x;
      k = 0; f = 0;                                   // ひざ・足首は まげない（まげると 地面の ひづめが 動いて すべって 見える）
    } else {                                          // ふり出し：はじめと おわりの 速さを 地面の 間と そろえる（エルミート 曲線）
      const x = (ph - g.st) / (1 - g.st), m = -2 * A / g.st * (1 - g.st), x2 = x * x, x3 = x2 * x;
      u = -A + 2 * A * (3 * x2 - 2 * x3) + m * (2 * x3 - 3 * x2 + x);
      k = -g.K * lift * bump(x + 0.4 * x * (1 - x), 2);      // ひざは ふり出しの 前半で いちばん まがる（ゆがめ方も なめらかな 式）
      f = -g.F * lift * bump(x + 0.6 * x * (1 - x), 2);      // 足首は もう少し 早く
    }
    if (!front) k *= 0.85;
    return [u, k, f];
  }
  const GAITS = {
    walk: { T: 1.3, st: 0.62, A: 0.22, K: 0.55, F: 0.45, ph: { HL: 0, FL: 0.25, HR: 0.5, FR: 0.75 }, bob: 0.012, pitch: 0.01, nod: 0.045 },      // 足の ふりは 小さめ（11/08 15:50）
    run: { T: 0.5, st: 0.38, A: 0.5, K: 1.3, F: 1.0, ph: { HL: 0, HR: 0.1, FL: 0.52, FR: 0.62 }, bob: 0.028, pitch: 0.045, nod: 0.12 },      // 体の 上下は 小さめ（大きいと 地面の ひづめが 動いて すべって 見える）
  };
  const DEEP_N = 0.22, DEEP_H = 0.1;                 // バケツで 食べる：エサが ぜんぶ 減った ときに 足す 首・頭（顔を バケツの 中へ：11/09 14:02）
  const RUN_V = 7.5;                                  // 走る 速さ（体の 高さ 1 ＝ 1／秒）：ギャロップの 大きな 歩はば（11/08 18:34）                                  // 走る 速さ（体の 高さ 1 ＝ 1／秒）
  // ---------- 歩き（本物の 馬の 歩き方：11/08 16:43 まさちゃんの 見本の 動画を 1コマずつ 見て 合わせた）----------
  //   1歩 1.2秒・地面に つく じゅん：後ろ左 → 前左（0.26 後）→ 後ろ右（0.5）→ 前右（0.76）・地面に ついて いる 割合 前 0.70・後ろ 0.73
  //   ひづめの 通り道と 向きを 決めて、足の 角度は 逆算（IK）：地面に ついて いる 間は ひづめが 動かない（すべらない）
  //   足は 体の 中の 高い 所（肩・こし）を 中心に ふる：足の 上も 前後に 動く（前の ひざは のびた まま）
  //   けり出し：つま先を 中心に かかとが 上がる → ふり出しの 前半で ひざ（後ろ足は 飛節）と 足首を まげて ひづめを 返す → 着く 前に のばして かかとから つく
  //   頭は 前足が つく 時に いちばん 低く（1歩で 2回 うなずく）・おしりは 後ろ足が つく 時に 少し 上がる・こしは 左右に 少し かたむく
  const WALK = {
    T: 1.2, stride: 1.4,
    touch: { HL: 0, FL: 0.258, HR: 0.5, FR: 0.758 },
    F: { beta: 0.70, piv: [-0.03, 1.45], c: -0.07, lift: 0.1, peak: 0.36, bo: 0.55, boLen: 0.12, land: 0.15, landLen: 0.10, flex: 1.35, fpeak: 0.3, bend: 1 },
    H: { beta: 0.73, piv: [-0.08, 1.36], c: -0.07, lift: 0.07, peak: 0.42, bo: 0.5, boLen: 0.12, land: 0.10, landLen: 0.08, flex: 0.8, fpeak: 0.32, bend: -1 },
    nod: 0.05, pitch: 0.0, roll: 0.025, tail: 0.12, drop: 0.02, slide: 0.11, neck: 0.16,
  };
  // ---------- 走り（ギャロップ：11/08 18:34 まさちゃんの ハイスピードカメラの 動画を 1コマずつ 見て 合わせた）----------
  //   地面に つく じゅん：後ろ右 → 後ろ左（0.07 後）→ 前右（0.32）→ 前左（0.47）→ 4本とも 体の 下に たたんで 宙に 浮く（0.75〜1）
  //   （反時計まわり：内がわの 左足が 先に 前へ）・地面に ついて いる 割合 前 0.29・後ろ 0.27
  //   前足：けり出した あと ひざを 深く まげて ひづめを ひじの 下まで たたむ → 大きく 前へ のばして 着く
  //   後ろ足：後ろへ のびきって けり出し → 飛節を まげて おなかの 下へ 大きく ふり出す
  //   体：前足で けり出す 時に 前が 上がり（宙に 浮く）、後ろ足で つく 時に 前が 下がる・首は 前足が ついて いる 間に 下がる
  const RUN = {
    T: 0.55,
    touch: { HR: 0, HL: 0.07, FR: 0.32, FL: 0.47 },
    F: { beta: 0.29, c: 0.12, lift: 0.42, peak: 0.34, bo: 0.8, boLen: 0.1, land: 0.2, landLen: 0.1, flex: 2.6, fpeak: 0.3, bend: 1, back: 0.12, reach: 0.38 },
    H: { beta: 0.27, c: -0.06, lift: 0.24, peak: 0.55, bo: 0.7, boLen: 0.1, land: 0.12, landLen: 0.08, flex: 1.5, fpeak: 0.42, bend: -1, back: 0.38, reach: 0.12 },
    pitch: 0.07, nod: 0.16, bob: 0.03, drop: 0.05, slide: 0.16, tail: 0.25,
  };
  // 馬ごとの 歩き：大きな 馬（幻の馬・神様馬）は どっしり（ゆっくり 大きく・体が ゆれる・頭を 深く うなずく：11/08 18:34）
  function walkOf(h) {
    if (h.walk) return h.walk;
    const hv = h.opt.heavy != null ? h.opt.heavy : ((h.opt.stage || 1) > 1.3 ? 1 : 0), W = JSON.parse(JSON.stringify(WALK));
    W.T *= 1 + 0.32 * hv; W.stride *= 1 + 0.06 * hv; W.nod *= 1 + 0.7 * hv; W.roll *= 1 + 1.4 * hv; W.neck += 0.08 * hv; W.drop += 0.012 * hv; W.tail *= 1 + 0.5 * hv;
    W.F.lift *= 1 - 0.3 * hv; W.H.lift *= 1 - 0.25 * hv; W.F.flex *= 1 - 0.2 * hv;
    W.heavy = hv; h.walk = W; return W;
  }
  // 歩く 速さ：足が 地面を すべらない 速さ（e：歩く 強さ 0〜1・w：歩きの まざり ぐあい）
  function walkSpeed(h, e, w) {
    const W = walkOf(h), a = (0.5 + 0.5 * e) * (w == null ? 1 : w), c = 0.7 + 0.3 * e;
    return W.stride * a * c / W.T;
  }
  const rot2 = (a, v) => [Math.cos(a) * v[0] - Math.sin(a) * v[1], Math.sin(a) * v[0] + Math.cos(a) * v[1]];
  // 0→1→0 の なめらかな 山（はじめと おわりは 速さ 0・いちばん 高いのは pk の 所）
  const peakBump = (x, pk) => { x = clamp(x, 0, 1); const p = 2.2, q = p * (1 - pk) / pk; return Math.pow(x, p) * Math.pow(1 - x, q) / (Math.pow(pk, p) * Math.pow(1 - pk, q)); };
  // 2本の 棒の 逆算：根もと P から 長さ L1・L2 で 先を Q に（bend＋1：ひざが 前・−1：後ろ）→ 棒の 向き a1・a2、足りない 長さ short
  function ik2(P, Q, L1, L2, bend) {
    const dx = Q[0] - P[0], dy = Q[1] - P[1], d = Math.hypot(dx, dy), base = Math.atan2(dy, dx);
    const dm = clamp(d, Math.abs(L1 - L2) + 1e-6, (L1 + L2) * 0.999999);
    const A = Math.acos(clamp((L1 * L1 + dm * dm - L2 * L2) / (2 * L1 * dm), -1, 1));
    const a1 = base + bend * A, kx = P[0] + L1 * Math.cos(a1), ky = P[1] + L1 * Math.sin(a1);
    return { a1, a2: Math.atan2(Q[1] - ky, Q[0] - kx), short: d - (L1 + L2) };
  }
  // 地面に ついて いる 間の ひづめ：φ（0＝つく・β＝はなれる）→ [足首の 点（体の 座標）, ひづめの 回転]
  function stanceFoot(lg, g, phi, A, S, xc0, gnd) {
    const xc = xc0 + S * (0.5 - phi / g.beta);        // ひづめの 底の まん中：体に 対して 一定の 速さで 後ろへ（＝地面に 止まって いる）
    const bs = g.beta - g.boLen; let th = 0, pv = lg.cen;
    if (phi < g.landLen) { th = g.land * A * Math.pow(1 - phi / g.landLen, 2); pv = lg.heel; }        // かかとから つく（つま先が 少し 上）
    else if (phi > bs) { th = -g.bo * A * Math.pow((phi - bs) / g.boLen, 2); pv = lg.toe; }          // つま先を 中心に かかとが 上がる（けり出し）
    const gx = xc + pv[0] - lg.cen[0], r = rot2(th, pv);
    return [[gx - r[0], gnd(gx) - r[1]], th];
  }
  // 足の 長さの 足りない／あまる 分は、足の つけ根（肩・こし）を 上下に ずらす（体の 中で 肩の 骨が 回る ぶん：WALK.slide まで・なめらかに）
  //   地面に ついて いる 前足の ひざは いつも のびた まま（まがると 不自然）
  const slideOf = (lg, Fp, m) => { const x = Math.hypot(Fp[0] - lg.P[0], Fp[1] - lg.P[1]) - (lg.L1 + lg.L2); return m * Math.tanh(x / m); };
  // 足 1本：φ（その 足の 時間 0〜1）・A（歩はば）→ 骨の 回転（つけ根・ひざ・足首）と つけ根の ずれ
  function walkLeg(lg, g, phi, A, S, gnd, msl) {
    const xc0 = lerp(lg.restC, lg.P[0] + lg.cen[0] + g.c, Math.min(1, A));       // ふみ出しの まん中（止まって いる 時の 足から なめらかに）
    let Fp, th, sl; const stance = phi < g.beta;
    if (stance) { [Fp, th] = stanceFoot(lg, g, phi, A, S, xc0, gnd); sl = slideOf(lg, Fp, msl); }
    else {
      const s = (phi - g.beta) / (1 - g.beta), e = 1e-3, sw = 1 - g.beta;
      const [F0, t0] = stanceFoot(lg, g, g.beta - 1e-6, A, S, xc0, gnd), [F0b] = stanceFoot(lg, g, g.beta - e, A, S, xc0, gnd);
      const [F1, t1] = stanceFoot(lg, g, 0, A, S, xc0, gnd), [F1b] = stanceFoot(lg, g, e, A, S, xc0, gnd);
      const m0 = [(F0[0] - F0b[0]) / e * sw, (F0[1] - F0b[1]) / e * sw], m1 = [(F1b[0] - F1[0]) / e * sw, Math.min(0, (F1b[1] - F1[1]) / e * sw)];      // 着く 時は 上から（下から 近づくと 地面に もぐる）
      const s2 = s * s, s3 = s2 * s, h00 = 2 * s3 - 3 * s2 + 1, h10 = s3 - 2 * s2 + s, h01 = -2 * s3 + 3 * s2, h11 = s3 - s2;
      const up = smooth(s / g.peak) * (1 - smooth((s - 0.72) / 0.28));          // 足首は 早めに 上がって、着く 前（ふり出しの 最後の 3割）に 下りる（地面を すらない）
      // 走り：けり出した あと 足を 後ろへ のばしきる（back）・着く 前に 前へ 大きく のばす（reach）
      const ex = (g.back ? -g.back * A * peakBump(s, 0.3) : 0) + (g.reach ? g.reach * A * peakBump(s, 0.7) : 0);
      Fp = [h00 * F0[0] + h10 * m0[0] + h01 * F1[0] + h11 * m1[0] + ex, h00 * F0[1] + h10 * m0[1] + h01 * F1[1] + h11 * m1[1] + g.lift * A * up];
      const sl0 = slideOf(lg, F0, msl), sl1 = slideOf(lg, F1, msl); sl = lerp(sl0, sl1, smooth(s));
      // 足首の まがり（すねに 対して）：はなれる 時と つく 時の 形を なめらかに つなぎ、ふり出しの 前半で 大きく まげる（ひづめを 返す）
      const P0 = [lg.P[0], lg.P[1] - sl0], P1 = [lg.P[0], lg.P[1] - sl1], Pc = [lg.P[0], lg.P[1] - sl];
      const k0 = ik2(P0, F0, lg.L1, lg.L2, g.bend), k1 = ik2(P1, F1, lg.L1, lg.L2, g.bend), kc = ik2(Pc, Fp, lg.L1, lg.L2, g.bend);
      const r0 = t0 - angDiff(lg.a2r, k0.a2), r1 = t1 - angDiff(lg.a2r, k1.a2);
      th = lerp(t0, t1, smooth(s / 0.78)) - g.flex * A * peakBump(s, g.fpeak);       // ひづめの 向き：ふり出しの 前半で 返し（うらが 後ろを 向く）、着く 前に 平らに（ひざが まがって いても つま先が 地面に ささらない）
    }
    const Ps = [lg.P[0], lg.P[1] - sl], k = ik2(Ps, Fp, lg.L1, lg.L2, g.bend);
    const au = angDiff(lg.a1r, k.a1), ak = angDiff(lg.a2r, k.a2) - au, af = th - au - ak;
    const dP = [lg.P[0] - lg.U[0], lg.P[1] - lg.U[1]], rP = rot2(au, dP);
    return { au, ak, af, tr: [dP[0] - rP[0], dP[1] - rP[1] - sl], short: stance ? k.short : -1 };
  }
  // 歩きの 足：根もとの 高い 中心（左右 そろえる）・棒の 長さ・ひづめの 底（つま先・かかと・まん中）
  function walkLegs(bones, bi, pos, bone, nv) {
    const legs = {}, pivX = {};
    for (const s of ['F', 'H']) if (bi[s + 'L_u'] != null && bi[s + 'R_u'] != null) pivX[s] = (bones[bi[s + 'L_u']].head[0] + bones[bi[s + 'R_u']].head[0]) / 2;
    for (const L of ['FL', 'FR', 'HL', 'HR']) {
      const bu = bi[L + '_u'], bk = bi[L + '_k'], bf = bi[L + '_f']; if (bu == null || bk == null || bf == null || pivX[L[0]] == null) continue;
      const g = WALK[L[0]], U = bones[bu].head, K = bones[bk].head, F = bones[bf].head;
      let my = 1e9; for (let i = 0; i < nv; i++) if (bone[i] === bf && pos[i * 3 + 1] < my) my = pos[i * 3 + 1];
      let tx = -1e9, hx = 1e9; for (let i = 0; i < nv; i++) if (bone[i] === bf && pos[i * 3 + 1] < my + 0.025) { tx = Math.max(tx, pos[i * 3]); hx = Math.min(hx, pos[i * 3]); }
      const P = [pivX[L[0]] + g.piv[0], g.piv[1]];
      legs[L] = { g, U, K, F, P, toe: [tx - F[0], my - F[1]], heel: [hx - F[0], my - F[1]], cen: [(tx + hx) / 2 - F[0], my - F[1]],
        L1: Math.hypot(K[0] - P[0], K[1] - P[1]), L2: Math.hypot(F[0] - K[0], F[1] - K[1]),
        a1r: Math.atan2(K[1] - P[1], K[0] - P[0]), a2r: Math.atan2(F[1] - K[1], F[0] - K[0]), restC: (tx + hx) / 2 };
    }
    return legs;
  }
  // 4本の 足と 体：G（WALK・RUN）・p（その 歩き方の 時間 0〜1）・A（歩はば）・sweep(g)（地面に ついて いる 間に 体に 対して 後ろへ 動く 長さ）
  //   off（体の ずれ：ここで 下げる 分を 足す）・wgt（まざり ぐあい）
  function gaitBody(h, G, p, A, sweep, off, wgt) {
    const bh = h.bones[0].head, out = {};
    // 地面の 高さ（体の 座標）：体の 下がり・前後の かたむき を 入れて
    let drop = G.drop * Math.min(1, A);
    for (let it = 0; it < 3; it++) {
      const oy = off[1] - drop, cp = Math.cos(off[3] || 0), sp = Math.sin(off[3] || 0);
      const gnd = x => bh[1] - (bh[1] + oy + (x - bh[0]) * sp) / cp;
      let need = 0;
      for (const L of ['FL', 'FR', 'HL', 'HR']) {
        const lg = h.legs[L]; if (!lg) continue;
        const g = G[L[0]], phi = ((p - G.touch[L]) % 1 + 1) % 1;
        out[L] = walkLeg(lg, g, phi, A, sweep(g), gnd, G.slide);
        const rp = smooth(phi / 0.12) * smooth((g.beta - phi) / 0.08);       // つく 直後・はなれる 直前は 少し 浮いても よい（体が がくっと 動かない）
        need = Math.max(need, out[L].short * rp);
      }
      if (need <= 1e-4) break;
      drop += need * 1.02;                            // 足が とどかない：体を 少し 下げる
    }
    off[1] -= drop * wgt;
    return out;
  }

  // ---------- 寝る・起きる（本物の 馬の 順番：11/08 13:46 まさちゃん「寝そべり方がリアルじゃない」）----------
  //   横に なる：頭を 下げて 足を よせる → 前の ひざを まげて ひざを つく → 後ろを 下ろす → むねと おなかで 寝る（足は 体の 下に たたむ）
  //   起きる：前足を 前に のばす → 前を 起こして 犬すわり → 後ろ足で 立つ
  //   足の 向きは「まっすぐ 下から 何 rad（＋は 頭がわ）」で 書いて、馬ごとの 骨の 長さで 体の 下がり（d）と 角度を 計算する
  //   d 下がる・p 前後の かたむき（＋で 頭が 上）・r 横の かたむき・x 前後の ずれ
  const FOLD_F = [1.33, -1.52, -2.0], FOLD_H = [-1.36, 1.55, 1.75];      // 前足：うでは 前へ・すねは 後ろへ／後ろ足：かかとを 地面に・すねは おなかの 下へ
  const XE = 0.22;            // 起きたら 体 1つぶんの 少し 前に 立つ（足は すべらせない・最後に 場所へ うつす）
  //   足：['abs', [つけ根, すね, 足首の 向き]]＝向きを じかに／['rest', X]＝立つ ときの つま先＋X に つま先を 地面に つけて おく／['toe', 'keep', 足首の 向き]＝前の キーの つま先の まま 足首を 返す
  const LIE_DEF = {   // tail：しっぽの 向き（まっすぐ 下＝0・後ろが −）。地面に とどく ぶんは fixGround が 後ろへ 寝かせる（長い しっぽも 短い しっぽも 自然に）
    gather: { p: -0.04, x: 0, d: 0.04, legs: { FL: ['rest', 0], FR: ['rest', 0], HL: ['rest', 0], HR: ['rest', 0] }, neck: -0.45, head: -0.25, tail: 0 },
    bend: { p: -0.07, x: 0.01, d: 0.06, legs: { FL: ['rest', 0], FR: ['rest', 0], HL: ['rest', 0], HR: ['rest', 0] }, neck: -0.42, head: -0.25, tail: -0.05 },
    fold1: { p: -0.1, x: 0.03, legs: { FL: ['abs', [0.12, -0.75, -1.45]], FR: ['rest', 0], HL: ['rest', 0], HR: ['rest', 0] }, neck: -0.4, head: -0.24, tail: -0.03 },      // 左の 前足から 曲げる
    knee1: { p: -0.1, x: 0.0, contact: 'lowF', legs: { FL: ['abs', [0.02, -1.15, -1.65]], FR: ['abs', [0.08, -0.9, -1.55]], HL: ['rest', 0], HR: ['rest', 0] }, neck: -0.38, head: -0.22, tail: 0 },
    kneel: { p: -0.13, x: -0.04, contact: 'kneeF', legs: { FL: ['abs', [0.02, -1.5, -1.8]], FR: ['abs', [0.06, -1.5, -1.8]], HL: ['rest', 0], HR: ['rest', 0] }, neck: -0.35, head: -0.2, tail: 0 },      // 前足が 体に もぐらない ように：前へ かたむけすぎない・うでは まっすぐ 下（11/09 15:18 まさちゃん「寝そべる時に一度前足が身体の中に入ってる」）
    settle: { p: -0.07, x: -0.06, contact: 'kneeF', legs: { FL: ['abs', [0.7, -1.52, -1.95]], FR: ['abs', [0.66, -1.5, -1.95]], HL: ['abs', [-0.75, 0.95, 1.1]], HR: ['abs', [-0.72, 0.92, 1.05]] }, neck: -0.3, head: -0.18, tail: -0.15 },      // ひざを 前へ すべらせ ながら うしろを 下ろす
    down: { p: -0.02, x: 0.0, contact: 'low', legs: { FL: ['abs', FOLD_F], FR: ['abs', [1.3, -1.5, -2.0]], HL: ['abs', FOLD_H], HR: ['abs', [-1.33, 1.52, 1.7]] }, neck: -0.3, head: -0.15, tail: -0.3 },
    rest: { p: 0.04, x: 0, r: 0.05, contact: 'low', legs: { FL: ['abs', FOLD_F], FR: ['abs', [1.3, -1.5, -2.0]], HL: ['abs', FOLD_H], HR: ['abs', [-1.33, 1.52, 1.7]] }, neck: 0.04, head: -0.1, tail: -0.35, tailY: 0.35 },      // おなかを つけて すわる（横に 寝ころばない・頭は 上げる：11/09 14:58 まさちゃんの 動画「この動画座り方と同じにして！寝ころばなくていいから！」）
    liftK: { p: 0.18, x: 0.02, r: 0.07, contact: 'lowH', legs: { FL: ['abs', [1.6, -0.8, -1.2]], FR: ['abs', [1.5, -0.95, -1.35]], HL: ['abs', FOLD_H], HR: ['abs', [-1.33, 1.52, 1.7]] }, neck: 0.25, head: 0.06, tail: -0.3, tailY: 0.15 },      // 前足は 前へ 水平くらい まで（上へ 上げすぎると 前足の つけ根が おれて 見える：11/09 14:36 まさちゃん）
    liftF: { p: 0.3, x: 0.03, r: 0.05, contact: 'lowH', legs: { FL: ['abs', [1.55, 0.2, 0.45]], FR: ['abs', [1.45, 0.05, 0.35]], HL: ['abs', FOLD_H], HR: ['abs', [-1.33, 1.52, 1.7]] }, neck: 0.28, head: 0.08, tail: -0.3, tailY: 0.1 },
    frontOut: { p: 0.42, x: 0.0, contact: 'lowH', legs: { FL: ['rest', XE], FR: ['rest', XE], HL: ['abs', [-1.2, 1.55, 1.75]], HR: ['abs', [-1.15, 1.5, 1.7]] }, neck: 0.2, head: 0.02, tail: -0.35, tailY: 0.1 },
    dogSit: { p: 0.55, x: 0.14, contact: 'lowH', legs: { FL: ['rest', XE], FR: ['rest', XE], HL: ['abs', [-0.85, 1.5, 1.7]], HR: ['abs', [-0.8, 1.45, 1.65]] }, neck: 0.1, head: -0.05, tail: -0.4 },
    hindPush: { p: 0.16, x: 0.23, d: 0.22, legs: { FL: ['rest', XE], FR: ['rest', XE], HL: ['rest', XE], HR: ['rest', XE] }, neck: 0.05, head: -0.05, tail: -0.12 },
    standUp: { p: 0, x: XE, d: 0, legs: { FL: ['rest', XE], FR: ['rest', XE], HL: ['rest', XE], HR: ['rest', XE] }, neck: 0, head: 0, tail: 0 },
  };
  // 横に なる：前と 後ろを いっしょに なめらかに しゃがむ（前に かたむけすぎない：11/08 18:34 まさちゃん「もっと滑らかにしゃがんで」）
  const LIE_SEQ = [[0, 'stand'], [0.18, 'gather'], [0.33, 'bend'], [0.43, 'fold1'], [0.54, 'knee1'], [0.64, 'kneel'], [0.75, 'settle'], [0.87, 'down'], [1, 'rest']];      // 動画の ように：頭を 下げて → 前ひざを 折って ひざを つく → うしろを 下ろして すわる
  const LIE_DUR = 4.6, RISE_DUR = 1.7, POOP_DUR = 3.4;      // 横に なる 時間（ゆっくり）・起きる 時間（勢いよく）
  const RISE_SEQ = [[0, 'rest'], [0.12, 'liftK'], [0.24, 'liftF'], [0.4, 'frontOut'], [0.58, 'dogSit'], [0.8, 'hindPush'], [1, 'standUp']];      // 起きる：前を 起こして 前足を 前へ → 犬すわり → 後ろ足を 体の 下に 入れて 立つ
  const KCH = ['d', 'p', 'x', 'r', 'neck', 'head', 'tail', 'tailY', 'nf'];      // nf：前足の すねを まげて 地面から 上げない（ひざ・すねが 地面に ついて いる 間：めりこみは 体を 上げて 直す）
  function buildLieKeys(bones, probe) {      // probe：骨ごとの 外がわの 点（足の 太さ：ひざを つく 高さに 使う）
    const B = {}; bones.forEach(b => { B[b.name] = b.head; });
    const bx = B.body[0], by = B.body[1];
    const dirv = a => [Math.sin(a), -Math.cos(a)], ang = v => Math.atan2(v[0], -v[1]), len = v => Math.hypot(v[0], v[1]);
    const tf = (p, d, x, q) => { const c = Math.cos(p), sn = Math.sin(p), u = q[0] - bx, v = q[1] - by; return [bx + c * u - sn * v + x, by + sn * u + c * v - d]; };
    const SEG = {}, AF0 = 0.25;
    for (const L of ['FL', 'FR', 'HL', 'HR']) {
      const u = B[L + '_u'], k = B[L + '_k'], f = B[L + '_f'], s3 = [0.05, -f[1]];
      SEG[L] = { u, fy: f[1], segs: [[k[0] - u[0], k[1] - u[1]], [f[0] - k[0], f[1] - k[1]], s3], toe: [f[0] + len(s3) * Math.sin(AF0), f[1] - len(s3) * Math.cos(AF0)] };
    }
    const chain = (L, p, d, x, A) => { const S = SEG[L]; let P = tf(p, d, x, S.u); const pts = [P]; for (let i = 0; i < 3; i++) { const l = len(S.segs[i]), dv = dirv(A[i]); P = [P[0] + l * dv[0], P[1] + l * dv[1]]; pts.push(P); } return pts; };
    // つま先 T・足首の 向き af に 合わせて 足を のばす（前足は ひざが 前・後ろ足は かかとが 後ろ）
    const ikToe = (L, p, d, x, T, af) => {
      const S = SEG[L], P = tf(p, d, x, S.u), L1 = len(S.segs[0]), L2 = len(S.segs[1]), L3 = len(S.segs[2]), dv3 = dirv(af);
      const F = [T[0] - L3 * dv3[0], T[1] - L3 * dv3[1]], D = [F[0] - P[0], F[1] - P[1]], bend = L[0] === 'H' ? -1 : 1;
      const dist = clamp(len(D), Math.abs(L1 - L2) + 1e-3, L1 + L2 - 1e-3);
      const a1 = Math.acos(clamp((L1 * L1 + dist * dist - L2 * L2) / (2 * L1 * dist), -1, 1)), Au = ang(D) + bend * a1, dv = dirv(Au);
      return [Au, ang([F[0] - P[0] - L1 * dv[0], F[1] - P[1] - L1 * dv[1]]), af];
    };
    const REST = {}; for (const L in SEG) REST[L] = SEG[L].segs.map(ang);
    const rel = (L, A, p) => { const r = REST[L], c = [A[0] - r[0], A[1] - r[1], A[2] - r[2]]; return [c[0] - p, c[1] - c[0], c[2] - c[1]]; };
    // 足の 形（太さ）の いちばん 低い 所：骨の まん中では なく すねの 表面で 地面に 合わせる（11/09 15:38 まさちゃん「まだ足が一瞬身体の中に入ってる」：
    //   ひざの 骨の まん中を 地面の 上 0.06 に したら すねの 太さで 地面に めりこみ、fixGround が すねを 胸・おなかの 中へ はね上げて いた）
    const rot2 = (q, a, o) => { const cc = Math.cos(a), ss = Math.sin(a), u = q[0] - o[0], v = q[1] - o[1]; return [o[0] + cc * u - ss * v, o[1] + ss * u + cc * v]; };
    const geoLow = (L, A, p, d, lvMin) => {
      const r = rel(L, A, p), hu = B[L + '_u'], hk = B[L + '_k'], hf = B[L + '_f']; let m = 1e9;
      for (const [lv, q0] of probe[L]) {
        if (lv < lvMin) continue;
        let q = q0; if (lv >= 2) q = rot2(q, r[2], hf); if (lv >= 1) q = rot2(q, r[1], hk); q = rot2(q, r[0], hu);
        m = Math.min(m, tf(p, d, 0, q)[1]);
      }
      return m;
    };
    const GEO = !!(probe && probe.FL && probe.FL.length && probe.FR && probe.FR.length), TG = 0.004;
    const stand = { d: 0, p: 0, x: 0, r: 0, neck: 0, head: 0, tail: 0, tailY: 0, FL: [0, 0, 0], FR: [0, 0, 0], HL: [0, 0, 0], HR: [0, 0, 0], pl: {}, tx: {}, ty: {}, af: {} };
    for (const L of ['FL', 'FR', 'HL', 'HR']) { stand.pl[L] = 1; stand.tx[L] = SEG[L].toe[0]; stand.ty[L] = SEG[L].toe[1]; stand.af[L] = AF0; }
    const out = { stand };
    const T0 = 0.06, belly = B.FL_u[1];
    let prev = stand;
    for (const name in LIE_DEF) {
      const k = LIE_DEF[name], p = k.p, x = k.x || 0;
      const toeOf = L => { const [m, v, af] = k.legs[L];
        if (m === 'rest') return [SEG[L].toe[0] + v, SEG[L].toe[1], AF0];
        if (m === 'toe') return [prev.tx[L] != null ? prev.tx[L] : SEG[L].toe[0], prev.ty[L] != null ? prev.ty[L] : SEG[L].toe[1], af];
        return null; };
      const legsAt = d => { const o = {}; for (const L in k.legs) { const tt = toeOf(L); o[L] = tt ? ikToe(L, p, d, x, tt, tt[2]) : k.legs[L][1].slice(); } return o; };
      const low = d => {
        const lg = legsAt(d); let m = 1e9;
        for (const L in lg) {
          const pts = chain(L, p, d, x, lg[L]);
          if (k.contact === 'kneeF') { if (L[0] === 'F') m = Math.min(m, GEO ? geoLow(L, lg[L], p, d, 1) - TG : pts[1][1] - T0); }      // ひざを つく：すね・ひづめの 表面を 地面に
          else if (k.contact === 'lowH') { if (L[0] === 'H') pts.slice(1).forEach(q => { m = Math.min(m, q[1] - T0); }); }
          else if (k.contact === 'lowF') { if (L[0] === 'F') { if (GEO) m = Math.min(m, geoLow(L, lg[L], p, d, 0) - TG); else pts.slice(1).forEach(q => { m = Math.min(m, q[1] - T0); }); } }
          else pts.slice(1).forEach(q => { m = Math.min(m, q[1] - T0); });
        }
        if (k.contact === 'low') for (let i = 0; i < 6; i++) m = Math.min(m, tf(p, d, x, [-0.8 + 0.22 * i, belly])[1] - 0.02);     // おなか
        return m;
      };
      let lo = -0.2, hi = 1.4;
      for (let it = 0; it < 50 && k.d == null; it++) { const mid = (lo + hi) / 2; if (low(mid) > 0) lo = mid; else hi = mid; }
      // 足を 地面に つけて おく 形は 体の 高さを じかに 書く（d）
      const d = k.d != null ? k.d : (lo + hi) / 2, lg = legsAt(d), key = { d, p, x, r: k.r || 0, neck: k.neck, head: k.head, tail: k.tail - p, tailY: k.tailY || 0, nf: k.contact === 'kneeF' || k.contact === 'low' ? 1 : 0, pl: {}, tx: {}, ty: {}, af: {} };
      for (const L in lg) {
        key[L] = rel(L, lg[L], p);
        const tt = toeOf(L);
        key.pl[L] = tt ? 1 : 0; key.tx[L] = tt ? tt[0] : null; key.ty[L] = tt ? tt[1] : null; key.af[L] = tt ? tt[2] : null;
      }
      out[name] = key; prev = key;
    }
    out.geo = { bx, by, SEG, REST, chain: (p, d, x, L, A) => chain(L, p, d, x, A), ikToe, rel };
    return out;
  }
  // 地面に つけて おく 足：体の 形に 合わせて つま先を その場に のこして 足を のばす（はねたり もぐったり すべったり しない）
  function plantLegs(h, k) {
    const G = h.lie.geo;
    for (const L of ['FL', 'FR', 'HL', 'HR']) {
      const w = k.pl ? k.pl[L] : 0; if (!(w > 0.001) || k.tx[L] == null) continue;
      const r = G.rel(L, G.ikToe(L, k.p, k.d, k.x, [k.tx[L], k.ty[L]], k.af[L]), k.p);
      k[L] = k[L].map((v, j) => v + (r[j] - v) * w);
    }
    return k;
  }
  function fixGround(h, k) {
    const G = h.lie.geo, c = Math.cos(k.p), sn = Math.sin(k.p);
    const rot = (q, a, o) => { const cc = Math.cos(a), ss = Math.sin(a), u = q[0] - o[0], v = q[1] - o[1]; return [o[0] + cc * u - ss * v, o[1] + ss * u + cc * v]; };
    const legPts = (L, a, lvMin) => {       // その 足の lvMin より 下の 骨の 外がわの 点（体の 中の 座標）
      const hu = h.bones[h.bi[L + '_u']].head, hk = h.bones[h.bi[L + '_k']].head, hf = h.bones[h.bi[L + '_f']].head, o = [];
      for (const [lv, q0] of (h.probe && h.probe[L]) || []) {
        if (lv < lvMin) continue;
        let q = q0;
        if (lv >= 2) q = rot(q, a[2], hf);
        if (lv >= 1) q = rot(q, a[1], hk);
        o.push(rot(q, a[0], hu));
      }
      return o;
    };
    const lowOf = (L, a, lvMin) => {        // その 足の lvMin より 下の 骨の いちばん 低い 所（地面からの 高さ）
      let m = 1e9;
      for (const q of legPts(L, a, lvMin)) { const u = q[0] - G.bx, v = q[1] - G.by, y = G.by + sn * u + c * v - k.d; if (y < m) m = y; }
      return m;
    };
    const U = h.under;
    const into = (L, a) => {                // すね・ひづめが 胴の 下の 面に 入った ぶん（体の 中の 座標・入って いなければ 0 以下）
      if (!U) return -1; let m = -1;
      for (const q of legPts(L, a, 1)) { const j = Math.floor((q[0] - U.x0) / U.dx); if (j >= 0 && j < U.y.length) m = Math.max(m, q[1] - (U.y[j] - 0.015)); }
      return m;
    };
    let lowY = 1e9;
    for (const L of ['FL', 'FR', 'HL', 'HR']) {
      const a = k[L].slice(), flex = L[0] === 'F' ? -1 : 1, in0 = Math.max(0, into(L, a)) + 0.002;
      // 地面に めりこむ ぶんだけ ひざ（前）・かかと（後ろ）を まげて すねを 上げる。少しずつ（なめらかに）・胴の 中には 上げない（のこりは 体を 上げる）
      //   前の ひざを ついて いる 間（nf）は まげない：すねは 地面に ねかせた まま 体を 上げる（すねが はね上がって 胸に 入って いた：11/09 15:38）
      const nMax = Math.round(150 * (L[0] === 'F' ? 1 - clamp(k.nf || 0, 0, 1) : 1));
      for (let i = 0; i < nMax && lowOf(L, a, 1) < -0.006; i++) { a[1] += 0.01 * flex; if (into(L, a) > in0) { a[1] -= 0.01 * flex; break; } }
      for (let i = 0; i < 200 && lowOf(L, a, 2) < -0.006; i++) { a[2] -= 0.01; if (into(L, a) > in0) { a[2] += 0.01; break; } }      // ひづめを 後ろへ 返す
      k[L] = a; lowY = Math.min(lowY, lowOf(L, a, 0));
    }
    if (lowY < -0.006) k.d -= -0.006 - lowY;          // それでも 下 → 体を 上げる
    if (h.tailTip) {            // しっぽ（はしの 点 いくつか）が 地面より 下なら 後ろへ 寝かせる
      const tb = h.bones[h.bi.tail].head, u = tb[0] - G.bx, v = tb[1] - G.by;
      const py = G.by + sn * u + c * v - k.d, pts = h.tailProbe || [h.tailTip];
      for (let i = 0; i < 30; i++) {
        const th = k.p + k.tail, ss = Math.sin(th), cc = Math.cos(th);
        let ty = 1e9; for (const q of pts) ty = Math.min(ty, py + ss * q[0] + cc * q[1]);
        if (ty >= 0.03) break; k.tail -= 0.06;
      }
    }
    return k;
  }
  // キーを なめらかに つなぐ（キーの 所で 止まらない：となりの キーで 速さを 決める・はじめと おわりは 速さ 0）
  function keyAt(keys, seq, u) {
    u = clamp(u, 0, 1);
    let i = 0; while (i < seq.length - 2 && u > seq[i + 1][0]) i++;
    const t0 = seq[i][0], t1 = seq[i + 1][0], s = (u - t0) / (t1 - t0), s2 = s * s, s3 = s2 * s;
    const h00 = 2 * s3 - 3 * s2 + 1, h10 = s3 - 2 * s2 + s, h01 = -2 * s3 + 3 * s2, h11 = s3 - s2;
    const K = j => keys[seq[clamp(j, 0, seq.length - 1)][1]], T = j => seq[clamp(j, 0, seq.length - 1)][0];
    const tan = (j, get) => (j <= 0 || j >= seq.length - 1) ? 0 : (get(K(j + 1)) - get(K(j - 1))) / (T(j + 1) - T(j - 1));
    const one = get => h00 * get(K(i)) + h10 * (t1 - t0) * tan(i, get) + h01 * get(K(i + 1)) + h11 * (t1 - t0) * tan(i + 1, get);
    const o = {};
    KCH.forEach(c => { o[c] = one(q => q[c] || 0); });
    ['FL', 'FR', 'HL', 'HR'].forEach(L => { o[L] = [0, 1, 2].map(j => one(q => q[L][j])); });
    o.pl = {}; o.tx = {}; o.ty = {}; o.af = {};
    ['FL', 'FR', 'HL', 'HR'].forEach(L => {
      o.pl[L] = clamp(one(q => q.pl[L]), 0, 1);
      for (const c of ['tx', 'ty', 'af']) {                       // つま先・足首：かたほうに しか なければ そちら
        const a = K(i)[c][L], b = K(i + 1)[c][L];
        o[c][L] = a == null ? b : b == null ? a : a + (b - a) * smooth(s);
      }
    });
    return o;
  }

  // 立ち方を 合わせる（11/09 10:01 まさちゃん「神様馬の肩幅と足の位置を幻の馬に合わせて！」）：
  //   体を 横に 広げて 肩幅を そろえ（sp.bodyW）、足は 上から 下へ なめらかに 外へ ひらいて ひづめの 場所を そろえる（sp.hoofZ）。
  //   首は つけ根だけ 広げて 頭・しっぽは そのまま（顔の 形は かえない）。骨の 回る 中心も いっしょに うごかす
  function morphStance(meta, pos, bone, nv, sp) {
    const bones = meta.bones, bi = {}; bones.forEach((b, i) => { bi[b.name] = i; });
    let x0 = 1e9, x1 = -1e9; for (let i = 0; i < nv; i++) if (bone[i] === bi.body) { x0 = Math.min(x0, pos[i * 3]); x1 = Math.max(x1, pos[i * 3]); }
    const xs = x0 + (x1 - x0) * 0.75; let z0 = 1e9, z1 = -1e9;
    for (let i = 0; i < nv; i++) if (bone[i] === bi.body && Math.abs(pos[i * 3] - xs) < 0.05) { z0 = Math.min(z0, pos[i * 3 + 2]); z1 = Math.max(z1, pos[i * 3 + 2]); }
    const kB = sp.bodyW && z1 > z0 ? sp.bodyW / (z1 - z0) : 1;
    const legOf = {}, hoofZ = {}, topY = {}, topZ = {};
    for (const L of ['FL', 'FR', 'HL', 'HR']) {
      for (const k of ['_u', '_k', '_f']) if (bi[L + k] != null) legOf[bi[L + k]] = L;
      const b = bi[L + '_f']; if (b == null || bi[L + '_u'] == null) continue; let my = 1e9;
      for (let i = 0; i < nv; i++) if (bone[i] === b && pos[i * 3 + 1] < my) my = pos[i * 3 + 1];
      let sz = 0, c = 0; for (let i = 0; i < nv; i++) if (bone[i] === b && pos[i * 3 + 1] < my + 0.04) { sz += pos[i * 3 + 2]; c++; }
      hoofZ[L] = c ? sz / c : 0; const hu = bones[bi[L + '_u']].head; topY[L] = hu[1]; topZ[L] = hu[2];
    }
    const side = L => (L === 'FL' || L === 'HL' ? -1 : 1) * (Math.sign(topZ[L] || 0) || 1) * (L === 'FL' || L === 'HL' ? -1 : 1);      // 足の 外がわの 向き（z の 符号）
    const out = sp.topOut || 0;          // 足の つけ根を 外へ（10:10 まさちゃん「神様馬足もう少し外側にして！」）
    const dzLeg = (L, y) => {
      if (topY[L] == null) return 0;
      const u = clamp((topY[L] - y) / Math.max(0.1, topY[L]), 0, 1), e = u * u * (3 - 2 * u);
      const want = sp.hoofZ && sp.hoofZ[L] != null ? sp.hoofZ[L] : hoofZ[L] * kB;
      return (1 - e) * (topZ[L] * (kB - 1) + side(L) * out) + e * (want - hoofZ[L]);
    };
    const topX = {}; for (const L in topY) topX[L] = bones[bi[L + '_u']].head[0];
    const bodyOut = (x, y, z) => {       // 足の つけ根の まわりの 体も いっしょに 外へ（肩・こしの 幅）
      let d = 0; for (const L in topY) { if (Math.sign(z) !== side(L)) continue; const r = Math.hypot(x - topX[L], (y - topY[L]) * 1.2); d += side(L) * out * smooth(clamp(1 - r / 0.5, 0, 1)); }
      return d;
    };
    const nB = bi.neck, hB = bi.head, nh = nB != null ? bones[nB].head : null, hh = hB != null ? bones[hB].head : null;
    const nL = nh && hh ? Math.hypot(hh[0] - nh[0], hh[1] - nh[1]) || 1 : 1;
    for (let i = 0; i < nv; i++) {
      const b = bone[i], x = pos[i * 3], y = pos[i * 3 + 1], z = pos[i * 3 + 2];
      let dz = 0;
      if (legOf[b]) dz = dzLeg(legOf[b], y);
      else if (b === bi.body) dz = z * (kB - 1) + bodyOut(x, y, z);
      else if (b === nB && nh) { const u = clamp(Math.hypot(x - nh[0], y - nh[1]) / nL, 0, 1); dz = z * (kB - 1) * (1 - smooth(u / 0.55)); }      // 首は つけ根だけ
      pos[i * 3 + 2] = z + dz;
    }
    bones.forEach((bo, k) => { const L = legOf[k]; if (L) bo.head = [bo.head[0], bo.head[1], bo.head[2] + dzLeg(L, bo.head[1])]; });
  }

  function mkTex(gl, img) {                // テクスチャ（ミップマップ・ななめでも くっきり）
    const tx = gl.createTexture(); gl.activeTexture(gl.TEXTURE6); gl.bindTexture(gl.TEXTURE_2D, tx);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, img);
    gl.generateMipmap(gl.TEXTURE_2D);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    const an = gl.getExtension('EXT_texture_filter_anisotropic') || gl.getExtension('WEBKIT_EXT_texture_filter_anisotropic');
    if (an) gl.texParameterf(gl.TEXTURE_2D, an.TEXTURE_MAX_ANISOTROPY_EXT, Math.min(8, gl.getParameter(an.MAX_TEXTURE_MAX_ANISOTROPY_EXT)));      // 第4.150版：4 → 8（ななめの 面の 毛の もようが くっきり：まさちゃん「トレーニングセンターも馬の画質は高く！」）
    gl.activeTexture(gl.TEXTURE0);
    return tx;
  }
  // ---------- 物（バケツ・エサ：まさちゃんの 3D・11/09 14:13「これエサとバケツの3Dモデル！これでやって！」）----------
  //   馬と 同じ 形式（json＋bin：fmt2）・骨は 1つ。馬の 体の 座標（x 前・y 上・z 横・地面 y＝0）に 置いて、馬と 同じ 光・同じ 見え方・同じ 深さで 描く
  //   → 顔を バケツに 入れると、手前の ふちに かくれて、奥の かべの 前に 見える（st.props：[{ P, m（置き方の 行列）, sh：[x, z, 半径, こさ] }]）
  function createProp(gl, meta, bin, opt) {
    opt = opt || {};
    const lay = meta.layout, nv = meta.v;
    const mk = (data, target) => { const b = gl.createBuffer(); gl.bindBuffer(target || gl.ARRAY_BUFFER, b); gl.bufferData(target || gl.ARRAY_BUFFER, data, gl.STATIC_DRAW); return b; };
    const pos = new Float32Array(bin, lay.pos[0], nv * 3);
    const idx = meta.idx32 ? new Uint32Array(bin, lay.idx[0], meta.i) : new Uint16Array(bin, lay.idx[0], meta.i);
    if (meta.idx32) gl.getExtension('OES_element_index_uint');
    const cvb = lay.cv ? new Uint8Array(bin, lay.cv[0], nv) : null;
    const B = { pos: mk(pos), nrm: mk(new Int8Array(bin, lay.nrm[0], nv * 4)), uv: mk(new Uint16Array(bin, lay.uv[0], nv * 2)), bone: mk(new Float32Array(nv)), bw: mk(new Uint8Array(nv)), cv: cvb ? mk(cvb) : null, idx: mk(idx, gl.ELEMENT_ARRAY_BUFFER) };
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9, z0 = 1e9, z1 = -1e9;
    for (let i = 0; i < nv; i++) { const x = pos[i * 3], y = pos[i * 3 + 1], z = pos[i * 3 + 2]; if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; if (z < z0) z0 = z; if (z > z1) z1 = z; }
    return { gl, B, meta, tex: opt.texImg ? mkTex(gl, opt.texImg) : null, ntex: opt.nrmImg ? mkTex(gl, opt.nrmImg) : null, box: [x0, y0, z0, x1, y1, z1] };
  }
  function drawProps(h, st, view) {
    const gl = h.gl, Q = view.quality || {};
    const at = (b, loc, n, type, norm, stride) => { if (loc < 0) return; gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, n, type || gl.FLOAT, !!norm, stride || 0, 0); };
    gl.useProgram(h.P); gl.enable(gl.DEPTH_TEST); gl.depthFunc(gl.LEQUAL);
    for (const pr of st.props) {
      const P = pr.P; if (!P || !pr.m) continue;
      at(P.B.pos, h.loc.aPos, 3); at(P.B.bone, h.loc.aBone, 1); at(P.B.bone, h.loc.aBone2, 1); at(P.B.bw, h.loc.aBw, 1, gl.UNSIGNED_BYTE, true);
      at(P.B.nrm, h.loc.aNrm, 4, gl.BYTE, true, 4); at(P.B.uv, h.loc.aUV, 2, gl.UNSIGNED_SHORT, true);
      if (h.loc.aCol >= 0) { gl.disableVertexAttribArray(h.loc.aCol); gl.vertexAttrib3f(h.loc.aCol, 1, 1, 1); }
      if (h.loc.aCv >= 0) { if (P.B.cv) at(P.B.cv, h.loc.aCv, 1, gl.UNSIGNED_BYTE, true); else { gl.disableVertexAttribArray(h.loc.aCv); gl.vertexAttrib1f(h.loc.aCv, 0.5); } }
      gl.uniform1f(h.loc.uBlend, 0); gl.uniformMatrix4fv(h.loc.uB, false, new Float32Array(pr.m));      // 骨 0番 だけ（物の 置き方）
      gl.activeTexture(gl.TEXTURE6); gl.bindTexture(gl.TEXTURE_2D, P.tex); gl.uniform1i(h.loc.uTex, 6); gl.uniform1f(h.loc.uTexOn, P.tex ? 1 : 0);
      gl.activeTexture(gl.TEXTURE7); gl.bindTexture(gl.TEXTURE_2D, P.ntex); gl.uniform1i(h.loc.uNrm, 7); gl.uniform1f(h.loc.uNrmOn, P.ntex && Q.nm !== 0 ? 1 : 0); gl.activeTexture(gl.TEXTURE0);
      gl.uniform1f(h.loc.uAoOn, P.meta.ao && Q.ao !== 0 ? 1 : 0); gl.uniform1f(h.loc.uCv, P.B.cv ? (Q.cv != null ? Q.cv : 1) : 0); gl.uniform1f(h.loc.uLift, pr.lift || 0);
      gl.uniform4f(h.loc.uEm, 0, 0, 0, -9); gl.uniform2f(h.loc.uGr, 1, 0);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, P.B.idx);
      gl.drawElements(gl.TRIANGLES, P.meta.i, P.meta.idx32 ? gl.UNSIGNED_INT : gl.UNSIGNED_SHORT, 0);
    }
    [h.loc.aPos, h.loc.aNrm, h.loc.aCol, h.loc.aBone, h.loc.aBone2, h.loc.aBw, h.loc.aUV, h.loc.aCv].forEach(l => { if (l >= 0) gl.disableVertexAttribArray(l); });
  }
  function create(gl, meta, bin, opt) {
    opt = opt || {};
    const P = prog(gl, VS, FS), S = prog(gl, SVS, SFS), G = prog(gl, SVS, GFS), PS = prog(gl, SVS, PFS);
    const lay = meta.layout, nv = meta.v;
    const buf = (key, Type, n) => new Type(bin, lay[key][0], n);
    const fmt2 = meta.fmt === 2;        // 2＝テクスチャ つき（法線 int8・UV uint16・三角 番号）
    const pos = buf('pos', Float32Array, nv * 3), bone = new Uint8Array(bin, lay.bone[0], nv);
    if (opt.stance) morphStance(meta, pos, bone, nv, opt.stance);      // 神様馬：肩幅と 足の 場所を 幻の馬に 合わせる
    const nrm = fmt2 ? new Int8Array(bin, lay.nrm[0], nv * 4) : buf('nrm', Float32Array, nv * 3);
    const col = fmt2 ? null : new Uint8Array(bin, lay.col[0], nv * 3), uv = fmt2 ? new Uint16Array(bin, lay.uv[0], nv * 2) : null;
    const idx = meta.idx32 ? new Uint32Array(bin, lay.idx[0], meta.i) : new Uint16Array(bin, lay.idx[0], meta.i);
    if (meta.idx32) gl.getExtension('OES_element_index_uint');
    const mk = (data, target) => { const b = gl.createBuffer(); gl.bindBuffer(target || gl.ARRAY_BUFFER, b); gl.bufferData(target || gl.ARRAY_BUFFER, data, gl.STATIC_DRAW); return b; };
    const bone2 = lay.bone2 ? new Uint8Array(bin, lay.bone2[0], nv) : bone, bwt = lay.bw ? new Uint8Array(bin, lay.bw[0], nv) : new Uint8Array(nv);
    const cvb = lay.cv ? new Uint8Array(bin, lay.cv[0], nv) : null;      // 折り目（bake_ao.py）
    const B = { cv: cvb ? mk(cvb) : null, pos: mk(pos), nrm: mk(nrm), col: col ? mk(col) : null, uv: uv ? mk(uv) : null, bone: mk(new Float32Array(bone)), bone2: mk(new Float32Array(bone2)), bw: mk(bwt), idx: mk(idx, gl.ELEMENT_ARRAY_BUFFER), quad: mk(new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1])) };
    const tex = fmt2 && opt.texImg ? mkTex(gl, opt.texImg) : null, ntex = fmt2 && opt.nrmImg ? mkTex(gl, opt.nrmImg) : null;
    const L = n => gl.getAttribLocation(P, n), U = n => gl.getUniformLocation(P, n);
    const loc = { aPos: L('aPos'), aNrm: L('aNrm'), aCol: L('aCol'), aBone: L('aBone'), aBone2: L('aBone2'), aBw: L('aBw'), uBlend: U('uBlend'), aUV: L('aUV'), uB: U('uB'), uV: U('uV'), uR: U('uR'), uP: U('uP'), uSun: U('uSun'), uSunC: U('uSunC'), uAmb: U('uAmb'), uA: U('uA'), uTexOn: U('uTexOn'), uTex: U('uTex'), uNrmOn: U('uNrmOn'), uNrm: U('uNrm'),
      sp: gl.getAttribLocation(S, 'p'), uE: gl.getUniformLocation(S, 'uE'), uO: gl.getUniformLocation(S, 'uO'),
      uFill: U('uFill'), uLift: U('uLift'), uSky: U('uSky'), uGnd: U('uGnd'), uAoOn: U('uAoOn'), uSm: U('uSm'), uGrain: U('uGrain'), uCv: U('uCv'), aCv: L('aCv'), uDbg: U('uDbg'), uEm: U('uEm'), uE0: U('uE0'), uE1: U('uE1'), uGc: U('uGc'), uGr: U('uGr'),
      gp: gl.getAttribLocation(G, 'p'), gE: gl.getUniformLocation(G, 'uE'), gGc: gl.getUniformLocation(G, 'uGc'), gGk: gl.getUniformLocation(G, 'uGk'),
      pp: gl.getAttribLocation(PS, 'p'), pE: gl.getUniformLocation(PS, 'uE'), pT: gl.getUniformLocation(PS, 'uT'), pTint: gl.getUniformLocation(PS, 'uTint') };
    const bones = meta.bones, bi = {}; bones.forEach((b, i) => { bi[b.name] = i; });
    const H = meta.height || 2.15;
    const legLen = bi.FL_u != null ? bones[bi.FL_u].head[1] : 1.0;
    const probe = {};
    for (const L of ['FL', 'FR', 'HL', 'HR']) {
      probe[L] = [];
      ['_u', '_k', '_f'].forEach((sfx, lv) => {
        const b = bi[L + sfx]; if (b == null) return;
        for (let dI = 0; dI < 8; dI++) {
          const dx = Math.cos(dI * Math.PI / 4), dy = Math.sin(dI * Math.PI / 4); let best = -1e9, q = null;
          for (let i = 0; i < nv; i++) if (bone[i] === b) { const v = pos[i * 3] * dx + pos[i * 3 + 1] * dy; if (v > best) { best = v; q = [pos[i * 3], pos[i * 3 + 1]]; } }
          if (q) probe[L].push([lv, q]);
        }
      });
    }
    // 胴の 下の 面（体の 中の 座標・前後 0.05 ごとの いちばん 低い 所）：寝る・起きる ときに すね・ひづめを 胴の 中へ 上げない（fixGround）
    let under = null;
    if (bi.body != null) {
      let x0 = 1e9, x1 = -1e9; for (let i = 0; i < nv; i++) if (bone[i] === bi.body) { x0 = Math.min(x0, pos[i * 3]); x1 = Math.max(x1, pos[i * 3]); }
      const dx = 0.05, n = Math.max(1, Math.ceil((x1 - x0) / dx)), y = new Array(n).fill(1e9);
      for (let i = 0; i < nv; i++) if (bone[i] === bi.body) { const j = Math.min(n - 1, Math.floor((pos[i * 3] - x0) / dx)); if (pos[i * 3 + 1] < y[j]) y[j] = pos[i * 3 + 1]; }
      under = { x0, dx, y };
    }
    let tailTip = null, tailProbe = null;
    if (bi.tail != null) {
      const isT = b => b === bi.tail || (bi.tail2 != null && b === bi.tail2);      // しっぽ（つけ根＋先）
      const th = bones[bi.tail].head; let my = 1e9; for (let i = 0; i < nv; i++) if (isT(bone[i]) && pos[i * 3 + 1] < my) { my = pos[i * 3 + 1]; tailTip = [pos[i * 3] - th[0], pos[i * 3 + 1] - th[1]]; }
      tailProbe = [];
      for (let dI = 0; dI < 12; dI++) {          // しっぽの いちばん 外の 点（12方向）
        const dx = Math.cos(dI * Math.PI / 6), dy = Math.sin(dI * Math.PI / 6); let best = -1e9, q = null;
        for (let i = 0; i < nv; i++) if (isT(bone[i])) { const v = pos[i * 3] * dx + pos[i * 3 + 1] * dy; if (v > best) { best = v; q = [pos[i * 3] - th[0], pos[i * 3 + 1] - th[1]]; } }
        if (q) tailProbe.push(q);
      }
    }
    const legs = walkLegs(bones, bi, pos, bone, nv);
    const hoof = {};
    for (const L of ['FL', 'FR', 'HL', 'HR']) {
      const b = bi[L + '_f']; if (b == null) continue; let my = 1e9;
      for (let i = 0; i < nv; i++) if (bone[i] === b && pos[i * 3 + 1] < my) my = pos[i * 3 + 1];
      let sx = 0, sy = 0, sz = 0, c = 0;
      for (let i = 0; i < nv; i++) if (bone[i] === b && pos[i * 3 + 1] < my + 0.04) { sx += pos[i * 3]; sy += pos[i * 3 + 1]; sz += pos[i * 3 + 2]; c++; }
      if (c) hoof[L] = [sx / c, sy / c, sz / c];
    }
    // 目（頭の 骨に ついて 動く）：光らせる 色は opt.eyeGlow（'purple'・'gold'・[r,g,b]）か、あとから h.glow に 入れる
    const eyes = meta.eyes && meta.eyes.length === 2 && bi.head != null ? meta.eyes : null;
    const em = eyes ? [0, 1, 2].map(k => (eyes[0].p[k] + eyes[1].p[k]) / 2) : [0, 0, 0];
    const glow = opt.eyeGlow ? (typeof opt.eyeGlow === 'string' ? EYE_GLOW[opt.eyeGlow] : opt.eyeGlow) : null;
    // 体の 目印（お世話：11/09 08:29 まさちゃん「お世話のアイディア全部組み込んで！」）：鼻・目・頭の 上・首・き甲・背中・おしり
    const anchors = {};
    const pick = (bs, score, frac) => {          // その 骨の 点の うち score が 大きい 上から frac の 点の まん中
      const cand = []; for (let i = 0; i < nv; i++) if (bs.includes(bone[i])) cand.push([score(pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]), i]);
      if (!cand.length) return null; cand.sort((a, b) => b[0] - a[0]); const n = Math.max(1, Math.floor(cand.length * frac)); let x = 0, y = 0, z = 0;
      for (let k = 0; k < n; k++) { const i = cand[k][1]; x += pos[i * 3]; y += pos[i * 3 + 1]; z += pos[i * 3 + 2]; } return [x / n, y / n, z / n];
    };
    const hb = [bi.head, bi.jaw].filter(v => v != null), nb = [bi.neck].filter(v => v != null), bb = [bi.body].filter(v => v != null);
    if (hb.length) { anchors.nose = { b: bi.head, p: pick(hb, (x) => x, 0.03) }; anchors.poll = { b: bi.head, p: pick(hb, (x, y) => y, 0.03) }; }
    if (eyes) anchors.eye = { b: bi.head, p: em.slice() };
    else if (anchors.nose && anchors.nose.p && anchors.poll && anchors.poll.p) anchors.eye = { b: bi.head, p: [0, 1, 2].map(k => anchors.poll.p[k] + (anchors.nose.p[k] - anchors.poll.p[k]) * 0.42) };      // 目の 印が ない 馬：頭の 上と 鼻の 間
    if (nb.length) anchors.neck = { b: bi.neck, p: pick(nb, (x, y) => y + 0.3 * x, 0.25) };
    if (bb.length) {
      let x0 = 1e9, x1 = -1e9; for (let i = 0; i < nv; i++) if (bone[i] === bi.body) { x0 = Math.min(x0, pos[i * 3]); x1 = Math.max(x1, pos[i * 3]); }
      const at = (fx) => pick(bb, (x, y, z) => y - 4 * Math.abs(x - (x0 + (x1 - x0) * fx)) - 0.5 * Math.abs(z), 0.03);
      anchors.withers = { b: bi.body, p: at(0.78) }; anchors.back = { b: bi.body, p: at(0.5) }; anchors.rump = { b: bi.body, p: at(0.18) };
    }
    const samp = []; for (let i = 0; i < nv; i += 7) samp.push(i);          // 画面の 中の 大きさを はかる 点（7つに 1つ：extent）
    const sampP = new Float32Array(samp.length * 3), sampB = new Uint8Array(samp.length);
    samp.forEach((i, k) => { sampP[k * 3] = pos[i * 3]; sampP[k * 3 + 1] = pos[i * 3 + 1]; sampP[k * 3 + 2] = pos[i * 3 + 2]; sampB[k] = bone[i]; });
    return { sampP, sampB, anchors, gl, P, S, G, B, loc, bones, bi, meta, H, legLen, opt, lie: buildLieKeys(bones, probe), tailTip, tailProbe, probe, under, tex, ntex, fmt2, eyes, em, eyeR: meta.eye_r || 0.02, glow, legs, hoof, PS,
      poopTex: (opt.poopImgs || []).map(im => { const t = gl.createTexture(); gl.activeTexture(gl.TEXTURE5); gl.bindTexture(gl.TEXTURE_2D, t); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, im);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE); gl.activeTexture(gl.TEXTURE0); return { t, w: im.width, h: im.height }; }) };      // 5番の 場所（フィールドの 絵 0〜2番を 上書きしない）
  }

  // 骨の 角度（rot：骨の 名前 → [z 回り（前後）, y 回り（左右）]）・体の ずれ → 16この 行列
  function boneMats(h, rot, bodyOff, trs) {
    const out = new Array(h.bones.length);
    h.bones.forEach((b, i) => {
      const r = rot[b.name] || [0, 0], q = trs && trs[b.name];
      let local = M.mul(M.tr(b.head[0], b.head[1], b.head[2]), M.mul(M.mul(M.ry(r[1] || 0), M.rz(r[0] || 0)), M.tr(-b.head[0], -b.head[1], -b.head[2])));
      if (q) local = M.mul(M.tr(q[0], q[1], q[2] || 0), local);
      if (b.parent < 0) {              // 体：下がる・前後の かたむき・横の かたむき・息で 少し ふくらむ
        const e = bodyOff[4] || 0, sc = M.sc(1 + e, 1 + e * 0.6, 1 + e);
        local = M.mul(M.tr(bodyOff[0], bodyOff[1], bodyOff[2]), M.mul(M.tr(b.head[0], b.head[1], b.head[2]), M.mul(M.rz(bodyOff[3] || 0), M.mul(M.rx(bodyOff[5] || 0), M.mul(sc, M.tr(-b.head[0], -b.head[1], -b.head[2]))))));
      }
      out[i] = b.parent < 0 ? local : M.mul(out[b.parent], local);
    });
    return out;
  }

  // 4本の 足を つま先の 場所で 決める（体の かたむき p・下がり d・前後 x と いっしょに）：f(L) → [前へ, 上へ, 足首（ひづめを 後ろへ 曲げる）]
  //   ずらさない 足は 地面の いつもの 場所に つけた まま（すべらない・もぐらない）
  function legIK(h, set, p, d, x, f) {
    const G = h.lie.geo;
    for (const L of ['FL', 'FR', 'HL', 'HR']) {
      const S = G.SEG[L]; if (!S) continue; const [dx, dy, da] = f(L);
      const R = G.rel(L, G.ikToe(L, p, d, x, [S.toe[0] + dx, S.toe[1] + dy], 0.25 + da), p);
      set(L + '_u', R[0]); set(L + '_k', R[1]); set(L + '_f', R[2]);
    }
  }
  // ---------- 体の 形（歩く・走る・止まる・草を 食べる・寝る）----------
  function pose(h, st, t) {
    const rot = {}, off = [0, 0, 0, 0, 0, 0];
    const set = (n, a, b) => { rot[n] = [(rot[n] ? rot[n][0] : 0) + a, (rot[n] ? rot[n][1] : 0) + (b || 0)]; };
    // 息・しっぽ（いつも 少し）
    const br = Math.sin(TAU * t / (st.mode === 'sleep' ? 4.2 : 3.1));
    off[4] = 0.006 * br * (st.mode === 'sleep' ? 2.2 : 1);
    set('tail', 0.04 * Math.sin(TAU * t / 2.7) + st.tailFlick, 0.18 * Math.sin(TAU * t / 3.9 + 1) + 0.25 * st.tailFlick);
    if (h.bi.tail2 != null && !(st.sl > 0.001)) set('tail2', 0.03 * Math.sin(TAU * t / 2.7 - 0.8), 0.14 * Math.sin(TAU * t / 3.9 + 0.3) + 0.2 * st.tailFlick);     // しっぽの 先は 少し おくれて ゆれる（寝て いる 間は 動かさない）
    // 歩く・走る（gw：歩きの 強さ 0〜1・gr：走りの 強さ）
    const mix = (n, a) => set(n, a[0], a[1]);
    const trs = {};
    const ww = smooth(st.gw), wr = smooth(st.gr);
    const addLegs = (legs, k) => {
      for (const L in legs) {
        const r = legs[L];
        set(L + '_u', r.au * k); set(L + '_k', r.ak * k); set(L + '_f', r.af * k);
        const q = trs[L + '_u'] || [0, 0, 0]; trs[L + '_u'] = [q[0] + r.tr[0] * k, q[1] + r.tr[1] * k, 0];
      }
    };
    if (ww > 0.001 && h.legs && h.legs.FL) {         // 歩き：ひづめの 通り道から 逆算（本物の 馬の 歩き方）
      const W = walkOf(h), A = (st.wAmp || 1) * ww, p = st.phase.walk, k = 1 - wr, Am = Math.min(1, A);
      off[4] *= 1 - ww;                                         // 歩く 間は 息の ふくらみを 止める（地面の ひづめが 動かない）
      off[3] += -W.pitch * Am * k * Math.cos(TAU * 2 * p);      // 後ろ足が つく 時に おしりが 上がる（前に かたむく）
      off[5] += W.roll * Am * k * Math.sin(TAU * (p - 0.11));      // こしが 左右に かたむく（地面に ついた 後ろ足の 方が 上がる）
      addLegs(gaitBody(h, W, p, A, g => W.stride * g.beta * A, off, k), k);
      set('neck', -W.nod * Am * k * Math.cos(TAU * 2 * (p - W.touch.FL)) - W.neck * ww * k); set('head', -W.nod * 0.35 * Am * k * Math.cos(TAU * 2 * (p - W.touch.FL) - 0.5) + W.neck * 0.45 * ww * k);      // 前足が つく 時に 頭が いちばん 低い・歩く 間は 首を 少し 下げて 前へ（動画の 馬と 同じ ゆったりした 首）
      set('tail', 0, W.tail * Am * k * Math.sin(TAU * (p - 0.36))); set('tail2', 0.03 * Am * k * Math.sin(TAU * 2 * p), 1.2 * W.tail * Am * k * Math.sin(TAU * (p - 0.5)));
    }
    if (wr > 0.001 && h.legs && h.legs.FL) {         // 走り：ギャロップ（ひづめの 通り道から 逆算・速さに 合わせて 歩はばが かわる）
      const p = st.phase.run, vr = Math.max(st.runV || 0, 0.01), cr = 0.8 + 0.2 * clamp(vr / RUN_V, 0, 1), Te = RUN.T / cr;
      const A = clamp(vr / RUN_V, 0.35, 1);
      off[4] *= 1 - wr;
      off[3] += RUN.pitch * A * wr * Math.sin(TAU * (p - 0.45));          // 前足で けり出す 時（0.7）に 前が 上がる・後ろ足で つく 時に 前が 下がる
      off[1] += -RUN.bob * A * wr * (0.5 + 0.5 * Math.cos(TAU * (p - 0.45)));   // 前足が ついて いる 間が いちばん 低い・宙に 浮く 時が 高い
      addLegs(gaitBody(h, RUN, p, A, g => vr * g.beta * Te, off, wr), wr);
      set('neck', -RUN.nod * A * wr * Math.cos(TAU * (p - 0.5)) - 0.3 * wr); set('head', RUN.nod * 0.4 * A * wr * Math.cos(TAU * (p - 0.5) - 0.4) + 0.14 * wr);     // 首は 前へ のばして 低く・前足が ついて いる 間に もっと 下がる
      // しっぽは 風で 後ろへ なびく：つけ根を 後ろへ 上げ、先は おくれて 波うつ（11/08 18:52 まさちゃん「尻尾も自然に靡かせて」）
      const fl = smooth(clamp((vr - 1.5) / 4.5, 0, 1)) * wr;
      set('tail', -1.05 * fl + 0.1 * fl * Math.sin(TAU * (p - 0.15)), 0.1 * fl * Math.sin(TAU * (p - 0.1)));
      set('tail2', -0.3 * fl + 0.28 * fl * Math.sin(TAU * (p - 0.4)) + 0.08 * fl * Math.sin(TAU * 2 * p + 1.3), 0.16 * fl * Math.sin(TAU * (p - 0.35)));
    }
    if (st.upT != null && t - st.upT < 0.9) {          // 起きた 直後：体が 少し 上に はずんで もどる・首を ふり上げる（勢いよく 立った あとの はずみ）
      const u = (t - st.upT) / 0.9, e = Math.sin(Math.PI * u) * Math.pow(1 - u, 1.5);
      off[1] += 0.035 * e; set('neck', 0.22 * e); set('head', -0.08 * e);
    }
    if (h.bi.jaw != null) set('jaw', h.meta.jaw_close || 0);      // 口は いつも 閉じる（幻の馬・神様馬も 口を 開けない：11/09 03:20 まさちゃん「幻の馬、神様馬、口開けるの無くして！」）
    if (st.poopE > 0.001) {                  // うんち：しっぽを 上げて 少し しゃがむ
      const k = smooth(st.poopE); set('tail', -0.85 * k, 0); if (h.bi.tail2 != null) set('tail2', -0.35 * k); off[1] -= 0.015 * k;
    }
    // お世話の 反応（11/09 08:29）：はじめ と おわりは ゆっくり。口は 開けない
    // 第4.151版（まさちゃん 11/11 09:07「撫でたあとのごろんをすると、馬が宙に少し浮き、地面と空中をいったりきたりする」）：
    //   横に なる 間（st.sl）は お世話の 反応を 弱めて 止める（前は はしゃぐ・のび などが 横に なった 体に 重なって、体が 浮いて はずんで いた）。
    //   r.cut（つづけて 撫でた とき：tc_care.js の cutReacts）＝その 時刻から 0.25秒で 弱めて 止める
    const lieF = st.sl > 0.001 ? 1 - smooth(clamp(st.sl / 0.12, 0, 1)) : 1;
    for (const r of (st.reacts || [])) {
      const u = (t - r.t0) / r.dur; if (u < 0 || u > 1) continue;
      const gn = lieF * (r.cut != null ? 1 - smooth(clamp((t - r.cut) / 0.25, 0, 1)) : 1); if (gn <= 0.001) continue;
      const e = smooth(clamp(u / 0.18, 0, 1)) * (1 - smooth(clamp((u - 0.78) / 0.22, 0, 1))) * gn, tt = t - r.t0;
      if (r.k === 'nuzzle') { set('neck', -0.16 * e); set('head', -0.12 * e + 0.07 * e * Math.sin(TAU * 1.5 * tt), 0.12 * e * (r.side || 1)); }            // 手に 頭を すりすり
      else if (r.k === 'swish') { set('tail', -0.25 * e, 0.75 * e * Math.sin(TAU * 1.3 * tt)); if (h.bi.tail2 != null) set('tail2', 0, 0.6 * e * Math.sin(TAU * 1.3 * tt - 0.9)); }      // しっぽを 大きく ふりふり
      else if (r.k === 'stretch' && h.lie) {          // ぐーっと のび（11/09 14:36 まさちゃん「前足を前に、トン・トンと出してから背中伸ばして！」）
        //   前足を 左・右と 1歩ずつ 前へ（トン・トン）→ うしろへ 体重を かけて 背中を のばす（首も 前へ）→ 右・左と もどす。ひづめは 地面に つけた まま（すべらない）
        const G = h.lie.geo, D = 0.3, st_ = (a, b) => smooth(clamp((u - a) / (b - a), 0, 1)), lf = (a, b) => { const q = clamp((u - a) / (b - a), 0, 1); return Math.sin(Math.PI * q); };
        const fw = { FL: st_(0.05, 0.19) - st_(0.8, 0.9), FR: st_(0.19, 0.33) - st_(0.88, 0.98), HL: 0, HR: 0 };
        const up = { FL: lf(0.05, 0.19) + lf(0.8, 0.9), FR: lf(0.19, 0.33) + lf(0.88, 0.98), HL: 0, HR: 0 };
        for (const L in fw) { fw[L] *= gn; up[L] *= gn; }
        const sk = st_(0.35, 0.52) * (1 - st_(0.68, 0.8)) * gn, p = -0.06 * sk, d = 0.06 * sk + 0.01 * (up.FL + up.FR), x = -0.07 * sk;
        off[0] += x; off[1] -= d; off[3] += p;
        legIK(h, set, p, d, x, L => [D * fw[L], 0.12 * up[L], -1.0 * up[L]]);
        set('neck', -0.34 * sk - 0.06 * (up.FL + up.FR)); set('head', 0.24 * sk + 0.04 * Math.sin(TAU * 0.8 * tt) * sk); set('tail', -0.12 * sk);
      }
      else if (r.k === 'sneeze') { const j = Math.exp(-Math.pow((u - 0.45) / 0.06, 2)) * gn; set('neck', -0.05 * e - 0.18 * j); set('head', -0.3 * j); off[1] -= 0.012 * j; }          // ぷしゅっ（くしゃみ）
      else if ((r.k === 'hop' || r.k === 'frisk') && h.lie) {      // ぴょん（当たり）・はしゃぐ（小さい ころ）：本物の 馬の ように その場で 足を バタバタ 上げ下げ（ななめの 2本ずつ 交互：11/09 14:36 まさちゃん）
        const per = r.k === 'hop' ? 0.56 : 0.48, ph = tt / per, k = e, hi = r.k === 'hop' ? 1 : 0.85;
        const sw = L => { const q = ((ph + (L === 'FL' || L === 'HR' ? 0 : 0.5)) % 1 + 1) % 1; return q < 0.56 ? Math.pow(Math.sin(Math.PI * q / 0.56), 1.3) : 0; };
        const bob = 0.03 * k * Math.abs(Math.sin(TAU * ph));                     // 足を かえる たびに 体が 少し はずむ
        off[1] += bob; off[3] += 0.03 * k;                                       // 前を 少し 上げる（うれしい）
        legIK(h, set, 0.03 * k, -bob, 0, L => { const w = sw(L) * k * hi, f = L[0] === 'F'; return [(f ? 0.07 : -0.03) * w, (f ? 0.3 : 0.13) * w, (f ? -1.35 : -0.7) * w]; });
        set('neck', (0.12 + 0.05 * Math.sin(TAU * 2 * ph)) * k); set('head', -0.08 * k * Math.abs(Math.sin(TAU * ph)));
        set('tail', -0.45 * k, 0.32 * k * Math.sin(TAU * ph));
      }
      else if (r.k === 'tilt') { set('head', 0.1 * e, 0.38 * e * (r.side || 1)); set('neck', 0.05 * e, 0.1 * e * (r.side || 1)); }                  // 首を かしげる
      else if (r.k === 'nod') { set('neck', -0.17 * e * (0.5 + 0.5 * Math.sin(TAU * 1.6 * tt - 1.57))); set('head', -0.08 * e * Math.sin(TAU * 1.6 * tt)); }   // 元気に うなずく
      else if (r.k === 'yawn') { const k = Math.sin(Math.PI * clamp(u * 1.15, 0, 1)) * gn; set('neck', 0.22 * k); set('head', 0.34 * k); off[4] += 0.01 * k; }          // あくび（首を のばす・口は 開けない）
      else if (r.k === 'sniff') { set('neck', -0.5 * e); set('head', -0.28 * e + 0.04 * e * Math.sin(TAU * 4.5 * tt), 0.15 * e * (r.side || 0)); }       // くんくん
      else if (r.k === 'eat') { set('neck', -0.08 * e); set('head', 0.06 * e + 0.035 * e * Math.sin(TAU * 2.4 * tt), 0.1 * e * (r.side || 0)); }          // 手から 食べる（もぐもぐは 頭で）
      else if (r.k === 'beg') { set('neck', 0.04 * e); set('head', 0.06 * e, 0.3 * e * (r.side || 1)); }                                          // おかわりの 目（こっちを 見つめる）
      else if (r.k === 'happy') { const j = Math.max(0, Math.sin(TAU * 1.1 * tt)) * e; set('neck', 0.1 * j); set('head', -0.06 * j); set('tail', -0.2 * e, 0.55 * e * Math.sin(TAU * 1.6 * tt)); }  // うれしい
      else if (r.k === 'shake') {          // 首を プルンッ（すばやく 左右に ふって 止まる）
        const j = Math.exp(-tt * 3.2) * smooth(clamp(tt / 0.08, 0, 1)) * gn, w = Math.sin(TAU * 4.6 * tt) * j;
        set('neck', 0.06 * e, 0.2 * w * (r.side || 1)); set('head', -0.05 * j * Math.abs(Math.sin(TAU * 4.6 * tt)), 0.34 * w * (r.side || 1)); off[5] += 0.012 * w;
      }
      else if (r.k === 'paw') {            // 前足で 地面を かく（上げて 前へ → 後ろへ ひっかく → 下ろす）
        const L = (r.side || 1) > 0 ? 'FR' : 'FL', ph = clamp((u - 0.12) / 0.76, 0, 1), lift = Math.sin(Math.PI * ph) * gn;
        set(L + '_u', (0.32 * Math.sin(TAU * ph * 1.5)) * lift + 0.18 * lift); set(L + '_k', 0.85 * lift); set(L + '_f', 0.5 * lift);
        set('neck', -0.08 * e); set('head', -0.05 * e);
      }
      else if (r.k === 'headup') { set('neck', 0.3 * e); set('head', -0.12 * e + 0.03 * e * Math.sin(TAU * 0.8 * tt), 0.08 * e * (r.side || 1)); }      // 頭を 上げて 遠くを 見る
      else if (r.k === 'sway') { const w = Math.sin(TAU * tt / r.dur); off[5] += 0.03 * w * e; off[2] += 0.012 * w * e; set('neck', 0.04 * e, 0.12 * w * e); set('head', 0, 0.1 * w * e); }      // 体を ゆらす（体重を かける 足を かえる）
      else if (r.k === 'gather') { set('neck', -0.18 * e); set('head', 0.1 * e); off[1] -= 0.025 * e; off[3] -= 0.02 * e; set('tail', -0.15 * e); }      // ためる（少し しゃがむ：ぴょん／ごろんの 前）
      else if (r.k === 'calm') { const w = Math.sin(TAU * 0.35 * tt); set('neck', -0.14 * e + 0.02 * w * e); set('head', 0.04 * e, 0.22 * e * (r.side || 1)); off[5] += 0.02 * e * (r.side || 1); set('tail', 0, 0.25 * e * w); }      // ゆったり よりかかる（夕方）
      else if (r.k === 'deep') {           // エサが 減るたびに 少しずつ 深く（r.ds：減った 時刻・11/09 14:02 まさちゃん「エサが減るごとに顔をバケツの中に入れることはできる？」）
        const d = r.ds && r.ds.length ? r.ds.reduce((a, s) => a + smooth(clamp((t - s) / 0.45, 0, 1)), 0) / r.ds.length : 0;
        const dn = r.dn != null ? r.dn : DEEP_N, dh = r.dh != null ? r.dh : DEEP_H;
        set('neck', (-0.1 - dn * d) * e); set('head', (-0.14 + dh * d) * e + 0.035 * e * Math.sin(TAU * 1.9 * tt));
      }      // バケツで 食べる：草を 食べる 形に 少し 足すだけ（顔は まっすぐ 下・鼻先が バケツへ：11/09 13:44 まさちゃん「顔がバケツから避けちゃってるからバケツに真っ直ぐにして！」）      // バケツに 顔を 入れて 食べる（首を 深く・顔は 下向きに のばして 鼻先から バケツへ：11:01 まさちゃん「バケツから顔超えてしまってる」）
      else if (r.k === 'lick') { const j = Math.sin(Math.PI * clamp((u - 0.2) / 0.6, 0, 1)); set('neck', -0.1 * e); set('head', 0.12 * j, 0.1 * j * (r.side || 1)); }      // ぺろっ（顔を 少し 上げて 口の まわりを なめる・口は 開けない）
      else if (r.k === 'nibble') { set('neck', -0.3 * e); set('head', -0.05 * e + 0.05 * e * Math.sin(TAU * 3.2 * tt), 0.2 * e * (r.side || 0)); }      // ほうきを かじろうと する
    }
    // 草を 食べる・まわりを 見る（首と 頭）：ゆっくり 動き はじめて ゆっくり 止まる
    const gz = smooth(st.graze), lk = st.lookS || st.look;
    set('neck', -0.62 * gz + 0.05 * lk[1], 0.35 * lk[0]); set('head', -0.38 * gz + 0.04 * lk[1], 0.25 * lk[0]);
    if (gz > 0.5) set('head', 0.04 * Math.sin(TAU * t * 1.7) * smooth((gz - 0.5) * 2) * 0.5);     // もぐもぐ
    // 寝る・起きる（キーを つないだ 形）＋ ねむる（頭を 下げる）
    if (!h.lie) h.lie = buildLieKeys(h.bones, h.probe);
    // 横に なる 時は はじめと おわりを ゆっくり（なめらかに しゃがむ）・起きる 時は 後半ほど 速く（勢いよく 立つ）
    const slE = lerp(st.sl, smooth(st.sl), 0.5), riE = Math.pow(st.rise, 1.3);
    const lieK = st.poseKey || (st.sl > 0.001 ? fixGround(h, plantLegs(h, st.rise > 0 ? keyAt(h.lie, RISE_SEQ, riE) : keyAt(h.lie, LIE_SEQ, slE))) : null);
    if (lieK) {
      off[0] += lieK.x; off[1] += -lieK.d; off[3] += lieK.p; off[5] = (off[5] || 0) + lieK.r;
      for (const L of ['FL', 'FR', 'HL', 'HR']) { set(L + '_u', lieK[L][0]); set(L + '_k', lieK[L][1]); set(L + '_f', lieK[L][2]); }
      set('neck', lieK.neck); set('head', lieK.head); set('tail', lieK.tail, lieK.tailY);
      const dz = smooth(st.doze || 0); set('neck', -0.26 * dz); set('head', -0.2 * dz);      // ねむると 頭が 少し 下がる（すわった まま）
      if (st.flop != null) {             // ごろん（なかよしハート 10この ハズレ：11/09 08:37）：横に なって 体を 少し かたむけ、首を のばして ゆったり
        const k = smooth(clamp((st.sl - 0.8) / 0.2, 0, 1)) * (1 - smooth(clamp(st.rise * 2.5, 0, 1))), tt = t - st.flop;
        off[5] += 0.02 * Math.sin(TAU * 0.55 * tt) * k; set('neck', -0.08 * k + 0.04 * k * Math.sin(TAU * 0.4 * tt)); set('head', -0.08 * k, 0.12 * k);      // 横には 寝ころばない（11/09 14:58）
        set('tail', 0, 0.3 * k * Math.sin(TAU * 0.7 * tt));
      }
    }
    return boneMats(h, rot, off, trs);
  }

  // ---------- 考える（ランダムに 歩く・止まる・30回に 1回 走る／寝る）----------
  //   場所は フィールドの 絵の px（1052×1657）：歩く 所＝だ円（中 526,1090・横 380・縦 330）・走る 道＝だ円（中 526,1070・横 430・縦 420）
  const AREA = { cx: 526, cy: 1090, rx: 280, ry: 300 }, TRACK = { cx: 526, cy: 1070, rx: 400, ry: 410, n: 3.2 };
  // 走る 道（角の 丸い 四角＝スーパー だ円）を 細かい 点に して、地面の 長さで 1周を 区切る（反時計まわり：手前を 右へ）
  let TP = null;
  function trackPts() {
    if (TP) return TP;
    const N = 1200, e = 2 / TRACK.n, P = [];
    for (let i = 0; i < N; i++) {
      const th = Math.PI / 2 - i / N * TAU, c = Math.cos(th), sn = Math.sin(th);
      P.push([TRACK.cx + TRACK.rx * Math.sign(c) * Math.pow(Math.abs(c), e), TRACK.cy + TRACK.ry * Math.sign(sn) * Math.pow(Math.abs(sn), e)]);
    }
    const L = [0];
    for (let i = 1; i <= N; i++) { const a = P[i - 1], b = P[i % N]; L.push(L[i - 1] + Math.hypot(b[0] - a[0], (b[1] - a[1]) / 0.5)); }
    TP = { P, L, N, total: L[N] }; return TP;
  }
  function trackAt(sArc) {           // → [x, y, 向き（地面）]
    const tp = trackPts(), N = tp.N; const s = ((sArc % tp.total) + tp.total) % tp.total;
    let lo = 0, hi = N; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (tp.L[m] <= s) lo = m; else hi = m; }
    const f = (s - tp.L[lo]) / ((tp.L[hi] - tp.L[lo]) || 1), a = tp.P[lo % N], b = tp.P[hi % N];
    const p0 = tp.P[(lo - 4 + N) % N], p1 = tp.P[(hi + 4) % N];        // 向きは 少し 広く 見て なめらかに
    return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, Math.atan2((p1[1] - p0[1]) / 0.5, p1[0] - p0[0])];
  }
  function trackNear(x, y) {         // いちばん 近い 道の 点（地面の 長さで）
    const tp = trackPts(); let bi = 0, bd = 1e18;
    for (let i = 0; i < tp.N; i += 2) { const d = (tp.P[i][0] - x) ** 2 + ((tp.P[i][1] - y) / 0.5) ** 2; if (d < bd) { bd = d; bi = i; } }
    return [tp.L[bi], Math.sqrt(bd)];
  }     // 歩く 所は 体が 画面から はみ出さない 広さ（馬を 大きく した：11/08 13:44）
  // 歩く 行き先：着いた ときに 体が 画面から はみ出さない 所（大きな 馬ほど 横に 行ける はばが せまい）
  function pickWalkTarget(h, st, rnd) {
    const fits = (x, y) => { const sc = scaleAt(h, y), d = Math.atan2((y - st.y) / 0.5, x - st.x), hx = sc * (1.45 * Math.abs(Math.cos(d)) + 0.35); return x - hx >= 8 && x + hx <= 1044; };
    st.tgt = null;
    for (let k = 0; k < 30; k++) {
      const a = rnd() * TAU, r = Math.sqrt(rnd());
      const x = AREA.cx + Math.cos(a) * r * AREA.rx, y = AREA.cy + Math.sin(a) * r * AREA.ry;
      if (Math.hypot(x - st.x, (y - st.y) * 1.6) > 140 && fits(x, y)) { st.tgt = [x, y]; break; }
    }
    if (!st.tgt) {                     // 見つからない：前後（画面の 上下）に 歩く
      const y = AREA.cy + (rnd() * 2 - 1) * AREA.ry; st.tgt = [clamp(st.x, AREA.cx - 40, AREA.cx + 40), y];
    }
    return true;
  }
  function brain(opt) {
    const rnd = opt.rnd || Math.random;
    const st = { x: 520, y: 1120, dir: Math.PI * 0.15, dirV: 0, mode: 'idle', until: 0, gw: 0, gr: 0, phase: { walk: 0, run: 0 }, graze: 0, look: [0, 0], lookS: [0, 0], sleep: 0, tailFlick: 0,
      eff: 0.6, wAmp: 1, rAmp: 1, runV: 0, tPrev: null, sl: 0, rise: 0, doze: 0,
      tgt: null, n: 0, tod: opt.tod || 'morning', lap: 0, lapA: 0, want: { graze: 0, look: [0, 0] }, nextFlick: 2, force: opt.force || null, stand: !!opt.stand };
    return st;
  }
  const depth = y => clamp((y - 600) / (1550 - 600), 0, 1);
  function decide(h, st, t, rnd) {
    st.n++;
    // 見本用：force＝['idle:3','graze:4','look:3','walk','run','sleep:8'] の じゅん（なくなったら ランダム）
    let special = null, fsec = 0;
    if (st.force && st.force.length) { const f = st.force.shift().split(':'); st._lastForce = f; special = f[0]; fsec = Number(f[1] || 0); }
    else if (rnd() < 1 / 30) special = 'special';
    st.forcedWalk = false;
    // 幻の馬・神様馬（11/09 08:42 まさちゃん「基本縦向きで歩かない（立ち止まりながら身体を動かしたり、首をプルンと振ったり動いている）・歩く演出、走る演出無くして！」）
    //   正面を 向いた まま：ふつうに 立つ・まわりを 見る・首を プルンッ・前足で 地面を かく・頭を 上げる・うなずく・しっぽを ふる・体を ゆらす（体重を かける 足を かえる）
    if (st.stand && !['idle', 'look', 'shake', 'paw', 'headup', 'nod', 'swish', 'sway'].includes(special)) {
      const k = rnd(); special = k < 0.26 ? 'idle' : k < 0.44 ? 'look' : k < 0.58 ? 'shake' : k < 0.68 ? 'paw' : k < 0.78 ? 'headup' : k < 0.86 ? 'sway' : k < 0.93 ? 'swish' : 'nod';
      if (!fsec) fsec = special === 'idle' ? 3 + rnd() * 3 : 0;
    }
    if (['shake', 'paw', 'headup', 'nod', 'swish', 'sway'].includes(special)) {
      const D = { shake: 1.1, paw: 2.2, headup: 3.2, nod: 1.6, swish: 2.2, sway: 4.2 }[special], side = rnd() < 0.5 ? -1 : 1;
      st.mode = 'idle'; st.want.graze = 0; st.want.look = [0, 0]; react(st, special, D, t, { side });
      st.until = t + D + (fsec || 0.8 + rnd() * 1.6); return;
    }
    if (st.stand && special === 'look') { st.mode = 'idle'; st.until = t + (fsec || 3 + rnd() * 2.5); st.want.graze = 0; st.want.look = [(rnd() < 0.5 ? -1 : 1) * (0.45 + 0.4 * rnd()), 0.1 + 0.2 * rnd()]; return; }
    if (special === 'gallop') { st.mode = 'gallop'; st.until = t + 1e9; st.runV = st.runV || 0; return; }      // 見本 用：まっすぐ 走りつづける
    if (special === 'walkto') { const f = st._lastForce; st.tgt = [Number(f[1]), Number(f[2])]; st.mode = 'walk'; st.until = t + 30; st.forcedWalk = true; return; }
    if (special === 'poop') { st.mode = 'idle'; st.until = t + (fsec || 4); st.want.graze = 0; st.want.look = [0, 0]; st.poopReq = true; return; }      // 見本 用：うんち
    if (special === 'idle' || special === 'graze' || special === 'look') {
      st.mode = 'idle'; st.until = t + (fsec || 5);
      st.want.graze = special === 'graze' ? 1 : 0; st.want.look = special === 'look' ? [0.7, -0.2] : [0, 0]; return;
    }
    if (special === 'special' || special === 'run' || special === 'sleep') {
      if (st.tod === 'night' && special !== 'run') { st.mode = 'sleep'; st.until = t + Math.max(9, fsec || 60); st.sleepT = t; st.sl = 0; st.rise = 0; st.doze = 0; st.lieDoneT = 0; return; }
      if (st.tod !== 'night' && special !== 'sleep' && (h.opt.stage || 1) > 1.4) {      // 大きな 馬（幻の馬・神様馬）は 道から はみ出すので 走らず、顔を 上げて まわりを 見る
        st.mode = 'idle'; st.until = t + 6; st.want.graze = 0; st.want.look = [0.6, 0.35]; return;
      }
      if (st.tod !== 'night' && special !== 'sleep') {
        st.mode = 'run'; st.lap = 0; st.runV = 0; st.runEnd = 0; st.runT = 0; st.tPrev = null; st.toTrack = true; return;
      }
    }
    if (special === 'walk' || (!special && rnd() < 0.4)) {          // 歩く（4割）
      pickWalkTarget(h, st, rnd);
      st.mode = 'walk'; st.until = t + 30; return;
    }
    // 止まる（6割）：ただ 立つ・まわりを 見る・草を 食べる
    st.mode = 'idle'; st.until = t + 5 + rnd() * 9;
    const k = rnd();
    st.want.graze = k < 0.35 ? 1 : 0;
    st.want.look = k >= 0.35 && k < 0.7 ? [(rnd() - 0.5) * 1.6, (rnd() - 0.5) * 0.8] : [0, 0];
  }
  // 向きを なめらかに 変える：回る 速さ（dirV）を 少しずつ 変える（急に 回り はじめない・急に 止まらない）
  function steer(st, target, dt, maxW, gain, resp, ff) {
    const w = clamp(angDiff(st.dir, target) * gain + (ff || 0), -maxW, maxW);
    st.dirV += (w - st.dirV) * Math.min(1, dt * resp);
    st.dir += st.dirV * dt;
  }
  // 1コマ 進める（dt 秒）。px：絵の px と 地面の 長さ（体の 高さ 1 ＝ 何 px）
  function step(h, st, t, dt, rnd) {
    rnd = rnd || Math.random;
    if (t >= st.until && st.mode !== 'run' && !st.careHold) decide(h, st, t, rnd);      // お世話の 間（careHold）は 勝手に 動かない
    const s = scaleAt(h, st.y);
    let wantW = 0, wantR = 0, effT = st.eff, steered = false;
    // 第4.151版（まさちゃん 11/11 09:07「ボタンを押してから行われるまでが遅すぎる」）：お世話で 呼ばれた ときは 急ぎ足（st.hurry 倍：tc_care.js の HURRY）。
    //   歩はばは そのまま・足の 回る 速さと 体の 進む 速さを 同じ 倍に する（ひづめは すべらない）・向きを かえる 速さも 同じ 倍
    const hk = (st.mode === 'walk' || st.mode === 'turn') && st.hurry > 1 ? st.hurry : 1;
    if (st.mode === 'walk' && st.tgt) {
      const dx = st.tgt[0] - st.x, dy = st.tgt[1] - st.y, dist = Math.hypot(dx, dy / 0.5);
      const want = Math.atan2(dy / 0.5, dx), turn = angDiff(st.dir, want);
      steer(st, want, dt, 1.1 * hk, 1.8 * hk, 3.5 * hk); steered = true;
      wantW = 1;
      effT = lerp(1, hk > 1 ? 0.5 : 0.25, smooth((Math.abs(turn) - 0.25) / 0.9)) * clamp(dist / 90, 0.5, 1);   // 向きを 変える 間・近く では 小さな 歩はばで ゆっくり（急ぎ足の ときは 少し 大きめ）
      if (dist < Math.max(28, 0.06 * s * h.H)) {
        // 着いた：ときどき そのまま 次の 場所へ 歩きつづける（ぶらぶら 歩く）・ふだんは 止まる
        if (!(st.force && st.force.length) && !st.forcedWalk && !st.careHold && rnd() < 0.45 && pickWalkTarget(h, st, rnd)) { st.until = t + 30; }
        else { st.mode = 'idle'; st.until = st.force && st.force.length ? t : t + 4 + rnd() * 7; st.want.graze = rnd() < 0.3 ? 1 : 0; st.want.look = [0, 0]; }
      }
    } else if (st.mode === 'turn') {               // その場で 向きを かえる（小さな 歩はばで 回る：お世話で 手前に 来た あと 横向きに なる・11/09）
      const d = angDiff(st.dir, st.turnTo);
      steer(st, st.turnTo, dt, 1.25 * hk, 2.4 * hk, 4.5 * hk); steered = true;
      wantW = Math.abs(d) > 0.07 ? 1 : 0; effT = 0.3;
      if (Math.abs(d) < 0.05 && Math.abs(st.dirV) < 0.12 * hk) { st.mode = 'idle'; st.until = st.careHold ? t + 1e3 : t + 3; }
    } else if (st.mode === 'gallop') {             // 見本 用：向きを かえずに まっすぐ ギャロップ
      const vWalk = walkSpeed(h, 1, 1);
      st.runV += clamp(RUN_V - st.runV, -3.6 * dt, 3.0 * dt);
      wantR = clamp((st.runV - vWalk) / (2.0 - vWalk), 0, 1); wantW = st.runV > 0.05 ? 1 - wantR : 0; effT = 1;
      st.x += Math.cos(st.dir) * st.runV * s * dt; st.y += Math.sin(st.dir) * st.runV * s * dt * 0.5;
    } else if (st.mode === 'run') {
      // 走る 道へ（少し 先へ ななめに 合流）→ 1周（反時計まわり：手前を 右へ・11/08 16:43 まさちゃん「走るの一周にして」）→ だんだん 歩きに もどる。速さは 体の 高さ 1 ＝ 1／秒
      const vWalk = walkSpeed(h, 1, 1);
      const tv = st.toTrack ? 3.4 : st.lap < 0.9 ? RUN_V : vWalk * 0.9;      // 1周の 終わりが 近づいたら ゆるめる
      st.runV += clamp(tv - st.runV, -3.6 * dt, 3.0 * dt);                   // 速さは なめらかに
      wantR = clamp((st.runV - vWalk) / (2.0 - vWalk), 0, 1); wantW = st.runV > 0.05 ? 1 - wantR : 0;   // 足の 動きは 速さに 合わせる
      effT = clamp(st.runV / vWalk, 0.25, 1);
      const v = st.runV * s;                                                 // px／秒
      if (st.toTrack) {
        // 少し 先の 道の 外がわを ねらう（道の 上の 点を ねらうと 内がわを まわりつづける）
        const [s0, d0] = trackNear(st.x, st.y), q = trackAt(s0 + 260);
        const ox = (q[0] - TRACK.cx) * 1.08 + TRACK.cx, oy = (q[1] - TRACK.cy) * 1.08 + TRACK.cy;
        st.runT = (st.runT || 0) + dt;
        steer(st, Math.atan2((oy - st.y) / 0.5, ox - st.x), dt, 2.2, 3.0, 6); steered = true;
        st.x += Math.cos(st.dir) * v * dt; st.y += Math.sin(st.dir) * v * dt * 0.5;
        if (d0 < 22 || st.runT > 4) { st.toTrack = false; st.lapS = s0; st.lapS0 = s0; st.tPrev = null; }
      } else {
        st.lapS += v * dt; st.lap = (st.lapS - st.lapS0) / trackPts().total;      // 地面の 長さで 進む（縦は 画面の 2倍）
        const q = trackAt(st.lapS);
        const e = Math.min(1, dt * 8); st.x += (q[0] - st.x) * e; st.y += (q[1] - st.y) * e;
        const ta = q[2];
        const ff = st.tPrev == null || dt <= 0 ? 0 : angDiff(st.tPrev, ta) / dt; st.tPrev = ta;     // 道の 曲がりに 合わせて 先に 回る
        steer(st, ta, dt, 4, 5, 8, ff); steered = true;
        if (st.lap >= 1 && st.runV < vWalk * 0.95) {                          // 歩きに もどって 少し 歩いたら 止まる
          st.runEnd += dt;
          if (st.runEnd > 1.6) { st.mode = 'idle'; st.until = st.force && st.force.length ? t : t + 5 + rnd() * 5; st.want.graze = 0; st.want.look = [0, 0]; }
        }
      }
    }
    if (!steered) { st.dirV *= Math.max(0, 1 - dt * 4); st.dir += st.dirV * dt; }      // 止まった 後も 回る 速さは ゆっくり 0 へ
    // なめらかに 切りかえ
    st.eff += (effT - st.eff) * Math.min(1, dt * 2.5 * hk);
    st.gw += clamp(wantW - st.gw, -dt * 1.8 * hk, dt * 1.8 * hk); st.gr += clamp(wantR - st.gr, -dt * 1.6, dt * 1.6);
    const gz = st.mode === 'idle' ? st.want.graze : 0; st.graze += clamp(gz - st.graze, -dt * 0.7, dt * 0.7);
    const lk = st.mode === 'idle' ? st.want.look : [0, 0]; st.look = st.look.map((v, i) => v + clamp(lk[i] - v, -dt * 0.9, dt * 0.9));
    st.lookS = st.lookS.map((v, i) => v + (st.look[i] - v) * Math.min(1, dt * 3));
    // 寝る：横に なる（5.6秒・なめらかに）→ 休む → ねむる（頭を 下げる）→ 頭を 上げる → 起きる（1.7秒・勢いよく）
    let dzT = 0;
    if (st.mode === 'sleep') {
      const tUp = st.until - RISE_DUR;
      if (st.sl < 1) { st.sl = Math.min(1, st.sl + dt / (st.lieDur || LIE_DUR)); if (st.sl >= 1) st.lieDoneT = t; }      // ごろん（お世話）は 速く 横に なる
      else if (t >= tUp) st.rise = Math.min(1, st.rise + dt / RISE_DUR);
      dzT = st.sl >= 1 && t > (st.lieDoneT || 0) + 1.5 && t < tUp - 2.0 ? 1 : 0;
      if (st.rise >= 1) {          // 起きた：前へ ずれた ぶんを 場所に うつす（見た目は そのまま）
        const sc = scaleAt(h, st.y); st.x += Math.cos(st.dir) * XE * sc; st.y += Math.sin(st.dir) * XE * sc * 0.5;
        st.mode = 'idle'; st.until = t + 4; st.sl = 0; st.rise = 0; st.doze = 0; st.upT = t; st.lieDur = null; st.flop = null;       // 立った 直後に 頭を ふり上げて 体が 少し はずむ
      }
    }
    st.doze = (st.doze || 0) + clamp(dzT - (st.doze || 0), -dt / 2.0, dt / 2.5);
    st.sleep = (st.sl || 0) * (1 - (st.rise || 0));          // かげ 用（寝て いる 強さ）
    // 足の 時間：歩はばと 足の 速さは 歩く 強さで かわる（体の 進む 速さと そろえる）
    const g = GAITS.walk, gR = GAITS.run;
    st.wAmp = 0.5 + 0.5 * st.eff;
    st.phase.walk = (st.phase.walk + dt / walkOf(h).T * (0.7 + 0.3 * st.eff) * hk * (st.gw > 0.01 ? 1 : 0)) % 1;
    const vr = Math.max(st.runV || 0, 0.01), cr = 0.8 + 0.2 * clamp(vr / RUN_V, 0, 1);
    st.rAmp = clamp(Math.asin(clamp(vr * gR.st * gR.T / (2 * h.legLen * cr), 0, 0.99)) / gR.A, 0.35, 1.15);
    st.phase.run = (st.phase.run + dt / gR.T * cr * (st.gr > 0.01 ? 1 : 0)) % 1;
    if (st.mode !== 'run' && st.mode !== 'gallop') {
      const v = walkSpeed(h, st.eff, smooth(st.gw)) * s * (st.mode === 'turn' ? 0.25 : 1) * hk;      // px／秒（足と 同じ 速さ・その場で 回る ときは 少しだけ 進む）
      st.x += Math.cos(st.dir) * v * dt; st.y += Math.sin(st.dir) * v * dt * 0.5;
    }
    // しっぽを ときどき ふる（ふり はじめも おわりも やわらかく）
    if (t > st.nextFlick) { st.nextFlick = t + 2.5 + rnd() * 6; st.flickT = t; }
    // 幻の馬・神様馬の 特別な 動き（口を 開ける・振動・紫の 煙・雷）は ぜんぶ なし（11/09 01:40・02:10・03:20 まさちゃん）
    // うんち：2分 ごとの リセットで 1/7（11/08 23:38 まさちゃん）。止まって しっぽを 上げ、しっぽの 下から 地面へ 落ちて その まま のこる
    if (st.nextReset == null) st.nextReset = t + 120;
    if (t >= st.nextReset) { st.nextReset += 120; if (rnd() < 1 / 7) st.poopReq = true; }
    if (st.stand) st.poopReq = false;          // 幻の馬・神様馬は うんち しない
    if (st.poopReq && st.poopT == null && !(st.sl > 0.001) && st.mode !== 'run' && st.mode !== 'gallop') {
      st.poopT = t; st.poopReq = false; st.mode = 'idle'; st.until = Math.max(st.until, t + POOP_DUR + 0.3); st.want.graze = 0; st.want.look = [0, 0];
      st.poopImg = Math.floor(rnd() * 3) % 3; st.poopDone = false;
    }
    if (st.poopT != null) {
      const pu = (t - st.poopT) / POOP_DUR;
      st.poopE = pu < 1 ? smooth(clamp(pu / 0.22, 0, 1)) * (1 - smooth(clamp((pu - 0.72) / 0.28, 0, 1))) : 0;
      if (pu >= 0.42 && !st.poopDone) {
        st.poopDone = true; st.poops = st.poops || [];
        const back = 1.08 * s;                                       // しっぽの 下（体の 長さ で 1.08 うしろ）
        st.poops.push({ x: st.x - Math.cos(st.dir) * back, y: st.y - Math.sin(st.dir) * back * 0.5, img: st.poopImg, t0: t, h0: 1.05, w: [0.3, 0.5, 0.42][st.poopImg] * (h.opt.stage || 1) });
        if (st.poops.length > 3) st.poops.shift();
      }
      if (pu >= 1) { st.poopT = null; st.poopE = 0; }
    }
    st.tailFlick = st.flickT ? 0.35 * bump((t - st.flickT) / 0.8, 2) : 0;
  }
  // 体の 高さ 1 → 絵の px（奥ほど 小さい）
  function scaleAt(h, y) { return (h.opt.base || 175) * lerp(0.68, 1.18, depth(y)) * (h.opt.stage || 1); }     // 馬を 約1.3倍・奥でも 小さく なりすぎない（まさちゃん「もう少し馬が見えやすい方がいい」）

  // 時間帯の 光（見る 向きの 座標：x 右・y 上・z 手前）
  const LIGHT = {
    morning: { sun: [-0.45, 0.75, 0.48], sunC: [1.0, 0.97, 0.9], amb: [0.53, 0.52, 0.51], fill: [0.9, 0.88, 0.9], shadow: 0.32, skyT: [0.569, 1.083, 1.348], gndT: [1.313, 1.012, 0.675] },      // 朝の かげは 少し あたたかく（白い 馬が 灰色に 見えない：11/08 16:26）
    evening: { sun: [-0.8, 0.35, 0.45], sunC: [1.05, 0.72, 0.48], amb: [0.42, 0.36, 0.38], fill: [0.85, 0.78, 0.82], shadow: 0.26, skyT: [1.134, 0.941, 0.924], gndT: [1.471, 0.978, 0.551] },
    night: { sun: [0.3, 0.6, 0.7], sunC: [0.36, 0.42, 0.62], amb: [0.2, 0.22, 0.3], fill: [0.75, 0.82, 1.0], shadow: 0.18, skyT: [0.214, 0.919, 1.867], gndT: [1.055, 0.962, 0.983] },
    divine: { sun: [0.45, 0.8, 0.45], sunC: [1.08, 1.0, 0.86], amb: [0.6, 0.57, 0.52], fill: [0.98, 0.92, 0.84], shadow: 0.26, skyT: [0.812, 1.013, 1.175], gndT: [1.364, 1.02, 0.616] },      // 神様馬の 背景：右上から 神々しい 光
    abyss: { sun: [0.25, 0.6, 0.75], sunC: [0.6, 0.48, 0.82], amb: [0.3, 0.24, 0.42], fill: [0.78, 0.6, 1.0], shadow: 0.22, skyT: [0.412, 0.683, 1.905], gndT: [0.984, 0.938, 1.078] },        // 幻の馬の 背景：紫の 月あかり
  };

  // 空と 地面の 光の 色（空：少しだけ 空の 色み・地面：馬場の 照りかえし）
  const hemiOf = lt => lt.hemi || (lt.hemi = {
    sky: lt.amb.map((a, i) => a * (1 + 0.3 * ((lt.skyT || [1, 1, 1])[i] - 1))),
    gnd: lt.amb.map((a, i) => a * (1 + 0.6 * ((lt.gndT || [1, 1, 1])[i] - 1)) * 0.5) });
  // 骨を まぜる 強さ：ふだんは 1（関節が なめらか）・寝る 間は 0（足を 大きく 折るので 1つの 骨の まま：形が つぶれない）
  function blendOf(st) { return st.sl > 0.001 ? (st.rise > 0 ? smooth((st.rise - 0.7) / 0.3) : 1 - smooth(st.sl * 3)) : 1; }
  // 描く（W,H：キャンバスの px・fw,fh：フィールドの 絵の px）
  function draw(h, st, t, view) {
    const gl = h.gl, lt = LIGHT[st.light || st.tod];
    const s = scaleAt(h, st.y) * view.k;                     // キャンバスの px／体の 高さ 1
    const cx = (st.x * view.k + view.ox) / view.W * 2 - 1, cy = 1 - (st.y * view.k + view.oy) / view.H * 2;
    const mats = pose(h, st, t);
    const pitch = view.pitch != null ? view.pitch : 0.49;      // 見下ろし 28°（見本の 比べ 用に 横からも）
    let V = M.mul(M.rx(pitch), M.ry(-st.dir));              // 体の x（前）を 進む 向きへ
    const R3 = [V[0], V[1], V[2], V[4], V[5], V[6], V[8], V[9], V[10]];      // 回転だけ（法線 用）
    V = M.mul(M.sc(s / view.W * 2, s / view.H * 2, 0.4), V);
    h.last = { mats, V, cx, cy, view, s, R3 };                // お世話の 絵を 置く ため（where）
    // かげ（足もと・時間帯で こさ と のび）
    gl.useProgram(h.S); gl.disable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    gl.bindBuffer(gl.ARRAY_BUFFER, h.B.quad); gl.enableVertexAttribArray(h.loc.sp); gl.vertexAttribPointer(h.loc.sp, 2, gl.FLOAT, false, 0, 0);
    const len = 0.62 * (1 - st.sleep * 0.15), sx = s * (Math.abs(Math.cos(st.dir)) * len + 0.32) / view.W * 2, sy = s * (0.2 + 0.2 * Math.abs(Math.sin(st.dir))) / view.H * 2;      // 正面・後ろ 向きの ときは 体の 長さぶん 縦に のびる
    gl.uniform4f(h.loc.uE, cx + (st.tod === 'evening' ? sx * 0.25 : 0), cy, sx * (st.tod === 'evening' ? 1.3 : 1), sy);
    gl.uniform1f(h.loc.uO, lt.shadow);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    if (h.hoof && (view.quality || {}).hoof !== 0) for (const L of ['FL', 'FR', 'HL', 'HR']) {      // ひづめの 下の かげ（背景の 絵の 物と 同じ ように 地面に なじむ）
      const b = h.bi[L + '_f'], p = h.hoof[L]; if (b == null || !p) continue; const Bm = mats[b];
      const w = [0, 1, 2].map(r => Bm[r] * p[0] + Bm[4 + r] * p[1] + Bm[8 + r] * p[2] + Bm[12 + r]);
      const k = 1 - smooth(clamp((w[1] - 0.03) / 0.45, 0, 1)); if (k < 0.01) continue;
      const qx = V[0] * w[0] + V[8] * w[2] + V[12], qy = V[1] * w[0] + V[9] * w[2] + V[13], r = 0.2 * s;
      gl.uniform4f(h.loc.uE, cx + qx, cy + qy, r / view.W * 2, r * 0.42 / view.H * 2);
      gl.uniform1f(h.loc.uO, lt.shadow * 0.9 * k);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    }
    if (st.props) for (const pr of st.props) {      // 物（バケツ）の かげ
      if (!pr.sh || !(pr.sh[3] > 0.001)) continue; const [x, z, r, o] = pr.sh;
      const qx = V[0] * x + V[8] * z + V[12], qy = V[1] * x + V[9] * z + V[13];
      gl.uniform4f(h.loc.uE, cx + qx, cy + qy, r * s / view.W * 2, r * s * 0.42 / view.H * 2); gl.uniform1f(h.loc.uO, lt.shadow * o);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    }
    gl.disableVertexAttribArray(h.loc.sp);
    if (st.poops && st.poops.length && h.poopTex.length) drawPoops(h, st, t, view, lt, s, false);
    // 馬
    gl.useProgram(h.P); gl.enable(gl.DEPTH_TEST); gl.clear(gl.DEPTH_BUFFER_BIT); gl.depthFunc(gl.LEQUAL);
    const at = (b, loc, n, type, norm, stride) => { if (loc < 0) return; gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, n, type || gl.FLOAT, !!norm, stride || 0, 0); };
    at(h.B.pos, h.loc.aPos, 3); at(h.B.bone, h.loc.aBone, 1); at(h.B.bone2, h.loc.aBone2, 1); at(h.B.bw, h.loc.aBw, 1, gl.UNSIGNED_BYTE, true);
    gl.uniform1f(h.loc.uBlend, blendOf(st));
    if (h.loc.aCv >= 0) { if (h.B.cv) at(h.B.cv, h.loc.aCv, 1, gl.UNSIGNED_BYTE, true); else { gl.disableVertexAttribArray(h.loc.aCv); gl.vertexAttrib1f(h.loc.aCv, 0.5); } }
    if (h.fmt2) {
      at(h.B.nrm, h.loc.aNrm, 4, gl.BYTE, true, 4); at(h.B.uv, h.loc.aUV, 2, gl.UNSIGNED_SHORT, true);
      if (h.loc.aCol >= 0) { gl.disableVertexAttribArray(h.loc.aCol); gl.vertexAttrib3f(h.loc.aCol, 1, 1, 1); }
      // 馬の 絵は 6番・7番の 場所を 使う（フィールドの 絵が 入って いる 0〜2番を 上書きしない：上書きすると 次の コマで 背景が 馬の 絵に なる）
      gl.activeTexture(gl.TEXTURE6); gl.bindTexture(gl.TEXTURE_2D, h.tex); gl.uniform1i(h.loc.uTex, 6); gl.uniform1f(h.loc.uTexOn, h.tex ? 1 : 0);
      gl.activeTexture(gl.TEXTURE7); gl.bindTexture(gl.TEXTURE_2D, h.ntex); gl.uniform1i(h.loc.uNrm, 7); gl.uniform1f(h.loc.uNrmOn, h.ntex && (view.quality || {}).nm !== 0 ? 1 : 0); gl.activeTexture(gl.TEXTURE0);
    } else {
      at(h.B.nrm, h.loc.aNrm, 3); at(h.B.col, h.loc.aCol, 3, gl.UNSIGNED_BYTE, true);
      if (h.loc.aUV >= 0) { gl.disableVertexAttribArray(h.loc.aUV); gl.vertexAttrib2f(h.loc.aUV, 0, 0); }
      gl.uniform1f(h.loc.uTexOn, 0); gl.uniform1f(h.loc.uNrmOn, 0);
    }
    const all = [].concat(...mats); while (all.length < 18 * 16) all.push(...M.id()); gl.uniformMatrix4fv(h.loc.uB, false, new Float32Array(all.slice(0, 18 * 16)));
    gl.uniformMatrix4fv(h.loc.uV, false, new Float32Array(V)); gl.uniformMatrix3fv(h.loc.uR, false, new Float32Array(R3));
    gl.uniform4f(h.loc.uP, cx, cy, 0.08, 0);
    const n = Math.hypot(...lt.sun); gl.uniform3f(h.loc.uSun, lt.sun[0] / n, lt.sun[1] / n, lt.sun[2] / n);
    gl.uniform3fv(h.loc.uSunC, lt.sunC); gl.uniform3fv(h.loc.uAmb, lt.amb); gl.uniform3fv(h.loc.uFill, lt.fill); gl.uniform1f(h.loc.uLift, h.opt.lift || 0); gl.uniform1f(h.loc.uA, 1);
    const hm = hemiOf(lt); gl.uniform3fv(h.loc.uSky, hm.sky); gl.uniform3fv(h.loc.uGnd, hm.gnd);
    const Q = view.quality || {};          // 画質（見本で くらべる 用に 変えられる）：sm 面の グラデーション・ao・grain 紙の ざらざら
    gl.uniform1f(h.loc.uAoOn, h.fmt2 && h.meta.ao && Q.ao !== 0 ? 1 : 0); gl.uniform1f(h.loc.uSm, Q.sm != null ? Q.sm : 0.55); gl.uniform1f(h.loc.uGrain, Q.grain != null ? Q.grain : 0); gl.uniform1f(h.loc.uCv, h.B.cv ? (Q.cv != null ? Q.cv : 1) : 0); gl.uniform1f(h.loc.uDbg, Q.dbg ? 1 : 0);      // 紙の ざらざらは なし（11/08 22:14 まさちゃん「紙のザラザラ感は一切いらないよ！」）
    // 光る 目：ゆっくり 息を する ように 明るさが かわる（2.8秒）・ねむって いる 間は 目を 閉じて 光らない
    const gk = h.glow && h.eyes ? (0.84 + 0.16 * Math.sin(TAU * t / 2.8)) * (1 - 0.92 * smooth(st.doze || 0)) * (st.glowK != null ? st.glowK : 1) * (h.opt.glowK != null ? h.opt.glowK : 1) : 0;      // opt.glowK：馬ごとの 強さ（神様馬は ひかえめ：11/09 10:03）
    gl.uniform4f(h.loc.uEm, h.em[0], h.em[1], h.em[2], h.bi.head != null ? h.bi.head : -9);
    if (gk > 0) {
      const e0 = h.eyes[0].p, e1 = h.eyes[1].p;
      gl.uniform3f(h.loc.uE0, e0[0] - h.em[0], e0[1] - h.em[1], e0[2] - h.em[2]); gl.uniform3f(h.loc.uE1, e1[0] - h.em[0], e1[1] - h.em[1], e1[2] - h.em[2]);
      gl.uniform3fv(h.loc.uGc, h.glow); gl.uniform2f(h.loc.uGr, h.eyeR, Math.min(1, gk * 1.1));
    } else gl.uniform2f(h.loc.uGr, 1, 0);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, h.B.idx);
    gl.drawElements(gl.TRIANGLES, h.meta.i, h.meta.idx32 ? gl.UNSIGNED_INT : gl.UNSIGNED_SHORT, 0);
    [h.loc.aPos, h.loc.aNrm, h.loc.aCol, h.loc.aBone, h.loc.aBone2, h.loc.aBw, h.loc.aUV, h.loc.aCv].forEach(l => { if (l >= 0) gl.disableVertexAttribArray(l); });
    if (st.props && st.props.length) drawProps(h, st, view);      // バケツ・エサ（馬の 深さと くらべて 描く：顔が バケツの 中に 入る）
    gl.disable(gl.DEPTH_TEST);
    if (gk > 0) drawEyeGlow(h, mats, V, R3, cx, cy, s, view, gk);
    if (st.poops && st.poops.length && h.poopTex.length) drawPoops(h, st, t, view, lt, s, true);
  }
  // うんち：地面に 立てた 絵（落ちる ときは しっぽの 高さから）。front＝馬より 手前の ものだけ／奥の ものだけ
  function drawPoops(h, st, t, view, lt, s, front) {
    const gl = h.gl, pitch = view.pitch != null ? view.pitch : 0.49;
    const tint = [0, 1, 2].map(i => Math.min(1.05, lt.amb[i] + lt.sunC[i] * 0.55));
    gl.disable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    gl.bindBuffer(gl.ARRAY_BUFFER, h.B.quad);
    for (const q of st.poops) {
      if ((q.y > st.y) !== front) continue;
      const tex = h.poopTex[q.img % h.poopTex.length]; if (!tex) continue;
      const ss = scaleAt(h, q.y) / (h.opt.stage || 1) * view.k;                // 場所の 大きさ（px／体の 高さ 1：馬の 大きさ 抜き）
      const tau = t - q.t0, TF = 0.32, fall = clamp(tau / TF, 0, 1);
      const hgt = q.h0 * (1 - fall * fall), sq = tau < TF ? 0.75 + 0.25 * fall : 1 - 0.12 * Math.exp(-(tau - TF) * 14) * Math.cos((tau - TF) * 30);
      const wpx = q.w * ss * (0.7 + 0.3 * fall), hpx = wpx * tex.h / tex.w * sq;
      const gx = q.x * view.k + view.ox, gy = q.y * view.k + view.oy - hgt * ss * (h.opt.stage || 1) * Math.cos(pitch);
      // かげ
      gl.useProgram(h.S); gl.enableVertexAttribArray(h.loc.sp); gl.vertexAttribPointer(h.loc.sp, 2, gl.FLOAT, false, 0, 0);
      const gy0 = q.y * view.k + view.oy;
      gl.uniform4f(h.loc.uE, gx / view.W * 2 - 1, 1 - gy0 / view.H * 2, wpx * 0.62 / view.W * 2, wpx * 0.2 / view.H * 2); gl.uniform1f(h.loc.uO, lt.shadow * 0.8 * fall);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); gl.disableVertexAttribArray(h.loc.sp);
      // 絵
      gl.useProgram(h.PS); gl.enableVertexAttribArray(h.loc.pp); gl.vertexAttribPointer(h.loc.pp, 2, gl.FLOAT, false, 0, 0);
      gl.activeTexture(gl.TEXTURE5); gl.bindTexture(gl.TEXTURE_2D, tex.t); gl.uniform1i(h.loc.pT, 5); gl.activeTexture(gl.TEXTURE0);
      gl.uniform3fv(h.loc.pTint, q.gold ? [1.55, 1.2, 0.42] : tint);      // 金のうんち（おそうじで「運がついた！」）
      gl.uniform4f(h.loc.pE, gx / view.W * 2 - 1, 1 - (gy - hpx * 0.46) / view.H * 2, wpx / view.W, hpx / view.H);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); gl.disableVertexAttribArray(h.loc.pp);
    }
  }
  // 目の まわりの やわらかい 光（こちらを 向いて いる 目だけ：顔の むこうがわの 目は 見えない）
  function drawEyeGlow(h, mats, V, R3, cx, cy, s, view, gk) {
    const gl = h.gl, Bh = mats[h.bi.head];
    gl.useProgram(h.G); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    gl.bindBuffer(gl.ARRAY_BUFFER, h.B.quad); gl.enableVertexAttribArray(h.loc.gp); gl.vertexAttribPointer(h.loc.gp, 2, gl.FLOAT, false, 0, 0);
    gl.uniform3fv(h.loc.gGc, h.glow);
    const rpx = h.eyeR * s * 4.5 * (0.96 + 0.04 * gk) * (h.opt.glowR || 1);
    for (const e of h.eyes) {
      const p = e.p, w = [0, 1, 2].map(r => Bh[r] * p[0] + Bh[4 + r] * p[1] + Bh[8 + r] * p[2] + Bh[12 + r]);
      const nb = [0, 1, 2].map(r => Bh[r] * e.n[0] + Bh[4 + r] * e.n[1] + Bh[8 + r] * e.n[2]);
      const fz = R3[2] * nb[0] + R3[5] * nb[1] + R3[8] * nb[2];          // 見る 向きの z（＋＝こちら 向き）
      const f = smooth((fz + 0.05) / 0.45); if (f <= 0.001) continue;
      const qx = V[0] * w[0] + V[4] * w[1] + V[8] * w[2] + V[12], qy = V[1] * w[0] + V[5] * w[1] + V[9] * w[2] + V[13];
      gl.uniform4f(h.loc.gE, cx + qx, cy + qy, rpx / view.W * 2, rpx / view.H * 2);
      gl.uniform1f(h.loc.gGk, gk * f);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    }
    gl.disableVertexAttribArray(h.loc.gp);
  }

  // 体の 目印の いまの 場所（フィールドの 絵の px）・z（＋＝こちら 向き）。draw の あとに よぶ
  function where(h, name, ground) {   // ground：その 真下の 地面
    const L = h.last, a = h.anchors[name]; if (!L || !a || !a.p) return null;
    const Bm = L.mats[a.b], p = a.p, w = [0, 1, 2].map(r => Bm[r] * p[0] + Bm[4 + r] * p[1] + Bm[8 + r] * p[2] + Bm[12 + r]);
    if (ground) w[1] = 0;
    const V = L.V, qx = V[0] * w[0] + V[4] * w[1] + V[8] * w[2] + V[12], qy = V[1] * w[0] + V[5] * w[1] + V[9] * w[2] + V[13];
    const px = (L.cx + qx + 1) / 2 * L.view.W, py = (1 - (L.cy + qy)) / 2 * L.view.H;
    return [(px - L.view.ox) / L.view.k, (py - L.view.oy) / L.view.k];
  }
  // 画面の 中の 大きさ（draw の あと：[左, 上, 右, 下]・フィールドの 絵の px）
  function extent(h) {
    const L = h.last; if (!L) return null; const V = L.V; let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (let k = 0; k < h.sampB.length; k++) {
      const Bm = L.mats[h.sampB[k]], p0 = h.sampP[k * 3], p1 = h.sampP[k * 3 + 1], p2 = h.sampP[k * 3 + 2];
      const w0 = Bm[0] * p0 + Bm[4] * p1 + Bm[8] * p2 + Bm[12], w1 = Bm[1] * p0 + Bm[5] * p1 + Bm[9] * p2 + Bm[13], w2 = Bm[2] * p0 + Bm[6] * p1 + Bm[10] * p2 + Bm[14];
      const qx = V[0] * w0 + V[4] * w1 + V[8] * w2 + V[12], qy = V[1] * w0 + V[5] * w1 + V[9] * w2 + V[13];
      const x = ((L.cx + qx + 1) / 2 * L.view.W - L.view.ox) / L.view.k, y = ((1 - (L.cy + qy)) / 2 * L.view.H - L.view.oy) / L.view.k;
      if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
    }
    return [x0, y0, x1, y1];
  }
  // pose の 結果（mats）で 目印の 場所を 出す（いま 描いて いる 場所・向きの まま：草を 食べた ときの 鼻 など）
  function wherePose(h, mats, name, ground) {
    const L = h.last, a = h.anchors[name]; if (!L || !a || !a.p) return null;
    const Bm = mats[a.b], p = a.p, w = [0, 1, 2].map(r => Bm[r] * p[0] + Bm[4 + r] * p[1] + Bm[8 + r] * p[2] + Bm[12 + r]);
    if (ground) w[1] = 0;
    const V = L.V, qx = V[0] * w[0] + V[4] * w[1] + V[8] * w[2] + V[12], qy = V[1] * w[0] + V[5] * w[1] + V[9] * w[2] + V[13];
    return [((L.cx + qx + 1) / 2 * L.view.W - L.view.ox) / L.view.k, ((1 - (L.cy + qy)) / 2 * L.view.H - L.view.oy) / L.view.k];
  }
  // pose の 結果（mats）で 目印の 体の 座標（x 前・y 上・z 横・地面 0）：物（バケツ）を 置く ため
  function anchorPose(h, mats, name) {
    const a = h.anchors[name]; if (!a || !a.p) return null; const Bm = mats[a.b], p = a.p;
    return [0, 1, 2].map(r => Bm[r] * p[0] + Bm[4 + r] * p[1] + Bm[8 + r] * p[2] + Bm[12 + r]);
  }
  // 体の 座標の 点 → フィールドの 絵の px（draw の あと）
  function project(h, w) {
    const L = h.last; if (!L) return null; const V = L.V;
    const qx = V[0] * w[0] + V[4] * w[1] + V[8] * w[2] + V[12], qy = V[1] * w[0] + V[5] * w[1] + V[9] * w[2] + V[13];
    return [((L.cx + qx + 1) / 2 * L.view.W - L.view.ox) / L.view.k, ((1 - (L.cy + qy)) / 2 * L.view.H - L.view.oy) / L.view.k];
  }
  // お世話の 反応（体の 動き）：react(st, 'nuzzle', 2.0, t) など。いくつか 重ねられる
  // 形（bin）の 番号を 詰めた 入れもの（kisekae/lite_assets.py の pack_idx：第4.151版）を もとの 形に もどす。詰めて いない bin は そのまま 返す
  //   頭 24バイト＝'TGIZ'・もとの 長さ・番号の 場所・番号の バイト数・番号の 数・詰めた 長さ → 番号より 前・番号より 後ろ・詰めた 番号（前の 番号との 差を ジグザグに して 7bit ずつ）
  function unz(ab) {
    const u = new Uint8Array(ab);
    if (u.length < 24 || u[0] !== 0x54 || u[1] !== 0x47 || u[2] !== 0x49 || u[3] !== 0x5A) return ab;
    const dv = new DataView(ab), L = dv.getUint32(4, true), io = dv.getUint32(8, true), ib = dv.getUint32(12, true), n = dv.getUint32(16, true), pl = dv.getUint32(20, true), tail = L - io - ib;
    if (tail < 0 || 24 + io + tail + pl !== u.length || ib !== n * 4 || io % 4) throw new Error('bin');
    const out = new ArrayBuffer(L), o8 = new Uint8Array(out); o8.set(u.subarray(24, 24 + io), 0); o8.set(u.subarray(24 + io, 24 + io + tail), io + ib);
    const idx = new Uint32Array(out, io, n), end = u.length; let p = 24 + io + tail, prev = 0;
    for (let i = 0; i < n; i++) {
      let v = 0, s = 0, b;
      do { if (p >= end) throw new Error('bin'); b = u[p++]; v += (b & 127) * Math.pow(2, s); s += 7; } while (b & 128);
      prev += (v % 2) ? -(v + 1) / 2 : v / 2; idx[i] = prev;
    }
    if (p !== end) throw new Error('bin');
    return out;
  }
  function react(st, k, dur, t, o) { st.reacts = (st.reacts || []).filter(r => t - r.t0 < r.dur); st.reacts.push(Object.assign({ k, t0: t, dur }, o || {})); }
  window.TCHorse = { create, createProp, anchorPose, project, M, brain, step, draw, pose, where, wherePose, react, unz, extent, scaleAt: (h, y) => scaleAt(h, y), GAITS, WALK, RUN, AREA, TRACK, EYE_GLOW, walkLegs, walkSpeed, blendOf };
})();
