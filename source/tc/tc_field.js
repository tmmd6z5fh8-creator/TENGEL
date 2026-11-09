// トレーニングセンターの フィールド（App Store版）：WebGL の 背景（草木の ゆれ・ライトの じんわり・幻の馬／神様馬の 光と 煙）
//   見本（preview3d.html）と 同じ シェーダー。馬は tc_horse.js（同じ gl）。絵の 名前は TC_ASSET（アプリは Resources に 名前だけ）
//   TCField.create(canvas) → { gl, setField('morning'|'evening'|'night'|'abyss'|'divine'), render(t, zoom), field }
const TCField = (() => {
const CFG = { w: 1052, h: 1657, amp: [5.0, 4.2, 4.6], per: [4.6, 3.7, 5.3], ph: [0.0, 0.37, 0.71] };
const VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.0,1.0);}';
const FS = ['precision highp float;', 'uniform sampler2D uImg,uMap,uLit;uniform vec2 uSz,uRes;uniform vec4 uXf;uniform float uT,uA,uLitOn,uFx;uniform vec3 uAmp,uPer,uPh;uniform float uK[12];',
  'const float TAU=6.2831853;',
  // 神様馬・幻の馬の 背景の 動き（11/08 19:12 まさちゃん）：uFx 1＝神々しい 光が 差しこむ／2＝闇に 紫の 煙が 光りながら ただよう（どれも ゆっくり・ちかちか しない）
  'float hs(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
  'float vn(vec2 p){vec2 i=floor(p),f=fract(p);vec2 u=f*f*(3.0-2.0*f);return mix(mix(hs(i),hs(i+vec2(1.0,0.0)),u.x),mix(hs(i+vec2(0.0,1.0)),hs(i+vec2(1.0,1.0)),u.x),u.y);}',
  'float fbm(vec2 p){float a=0.5,s=0.0;for(int i=0;i<4;i++){s+=a*vn(p);p=p*2.03+vec2(17.1,9.2);a*=0.5;}return s;}',
  // 光の つぶ（ゆっくり 上へ・ゆっくり またたく）：cs＝つぶの 間・pr＝出る 割合・sz＝大きさ・up＝上る 速さ
  'float motes(vec2 ip,float t,float cs,float pr,float sz,float up,float sd){vec2 q=ip+vec2(6.0*sin(t*0.21+ip.y*0.004),t*up);vec2 c=floor(q/cs),f=fract(q/cs)-0.5;',
  '  vec2 r=vec2(hs(c+sd),hs(c+sd+3.7))-0.5;float d=length(f-r*0.6)*cs;float tw=0.5+0.5*sin(t*(0.9+0.6*hs(c+sd+5.3))+hs(c+sd+9.1)*TAU);',
  '  return step(1.0-pr,hs(c+sd+1.3))*tw*tw*((1.0-smoothstep(0.0,sz,d))+0.3*(1.0-smoothstep(0.0,sz*3.0,d)));}',
  // 金の 光の かけら（ひらひら 舞いおりる・裏返る たびに ゆっくり きらっと）：sp＝落ちる 速さ
  'float flakes(vec2 ip,float t,float cs,float pr,float sz,float sp,float sd){float cx=floor(ip.x/cs);float v=sp*(0.6+0.8*hs(vec2(cx,sd)));',
  '  float qy=ip.y-t*v+hs(vec2(cx,sd+1.0))*cs*7.0;vec2 c=vec2(cx,floor(qy/cs));vec2 f=vec2(fract(ip.x/cs),fract(qy/cs))-0.5;float ph=hs(c+sd+2.1)*TAU;',
  '  vec2 o=vec2(0.22*sin(t*(0.7+0.5*hs(c+sd+4.4))+ph),0.18*(hs(c+sd+6.6)-0.5));float d=length(f-o)*cs;',
  '  float fl=abs(sin(t*(0.8+0.6*hs(c+sd+8.8))+ph));',
  '  return step(1.0-pr,hs(c+sd+1.3))*(0.25+0.75*fl*fl)*((1.0-smoothstep(0.0,sz,d))+0.35*(1.0-smoothstep(0.0,sz*3.2,d)));}',
  // 神様馬：空の 上から 光の すじが 差しこむ（すじごとに 8〜18秒で ゆっくり 明るく／うすく・少しずつ ゆれる）
  //   金の かけら（黄色い 玉の ような 光）は 入れない（11/08 21:08 まさちゃん「神様馬ステージの黄色の玉みたいな光いらない！」）
  'vec3 divine(vec3 col,vec2 ip,float t){',
  '  vec2 v=ip-vec2(600.0,-380.0);float an=atan(v.x,v.y),dd=length(v);float r=0.0;',
  '  for(int i=0;i<7;i++){float fi=float(i);float th=-0.55+fi*0.16+0.035*sin(t*(0.09+0.025*fi)+fi*1.7);float wd=0.04+0.045*hs(vec2(fi,2.0));',
  '    float am=0.5+0.5*sin(t*TAU/(8.0+1.7*fi)+fi*2.1);float x=(an-th)/wd;r+=(0.35+0.65*am)*exp(-x*x);}',
  '  r*=0.7+0.6*fbm(vec2(an*18.0,dd*0.003-t*0.05));',       // 光の 中の ほこりが ゆっくり 流れる
  '  float fall=smoothstep(60.0,480.0,dd)*(1.0-smoothstep(700.0,2300.0,dd));float glow=exp(-dd/650.0)*(0.8+0.2*sin(t*0.45));',
  '  vec3 L=vec3(1.0,0.92,0.7)*min(r*0.36*fall+glow*0.3,0.7);col=1.0-(1.0-col)*(1.0-L);',        // スクリーン（明るく する だけ）
  '  return col;}',
  // 幻の馬：まわりを 暗く（闇）・紫の 煙が ねじれながら ただよい、ふちと 中が ゆっくり 光る・紫の 光の かけらが 上る
  'vec3 abyss(vec3 col,vec2 ip,float t){',
  '  float vg=smoothstep(1300.0,380.0,length((ip-vec2(526.0,900.0))*vec2(1.0,0.72)));col*=0.72+0.2*vg;',
  '  vec2 w=vec2(fbm(ip*0.0024+vec2(t*0.03,0.0)),fbm(ip*0.0024+vec2(3.1,-t*0.025)));',
  '  float n=fbm(ip*0.0034+1.6*w+vec2(t*0.045,-t*0.012)),n2=fbm(ip*0.0072+1.2*w+vec2(-t*0.06,t*0.02)+5.0);',
  '  float den=smoothstep(0.45,0.85,0.65*n+0.35*n2);float m=0.4+0.6*smoothstep(380.0,720.0,ip.y);',
  '  float gl=0.6+0.4*sin(t*0.55+n2*9.0);float edge=den*(1.0-den)*4.0;',
  '  vec3 smk=mix(vec3(0.3,0.12,0.45),vec3(0.78,0.42,1.0),den);',
  '  col=mix(col,smk,den*m*0.42);col+=vec3(0.72,0.3,1.0)*(edge*0.22+den*den*0.18)*m*gl;',
  '  col+=vec3(0.85,0.5,1.0)*motes(ip,t,92.0,0.32,4.5,11.0,3.0)*0.6*m;',
  '  return col;}',
  'void main(){',
  '  vec2 px=vec2(gl_FragCoord.x,uRes.y-gl_FragCoord.y);vec2 ip=px*uXf.xy+uXf.zw;',
  '  vec3 w=texture2D(uMap,ip/uSz).rgb;vec2 d=vec2(0.0);',
  '  if(w.r+w.g+w.b>0.002){',
  '    vec3 a=TAU*(uT/uPer+uPh)-(ip.x*0.004+ip.y*0.0025);',
  '    vec3 s=sin(a)*0.62+sin(a*1.73+1.1)*0.24+sin(a*0.41+2.3)*0.3;',
  '    float g=0.78+0.22*sin(TAU*uT/12.7+0.6)+0.16*sin(TAU*uT/6.1+1.9);',
  '    float dx=dot(w*uAmp,s)*g*uA;d=vec2(dx,-0.16*abs(dx));',
  '  }',
  '  vec3 col=texture2D(uImg,(ip-d)/uSz).rgb;',
  '  if(uLitOn>0.5){vec3 L=texture2D(uLit,ip/uSz).rgb;',
  '    if(L.r>0.004){float id=floor(L.g*255.0/16.0+0.5);float k=0.0;',
  '      for(int i=0;i<12;i++){if(abs(id-float(i))<0.5)k=uK[i];}',
  '      col*=1.0-L.r*L.b*k;}}',
  '  if(uFx>0.5&&uFx<1.5)col=divine(col,ip,uT);else if(uFx>1.5)col=abyss(col,ip,uT);',
  '  gl_FragColor=vec4(col,1.0);',
  '}'].join('\n');

// ライトの ゆらぎ（11/08 まさちゃん：08:59「じんわりって感じでゆっくり、よく見れば分かるくらい」・09:06「もう少し速度だけ上げて」・09:11「もう少しだけ光りの緩急つけて」）
//   ライトごとに ばらばらに：ゆっくり（2.8〜4秒）・すっと（1〜1.6秒：すっと 弱く なって ゆっくり 戻る）・2回（2〜2.8秒）の どれか。ちらちら しない（なめらか）。
//   弱く なるのは ライトの 光の 20〜40%（ランプの まん中で 8〜17%）。次まで 0.8〜7秒
function mkRand(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const FL = { rnd: mkRand(20261108), lamps: [] };
function flNext(L, t) {
  const r = FL.rnd, k = r();
  L.at = t + 0.8 + r() * 6.2;
  if (k < 0.4) { L.ty = 0; L.dur = 2.8 + r() * 1.2; L.sk = 0.45 + r() * 0.1; L.dep = 0.2 + r() * 0.1; }
  else if (k < 0.8) { L.ty = 1; L.dur = 1.0 + r() * 0.6; L.sk = 0.25 + r() * 0.1; L.dep = 0.28 + r() * 0.12; }
  else { L.ty = 2; L.dur = 2.0 + r() * 0.8; L.sk = 0.5; L.dep = 0.26 + r() * 0.1; }
}
const hump = (u, sk) => { const x = u < sk ? u / sk : 1 - (u - sk) / (1 - sk); return 0.5 - 0.5 * Math.cos(Math.PI * Math.max(0, Math.min(1, x))); };
for (let i = 0; i < 12; i++) { const L = {}; flNext(L, -FL.rnd() * 6); FL.lamps.push(L); }
function flK(t) {
  return FL.lamps.map((L, i) => {
    while (t > L.at + L.dur) flNext(L, L.at + L.dur);
    let k = 0.012 * (0.5 + 0.5 * Math.sin(t * 0.9 + i * 1.3));
    if (t >= L.at) {
      const u = (t - L.at) / L.dur;
      const e = L.ty === 2 ? (u < 0.45 ? hump(u / 0.45, 0.4) : 0.75 * hump((u - 0.45) / 0.55, 0.4)) : hump(u, L.sk);
      k += L.dep * e;
    }
    return k;
  });
}

  const AP = p => (typeof window !== 'undefined' && typeof window.TC_ASSET === 'function') ? window.TC_ASSET(p) : p;
  const loadImg = s => new Promise((ok, ng) => { const im = new Image(); im.onload = () => ok(im); im.onerror = () => ng(new Error('img ' + s)); im.src = AP(s); });
  function create(cv) {
    const gl = cv.getContext('webgl', { preserveDrawingBuffer: false, premultipliedAlpha: false, alpha: false, depth: true, antialias: true });
    if (!gl) return null;
    const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
    const PR = gl.createProgram(); gl.attachShader(PR, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(PR, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(PR);
    const QB = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, QB); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const LP = gl.getAttribLocation(PR, 'p'), U = n => gl.getUniformLocation(PR, n);
    const T = [gl.createTexture(), gl.createTexture(), gl.createTexture()];
    function up(unit, im, raw) {
      gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, T[unit]);
      gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, raw ? gl.NONE : gl.BROWSER_DEFAULT_WEBGL);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, im);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, gl.BROWSER_DEFAULT_WEBGL);
    }
    let cur = null, lit = false, fxn = 0, t0 = null, loading = null;
    async function setField(name) {             // 背景を 入れかえる（時間帯・幻の馬・神様馬）
      if (cur === name) return; const want = name;
      const tod = ['morning', 'evening', 'night'].includes(name) ? name : null;
      const p = Promise.all([loadImg(`tc_field_${name}.webp`), loadImg(tod ? `tc_sway_${tod}.webp` : 'tc_sway_none.webp'), tod && tod !== 'morning' ? loadImg(`tc_light_${tod}.webp`) : Promise.resolve(null)]);
      loading = p; const [img, map, lmap] = await p;
      if (loading !== p) return;
      up(0, img, false); up(1, map, true); if (lmap) up(2, lmap, true);
      cur = want; lit = !!lmap; fxn = name === 'divine' ? 1 : name === 'abyss' ? 2 : 0; t0 = null;
    }
    function render(t, Z) {                       // Z：{ z, cx, cy }（ズーム・フィールドの px）
      if (!cur) { gl.clearColor(0.85, 0.72, 0.52, 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT); return; }
      if (t0 == null) t0 = t;
      const cw = gl.canvas.width, ch = gl.canvas.height, z = Z ? Z.z : 1, zx = Z ? Z.cx : CFG.w / 2, zy = Z ? Z.cy : CFG.h / 2, kz = cw / CFG.w * z;
      gl.viewport(0, 0, cw, ch); gl.useProgram(PR);
      gl.bindBuffer(gl.ARRAY_BUFFER, QB); gl.enableVertexAttribArray(LP); gl.vertexAttribPointer(LP, 2, gl.FLOAT, false, 0, 0);
      for (let i = 0; i < 3; i++) { gl.activeTexture(gl.TEXTURE0 + i); gl.bindTexture(gl.TEXTURE_2D, T[i]); }
      gl.uniform1i(U('uImg'), 0); gl.uniform1i(U('uMap'), 1); gl.uniform1i(U('uLit'), lit ? 2 : 1); gl.uniform1f(U('uLitOn'), lit ? 1 : 0);
      gl.uniform2f(U('uSz'), CFG.w, CFG.h); gl.uniform2f(U('uRes'), cw, ch); gl.uniform1f(U('uFx'), fxn);
      gl.uniform4f(U('uXf'), 1 / kz, 1 / kz, zx - cw / 2 / kz, zy - ch / 2 / kz);
      gl.uniform3fv(U('uAmp'), CFG.amp); gl.uniform3fv(U('uPer'), CFG.per); gl.uniform3fv(U('uPh'), CFG.ph);
      const ua = Math.min(1, (t - t0) / 1.2);
      gl.uniform1fv(U('uK'), flK(t)); gl.uniform1f(U('uT'), t); gl.uniform1f(U('uA'), ua * ua * (3 - 2 * ua));
      gl.disable(gl.BLEND); gl.disable(gl.DEPTH_TEST);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      gl.disableVertexAttribArray(LP);
    }
    return { gl, setField, render, get field() { return cur; } };
  }
  return { create, CFG, mkRand };
})();
