



(function () {
  'use strict';
  const TAU = Math.PI * 2;
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const smooth = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
  const lerp = (a, b, t) => a + (b - a) * t;
  const angDiff = (a, b) => { let d = (b - a) % TAU; if (d > Math.PI) d -= TAU; if (d < -Math.PI) d += TAU; return d; };

  
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
    'attribute vec3 aPos,aCol;attribute vec4 aNrm;attribute float aBone,aBone2,aBw,aCv;attribute vec2 aUV;uniform float uBlend;',       
    'uniform mat4 uB[18];uniform mat4 uV;uniform mat3 uR;uniform vec4 uP;uniform vec4 uEm;',     
    'varying vec3 vN,vC;varying vec3 vW;varying vec2 vUV;varying vec3 vR0,vR1,vR2;varying vec4 vP;varying float vAo,vCv,vB;',
    'void main(){float bw=aBw*uBlend;mat4 B=uB[int(aBone+0.5)]*(1.0-bw)+uB[int(aBone2+0.5)]*bw;vec4 w=B*vec4(aPos,1.0);vec4 q=uV*w;mat3 RB=uR*mat3(B);',
    '  gl_Position=vec4(uP.x+q.x,uP.y+q.y,0.5-q.z*uP.z,1.0);vN=RB*aNrm.xyz;vAo=aNrm.w;vCv=aCv*2.0-1.0;vB=aBone;vC=aCol;vW=w.xyz;vUV=aUV;vR0=RB[0];vR1=RB[1];vR2=RB[2];vP=vec4(aPos-uEm.xyz,abs(aBone-uEm.w)<0.5?1.0:0.0);}'].join('\n');
  const FS = [
    'precision highp float;varying vec3 vN,vC;varying vec3 vW;varying vec2 vUV;varying vec3 vR0,vR1,vR2;varying vec4 vP;varying float vAo,vCv,vB;',
    'uniform vec3 uSun,uSunC,uAmb,uFill;uniform float uA,uTexOn,uNrmOn,uLift;uniform sampler2D uTex,uNrm;',
    'uniform vec3 uSky,uGnd;uniform float uAoOn,uSm,uGrain,uCv,uDbg;',      
    'uniform vec3 uE0,uE1,uGc;uniform vec2 uGr;',       
    'float h(vec3 p){return fract(sin(dot(p,vec3(12.9898,78.233,37.719)))*43758.5453);}',
    'float vn3(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);',       
    '  return mix(mix(mix(h(i),h(i+vec3(1.0,0.0,0.0)),f.x),mix(h(i+vec3(0.0,1.0,0.0)),h(i+vec3(1.0,1.0,0.0)),f.x),f.y),',
    '    mix(mix(h(i+vec3(0.0,0.0,1.0)),h(i+vec3(1.0,0.0,1.0)),f.x),mix(h(i+vec3(0.0,1.0,1.0)),h(i+vec3(1.0,1.0,1.0)),f.x),f.y),f.z);}',
    'void main(){vec3 n=normalize(vN);',
    '  if(uNrmOn>0.5){vec3 nm=normalize(mat3(vR0,vR1,vR2)*(texture2D(uNrm,vUV).xyz*2.0-1.0));',     
    '    float sl=length(vN);vec3 ns=vN/max(sl,0.0001);n=normalize(mix(nm,ns,uSm*step(0.5,sl)*smoothstep(0.0,0.35,dot(nm,ns))));}',      
    '  else if(!gl_FrontFacing)n=-n;',
    '  float ds=dot(n,uSun);float d=mix(max(ds,0.0),max((ds+0.3)/1.3,0.0),0.55);',       
    '  float ao=uAoOn>0.5?mix(1.0,clamp(vAo,0.0,1.0),0.55):1.0;float gc=mix(0.8,1.0,smoothstep(0.0,0.42,vW.y));',      
    '  vec3 hemi=mix(uGnd,uSky,0.5+0.5*n.y);',      
    '  float rim=uTexOn>0.5?pow(1.0-abs(n.z),3.0)*0.16:pow(1.0-abs(n.z),2.0)*0.12;',
    '  vec3 hv=normalize(uSun+vec3(0.0,0.0,1.0));float sp=uTexOn>0.5?pow(max(dot(n,hv),0.0),24.0)*0.14:0.0;',      
    '  vec3 base=uTexOn>0.5?texture2D(uTex,vUV).rgb:vC;',     
    '  float g=uTexOn>0.5?1.0+uGrain*((vn3(vP.xyz*38.0)-0.5)+0.7*(vn3(vP.xyz*8.0+7.0)-0.5)):0.97+0.06*h(floor(vW*90.0));',   
    '  vec3 fd=normalize(vec3(-uSun.x,0.25,0.65));float fl=uTexOn>0.5?max(dot(n,fd),0.0)*0.22:0.0;',      
    '  float kk=uTexOn>0.5?1.12:1.0;',
    '  vec3 tn=uTexOn>0.5?mix(vec3(1.0),base/max(max(base.r,base.g),max(base.b,0.04)),0.65):vec3(1.0);',      
    '  float cr=max(vCv,0.0),cc=max(-vCv,0.0);float fold=1.0+uCv*(0.55*cr*(0.45+0.55*d)-0.25*cc);',      
    '  vec3 hv2=normalize(uSun+vec3(0.0,0.0,1.0));float sh=uTexOn>0.5?pow(max(dot(n,hv2),0.0),6.0)*0.07*uSm:0.0;',      
    '  vec3 c=base*(hemi*ao*gc+uSunC*d*kk*mix(1.0,ao,0.3)*gc+fl*uFill*ao+uLift)*g*fold+(rim*0.5+sp+sh)*uSunC*tn*ao;',      
    '  if(uTexOn>0.5){float mx=max(c.r,max(c.g,c.b));if(mx>0.8)c*=(0.8+0.2*(1.0-exp((0.8-mx)*5.0)))/mx;}',      
    '  if(uGr.y>0.0){float e=min(length(vP.xyz-uE0),length(vP.xyz-uE1))/uGr.x;',       
    '    float gg=(1.0-smoothstep(0.55,1.35,e))*vP.w*uGr.y;float co=1.0-smoothstep(0.0,0.6,e);',
    '    c=mix(c,mix(uGc,vec3(1.0,0.98,0.94),co*0.6),clamp(gg,0.0,1.0));}',
    '  if(uDbg>0.5)c=vec3(fract(vB*0.37+0.1),fract(vB*0.61+0.3),fract(vB*0.83+0.5));',      
    '  gl_FragColor=vec4(c*uA,uA);}'].join('\n');
  const SVS = 'attribute vec2 p;uniform vec4 uE;varying vec2 v;void main(){v=p;gl_Position=vec4(uE.x+p.x*uE.z,uE.y+p.y*uE.w,0.0,1.0);}';
  const SFS = 'precision mediump float;varying vec2 v;uniform float uO;void main(){float r=length(v);float a=uO*(1.0-smoothstep(0.35,1.0,r));gl_FragColor=vec4(0.0,0.0,0.0,a);}';
  const GFS = 'precision mediump float;varying vec2 v;uniform vec3 uGc;uniform float uGk;void main(){float r=length(v);float a=exp(-r*r*5.0)*(1.0-smoothstep(0.75,1.0,r));float co=exp(-r*r*45.0);' +
    'vec3 c=uGc*a*1.15+vec3(1.0,0.97,0.92)*co*0.7;gl_FragColor=vec4(c*uGk,a*uGk*0.4);}';
  
  
  const PFS = 'precision mediump float;varying vec2 v;uniform sampler2D uT;uniform vec3 uTint;void main(){vec4 c=texture2D(uT,vec2(v.x*0.5+0.5,0.5-v.y*0.5));gl_FragColor=vec4(c.rgb*uTint*c.a,c.a);}';
  const EYE_GLOW = { purple: [0.78, 0.36, 1.0], gold: [1.0, 0.78, 0.25] };

  function prog(gl, vs, fs) {
    const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
    const p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    return p;
  }

  
  
  
  const bump = (x, p) => Math.pow(Math.max(0, Math.sin(Math.PI * clamp(x, 0, 1))), p);     
  function legAngles(ph, g, front, amp) {
    ph = ((ph % 1) + 1) % 1; amp = amp == null ? 1 : amp;
    const A = g.A * amp, lift = 0.4 + 0.6 * Math.min(1, amp);
    let u, k, f;
    if (ph < g.st) {                                  
      const x = ph / g.st;
      u = A - 2 * A * x;
      k = 0; f = 0;                                   
    } else {                                          
      const x = (ph - g.st) / (1 - g.st), m = -2 * A / g.st * (1 - g.st), x2 = x * x, x3 = x2 * x;
      u = -A + 2 * A * (3 * x2 - 2 * x3) + m * (2 * x3 - 3 * x2 + x);
      k = -g.K * lift * bump(x + 0.4 * x * (1 - x), 2);      
      f = -g.F * lift * bump(x + 0.6 * x * (1 - x), 2);      
    }
    if (!front) k *= 0.85;
    return [u, k, f];
  }
  const GAITS = {
    walk: { T: 1.3, st: 0.62, A: 0.22, K: 0.55, F: 0.45, ph: { HL: 0, FL: 0.25, HR: 0.5, FR: 0.75 }, bob: 0.012, pitch: 0.01, nod: 0.045 },      
    run: { T: 0.5, st: 0.38, A: 0.5, K: 1.3, F: 1.0, ph: { HL: 0, HR: 0.1, FL: 0.52, FR: 0.62 }, bob: 0.028, pitch: 0.045, nod: 0.12 },      
  };
  const DEEP_N = 0.22, DEEP_H = 0.1;                 
  const RUN_V = 7.5;                                  
  
  
  
  
  
  
  const WALK = {
    T: 1.2, stride: 1.4,
    touch: { HL: 0, FL: 0.258, HR: 0.5, FR: 0.758 },
    F: { beta: 0.70, piv: [-0.03, 1.45], c: -0.07, lift: 0.1, peak: 0.36, bo: 0.55, boLen: 0.12, land: 0.15, landLen: 0.10, flex: 1.35, fpeak: 0.3, bend: 1 },
    H: { beta: 0.73, piv: [-0.08, 1.36], c: -0.07, lift: 0.07, peak: 0.42, bo: 0.5, boLen: 0.12, land: 0.10, landLen: 0.08, flex: 0.8, fpeak: 0.32, bend: -1 },
    nod: 0.05, pitch: 0.0, roll: 0.025, tail: 0.12, drop: 0.02, slide: 0.11, neck: 0.16,
  };
  
  
  
  
  
  
  const RUN = {
    T: 0.55,
    touch: { HR: 0, HL: 0.07, FR: 0.32, FL: 0.47 },
    F: { beta: 0.29, c: 0.12, lift: 0.42, peak: 0.34, bo: 0.8, boLen: 0.1, land: 0.2, landLen: 0.1, flex: 2.6, fpeak: 0.3, bend: 1, back: 0.12, reach: 0.38 },
    H: { beta: 0.27, c: -0.06, lift: 0.24, peak: 0.55, bo: 0.7, boLen: 0.1, land: 0.12, landLen: 0.08, flex: 1.5, fpeak: 0.42, bend: -1, back: 0.38, reach: 0.12 },
    pitch: 0.07, nod: 0.16, bob: 0.03, drop: 0.05, slide: 0.16, tail: 0.25,
  };
  
  function walkOf(h) {
    if (h.walk) return h.walk;
    const hv = h.opt.heavy != null ? h.opt.heavy : ((h.opt.stage || 1) > 1.3 ? 1 : 0), W = JSON.parse(JSON.stringify(WALK));
    W.T *= 1 + 0.32 * hv; W.stride *= 1 + 0.06 * hv; W.nod *= 1 + 0.7 * hv; W.roll *= 1 + 1.4 * hv; W.neck += 0.08 * hv; W.drop += 0.012 * hv; W.tail *= 1 + 0.5 * hv;
    W.F.lift *= 1 - 0.3 * hv; W.H.lift *= 1 - 0.25 * hv; W.F.flex *= 1 - 0.2 * hv;
    W.heavy = hv; h.walk = W; return W;
  }
  
  function walkSpeed(h, e, w) {
    const W = walkOf(h), a = (0.5 + 0.5 * e) * (w == null ? 1 : w), c = 0.7 + 0.3 * e;
    return W.stride * a * c / W.T;
  }
  const rot2 = (a, v) => [Math.cos(a) * v[0] - Math.sin(a) * v[1], Math.sin(a) * v[0] + Math.cos(a) * v[1]];
  
  const peakBump = (x, pk) => { x = clamp(x, 0, 1); const p = 2.2, q = p * (1 - pk) / pk; return Math.pow(x, p) * Math.pow(1 - x, q) / (Math.pow(pk, p) * Math.pow(1 - pk, q)); };
  
  function ik2(P, Q, L1, L2, bend) {
    const dx = Q[0] - P[0], dy = Q[1] - P[1], d = Math.hypot(dx, dy), base = Math.atan2(dy, dx);
    const dm = clamp(d, Math.abs(L1 - L2) + 1e-6, (L1 + L2) * 0.999999);
    const A = Math.acos(clamp((L1 * L1 + dm * dm - L2 * L2) / (2 * L1 * dm), -1, 1));
    const a1 = base + bend * A, kx = P[0] + L1 * Math.cos(a1), ky = P[1] + L1 * Math.sin(a1);
    return { a1, a2: Math.atan2(Q[1] - ky, Q[0] - kx), short: d - (L1 + L2) };
  }
  
  function stanceFoot(lg, g, phi, A, S, xc0, gnd) {
    const xc = xc0 + S * (0.5 - phi / g.beta);        
    const bs = g.beta - g.boLen; let th = 0, pv = lg.cen;
    if (phi < g.landLen) { th = g.land * A * Math.pow(1 - phi / g.landLen, 2); pv = lg.heel; }        
    else if (phi > bs) { th = -g.bo * A * Math.pow((phi - bs) / g.boLen, 2); pv = lg.toe; }          
    const gx = xc + pv[0] - lg.cen[0], r = rot2(th, pv);
    return [[gx - r[0], gnd(gx) - r[1]], th];
  }
  
  
  const slideOf = (lg, Fp, m) => { const x = Math.hypot(Fp[0] - lg.P[0], Fp[1] - lg.P[1]) - (lg.L1 + lg.L2); return m * Math.tanh(x / m); };
  
  function walkLeg(lg, g, phi, A, S, gnd, msl) {
    const xc0 = lerp(lg.restC, lg.P[0] + lg.cen[0] + g.c, Math.min(1, A));       
    let Fp, th, sl; const stance = phi < g.beta;
    if (stance) { [Fp, th] = stanceFoot(lg, g, phi, A, S, xc0, gnd); sl = slideOf(lg, Fp, msl); }
    else {
      const s = (phi - g.beta) / (1 - g.beta), e = 1e-3, sw = 1 - g.beta;
      const [F0, t0] = stanceFoot(lg, g, g.beta - 1e-6, A, S, xc0, gnd), [F0b] = stanceFoot(lg, g, g.beta - e, A, S, xc0, gnd);
      const [F1, t1] = stanceFoot(lg, g, 0, A, S, xc0, gnd), [F1b] = stanceFoot(lg, g, e, A, S, xc0, gnd);
      const m0 = [(F0[0] - F0b[0]) / e * sw, (F0[1] - F0b[1]) / e * sw], m1 = [(F1b[0] - F1[0]) / e * sw, Math.min(0, (F1b[1] - F1[1]) / e * sw)];      
      const s2 = s * s, s3 = s2 * s, h00 = 2 * s3 - 3 * s2 + 1, h10 = s3 - 2 * s2 + s, h01 = -2 * s3 + 3 * s2, h11 = s3 - s2;
      const up = smooth(s / g.peak) * (1 - smooth((s - 0.72) / 0.28));          
      
      const ex = (g.back ? -g.back * A * peakBump(s, 0.3) : 0) + (g.reach ? g.reach * A * peakBump(s, 0.7) : 0);
      Fp = [h00 * F0[0] + h10 * m0[0] + h01 * F1[0] + h11 * m1[0] + ex, h00 * F0[1] + h10 * m0[1] + h01 * F1[1] + h11 * m1[1] + g.lift * A * up];
      const sl0 = slideOf(lg, F0, msl), sl1 = slideOf(lg, F1, msl); sl = lerp(sl0, sl1, smooth(s));
      
      const P0 = [lg.P[0], lg.P[1] - sl0], P1 = [lg.P[0], lg.P[1] - sl1], Pc = [lg.P[0], lg.P[1] - sl];
      const k0 = ik2(P0, F0, lg.L1, lg.L2, g.bend), k1 = ik2(P1, F1, lg.L1, lg.L2, g.bend), kc = ik2(Pc, Fp, lg.L1, lg.L2, g.bend);
      const r0 = t0 - angDiff(lg.a2r, k0.a2), r1 = t1 - angDiff(lg.a2r, k1.a2);
      th = lerp(t0, t1, smooth(s / 0.78)) - g.flex * A * peakBump(s, g.fpeak);       
    }
    const Ps = [lg.P[0], lg.P[1] - sl], k = ik2(Ps, Fp, lg.L1, lg.L2, g.bend);
    const au = angDiff(lg.a1r, k.a1), ak = angDiff(lg.a2r, k.a2) - au, af = th - au - ak;
    const dP = [lg.P[0] - lg.U[0], lg.P[1] - lg.U[1]], rP = rot2(au, dP);
    return { au, ak, af, tr: [dP[0] - rP[0], dP[1] - rP[1] - sl], short: stance ? k.short : -1 };
  }
  
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
  
  
  function gaitBody(h, G, p, A, sweep, off, wgt) {
    const bh = h.bones[0].head, out = {};
    
    let drop = G.drop * Math.min(1, A);
    for (let it = 0; it < 3; it++) {
      const oy = off[1] - drop, cp = Math.cos(off[3] || 0), sp = Math.sin(off[3] || 0);
      const gnd = x => bh[1] - (bh[1] + oy + (x - bh[0]) * sp) / cp;
      let need = 0;
      for (const L of ['FL', 'FR', 'HL', 'HR']) {
        const lg = h.legs[L]; if (!lg) continue;
        const g = G[L[0]], phi = ((p - G.touch[L]) % 1 + 1) % 1;
        out[L] = walkLeg(lg, g, phi, A, sweep(g), gnd, G.slide);
        const rp = smooth(phi / 0.12) * smooth((g.beta - phi) / 0.08);       
        need = Math.max(need, out[L].short * rp);
      }
      if (need <= 1e-4) break;
      drop += need * 1.02;                            
    }
    off[1] -= drop * wgt;
    return out;
  }

  
  
  
  
  
  const FOLD_F = [1.33, -1.52, -2.0], FOLD_H = [-1.36, 1.55, 1.75];      
  const XE = 0.22;            
  
  const LIE_DEF = {   
    gather: { p: -0.04, x: 0, d: 0.04, legs: { FL: ['rest', 0], FR: ['rest', 0], HL: ['rest', 0], HR: ['rest', 0] }, neck: -0.45, head: -0.25, tail: 0 },
    bend: { p: -0.07, x: 0.01, d: 0.06, legs: { FL: ['rest', 0], FR: ['rest', 0], HL: ['rest', 0], HR: ['rest', 0] }, neck: -0.42, head: -0.25, tail: -0.05 },
    fold1: { p: -0.1, x: 0.03, legs: { FL: ['abs', [0.12, -0.75, -1.45]], FR: ['rest', 0], HL: ['rest', 0], HR: ['rest', 0] }, neck: -0.4, head: -0.24, tail: -0.03 },      
    knee1: { p: -0.1, x: 0.0, contact: 'lowF', legs: { FL: ['abs', [0.02, -1.15, -1.65]], FR: ['abs', [0.08, -0.9, -1.55]], HL: ['rest', 0], HR: ['rest', 0] }, neck: -0.38, head: -0.22, tail: 0 },
    kneel: { p: -0.13, x: -0.04, contact: 'kneeF', legs: { FL: ['abs', [0.02, -1.5, -1.8]], FR: ['abs', [0.06, -1.5, -1.8]], HL: ['rest', 0], HR: ['rest', 0] }, neck: -0.35, head: -0.2, tail: 0 },      
    settle: { p: -0.07, x: -0.06, contact: 'kneeF', legs: { FL: ['abs', [0.7, -1.52, -1.95]], FR: ['abs', [0.66, -1.5, -1.95]], HL: ['abs', [-0.75, 0.95, 1.1]], HR: ['abs', [-0.72, 0.92, 1.05]] }, neck: -0.3, head: -0.18, tail: -0.15 },      
    down: { p: -0.02, x: 0.0, contact: 'low', legs: { FL: ['abs', FOLD_F], FR: ['abs', [1.3, -1.5, -2.0]], HL: ['abs', FOLD_H], HR: ['abs', [-1.33, 1.52, 1.7]] }, neck: -0.3, head: -0.15, tail: -0.3 },
    rest: { p: 0.04, x: 0, r: 0.05, contact: 'low', legs: { FL: ['abs', FOLD_F], FR: ['abs', [1.3, -1.5, -2.0]], HL: ['abs', FOLD_H], HR: ['abs', [-1.33, 1.52, 1.7]] }, neck: 0.04, head: -0.1, tail: -0.35, tailY: 0.35 },      
    liftK: { p: 0.18, x: 0.02, r: 0.07, contact: 'lowH', legs: { FL: ['abs', [1.6, -0.8, -1.2]], FR: ['abs', [1.5, -0.95, -1.35]], HL: ['abs', FOLD_H], HR: ['abs', [-1.33, 1.52, 1.7]] }, neck: 0.25, head: 0.06, tail: -0.3, tailY: 0.15 },      
    liftF: { p: 0.3, x: 0.03, r: 0.05, contact: 'lowH', legs: { FL: ['abs', [1.55, 0.2, 0.45]], FR: ['abs', [1.45, 0.05, 0.35]], HL: ['abs', FOLD_H], HR: ['abs', [-1.33, 1.52, 1.7]] }, neck: 0.28, head: 0.08, tail: -0.3, tailY: 0.1 },
    frontOut: { p: 0.42, x: 0.0, contact: 'lowH', legs: { FL: ['rest', XE], FR: ['rest', XE], HL: ['abs', [-1.2, 1.55, 1.75]], HR: ['abs', [-1.15, 1.5, 1.7]] }, neck: 0.2, head: 0.02, tail: -0.35, tailY: 0.1 },
    dogSit: { p: 0.55, x: 0.14, contact: 'lowH', legs: { FL: ['rest', XE], FR: ['rest', XE], HL: ['abs', [-0.85, 1.5, 1.7]], HR: ['abs', [-0.8, 1.45, 1.65]] }, neck: 0.1, head: -0.05, tail: -0.4 },
    hindPush: { p: 0.16, x: 0.23, d: 0.22, legs: { FL: ['rest', XE], FR: ['rest', XE], HL: ['rest', XE], HR: ['rest', XE] }, neck: 0.05, head: -0.05, tail: -0.12 },
    standUp: { p: 0, x: XE, d: 0, legs: { FL: ['rest', XE], FR: ['rest', XE], HL: ['rest', XE], HR: ['rest', XE] }, neck: 0, head: 0, tail: 0 },
  };
  
  const LIE_SEQ = [[0, 'stand'], [0.18, 'gather'], [0.33, 'bend'], [0.43, 'fold1'], [0.54, 'knee1'], [0.64, 'kneel'], [0.75, 'settle'], [0.87, 'down'], [1, 'rest']];      
  const LIE_DUR = 4.6, RISE_DUR = 1.7, POOP_DUR = 3.4;      
  const RISE_SEQ = [[0, 'rest'], [0.12, 'liftK'], [0.24, 'liftF'], [0.4, 'frontOut'], [0.58, 'dogSit'], [0.8, 'hindPush'], [1, 'standUp']];      
  const KCH = ['d', 'p', 'x', 'r', 'neck', 'head', 'tail', 'tailY', 'nf'];      
  function buildLieKeys(bones, probe) {      
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
    
    const ikToe = (L, p, d, x, T, af) => {
      const S = SEG[L], P = tf(p, d, x, S.u), L1 = len(S.segs[0]), L2 = len(S.segs[1]), L3 = len(S.segs[2]), dv3 = dirv(af);
      const F = [T[0] - L3 * dv3[0], T[1] - L3 * dv3[1]], D = [F[0] - P[0], F[1] - P[1]], bend = L[0] === 'H' ? -1 : 1;
      const dist = clamp(len(D), Math.abs(L1 - L2) + 1e-3, L1 + L2 - 1e-3);
      const a1 = Math.acos(clamp((L1 * L1 + dist * dist - L2 * L2) / (2 * L1 * dist), -1, 1)), Au = ang(D) + bend * a1, dv = dirv(Au);
      return [Au, ang([F[0] - P[0] - L1 * dv[0], F[1] - P[1] - L1 * dv[1]]), af];
    };
    const REST = {}; for (const L in SEG) REST[L] = SEG[L].segs.map(ang);
    const rel = (L, A, p) => { const r = REST[L], c = [A[0] - r[0], A[1] - r[1], A[2] - r[2]]; return [c[0] - p, c[1] - c[0], c[2] - c[1]]; };
    
    
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
          if (k.contact === 'kneeF') { if (L[0] === 'F') m = Math.min(m, GEO ? geoLow(L, lg[L], p, d, 1) - TG : pts[1][1] - T0); }      
          else if (k.contact === 'lowH') { if (L[0] === 'H') pts.slice(1).forEach(q => { m = Math.min(m, q[1] - T0); }); }
          else if (k.contact === 'lowF') { if (L[0] === 'F') { if (GEO) m = Math.min(m, geoLow(L, lg[L], p, d, 0) - TG); else pts.slice(1).forEach(q => { m = Math.min(m, q[1] - T0); }); } }
          else pts.slice(1).forEach(q => { m = Math.min(m, q[1] - T0); });
        }
        if (k.contact === 'low') for (let i = 0; i < 6; i++) m = Math.min(m, tf(p, d, x, [-0.8 + 0.22 * i, belly])[1] - 0.02);     
        return m;
      };
      let lo = -0.2, hi = 1.4;
      for (let it = 0; it < 50 && k.d == null; it++) { const mid = (lo + hi) / 2; if (low(mid) > 0) lo = mid; else hi = mid; }
      
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
    const legPts = (L, a, lvMin) => {       
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
    const lowOf = (L, a, lvMin) => {        
      let m = 1e9;
      for (const q of legPts(L, a, lvMin)) { const u = q[0] - G.bx, v = q[1] - G.by, y = G.by + sn * u + c * v - k.d; if (y < m) m = y; }
      return m;
    };
    const U = h.under;
    const into = (L, a) => {                
      if (!U) return -1; let m = -1;
      for (const q of legPts(L, a, 1)) { const j = Math.floor((q[0] - U.x0) / U.dx); if (j >= 0 && j < U.y.length) m = Math.max(m, q[1] - (U.y[j] - 0.015)); }
      return m;
    };
    let lowY = 1e9;
    for (const L of ['FL', 'FR', 'HL', 'HR']) {
      const a = k[L].slice(), flex = L[0] === 'F' ? -1 : 1, in0 = Math.max(0, into(L, a)) + 0.002;
      
      
      const nMax = Math.round(150 * (L[0] === 'F' ? 1 - clamp(k.nf || 0, 0, 1) : 1));
      for (let i = 0; i < nMax && lowOf(L, a, 1) < -0.006; i++) { a[1] += 0.01 * flex; if (into(L, a) > in0) { a[1] -= 0.01 * flex; break; } }
      for (let i = 0; i < 200 && lowOf(L, a, 2) < -0.006; i++) { a[2] -= 0.01; if (into(L, a) > in0) { a[2] += 0.01; break; } }      
      k[L] = a; lowY = Math.min(lowY, lowOf(L, a, 0));
    }
    if (lowY < -0.006) k.d -= -0.006 - lowY;          
    if (h.tailTip) {            
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
      for (const c of ['tx', 'ty', 'af']) {                       
        const a = K(i)[c][L], b = K(i + 1)[c][L];
        o[c][L] = a == null ? b : b == null ? a : a + (b - a) * smooth(s);
      }
    });
    return o;
  }

  
  
  
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
    const side = L => (L === 'FL' || L === 'HL' ? -1 : 1) * (Math.sign(topZ[L] || 0) || 1) * (L === 'FL' || L === 'HL' ? -1 : 1);      
    const out = sp.topOut || 0;          
    const dzLeg = (L, y) => {
      if (topY[L] == null) return 0;
      const u = clamp((topY[L] - y) / Math.max(0.1, topY[L]), 0, 1), e = u * u * (3 - 2 * u);
      const want = sp.hoofZ && sp.hoofZ[L] != null ? sp.hoofZ[L] : hoofZ[L] * kB;
      return (1 - e) * (topZ[L] * (kB - 1) + side(L) * out) + e * (want - hoofZ[L]);
    };
    const topX = {}; for (const L in topY) topX[L] = bones[bi[L + '_u']].head[0];
    const bodyOut = (x, y, z) => {       
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
      else if (b === nB && nh) { const u = clamp(Math.hypot(x - nh[0], y - nh[1]) / nL, 0, 1); dz = z * (kB - 1) * (1 - smooth(u / 0.55)); }      
      pos[i * 3 + 2] = z + dz;
    }
    bones.forEach((bo, k) => { const L = legOf[k]; if (L) bo.head = [bo.head[0], bo.head[1], bo.head[2] + dzLeg(L, bo.head[1])]; });
  }

  function mkTex(gl, img) {                
    const tx = gl.createTexture(); gl.activeTexture(gl.TEXTURE6); gl.bindTexture(gl.TEXTURE_2D, tx);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, img);
    gl.generateMipmap(gl.TEXTURE_2D);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    const an = gl.getExtension('EXT_texture_filter_anisotropic') || gl.getExtension('WEBKIT_EXT_texture_filter_anisotropic');
    if (an) gl.texParameterf(gl.TEXTURE_2D, an.TEXTURE_MAX_ANISOTROPY_EXT, Math.min(4, gl.getParameter(an.MAX_TEXTURE_MAX_ANISOTROPY_EXT)));
    gl.activeTexture(gl.TEXTURE0);
    return tx;
  }
  
  
  
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
      gl.uniform1f(h.loc.uBlend, 0); gl.uniformMatrix4fv(h.loc.uB, false, new Float32Array(pr.m));      
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
    const fmt2 = meta.fmt === 2;        
    const pos = buf('pos', Float32Array, nv * 3), bone = new Uint8Array(bin, lay.bone[0], nv);
    if (opt.stance) morphStance(meta, pos, bone, nv, opt.stance);      
    const nrm = fmt2 ? new Int8Array(bin, lay.nrm[0], nv * 4) : buf('nrm', Float32Array, nv * 3);
    const col = fmt2 ? null : new Uint8Array(bin, lay.col[0], nv * 3), uv = fmt2 ? new Uint16Array(bin, lay.uv[0], nv * 2) : null;
    const idx = meta.idx32 ? new Uint32Array(bin, lay.idx[0], meta.i) : new Uint16Array(bin, lay.idx[0], meta.i);
    if (meta.idx32) gl.getExtension('OES_element_index_uint');
    const mk = (data, target) => { const b = gl.createBuffer(); gl.bindBuffer(target || gl.ARRAY_BUFFER, b); gl.bufferData(target || gl.ARRAY_BUFFER, data, gl.STATIC_DRAW); return b; };
    const bone2 = lay.bone2 ? new Uint8Array(bin, lay.bone2[0], nv) : bone, bwt = lay.bw ? new Uint8Array(bin, lay.bw[0], nv) : new Uint8Array(nv);
    const cvb = lay.cv ? new Uint8Array(bin, lay.cv[0], nv) : null;      
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
    
    let under = null;
    if (bi.body != null) {
      let x0 = 1e9, x1 = -1e9; for (let i = 0; i < nv; i++) if (bone[i] === bi.body) { x0 = Math.min(x0, pos[i * 3]); x1 = Math.max(x1, pos[i * 3]); }
      const dx = 0.05, n = Math.max(1, Math.ceil((x1 - x0) / dx)), y = new Array(n).fill(1e9);
      for (let i = 0; i < nv; i++) if (bone[i] === bi.body) { const j = Math.min(n - 1, Math.floor((pos[i * 3] - x0) / dx)); if (pos[i * 3 + 1] < y[j]) y[j] = pos[i * 3 + 1]; }
      under = { x0, dx, y };
    }
    let tailTip = null, tailProbe = null;
    if (bi.tail != null) {
      const isT = b => b === bi.tail || (bi.tail2 != null && b === bi.tail2);      
      const th = bones[bi.tail].head; let my = 1e9; for (let i = 0; i < nv; i++) if (isT(bone[i]) && pos[i * 3 + 1] < my) { my = pos[i * 3 + 1]; tailTip = [pos[i * 3] - th[0], pos[i * 3 + 1] - th[1]]; }
      tailProbe = [];
      for (let dI = 0; dI < 12; dI++) {          
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
    
    const eyes = meta.eyes && meta.eyes.length === 2 && bi.head != null ? meta.eyes : null;
    const em = eyes ? [0, 1, 2].map(k => (eyes[0].p[k] + eyes[1].p[k]) / 2) : [0, 0, 0];
    const glow = opt.eyeGlow ? (typeof opt.eyeGlow === 'string' ? EYE_GLOW[opt.eyeGlow] : opt.eyeGlow) : null;
    
    const anchors = {};
    const pick = (bs, score, frac) => {          
      const cand = []; for (let i = 0; i < nv; i++) if (bs.includes(bone[i])) cand.push([score(pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]), i]);
      if (!cand.length) return null; cand.sort((a, b) => b[0] - a[0]); const n = Math.max(1, Math.floor(cand.length * frac)); let x = 0, y = 0, z = 0;
      for (let k = 0; k < n; k++) { const i = cand[k][1]; x += pos[i * 3]; y += pos[i * 3 + 1]; z += pos[i * 3 + 2]; } return [x / n, y / n, z / n];
    };
    const hb = [bi.head, bi.jaw].filter(v => v != null), nb = [bi.neck].filter(v => v != null), bb = [bi.body].filter(v => v != null);
    if (hb.length) { anchors.nose = { b: bi.head, p: pick(hb, (x) => x, 0.03) }; anchors.poll = { b: bi.head, p: pick(hb, (x, y) => y, 0.03) }; }
    if (eyes) anchors.eye = { b: bi.head, p: em.slice() };
    else if (anchors.nose && anchors.nose.p && anchors.poll && anchors.poll.p) anchors.eye = { b: bi.head, p: [0, 1, 2].map(k => anchors.poll.p[k] + (anchors.nose.p[k] - anchors.poll.p[k]) * 0.42) };      
    if (nb.length) anchors.neck = { b: bi.neck, p: pick(nb, (x, y) => y + 0.3 * x, 0.25) };
    if (bb.length) {
      let x0 = 1e9, x1 = -1e9; for (let i = 0; i < nv; i++) if (bone[i] === bi.body) { x0 = Math.min(x0, pos[i * 3]); x1 = Math.max(x1, pos[i * 3]); }
      const at = (fx) => pick(bb, (x, y, z) => y - 4 * Math.abs(x - (x0 + (x1 - x0) * fx)) - 0.5 * Math.abs(z), 0.03);
      anchors.withers = { b: bi.body, p: at(0.78) }; anchors.back = { b: bi.body, p: at(0.5) }; anchors.rump = { b: bi.body, p: at(0.18) };
    }
    const samp = []; for (let i = 0; i < nv; i += 7) samp.push(i);          
    const sampP = new Float32Array(samp.length * 3), sampB = new Uint8Array(samp.length);
    samp.forEach((i, k) => { sampP[k * 3] = pos[i * 3]; sampP[k * 3 + 1] = pos[i * 3 + 1]; sampP[k * 3 + 2] = pos[i * 3 + 2]; sampB[k] = bone[i]; });
    return { sampP, sampB, anchors, gl, P, S, G, B, loc, bones, bi, meta, H, legLen, opt, lie: buildLieKeys(bones, probe), tailTip, tailProbe, probe, under, tex, ntex, fmt2, eyes, em, eyeR: meta.eye_r || 0.02, glow, legs, hoof, PS,
      poopTex: (opt.poopImgs || []).map(im => { const t = gl.createTexture(); gl.activeTexture(gl.TEXTURE5); gl.bindTexture(gl.TEXTURE_2D, t); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, im);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE); gl.activeTexture(gl.TEXTURE0); return { t, w: im.width, h: im.height }; }) };      
  }

  
  function boneMats(h, rot, bodyOff, trs) {
    const out = new Array(h.bones.length);
    h.bones.forEach((b, i) => {
      const r = rot[b.name] || [0, 0], q = trs && trs[b.name];
      let local = M.mul(M.tr(b.head[0], b.head[1], b.head[2]), M.mul(M.mul(M.ry(r[1] || 0), M.rz(r[0] || 0)), M.tr(-b.head[0], -b.head[1], -b.head[2])));
      if (q) local = M.mul(M.tr(q[0], q[1], q[2] || 0), local);
      if (b.parent < 0) {              
        const e = bodyOff[4] || 0, sc = M.sc(1 + e, 1 + e * 0.6, 1 + e);
        local = M.mul(M.tr(bodyOff[0], bodyOff[1], bodyOff[2]), M.mul(M.tr(b.head[0], b.head[1], b.head[2]), M.mul(M.rz(bodyOff[3] || 0), M.mul(M.rx(bodyOff[5] || 0), M.mul(sc, M.tr(-b.head[0], -b.head[1], -b.head[2]))))));
      }
      out[i] = b.parent < 0 ? local : M.mul(out[b.parent], local);
    });
    return out;
  }

  
  
  function legIK(h, set, p, d, x, f) {
    const G = h.lie.geo;
    for (const L of ['FL', 'FR', 'HL', 'HR']) {
      const S = G.SEG[L]; if (!S) continue; const [dx, dy, da] = f(L);
      const R = G.rel(L, G.ikToe(L, p, d, x, [S.toe[0] + dx, S.toe[1] + dy], 0.25 + da), p);
      set(L + '_u', R[0]); set(L + '_k', R[1]); set(L + '_f', R[2]);
    }
  }
  
  function pose(h, st, t) {
    const rot = {}, off = [0, 0, 0, 0, 0, 0];
    const set = (n, a, b) => { rot[n] = [(rot[n] ? rot[n][0] : 0) + a, (rot[n] ? rot[n][1] : 0) + (b || 0)]; };
    
    const br = Math.sin(TAU * t / (st.mode === 'sleep' ? 4.2 : 3.1));
    off[4] = 0.006 * br * (st.mode === 'sleep' ? 2.2 : 1);
    set('tail', 0.04 * Math.sin(TAU * t / 2.7) + st.tailFlick, 0.18 * Math.sin(TAU * t / 3.9 + 1) + 0.25 * st.tailFlick);
    if (h.bi.tail2 != null && !(st.sl > 0.001)) set('tail2', 0.03 * Math.sin(TAU * t / 2.7 - 0.8), 0.14 * Math.sin(TAU * t / 3.9 + 0.3) + 0.2 * st.tailFlick);     
    
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
    if (ww > 0.001 && h.legs && h.legs.FL) {         
      const W = walkOf(h), A = (st.wAmp || 1) * ww, p = st.phase.walk, k = 1 - wr, Am = Math.min(1, A);
      off[4] *= 1 - ww;                                         
      off[3] += -W.pitch * Am * k * Math.cos(TAU * 2 * p);      
      off[5] += W.roll * Am * k * Math.sin(TAU * (p - 0.11));      
      addLegs(gaitBody(h, W, p, A, g => W.stride * g.beta * A, off, k), k);
      set('neck', -W.nod * Am * k * Math.cos(TAU * 2 * (p - W.touch.FL)) - W.neck * ww * k); set('head', -W.nod * 0.35 * Am * k * Math.cos(TAU * 2 * (p - W.touch.FL) - 0.5) + W.neck * 0.45 * ww * k);      
      set('tail', 0, W.tail * Am * k * Math.sin(TAU * (p - 0.36))); set('tail2', 0.03 * Am * k * Math.sin(TAU * 2 * p), 1.2 * W.tail * Am * k * Math.sin(TAU * (p - 0.5)));
    }
    if (wr > 0.001 && h.legs && h.legs.FL) {         
      const p = st.phase.run, vr = Math.max(st.runV || 0, 0.01), cr = 0.8 + 0.2 * clamp(vr / RUN_V, 0, 1), Te = RUN.T / cr;
      const A = clamp(vr / RUN_V, 0.35, 1);
      off[4] *= 1 - wr;
      off[3] += RUN.pitch * A * wr * Math.sin(TAU * (p - 0.45));          
      off[1] += -RUN.bob * A * wr * (0.5 + 0.5 * Math.cos(TAU * (p - 0.45)));   
      addLegs(gaitBody(h, RUN, p, A, g => vr * g.beta * Te, off, wr), wr);
      set('neck', -RUN.nod * A * wr * Math.cos(TAU * (p - 0.5)) - 0.3 * wr); set('head', RUN.nod * 0.4 * A * wr * Math.cos(TAU * (p - 0.5) - 0.4) + 0.14 * wr);     
      
      const fl = smooth(clamp((vr - 1.5) / 4.5, 0, 1)) * wr;
      set('tail', -1.05 * fl + 0.1 * fl * Math.sin(TAU * (p - 0.15)), 0.1 * fl * Math.sin(TAU * (p - 0.1)));
      set('tail2', -0.3 * fl + 0.28 * fl * Math.sin(TAU * (p - 0.4)) + 0.08 * fl * Math.sin(TAU * 2 * p + 1.3), 0.16 * fl * Math.sin(TAU * (p - 0.35)));
    }
    if (st.upT != null && t - st.upT < 0.9) {          
      const u = (t - st.upT) / 0.9, e = Math.sin(Math.PI * u) * Math.pow(1 - u, 1.5);
      off[1] += 0.035 * e; set('neck', 0.22 * e); set('head', -0.08 * e);
    }
    if (h.bi.jaw != null) set('jaw', h.meta.jaw_close || 0);      
    if (st.poopE > 0.001) {                  
      const k = smooth(st.poopE); set('tail', -0.85 * k, 0); if (h.bi.tail2 != null) set('tail2', -0.35 * k); off[1] -= 0.015 * k;
    }
    
    for (const r of (st.reacts || [])) {
      const u = (t - r.t0) / r.dur; if (u < 0 || u > 1) continue;
      const e = smooth(clamp(u / 0.18, 0, 1)) * (1 - smooth(clamp((u - 0.78) / 0.22, 0, 1))), tt = t - r.t0;
      if (r.k === 'nuzzle') { set('neck', -0.16 * e); set('head', -0.12 * e + 0.07 * e * Math.sin(TAU * 1.5 * tt), 0.12 * e * (r.side || 1)); }            
      else if (r.k === 'swish') { set('tail', -0.25 * e, 0.75 * e * Math.sin(TAU * 1.3 * tt)); if (h.bi.tail2 != null) set('tail2', 0, 0.6 * e * Math.sin(TAU * 1.3 * tt - 0.9)); }      
      else if (r.k === 'stretch' && h.lie) {          
        
        const G = h.lie.geo, D = 0.3, st_ = (a, b) => smooth(clamp((u - a) / (b - a), 0, 1)), lf = (a, b) => { const q = clamp((u - a) / (b - a), 0, 1); return Math.sin(Math.PI * q); };
        const fw = { FL: st_(0.05, 0.19) - st_(0.8, 0.9), FR: st_(0.19, 0.33) - st_(0.88, 0.98), HL: 0, HR: 0 };
        const up = { FL: lf(0.05, 0.19) + lf(0.8, 0.9), FR: lf(0.19, 0.33) + lf(0.88, 0.98), HL: 0, HR: 0 };
        const sk = st_(0.35, 0.52) * (1 - st_(0.68, 0.8)), p = -0.06 * sk, d = 0.06 * sk + 0.01 * (up.FL + up.FR), x = -0.07 * sk;
        off[0] += x; off[1] -= d; off[3] += p;
        legIK(h, set, p, d, x, L => [D * fw[L], 0.12 * up[L], -1.0 * up[L]]);
        set('neck', -0.34 * sk - 0.06 * (up.FL + up.FR)); set('head', 0.24 * sk + 0.04 * Math.sin(TAU * 0.8 * tt) * sk); set('tail', -0.12 * sk);
      }
      else if (r.k === 'sneeze') { const j = Math.exp(-Math.pow((u - 0.45) / 0.06, 2)); set('neck', -0.05 * e - 0.18 * j); set('head', -0.3 * j); off[1] -= 0.012 * j; }          
      else if ((r.k === 'hop' || r.k === 'frisk') && h.lie) {      
        const per = r.k === 'hop' ? 0.56 : 0.48, ph = tt / per, k = e, hi = r.k === 'hop' ? 1 : 0.85;
        const sw = L => { const q = ((ph + (L === 'FL' || L === 'HR' ? 0 : 0.5)) % 1 + 1) % 1; return q < 0.56 ? Math.pow(Math.sin(Math.PI * q / 0.56), 1.3) : 0; };
        const bob = 0.03 * k * Math.abs(Math.sin(TAU * ph));                     
        off[1] += bob; off[3] += 0.03 * k;                                       
        legIK(h, set, 0.03 * k, -bob, 0, L => { const w = sw(L) * k * hi, f = L[0] === 'F'; return [(f ? 0.07 : -0.03) * w, (f ? 0.3 : 0.13) * w, (f ? -1.35 : -0.7) * w]; });
        set('neck', (0.12 + 0.05 * Math.sin(TAU * 2 * ph)) * k); set('head', -0.08 * k * Math.abs(Math.sin(TAU * ph)));
        set('tail', -0.45 * k, 0.32 * k * Math.sin(TAU * ph));
      }
      else if (r.k === 'tilt') { set('head', 0.1 * e, 0.38 * e * (r.side || 1)); set('neck', 0.05 * e, 0.1 * e * (r.side || 1)); }                  
      else if (r.k === 'nod') { set('neck', -0.17 * e * (0.5 + 0.5 * Math.sin(TAU * 1.6 * tt - 1.57))); set('head', -0.08 * e * Math.sin(TAU * 1.6 * tt)); }   
      else if (r.k === 'yawn') { const k = Math.sin(Math.PI * clamp(u * 1.15, 0, 1)); set('neck', 0.22 * k); set('head', 0.34 * k); off[4] += 0.01 * k; }          
      else if (r.k === 'sniff') { set('neck', -0.5 * e); set('head', -0.28 * e + 0.04 * e * Math.sin(TAU * 4.5 * tt), 0.15 * e * (r.side || 0)); }       
      else if (r.k === 'eat') { set('neck', -0.08 * e); set('head', 0.06 * e + 0.035 * e * Math.sin(TAU * 2.4 * tt), 0.1 * e * (r.side || 0)); }          
      else if (r.k === 'beg') { set('neck', 0.04 * e); set('head', 0.06 * e, 0.3 * e * (r.side || 1)); }                                          
      else if (r.k === 'happy') { const j = Math.max(0, Math.sin(TAU * 1.1 * tt)) * e; set('neck', 0.1 * j); set('head', -0.06 * j); set('tail', -0.2 * e, 0.55 * e * Math.sin(TAU * 1.6 * tt)); }  
      else if (r.k === 'shake') {          
        const j = Math.exp(-tt * 3.2) * smooth(clamp(tt / 0.08, 0, 1)), w = Math.sin(TAU * 4.6 * tt) * j;
        set('neck', 0.06 * e, 0.2 * w * (r.side || 1)); set('head', -0.05 * j * Math.abs(Math.sin(TAU * 4.6 * tt)), 0.34 * w * (r.side || 1)); off[5] += 0.012 * w;
      }
      else if (r.k === 'paw') {            
        const L = (r.side || 1) > 0 ? 'FR' : 'FL', ph = clamp((u - 0.12) / 0.76, 0, 1), lift = Math.sin(Math.PI * ph);
        set(L + '_u', (0.32 * Math.sin(TAU * ph * 1.5)) * lift + 0.18 * lift); set(L + '_k', 0.85 * lift); set(L + '_f', 0.5 * lift);
        set('neck', -0.08 * e); set('head', -0.05 * e);
      }
      else if (r.k === 'headup') { set('neck', 0.3 * e); set('head', -0.12 * e + 0.03 * e * Math.sin(TAU * 0.8 * tt), 0.08 * e * (r.side || 1)); }      
      else if (r.k === 'sway') { const w = Math.sin(TAU * tt / r.dur); off[5] += 0.03 * w * e; off[2] += 0.012 * w * e; set('neck', 0.04 * e, 0.12 * w * e); set('head', 0, 0.1 * w * e); }      
      else if (r.k === 'gather') { set('neck', -0.18 * e); set('head', 0.1 * e); off[1] -= 0.025 * e; off[3] -= 0.02 * e; set('tail', -0.15 * e); }      
      else if (r.k === 'calm') { const w = Math.sin(TAU * 0.35 * tt); set('neck', -0.14 * e + 0.02 * w * e); set('head', 0.04 * e, 0.22 * e * (r.side || 1)); off[5] += 0.02 * e * (r.side || 1); set('tail', 0, 0.25 * e * w); }      
      else if (r.k === 'deep') {           
        const d = r.ds && r.ds.length ? r.ds.reduce((a, s) => a + smooth(clamp((t - s) / 0.45, 0, 1)), 0) / r.ds.length : 0;
        const dn = r.dn != null ? r.dn : DEEP_N, dh = r.dh != null ? r.dh : DEEP_H;
        set('neck', (-0.1 - dn * d) * e); set('head', (-0.14 + dh * d) * e + 0.035 * e * Math.sin(TAU * 1.9 * tt));
      }      
      else if (r.k === 'lick') { const j = Math.sin(Math.PI * clamp((u - 0.2) / 0.6, 0, 1)); set('neck', -0.1 * e); set('head', 0.12 * j, 0.1 * j * (r.side || 1)); }      
      else if (r.k === 'nibble') { set('neck', -0.3 * e); set('head', -0.05 * e + 0.05 * e * Math.sin(TAU * 3.2 * tt), 0.2 * e * (r.side || 0)); }      
    }
    
    const gz = smooth(st.graze), lk = st.lookS || st.look;
    set('neck', -0.62 * gz + 0.05 * lk[1], 0.35 * lk[0]); set('head', -0.38 * gz + 0.04 * lk[1], 0.25 * lk[0]);
    if (gz > 0.5) set('head', 0.04 * Math.sin(TAU * t * 1.7) * smooth((gz - 0.5) * 2) * 0.5);     
    
    if (!h.lie) h.lie = buildLieKeys(h.bones, h.probe);
    
    const slE = lerp(st.sl, smooth(st.sl), 0.5), riE = Math.pow(st.rise, 1.3);
    const lieK = st.poseKey || (st.sl > 0.001 ? fixGround(h, plantLegs(h, st.rise > 0 ? keyAt(h.lie, RISE_SEQ, riE) : keyAt(h.lie, LIE_SEQ, slE))) : null);
    if (lieK) {
      off[0] += lieK.x; off[1] += -lieK.d; off[3] += lieK.p; off[5] = (off[5] || 0) + lieK.r;
      for (const L of ['FL', 'FR', 'HL', 'HR']) { set(L + '_u', lieK[L][0]); set(L + '_k', lieK[L][1]); set(L + '_f', lieK[L][2]); }
      set('neck', lieK.neck); set('head', lieK.head); set('tail', lieK.tail, lieK.tailY);
      const dz = smooth(st.doze || 0); set('neck', -0.26 * dz); set('head', -0.2 * dz);      
      if (st.flop != null) {             
        const k = smooth(clamp((st.sl - 0.8) / 0.2, 0, 1)) * (1 - smooth(clamp(st.rise * 2.5, 0, 1))), tt = t - st.flop;
        off[5] += 0.02 * Math.sin(TAU * 0.55 * tt) * k; set('neck', -0.08 * k + 0.04 * k * Math.sin(TAU * 0.4 * tt)); set('head', -0.08 * k, 0.12 * k);      
        set('tail', 0, 0.3 * k * Math.sin(TAU * 0.7 * tt));
      }
    }
    return boneMats(h, rot, off, trs);
  }

  
  
  const AREA = { cx: 526, cy: 1090, rx: 280, ry: 300 }, TRACK = { cx: 526, cy: 1070, rx: 400, ry: 410, n: 3.2 };
  
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
  function trackAt(sArc) {           
    const tp = trackPts(), N = tp.N; const s = ((sArc % tp.total) + tp.total) % tp.total;
    let lo = 0, hi = N; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (tp.L[m] <= s) lo = m; else hi = m; }
    const f = (s - tp.L[lo]) / ((tp.L[hi] - tp.L[lo]) || 1), a = tp.P[lo % N], b = tp.P[hi % N];
    const p0 = tp.P[(lo - 4 + N) % N], p1 = tp.P[(hi + 4) % N];        
    return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, Math.atan2((p1[1] - p0[1]) / 0.5, p1[0] - p0[0])];
  }
  function trackNear(x, y) {         
    const tp = trackPts(); let bi = 0, bd = 1e18;
    for (let i = 0; i < tp.N; i += 2) { const d = (tp.P[i][0] - x) ** 2 + ((tp.P[i][1] - y) / 0.5) ** 2; if (d < bd) { bd = d; bi = i; } }
    return [tp.L[bi], Math.sqrt(bd)];
  }     
  
  function pickWalkTarget(h, st, rnd) {
    const fits = (x, y) => { const sc = scaleAt(h, y), d = Math.atan2((y - st.y) / 0.5, x - st.x), hx = sc * (1.45 * Math.abs(Math.cos(d)) + 0.35); return x - hx >= 8 && x + hx <= 1044; };
    st.tgt = null;
    for (let k = 0; k < 30; k++) {
      const a = rnd() * TAU, r = Math.sqrt(rnd());
      const x = AREA.cx + Math.cos(a) * r * AREA.rx, y = AREA.cy + Math.sin(a) * r * AREA.ry;
      if (Math.hypot(x - st.x, (y - st.y) * 1.6) > 140 && fits(x, y)) { st.tgt = [x, y]; break; }
    }
    if (!st.tgt) {                     
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
    
    let special = null, fsec = 0;
    if (st.force && st.force.length) { const f = st.force.shift().split(':'); st._lastForce = f; special = f[0]; fsec = Number(f[1] || 0); }
    else if (rnd() < 1 / 30) special = 'special';
    st.forcedWalk = false;
    
    
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
    if (special === 'gallop') { st.mode = 'gallop'; st.until = t + 1e9; st.runV = st.runV || 0; return; }      
    if (special === 'walkto') { const f = st._lastForce; st.tgt = [Number(f[1]), Number(f[2])]; st.mode = 'walk'; st.until = t + 30; st.forcedWalk = true; return; }
    if (special === 'poop') { st.mode = 'idle'; st.until = t + (fsec || 4); st.want.graze = 0; st.want.look = [0, 0]; st.poopReq = true; return; }      
    if (special === 'idle' || special === 'graze' || special === 'look') {
      st.mode = 'idle'; st.until = t + (fsec || 5);
      st.want.graze = special === 'graze' ? 1 : 0; st.want.look = special === 'look' ? [0.7, -0.2] : [0, 0]; return;
    }
    if (special === 'special' || special === 'run' || special === 'sleep') {
      if (st.tod === 'night' && special !== 'run') { st.mode = 'sleep'; st.until = t + Math.max(9, fsec || 60); st.sleepT = t; st.sl = 0; st.rise = 0; st.doze = 0; st.lieDoneT = 0; return; }
      if (st.tod !== 'night' && special !== 'sleep' && (h.opt.stage || 1) > 1.4) {      
        st.mode = 'idle'; st.until = t + 6; st.want.graze = 0; st.want.look = [0.6, 0.35]; return;
      }
      if (st.tod !== 'night' && special !== 'sleep') {
        st.mode = 'run'; st.lap = 0; st.runV = 0; st.runEnd = 0; st.runT = 0; st.tPrev = null; st.toTrack = true; return;
      }
    }
    if (special === 'walk' || (!special && rnd() < 0.4)) {          
      pickWalkTarget(h, st, rnd);
      st.mode = 'walk'; st.until = t + 30; return;
    }
    
    st.mode = 'idle'; st.until = t + 5 + rnd() * 9;
    const k = rnd();
    st.want.graze = k < 0.35 ? 1 : 0;
    st.want.look = k >= 0.35 && k < 0.7 ? [(rnd() - 0.5) * 1.6, (rnd() - 0.5) * 0.8] : [0, 0];
  }
  
  function steer(st, target, dt, maxW, gain, resp, ff) {
    const w = clamp(angDiff(st.dir, target) * gain + (ff || 0), -maxW, maxW);
    st.dirV += (w - st.dirV) * Math.min(1, dt * resp);
    st.dir += st.dirV * dt;
  }
  
  function step(h, st, t, dt, rnd) {
    rnd = rnd || Math.random;
    if (t >= st.until && st.mode !== 'run' && !st.careHold) decide(h, st, t, rnd);      
    const s = scaleAt(h, st.y);
    let wantW = 0, wantR = 0, effT = st.eff, steered = false;
    if (st.mode === 'walk' && st.tgt) {
      const dx = st.tgt[0] - st.x, dy = st.tgt[1] - st.y, dist = Math.hypot(dx, dy / 0.5);
      const want = Math.atan2(dy / 0.5, dx), turn = angDiff(st.dir, want);
      steer(st, want, dt, 1.1, 1.8, 3.5); steered = true;
      wantW = 1;
      effT = lerp(1, 0.25, smooth((Math.abs(turn) - 0.25) / 0.9)) * clamp(dist / 90, 0.5, 1);   
      if (dist < Math.max(28, 0.06 * s * h.H)) {
        
        if (!(st.force && st.force.length) && !st.forcedWalk && !st.careHold && rnd() < 0.45 && pickWalkTarget(h, st, rnd)) { st.until = t + 30; }
        else { st.mode = 'idle'; st.until = st.force && st.force.length ? t : t + 4 + rnd() * 7; st.want.graze = rnd() < 0.3 ? 1 : 0; st.want.look = [0, 0]; }
      }
    } else if (st.mode === 'turn') {               
      const d = angDiff(st.dir, st.turnTo);
      steer(st, st.turnTo, dt, 1.25, 2.4, 4.5); steered = true;
      wantW = Math.abs(d) > 0.07 ? 1 : 0; effT = 0.3;
      if (Math.abs(d) < 0.05 && Math.abs(st.dirV) < 0.12) { st.mode = 'idle'; st.until = st.careHold ? t + 1e3 : t + 3; }
    } else if (st.mode === 'gallop') {             
      const vWalk = walkSpeed(h, 1, 1);
      st.runV += clamp(RUN_V - st.runV, -3.6 * dt, 3.0 * dt);
      wantR = clamp((st.runV - vWalk) / (2.0 - vWalk), 0, 1); wantW = st.runV > 0.05 ? 1 - wantR : 0; effT = 1;
      st.x += Math.cos(st.dir) * st.runV * s * dt; st.y += Math.sin(st.dir) * st.runV * s * dt * 0.5;
    } else if (st.mode === 'run') {
      
      const vWalk = walkSpeed(h, 1, 1);
      const tv = st.toTrack ? 3.4 : st.lap < 0.9 ? RUN_V : vWalk * 0.9;      
      st.runV += clamp(tv - st.runV, -3.6 * dt, 3.0 * dt);                   
      wantR = clamp((st.runV - vWalk) / (2.0 - vWalk), 0, 1); wantW = st.runV > 0.05 ? 1 - wantR : 0;   
      effT = clamp(st.runV / vWalk, 0.25, 1);
      const v = st.runV * s;                                                 
      if (st.toTrack) {
        
        const [s0, d0] = trackNear(st.x, st.y), q = trackAt(s0 + 260);
        const ox = (q[0] - TRACK.cx) * 1.08 + TRACK.cx, oy = (q[1] - TRACK.cy) * 1.08 + TRACK.cy;
        st.runT = (st.runT || 0) + dt;
        steer(st, Math.atan2((oy - st.y) / 0.5, ox - st.x), dt, 2.2, 3.0, 6); steered = true;
        st.x += Math.cos(st.dir) * v * dt; st.y += Math.sin(st.dir) * v * dt * 0.5;
        if (d0 < 22 || st.runT > 4) { st.toTrack = false; st.lapS = s0; st.lapS0 = s0; st.tPrev = null; }
      } else {
        st.lapS += v * dt; st.lap = (st.lapS - st.lapS0) / trackPts().total;      
        const q = trackAt(st.lapS);
        const e = Math.min(1, dt * 8); st.x += (q[0] - st.x) * e; st.y += (q[1] - st.y) * e;
        const ta = q[2];
        const ff = st.tPrev == null || dt <= 0 ? 0 : angDiff(st.tPrev, ta) / dt; st.tPrev = ta;     
        steer(st, ta, dt, 4, 5, 8, ff); steered = true;
        if (st.lap >= 1 && st.runV < vWalk * 0.95) {                          
          st.runEnd += dt;
          if (st.runEnd > 1.6) { st.mode = 'idle'; st.until = st.force && st.force.length ? t : t + 5 + rnd() * 5; st.want.graze = 0; st.want.look = [0, 0]; }
        }
      }
    }
    if (!steered) { st.dirV *= Math.max(0, 1 - dt * 4); st.dir += st.dirV * dt; }      
    
    st.eff += (effT - st.eff) * Math.min(1, dt * 2.5);
    st.gw += clamp(wantW - st.gw, -dt * 1.8, dt * 1.8); st.gr += clamp(wantR - st.gr, -dt * 1.6, dt * 1.6);
    const gz = st.mode === 'idle' ? st.want.graze : 0; st.graze += clamp(gz - st.graze, -dt * 0.7, dt * 0.7);
    const lk = st.mode === 'idle' ? st.want.look : [0, 0]; st.look = st.look.map((v, i) => v + clamp(lk[i] - v, -dt * 0.9, dt * 0.9));
    st.lookS = st.lookS.map((v, i) => v + (st.look[i] - v) * Math.min(1, dt * 3));
    
    let dzT = 0;
    if (st.mode === 'sleep') {
      const tUp = st.until - RISE_DUR;
      if (st.sl < 1) { st.sl = Math.min(1, st.sl + dt / (st.lieDur || LIE_DUR)); if (st.sl >= 1) st.lieDoneT = t; }      
      else if (t >= tUp) st.rise = Math.min(1, st.rise + dt / RISE_DUR);
      dzT = st.sl >= 1 && t > (st.lieDoneT || 0) + 1.5 && t < tUp - 2.0 ? 1 : 0;
      if (st.rise >= 1) {          
        const sc = scaleAt(h, st.y); st.x += Math.cos(st.dir) * XE * sc; st.y += Math.sin(st.dir) * XE * sc * 0.5;
        st.mode = 'idle'; st.until = t + 4; st.sl = 0; st.rise = 0; st.doze = 0; st.upT = t; st.lieDur = null; st.flop = null;       
      }
    }
    st.doze = (st.doze || 0) + clamp(dzT - (st.doze || 0), -dt / 2.0, dt / 2.5);
    st.sleep = (st.sl || 0) * (1 - (st.rise || 0));          
    
    const g = GAITS.walk, gR = GAITS.run;
    st.wAmp = 0.5 + 0.5 * st.eff;
    st.phase.walk = (st.phase.walk + dt / walkOf(h).T * (0.7 + 0.3 * st.eff) * (st.gw > 0.01 ? 1 : 0)) % 1;
    const vr = Math.max(st.runV || 0, 0.01), cr = 0.8 + 0.2 * clamp(vr / RUN_V, 0, 1);
    st.rAmp = clamp(Math.asin(clamp(vr * gR.st * gR.T / (2 * h.legLen * cr), 0, 0.99)) / gR.A, 0.35, 1.15);
    st.phase.run = (st.phase.run + dt / gR.T * cr * (st.gr > 0.01 ? 1 : 0)) % 1;
    if (st.mode !== 'run' && st.mode !== 'gallop') {
      const v = walkSpeed(h, st.eff, smooth(st.gw)) * s * (st.mode === 'turn' ? 0.25 : 1);      
      st.x += Math.cos(st.dir) * v * dt; st.y += Math.sin(st.dir) * v * dt * 0.5;
    }
    
    if (t > st.nextFlick) { st.nextFlick = t + 2.5 + rnd() * 6; st.flickT = t; }
    
    
    if (st.nextReset == null) st.nextReset = t + 120;
    if (t >= st.nextReset) { st.nextReset += 120; if (rnd() < 1 / 7) st.poopReq = true; }
    if (st.stand) st.poopReq = false;          
    if (st.poopReq && st.poopT == null && !(st.sl > 0.001) && st.mode !== 'run' && st.mode !== 'gallop') {
      st.poopT = t; st.poopReq = false; st.mode = 'idle'; st.until = Math.max(st.until, t + POOP_DUR + 0.3); st.want.graze = 0; st.want.look = [0, 0];
      st.poopImg = Math.floor(rnd() * 3) % 3; st.poopDone = false;
    }
    if (st.poopT != null) {
      const pu = (t - st.poopT) / POOP_DUR;
      st.poopE = pu < 1 ? smooth(clamp(pu / 0.22, 0, 1)) * (1 - smooth(clamp((pu - 0.72) / 0.28, 0, 1))) : 0;
      if (pu >= 0.42 && !st.poopDone) {
        st.poopDone = true; st.poops = st.poops || [];
        const back = 1.08 * s;                                       
        st.poops.push({ x: st.x - Math.cos(st.dir) * back, y: st.y - Math.sin(st.dir) * back * 0.5, img: st.poopImg, t0: t, h0: 1.05, w: [0.3, 0.5, 0.42][st.poopImg] * (h.opt.stage || 1) });
        if (st.poops.length > 3) st.poops.shift();
      }
      if (pu >= 1) { st.poopT = null; st.poopE = 0; }
    }
    st.tailFlick = st.flickT ? 0.35 * bump((t - st.flickT) / 0.8, 2) : 0;
  }
  
  function scaleAt(h, y) { return (h.opt.base || 175) * lerp(0.68, 1.18, depth(y)) * (h.opt.stage || 1); }     

  
  const LIGHT = {
    morning: { sun: [-0.45, 0.75, 0.48], sunC: [1.0, 0.97, 0.9], amb: [0.53, 0.52, 0.51], fill: [0.9, 0.88, 0.9], shadow: 0.32, skyT: [0.569, 1.083, 1.348], gndT: [1.313, 1.012, 0.675] },      
    evening: { sun: [-0.8, 0.35, 0.45], sunC: [1.05, 0.72, 0.48], amb: [0.42, 0.36, 0.38], fill: [0.85, 0.78, 0.82], shadow: 0.26, skyT: [1.134, 0.941, 0.924], gndT: [1.471, 0.978, 0.551] },
    night: { sun: [0.3, 0.6, 0.7], sunC: [0.36, 0.42, 0.62], amb: [0.2, 0.22, 0.3], fill: [0.75, 0.82, 1.0], shadow: 0.18, skyT: [0.214, 0.919, 1.867], gndT: [1.055, 0.962, 0.983] },
    divine: { sun: [0.45, 0.8, 0.45], sunC: [1.08, 1.0, 0.86], amb: [0.6, 0.57, 0.52], fill: [0.98, 0.92, 0.84], shadow: 0.26, skyT: [0.812, 1.013, 1.175], gndT: [1.364, 1.02, 0.616] },      
    abyss: { sun: [0.25, 0.6, 0.75], sunC: [0.6, 0.48, 0.82], amb: [0.3, 0.24, 0.42], fill: [0.78, 0.6, 1.0], shadow: 0.22, skyT: [0.412, 0.683, 1.905], gndT: [0.984, 0.938, 1.078] },        
  };

  
  const hemiOf = lt => lt.hemi || (lt.hemi = {
    sky: lt.amb.map((a, i) => a * (1 + 0.3 * ((lt.skyT || [1, 1, 1])[i] - 1))),
    gnd: lt.amb.map((a, i) => a * (1 + 0.6 * ((lt.gndT || [1, 1, 1])[i] - 1)) * 0.5) });
  
  function blendOf(st) { return st.sl > 0.001 ? (st.rise > 0 ? smooth((st.rise - 0.7) / 0.3) : 1 - smooth(st.sl * 3)) : 1; }
  
  function draw(h, st, t, view) {
    const gl = h.gl, lt = LIGHT[st.light || st.tod];
    const s = scaleAt(h, st.y) * view.k;                     
    const cx = (st.x * view.k + view.ox) / view.W * 2 - 1, cy = 1 - (st.y * view.k + view.oy) / view.H * 2;
    const mats = pose(h, st, t);
    const pitch = view.pitch != null ? view.pitch : 0.49;      
    let V = M.mul(M.rx(pitch), M.ry(-st.dir));              
    const R3 = [V[0], V[1], V[2], V[4], V[5], V[6], V[8], V[9], V[10]];      
    V = M.mul(M.sc(s / view.W * 2, s / view.H * 2, 0.4), V);
    h.last = { mats, V, cx, cy, view, s, R3 };                
    
    gl.useProgram(h.S); gl.disable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    gl.bindBuffer(gl.ARRAY_BUFFER, h.B.quad); gl.enableVertexAttribArray(h.loc.sp); gl.vertexAttribPointer(h.loc.sp, 2, gl.FLOAT, false, 0, 0);
    const len = 0.62 * (1 - st.sleep * 0.15), sx = s * (Math.abs(Math.cos(st.dir)) * len + 0.32) / view.W * 2, sy = s * (0.2 + 0.2 * Math.abs(Math.sin(st.dir))) / view.H * 2;      
    gl.uniform4f(h.loc.uE, cx + (st.tod === 'evening' ? sx * 0.25 : 0), cy, sx * (st.tod === 'evening' ? 1.3 : 1), sy);
    gl.uniform1f(h.loc.uO, lt.shadow);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    if (h.hoof && (view.quality || {}).hoof !== 0) for (const L of ['FL', 'FR', 'HL', 'HR']) {      
      const b = h.bi[L + '_f'], p = h.hoof[L]; if (b == null || !p) continue; const Bm = mats[b];
      const w = [0, 1, 2].map(r => Bm[r] * p[0] + Bm[4 + r] * p[1] + Bm[8 + r] * p[2] + Bm[12 + r]);
      const k = 1 - smooth(clamp((w[1] - 0.03) / 0.45, 0, 1)); if (k < 0.01) continue;
      const qx = V[0] * w[0] + V[8] * w[2] + V[12], qy = V[1] * w[0] + V[9] * w[2] + V[13], r = 0.2 * s;
      gl.uniform4f(h.loc.uE, cx + qx, cy + qy, r / view.W * 2, r * 0.42 / view.H * 2);
      gl.uniform1f(h.loc.uO, lt.shadow * 0.9 * k);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    }
    if (st.props) for (const pr of st.props) {      
      if (!pr.sh || !(pr.sh[3] > 0.001)) continue; const [x, z, r, o] = pr.sh;
      const qx = V[0] * x + V[8] * z + V[12], qy = V[1] * x + V[9] * z + V[13];
      gl.uniform4f(h.loc.uE, cx + qx, cy + qy, r * s / view.W * 2, r * s * 0.42 / view.H * 2); gl.uniform1f(h.loc.uO, lt.shadow * o);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    }
    gl.disableVertexAttribArray(h.loc.sp);
    if (st.poops && st.poops.length && h.poopTex.length) drawPoops(h, st, t, view, lt, s, false);
    
    gl.useProgram(h.P); gl.enable(gl.DEPTH_TEST); gl.clear(gl.DEPTH_BUFFER_BIT); gl.depthFunc(gl.LEQUAL);
    const at = (b, loc, n, type, norm, stride) => { if (loc < 0) return; gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, n, type || gl.FLOAT, !!norm, stride || 0, 0); };
    at(h.B.pos, h.loc.aPos, 3); at(h.B.bone, h.loc.aBone, 1); at(h.B.bone2, h.loc.aBone2, 1); at(h.B.bw, h.loc.aBw, 1, gl.UNSIGNED_BYTE, true);
    gl.uniform1f(h.loc.uBlend, blendOf(st));
    if (h.loc.aCv >= 0) { if (h.B.cv) at(h.B.cv, h.loc.aCv, 1, gl.UNSIGNED_BYTE, true); else { gl.disableVertexAttribArray(h.loc.aCv); gl.vertexAttrib1f(h.loc.aCv, 0.5); } }
    if (h.fmt2) {
      at(h.B.nrm, h.loc.aNrm, 4, gl.BYTE, true, 4); at(h.B.uv, h.loc.aUV, 2, gl.UNSIGNED_SHORT, true);
      if (h.loc.aCol >= 0) { gl.disableVertexAttribArray(h.loc.aCol); gl.vertexAttrib3f(h.loc.aCol, 1, 1, 1); }
      
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
    const Q = view.quality || {};          
    gl.uniform1f(h.loc.uAoOn, h.fmt2 && h.meta.ao && Q.ao !== 0 ? 1 : 0); gl.uniform1f(h.loc.uSm, Q.sm != null ? Q.sm : 0.55); gl.uniform1f(h.loc.uGrain, Q.grain != null ? Q.grain : 0); gl.uniform1f(h.loc.uCv, h.B.cv ? (Q.cv != null ? Q.cv : 1) : 0); gl.uniform1f(h.loc.uDbg, Q.dbg ? 1 : 0);      
    
    const gk = h.glow && h.eyes ? (0.84 + 0.16 * Math.sin(TAU * t / 2.8)) * (1 - 0.92 * smooth(st.doze || 0)) * (st.glowK != null ? st.glowK : 1) * (h.opt.glowK != null ? h.opt.glowK : 1) : 0;      
    gl.uniform4f(h.loc.uEm, h.em[0], h.em[1], h.em[2], h.bi.head != null ? h.bi.head : -9);
    if (gk > 0) {
      const e0 = h.eyes[0].p, e1 = h.eyes[1].p;
      gl.uniform3f(h.loc.uE0, e0[0] - h.em[0], e0[1] - h.em[1], e0[2] - h.em[2]); gl.uniform3f(h.loc.uE1, e1[0] - h.em[0], e1[1] - h.em[1], e1[2] - h.em[2]);
      gl.uniform3fv(h.loc.uGc, h.glow); gl.uniform2f(h.loc.uGr, h.eyeR, Math.min(1, gk * 1.1));
    } else gl.uniform2f(h.loc.uGr, 1, 0);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, h.B.idx);
    gl.drawElements(gl.TRIANGLES, h.meta.i, h.meta.idx32 ? gl.UNSIGNED_INT : gl.UNSIGNED_SHORT, 0);
    [h.loc.aPos, h.loc.aNrm, h.loc.aCol, h.loc.aBone, h.loc.aBone2, h.loc.aBw, h.loc.aUV, h.loc.aCv].forEach(l => { if (l >= 0) gl.disableVertexAttribArray(l); });
    if (st.props && st.props.length) drawProps(h, st, view);      
    gl.disable(gl.DEPTH_TEST);
    if (gk > 0) drawEyeGlow(h, mats, V, R3, cx, cy, s, view, gk);
    if (st.poops && st.poops.length && h.poopTex.length) drawPoops(h, st, t, view, lt, s, true);
  }
  
  function drawPoops(h, st, t, view, lt, s, front) {
    const gl = h.gl, pitch = view.pitch != null ? view.pitch : 0.49;
    const tint = [0, 1, 2].map(i => Math.min(1.05, lt.amb[i] + lt.sunC[i] * 0.55));
    gl.disable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    gl.bindBuffer(gl.ARRAY_BUFFER, h.B.quad);
    for (const q of st.poops) {
      if ((q.y > st.y) !== front) continue;
      const tex = h.poopTex[q.img % h.poopTex.length]; if (!tex) continue;
      const ss = scaleAt(h, q.y) / (h.opt.stage || 1) * view.k;                
      const tau = t - q.t0, TF = 0.32, fall = clamp(tau / TF, 0, 1);
      const hgt = q.h0 * (1 - fall * fall), sq = tau < TF ? 0.75 + 0.25 * fall : 1 - 0.12 * Math.exp(-(tau - TF) * 14) * Math.cos((tau - TF) * 30);
      const wpx = q.w * ss * (0.7 + 0.3 * fall), hpx = wpx * tex.h / tex.w * sq;
      const gx = q.x * view.k + view.ox, gy = q.y * view.k + view.oy - hgt * ss * (h.opt.stage || 1) * Math.cos(pitch);
      
      gl.useProgram(h.S); gl.enableVertexAttribArray(h.loc.sp); gl.vertexAttribPointer(h.loc.sp, 2, gl.FLOAT, false, 0, 0);
      const gy0 = q.y * view.k + view.oy;
      gl.uniform4f(h.loc.uE, gx / view.W * 2 - 1, 1 - gy0 / view.H * 2, wpx * 0.62 / view.W * 2, wpx * 0.2 / view.H * 2); gl.uniform1f(h.loc.uO, lt.shadow * 0.8 * fall);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); gl.disableVertexAttribArray(h.loc.sp);
      
      gl.useProgram(h.PS); gl.enableVertexAttribArray(h.loc.pp); gl.vertexAttribPointer(h.loc.pp, 2, gl.FLOAT, false, 0, 0);
      gl.activeTexture(gl.TEXTURE5); gl.bindTexture(gl.TEXTURE_2D, tex.t); gl.uniform1i(h.loc.pT, 5); gl.activeTexture(gl.TEXTURE0);
      gl.uniform3fv(h.loc.pTint, q.gold ? [1.55, 1.2, 0.42] : tint);      
      gl.uniform4f(h.loc.pE, gx / view.W * 2 - 1, 1 - (gy - hpx * 0.46) / view.H * 2, wpx / view.W, hpx / view.H);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); gl.disableVertexAttribArray(h.loc.pp);
    }
  }
  
  function drawEyeGlow(h, mats, V, R3, cx, cy, s, view, gk) {
    const gl = h.gl, Bh = mats[h.bi.head];
    gl.useProgram(h.G); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    gl.bindBuffer(gl.ARRAY_BUFFER, h.B.quad); gl.enableVertexAttribArray(h.loc.gp); gl.vertexAttribPointer(h.loc.gp, 2, gl.FLOAT, false, 0, 0);
    gl.uniform3fv(h.loc.gGc, h.glow);
    const rpx = h.eyeR * s * 4.5 * (0.96 + 0.04 * gk) * (h.opt.glowR || 1);
    for (const e of h.eyes) {
      const p = e.p, w = [0, 1, 2].map(r => Bh[r] * p[0] + Bh[4 + r] * p[1] + Bh[8 + r] * p[2] + Bh[12 + r]);
      const nb = [0, 1, 2].map(r => Bh[r] * e.n[0] + Bh[4 + r] * e.n[1] + Bh[8 + r] * e.n[2]);
      const fz = R3[2] * nb[0] + R3[5] * nb[1] + R3[8] * nb[2];          
      const f = smooth((fz + 0.05) / 0.45); if (f <= 0.001) continue;
      const qx = V[0] * w[0] + V[4] * w[1] + V[8] * w[2] + V[12], qy = V[1] * w[0] + V[5] * w[1] + V[9] * w[2] + V[13];
      gl.uniform4f(h.loc.gE, cx + qx, cy + qy, rpx / view.W * 2, rpx / view.H * 2);
      gl.uniform1f(h.loc.gGk, gk * f);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    }
    gl.disableVertexAttribArray(h.loc.gp);
  }

  
  function where(h, name, ground) {   
    const L = h.last, a = h.anchors[name]; if (!L || !a || !a.p) return null;
    const Bm = L.mats[a.b], p = a.p, w = [0, 1, 2].map(r => Bm[r] * p[0] + Bm[4 + r] * p[1] + Bm[8 + r] * p[2] + Bm[12 + r]);
    if (ground) w[1] = 0;
    const V = L.V, qx = V[0] * w[0] + V[4] * w[1] + V[8] * w[2] + V[12], qy = V[1] * w[0] + V[5] * w[1] + V[9] * w[2] + V[13];
    const px = (L.cx + qx + 1) / 2 * L.view.W, py = (1 - (L.cy + qy)) / 2 * L.view.H;
    return [(px - L.view.ox) / L.view.k, (py - L.view.oy) / L.view.k];
  }
  
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
  
  function wherePose(h, mats, name, ground) {
    const L = h.last, a = h.anchors[name]; if (!L || !a || !a.p) return null;
    const Bm = mats[a.b], p = a.p, w = [0, 1, 2].map(r => Bm[r] * p[0] + Bm[4 + r] * p[1] + Bm[8 + r] * p[2] + Bm[12 + r]);
    if (ground) w[1] = 0;
    const V = L.V, qx = V[0] * w[0] + V[4] * w[1] + V[8] * w[2] + V[12], qy = V[1] * w[0] + V[5] * w[1] + V[9] * w[2] + V[13];
    return [((L.cx + qx + 1) / 2 * L.view.W - L.view.ox) / L.view.k, ((1 - (L.cy + qy)) / 2 * L.view.H - L.view.oy) / L.view.k];
  }
  
  function anchorPose(h, mats, name) {
    const a = h.anchors[name]; if (!a || !a.p) return null; const Bm = mats[a.b], p = a.p;
    return [0, 1, 2].map(r => Bm[r] * p[0] + Bm[4 + r] * p[1] + Bm[8 + r] * p[2] + Bm[12 + r]);
  }
  
  function project(h, w) {
    const L = h.last; if (!L) return null; const V = L.V;
    const qx = V[0] * w[0] + V[4] * w[1] + V[8] * w[2] + V[12], qy = V[1] * w[0] + V[5] * w[1] + V[9] * w[2] + V[13];
    return [((L.cx + qx + 1) / 2 * L.view.W - L.view.ox) / L.view.k, ((1 - (L.cy + qy)) / 2 * L.view.H - L.view.oy) / L.view.k];
  }
  
  function react(st, k, dur, t, o) { st.reacts = (st.reacts || []).filter(r => t - r.t0 < r.dur); st.reacts.push(Object.assign({ k, t0: t, dur }, o || {})); }
  window.TCHorse = { create, createProp, anchorPose, project, M, brain, step, draw, pose, where, wherePose, react, extent, scaleAt: (h, y) => scaleAt(h, y), GAITS, WALK, RUN, AREA, TRACK, EYE_GLOW, walkLegs, walkSpeed, blendOf };
})();

;



const TCField = (() => {
const CFG = { w: 1052, h: 1657, amp: [5.0, 4.2, 4.6], per: [4.6, 3.7, 5.3], ph: [0.0, 0.37, 0.71] };
const VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.0,1.0);}';
const FS = ['precision highp float;', 'uniform sampler2D uImg,uMap,uLit;uniform vec2 uSz,uRes;uniform vec4 uXf;uniform float uT,uA,uLitOn,uFx;uniform vec3 uAmp,uPer,uPh;uniform float uK[12];',
  'const float TAU=6.2831853;',
  
  'float hs(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
  'float vn(vec2 p){vec2 i=floor(p),f=fract(p);vec2 u=f*f*(3.0-2.0*f);return mix(mix(hs(i),hs(i+vec2(1.0,0.0)),u.x),mix(hs(i+vec2(0.0,1.0)),hs(i+vec2(1.0,1.0)),u.x),u.y);}',
  'float fbm(vec2 p){float a=0.5,s=0.0;for(int i=0;i<4;i++){s+=a*vn(p);p=p*2.03+vec2(17.1,9.2);a*=0.5;}return s;}',
  
  'float motes(vec2 ip,float t,float cs,float pr,float sz,float up,float sd){vec2 q=ip+vec2(6.0*sin(t*0.21+ip.y*0.004),t*up);vec2 c=floor(q/cs),f=fract(q/cs)-0.5;',
  '  vec2 r=vec2(hs(c+sd),hs(c+sd+3.7))-0.5;float d=length(f-r*0.6)*cs;float tw=0.5+0.5*sin(t*(0.9+0.6*hs(c+sd+5.3))+hs(c+sd+9.1)*TAU);',
  '  return step(1.0-pr,hs(c+sd+1.3))*tw*tw*((1.0-smoothstep(0.0,sz,d))+0.3*(1.0-smoothstep(0.0,sz*3.0,d)));}',
  
  'float flakes(vec2 ip,float t,float cs,float pr,float sz,float sp,float sd){float cx=floor(ip.x/cs);float v=sp*(0.6+0.8*hs(vec2(cx,sd)));',
  '  float qy=ip.y-t*v+hs(vec2(cx,sd+1.0))*cs*7.0;vec2 c=vec2(cx,floor(qy/cs));vec2 f=vec2(fract(ip.x/cs),fract(qy/cs))-0.5;float ph=hs(c+sd+2.1)*TAU;',
  '  vec2 o=vec2(0.22*sin(t*(0.7+0.5*hs(c+sd+4.4))+ph),0.18*(hs(c+sd+6.6)-0.5));float d=length(f-o)*cs;',
  '  float fl=abs(sin(t*(0.8+0.6*hs(c+sd+8.8))+ph));',
  '  return step(1.0-pr,hs(c+sd+1.3))*(0.25+0.75*fl*fl)*((1.0-smoothstep(0.0,sz,d))+0.35*(1.0-smoothstep(0.0,sz*3.2,d)));}',
  
  
  'vec3 divine(vec3 col,vec2 ip,float t){',
  '  vec2 v=ip-vec2(600.0,-380.0);float an=atan(v.x,v.y),dd=length(v);float r=0.0;',
  '  for(int i=0;i<7;i++){float fi=float(i);float th=-0.55+fi*0.16+0.035*sin(t*(0.09+0.025*fi)+fi*1.7);float wd=0.04+0.045*hs(vec2(fi,2.0));',
  '    float am=0.5+0.5*sin(t*TAU/(8.0+1.7*fi)+fi*2.1);float x=(an-th)/wd;r+=(0.35+0.65*am)*exp(-x*x);}',
  '  r*=0.7+0.6*fbm(vec2(an*18.0,dd*0.003-t*0.05));',       
  '  float fall=smoothstep(60.0,480.0,dd)*(1.0-smoothstep(700.0,2300.0,dd));float glow=exp(-dd/650.0)*(0.8+0.2*sin(t*0.45));',
  '  vec3 L=vec3(1.0,0.92,0.7)*min(r*0.36*fall+glow*0.3,0.7);col=1.0-(1.0-col)*(1.0-L);',        
  '  return col;}',
  
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
    async function setField(name) {             
      if (cur === name) return; const want = name;
      const tod = ['morning', 'evening', 'night'].includes(name) ? name : null;
      const p = Promise.all([loadImg(`tc_field_${name}.webp`), loadImg(tod ? `tc_sway_${tod}.webp` : 'tc_sway_none.webp'), tod && tod !== 'morning' ? loadImg(`tc_light_${tod}.webp`) : Promise.resolve(null)]);
      loading = p; const [img, map, lmap] = await p;
      if (loading !== p) return;
      up(0, img, false); up(1, map, true); if (lmap) up(2, lmap, true);
      cur = want; lit = !!lmap; fxn = name === 'divine' ? 1 : name === 'abyss' ? 2 : 0; t0 = null;
    }
    function render(t, Z) {                       
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

;

























const TCCare = (() => {
  const TAU = Math.PI * 2, W = 1052, H = 1657;
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x)), sm = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
  const lerp = (a, b, u) => a + (b - a) * u, mixP = (a, b, u) => [lerp(a[0], b[0], u), lerp(a[1], b[1], u)];
  const backOut = x => { x = clamp(x, 0, 1); const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  const easeOut = x => 1 - Math.pow(1 - clamp(x, 0, 1), 3), easeIO = x => { x = clamp(x, 0, 1); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
  const angDiff = (a, b) => { let d = (b - a) % TAU; if (d > Math.PI) d -= TAU; if (d < -Math.PI) d += TAU; return d; };
  const FONT = '"BIZ UDPGothic", BIZ, "Hiragino Sans", "Noto Sans CJK JP", sans-serif';
  const AP = p => (typeof window !== 'undefined' && typeof window.TC_ASSET === 'function') ? window.TC_ASSET(p) : p;      
  const RULE = { strokes: 3, strokeLen: 34, cool: 7, perMin: 5, max: 10, win: 1 / 66, unlock: 5, stockMax: 20, stockEvery: 600 };

  let g = null, HO = null, BR = null, O = {}, rnd = Math.random, apple = null, carrot = null, carrotG = null, bucket = null, BANNER = null, PROPS = null;
  const FRONT = { x: 526, y: 1372 };          
  function front() {                          
    let y = FRONT.y; while (y > 960 && TCHorse.scaleAt(HO, y) * 1.8 > 0.47 * W) y -= 8; return { x: FRONT.x, y, big: y < FRONT.y };      
  }
  const BTN = { pet: [170, 1494], feed: [407, 1494], clean: [644, 1494], call: [881, 1494] }, BTN_R = 70, HELP = [678, 97];      
  const S = { on: false, heart: 0, heartShow: 0, stock: 3, stockShow: 3, got: [], coolUntil: -1e9, coolFrom: -1e9, ses: null, hand: null, fx: [], ev: [], sched: [],
    greeted: false, busy: false, lot: null, holdUntil: -1, drainT: null, demo: null, t0: null, finger: null, readyT: null, stockBump: null,
    phase: 'idle', mode: null, route: null, zoom: { z: 1, cx: W / 2, cy: H / 2 }, zA: null, zB: null, zT0: 0, zDur: 1, marks: {}, press: { pet: -9, call: -9, feed: -9, clean: -9 }, petIdle: 0, callKind: null,
    chooser: null, feed: null, clean: null, fav: 'apple', high: 0, highBump: null, popVal: null, stockDrop: null };
  const POOP = [];          

  
  function tone(hex, k) {
    const n = parseInt(hex.slice(1), 16); let r = n >> 16, gg = (n >> 8) & 255, b = n & 255;
    if (k >= 1) { const u = k - 1; r += (255 - r) * u; gg += (255 - gg) * u; b += (255 - b) * u; } else { r *= k; gg *= k; b *= k; }
    return `rgb(${r | 0},${gg | 0},${b | 0})`;
  }
  function pf(pts, fill) {            
    g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]); g.closePath();
    g.fillStyle = fill; g.fill(); g.strokeStyle = fill; g.stroke();
  }
  function polyP(q, x, y, r, n, rot) { q.beginPath(); for (let i = 0; i < n; i++) { const an = rot + i * TAU / n; if (i) q.lineTo(x + Math.cos(an) * r, y + Math.sin(an) * r); else q.moveTo(x + Math.cos(an) * r, y + Math.sin(an) * r); } q.closePath(); }      
  function line(a, b, col) { g.strokeStyle = col; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); }
  function label(txt, x, y, size, fill, edge, ew, align) {
    g.font = `700 ${size}px ${FONT}`; g.textAlign = align || 'center'; g.textBaseline = 'middle';
    if (edge) { g.lineJoin = 'round'; g.lineWidth = ew; g.strokeStyle = edge; g.strokeText(txt, x, y); }
    g.fillStyle = fill; g.fillText(txt, x, y);
  }
  
  const HP = [[0, 0.95], [-0.98, -0.02], [-1.0, -0.42], [-0.72, -0.82], [-0.3, -0.86], [0, -0.5], [0.3, -0.86], [0.72, -0.82], [1.0, -0.42], [0.98, -0.02]];
  function heart(x, y, r, rot, a, col) {
    if (a <= 0.003 || r <= 0.3) return;
    col = col || '#ff7aa6';
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot || 0); g.scale(r, r); g.lineWidth = 0.9 / r; g.lineJoin = 'round';
    const [B, L1, L2, L3, L4, C, R4, R3, R2, R1] = HP;
    pf([B, L1, C], tone(col, 1.05)); pf([L1, L2, L3, C], tone(col, 1.15)); pf([L3, L4, C], tone(col, 1.3));
    pf([B, C, R1], tone(col, 0.84)); pf([C, R3, R2, R1], tone(col, 0.93)); pf([C, R4, R3], tone(col, 1.05));
    g.lineWidth = 1.2 / r; line(B, C, 'rgba(120,40,70,0.22)'); line(L1, C, 'rgba(120,40,70,0.1)'); line(R1, C, 'rgba(120,40,70,0.12)'); line(L3, C, 'rgba(255,255,255,0.25)'); line(R3, C, 'rgba(120,40,70,0.1)');
    g.restore();
  }
  function heartSlot(x, y, r) {        
    g.save(); g.translate(x, y); g.scale(r, r); g.lineWidth = 2 / r;
    g.beginPath(); HP.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.closePath();
    g.fillStyle = '#f6e2e6'; g.fill(); g.strokeStyle = '#e8c1cc'; g.stroke(); g.restore();
  }
  
  function star(x, y, r, rot, a, col) {
    if (a <= 0.003 || r <= 0.3) return; col = col || '#f5d06a';
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot || 0); g.lineWidth = 0.8;
    const k = 0.3;
    pf([[0, -r], [r * k, -r * k], [r, 0], [r * k, r * k], [0, r], [-r * k, r * k], [-r, 0], [-r * k, -r * k]], tone(col, 1.18));
    pf([[0, -r], [r * k, -r * k], [r, 0], [0, 0]], col); pf([[0, r], [-r * k, r * k], [-r, 0], [0, 0]], col);
    g.restore();
  }
  
  const HAND = (() => {
    const F = [[-0.335, 0.15, 0.215], [-0.105, 0.0, 0.225], [0.125, 0.08, 0.215], [0.34, 0.3, 0.19]], base = 0.76;
    const fingers = F.map(([cx, tip, w]) => ({
      L: [[cx - w / 2, base], [cx - w / 2, tip + w * 0.45], [cx - w * 0.2, tip], [cx, tip], [cx, base]],
      R: [[cx, base], [cx, tip], [cx + w * 0.2, tip], [cx + w / 2, tip + w * 0.45], [cx + w / 2, base]],
      k: [[cx - w / 2, tip + (base - tip) * 0.5], [cx + w / 2, tip + (base - tip) * 0.5]] }));
    const T = [[-0.47, 1.12], [-0.73, 0.82], [-0.8, 0.55], [-0.69, 0.46], [-0.56, 0.62], [-0.46, 0.8]];
    return { fingers, thumb: [[T[0], T[1], T[2], T[3]], [T[0], T[3], T[4], T[5]]],
      palm: [[[-0.47, 0.72], [0.47, 0.72], [0.0, 1.08]], [[0.47, 0.72], [0.5, 1.2], [0.28, 1.5], [0.0, 1.08]], [[-0.47, 0.72], [0.0, 1.08], [-0.27, 1.5], [-0.49, 1.18]], [[0.0, 1.08], [0.28, 1.5], [-0.27, 1.5]]],
      cuff: [[[-0.31, 1.45], [0.31, 1.45], [0.34, 1.62], [-0.34, 1.62]], [[-0.34, 1.62], [0.34, 1.62], [0.36, 1.82], [-0.36, 1.82]]] };
  })();
  let HAND_PATH = null, HAND_BB = null;
  function handPath() {                
    if (!HAND_PATH) {
      HAND_PATH = new Path2D(); let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      for (const p of [...HAND.thumb, ...HAND.palm, ...HAND.cuff, ...HAND.fingers.flatMap(f => [f.L, f.R])]) {
        HAND_PATH.moveTo(p[0][0], p[0][1]); for (let i = 1; i < p.length; i++) HAND_PATH.lineTo(p[i][0], p[i][1]); HAND_PATH.closePath();
        for (const q of p) { x0 = Math.min(x0, q[0]); y0 = Math.min(y0, q[1]); x1 = Math.max(x1, q[0]); y1 = Math.max(y1, q[1]); }
      }
      HAND_BB = [x0, y0, x1, y1];
    }
    return HAND_PATH;
  }
  const HAND_SH = {};
  function handShadow(lv) {            
    if (HAND_SH[lv]) return HAND_SH[lv];
    const path = handPath(), [x0, y0, x1, y1] = HAND_BB, S0 = 64, bl = (1.5 + 3.5 * lv / 4) * S0 / 62, pad = Math.ceil(bl * 3) + 2;
    const c = document.createElement('canvas'); c.width = Math.ceil((x1 - x0) * S0) + pad * 2; c.height = Math.ceil((y1 - y0) * S0) + pad * 2;
    const q = c.getContext('2d'), off = c.width + 60;
    q.shadowColor = '#2b1a0e'; q.shadowBlur = bl * 2; q.shadowOffsetX = off;      
    q.setTransform(S0, 0, 0, S0, pad - x0 * S0 - off, pad - y0 * S0); q.fillStyle = '#2b1a0e'; q.fill(path, 'nonzero');
    return (HAND_SH[lv] = { c, S0, ox: pad - x0 * S0, oy: pad - y0 * S0 });
  }
  function hand(x, y, s, rot, press, a, open) {
    if (a <= 0.003 || open <= 0.003) return;
    const lift = 1 - press, P = '#fdf1dd';
    const sh = handShadow(Math.round(clamp(lift, 0, 1) * 4));
    g.save(); g.globalAlpha *= a * (0.2 + 0.08 * press);
    g.translate(x + (4 + 12 * lift) * s / 46, y + (6 + 16 * lift) * s / 46); g.rotate(rot); g.scale(s * open / sh.S0, s / sh.S0); g.drawImage(sh.c, -sh.ox, -sh.oy);
    g.restore();
    g.save(); g.globalAlpha *= a; g.translate(x, y - 5 * lift * s / 46); g.rotate(rot); const sc = s * (1 + 0.05 * lift); g.scale(sc * open, sc); g.lineWidth = 0.9 / sc; g.lineJoin = 'round';
    const [c0, c1] = HAND.cuff; pf(c0, '#9fd0f0'); pf(c1, '#7db9e2'); g.lineWidth = 1.2 / sc; line([-0.34, 1.62], [0.34, 1.62], 'rgba(40,80,120,0.25)'); g.lineWidth = 0.9 / sc;
    const [p0, p1, p2, p3] = HAND.palm; pf(p0, tone(P, 1.04)); pf(p2, tone(P, 0.97)); pf(p1, tone(P, 0.88)); pf(p3, tone(P, 0.92));
    pf(HAND.thumb[0], tone(P, 1.02)); pf(HAND.thumb[1], tone(P, 0.9));
    for (const f of HAND.fingers) { pf(f.L, tone(P, 1.03)); pf(f.R, tone(P, 0.9)); }
    g.lineWidth = 1.3 / sc;
    for (const f of HAND.fingers) line(f.k[0], f.k[1], 'rgba(150,100,60,0.22)');
    line([-0.47, 0.72], [0.47, 0.72], 'rgba(150,100,60,0.18)'); line([0, 1.08], [-0.47, 0.72], 'rgba(150,100,60,0.12)'); line([0, 1.08], [0.47, 0.72], 'rgba(150,100,60,0.16)');
    g.restore();
  }
  function paperSquare(x, y, r, rot, a) {       
    if (a <= 0.003 || r <= 0.3) return;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot); g.lineWidth = 0.8;
    pf([[0, -r], [r, 0], [0, r], [-r, 0]], '#fbeeda'); pf([[0, -r], [r, 0], [0, r]], '#ecd9bb'); pf([[-r, 0], [0, -r], [0, 0]], '#fff6e8');
    g.restore();
  }
  
  function tag(x, y, txt, size, a, sc, rot, col) {
    if (a <= 0.003 || sc <= 0.01) return;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot || 0); g.scale(sc, sc);
    g.font = `700 ${size}px ${FONT}`; const w = g.measureText(txt).width + size * 1.0, h = size * 1.55, c = size * 0.38; g.lineWidth = 0.8;
    pf([[-w / 2 + 4, -h / 2 + 6], [w / 2 + 4, -h / 2 + 6], [w / 2 + 4, h / 2 + 6], [-w / 2 + 4, h / 2 + 6]], 'rgba(40,20,5,0.18)');
    pf([[-w / 2, -h / 2], [w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2, h / 2], [-w / 2, h / 2]], '#fff8ea');
    pf([[-w / 2, 0.06 * h], [w / 2, 0.06 * h], [w / 2, h / 2], [-w / 2, h / 2]], '#f6e8cc');
    pf([[w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2 - c, -h / 2 + c]], '#e3c993');
    label(txt, 0, 1, size, col || '#7a4520');
    g.restore();
  }
  
  function panel(x, y, w, h, c) {
    g.save(); g.lineWidth = 0.8;
    pf([[x + 5, y + 7], [x + w + 5, y + 7], [x + w + 5, y + h + 7], [x + 5, y + h + 7]], 'rgba(40,20,5,0.2)');
    pf([[x, y], [x + w - c, y], [x + w, y + c], [x + w, y + h], [x, y + h]], '#fff8ec');
    pf([[x, y + h * 0.55], [x + w, y + h * 0.55], [x + w, y + h], [x, y + h]], '#f8ecd4');
    pf([[x + w - c, y], [x + w, y + c], [x + w - c, y + c]], '#e6cf9f');
    g.restore();
  }

  
  const toS = p => [(p[0] - S.zoom.cx) * S.zoom.z + W / 2, (p[1] - S.zoom.cy) * S.zoom.z + H / 2];       
  const toW = q => [(q[0] - W / 2) / S.zoom.z + S.zoom.cx, (q[1] - H / 2) / S.zoom.z + S.zoom.cy];
  function setZoom(t, to, dur) { S.zA = Object.assign({}, S.zoom); S.zB = to; S.zT0 = t; S.zDur = dur; }
  function zoomFor() {                 
    const e = TCHorse.extent(HO); if (!e) return { z: 1, cx: W / 2, cy: H / 2 };
    const z = clamp(Math.min(0.8 * W / (e[2] - e[0]), 0.56 * H / (e[3] - e[1])), 1, 2.2);
    const hw = W / (2 * z), hh = H / (2 * z);
    return { z, cx: clamp((e[0] + e[2]) / 2, hw, W - hw), cy: clamp((e[1] + e[3]) / 2 + 0.01 * H / z, hh, H - hh) };
  }

  
  const P = n => TCHorse.where(HO, n);
  const CHAIN = [['nose', 'nose'], ['eye', 'head'], ['poll', 'head'], ['neck', 'neck'], ['withers', 'neck'], ['back', 'back'], ['rump', 'back']];
  function zoneAt(x, y) {              
    const pts = CHAIN.map(([n, z]) => [P(n), z]).filter(q => q[0]);
    if (pts.length < 2) return null;
    const R = 0.46 * TCHorse.scaleAt(HO, BR.y); let best = null;
    for (let i = 0; i < pts.length - 1; i++) {
      const a = pts[i][0], b = pts[i + 1][0], dx = b[0] - a[0], dy = b[1] - a[1], L2 = dx * dx + dy * dy || 1;
      const u = clamp(((x - a[0]) * dx + (y - a[1]) * dy) / L2, 0, 1), d = Math.hypot(x - a[0] - dx * u, y - a[1] - dy * u);
      if (d < R && (!best || d < best.d)) best = { d, zone: u < 0.5 ? pts[i][1] : pts[i + 1][1] };
    }
    return best;
  }
  function sideToward(x, y) {          
    
    const L = HO.last, n = P('nose'); if (!L || !n) return 1;
    const zz = L.R3[8], zx = L.R3[6];
    if (Math.abs(zz) > 0.25) return zz > 0 ? -1 : 1;
    return ((x - n[0]) * -zx) >= 0 ? 1 : -1;
  }
  const react = (k, dur, t, o) => TCHorse.react(BR, k, dur, t, o);
  const ev = (t, k, o) => { const e = Object.assign({ t: +t.toFixed(4), k }, o || {}); if (S.demo || !O.onEvent) S.ev.push(e); if (O.onEvent) { try { O.onEvent(e); } catch (er) { } } };
  const at = (t, fn) => S.sched.push({ t, fn });
  const fx = o => S.fx.push(o);
  const SLOT = i => [26 + 134 + i * 44, 34 + 86];          
  const mark = (k, t) => { if (S.marks[k] == null) S.marks[k] = t - S.t0; };
  const tagW = (p, txt, t, o) => { if (p) fx(Object.assign({ k: 'tag', t0: t, w: p.slice(), txt, size: 36, dur: 1.5, rot: (hash(t) - 0.5) * 0.16 }, o || {})); };      

  
  function approach(t) {               
    const fr = front(), ex = fr.big ? fr.x : lerp(fr.x, clamp(BR.x, fr.x - 170, fr.x + 170), 0.45);
    S.route = [[ex, fr.y]]; S.turnAfter = true; S.phase = 'approach'; nextLeg(t);
  }
  function nextLeg(t) { const p = S.route.shift(); Object.assign(BR, { tgt: p, mode: 'walk', until: t + 30, forcedWalk: true }); BR.want.graze = 0; BR.want.look = [0, 0]; }
  function arrived(t) {
    mark('A', t);
    if (S.mode === 'pet' || S.mode === 'feed') {
      const zf = zoomFor();
      if (S.mode === 'feed') { const n = P('nose'); if (n) { const hw = W / (2 * zf.z); zf.cx = clamp(lerp(zf.cx, n[0], 0.3), hw, W - hw); } }      
      S.phase = 'zoomin'; setZoom(t, zf, 0.95); ev(t, 'zoomin');
    }
    else callArrive(t);
  }
  function endCare(t) {                 
    if (S.zoom.z > 1.001 || S.zB) { S.phase = 'zoomout'; setZoom(t, { z: 1, cx: W / 2, cy: H / 2 }, 0.95); ev(t, 'zoomout'); }
    else release(t);
  }
  function release(t) {
    const m = S.mode; S.phase = 'idle'; S.mode = null; mark('Z', t); BR.careHold = false; BR.want.look = [0, 0]; BR.until = t + 2.5; BR.forcedWalk = false; S.grazeOK = false;
    if ((m === 'feed' || m === 'clean') && S.popVal) {
      const pz = typeof S.popVal === 'object' ? S.popVal : { k: 'pt', v: S.popVal }; S.popVal = null;
      if (pz.k === 'pt') at(t + 0.15, tt => { fx({ k: 'pointpop', t0: tt, v: pz.v, dur: 2.0 }); ev(tt, 'piron'); if (O.onPrize) O.onPrize(pz); });
      else if (O.onPrize) at(t + 0.4, tt => O.onPrize(pz));          
    }      
    if (m === 'clean' && S.clean && S.clean.sniff && !BR.stand) {          
      const c = S.clean; S.clean = null; BR.careHold = true; S.mode = 'after'; S.phase = 'after'; S.holdUntil = Infinity; S.flowersAt = { x: c.x, y: c.y, t0: c.flowerT };
      const d = Math.atan2((c.y - BR.y) / 0.5, c.x - BR.x), sc = TCHorse.scaleAt(HO, c.y);
      Object.assign(BR, { tgt: [c.x - Math.cos(d) * 1.05 * sc, c.y - Math.sin(d) * 0.5 * 1.05 * sc], mode: 'walk', until: t + 30, forcedWalk: true });
      S.afterSniff = true;
    } else if (m === 'clean') { if (S.clean) S.flowersAt = { x: S.clean.x, y: S.clean.y, t0: S.clean.flowerT }; S.clean = null; mark('Z2', t); }
    if (m === 'feed') S.feed = null;
  }

  
  const FOOD = { esa: 'エサ', apple: 'リンゴ', carrot: 'ニンジン' };
  function useToken(t, k) {
    if (S.stock < 1) { fx({ k: 'tagUI', t0: t, x: BTN[k][0], y: BTN[k][1] - 150, txt: 'お世話トークンが たまるまで まってね', size: 30, dur: 1.8 }); ev(t, 'wait'); return false; }
    S.stock -= 1; S.stockDrop = t; ev(t, 'token'); return true;
  }
  function careLottery() {               
    if (O.lottery) return O.lottery();
    if (S.demo && S.demo.pt !== undefined) return S.demo.pt;
    const r = rnd(); let a = 0;
    for (const [p, v] of [[1 / 85, 100], [1 / 99, 200], [1 / 121, 300]]) { a += p; if (r < a) return v; }
    return null;
  }
  function pressFeed(t) {
    S.press.feed = t; ev(t, 'button');
    if (S.busy || S.phase !== 'idle' || BR.sl > 0.001) return;
    S.chooser = { t0: t, pick: null, pickT: null }; S.phase = 'choose'; S.mode = 'feed'; BR.careHold = true; S.holdUntil = Infinity; ev(t, 'chooser');
  }
  function pick(t, kind) {
    if (!S.chooser || S.chooser.pick) return;
    S.chooser.pick = kind; S.chooser.pickT = t; ev(t, 'pick');
    at(t + 0.5, tt => {
      S.chooser = null;
      if (!useToken(tt, 'feed')) { S.phase = 'idle'; S.mode = null; BR.careHold = false; return; }
      const gold = kind === 'carrot' && (S.demo && S.demo.gold != null ? S.demo.gold : rnd() < 1 / 30);
      S.feed = { kind, gold, fav: kind === S.fav, bites: 0, t0: tt }; S.popVal = careLottery();
      if (BR.stand) { BR.reacts = []; mark('A', tt); feedStart(tt); return; }          
      const fr = front(); if (Math.abs(BR.y - fr.y) < 36 && Math.abs(BR.x - fr.x) < (fr.big ? 50 : 280) && Math.abs(Math.sin(BR.dir)) < 0.4) arrived(tt); else approach(tt);
    });
  }
  function feedStart(t) {
    const F = S.feed; S.phase = 'feed'; mark('F', t); ev(t, 'feedstart');
    BR.want.look = [0, 0]; BR.reacts = (BR.reacts || []).filter(r => r.k !== 'look');      
    const s = TCHorse.scaleAt(HO, BR.y), n = P('nose');
    if (F.kind === 'esa') {             
      const tmp = Object.assign({}, BR, { graze: 1, look: [0, 0], lookS: [0, 0], reacts: [{ k: 'deep', t0: t - 2, dur: 4.4 }] }), mats = TCHorse.pose(HO, tmp, t);
      const gq = TCHorse.wherePose(HO, mats, 'nose', true) || [BR.x, BR.y], nq = TCHorse.wherePose(HO, mats, 'nose'), pq = TCHorse.wherePose(HO, mats, 'poll');
      
      
      const eq = TCHorse.wherePose(HO, mats, 'eye'), bx = nq ? (pq ? nq[0] * 0.86 + pq[0] * 0.14 : nq[0]) : gq[0];
      const by = gq[1] + 4, rimW = nq && eq ? nq[1] - 0.3 * (nq[1] - eq[1]) : by - 0.78 * s;
      const lh = clamp((by - rimW) / s - 0.48, 0.04, 0.9);          
      F.bucket = { x: bx, y: by, lh, level: 3, t0: t, hideT: null }; ev(t, 'unfold'); at(t + 0.35, tt => ev(tt, 'bucket'));
      const ds = [t + 1.7, t + 2.7, t + 3.7];          
      if (PROPS && PROPS.bucket) {                      
        const tmp1 = Object.assign({}, tmp, { reacts: [{ k: 'deep', t0: t - 2, dur: 4.4, ds: [t - 10] }] }), mats1 = TCHorse.pose(HO, tmp1, t);
        F.b3 = place3(TCHorse.anchorPose(HO, mats, 'nose'), TCHorse.anchorPose(HO, mats, 'eye'), TCHorse.anchorPose(HO, mats, 'poll'), TCHorse.anchorPose(HO, mats1, 'nose'), ds);
      }
      at(t + 0.8, tt => { S.grazeOK = true; BR.want.graze = 1; react('deep', F.b3 ? 4.8 : 4.4, tt, F.b3 ? { ds } : null); });
      for (let k = 0; k < 3; k++) at(t + 1.7 + k * 1.0, tt => { F.bucket.level = 2 - k; ev(tt, 'munch', { n: k }); const b = F.bucket, rw = F.b3 ? TCHorse.project(HO, [F.b3.cx, F.b3.R, F.b3.cz]) : null; fx({ k: 'crumbs', t0: tt, w: rw || [b.x, b.y - (b.lh + 0.48) * s], col: ['#e8c46a', '#d9a94a', '#f2dc94'] }); });
      at(t + 4.9, tt => { BR.want.graze = 0; S.grazeOK = false; });
      at(t + 5.4, tt => { react('lick', 1.3, tt, { side: sideToward(BR.x, BR.y + 200) }); ev(tt, 'lick'); tagW(P('nose'), 'ぺろっ', tt + 0.2, { off: [0, -90], size: 34 }); });
      at(t + 6.6, tt => { F.bucket.hideT = tt; ev(tt, 'fold'); });
      at(t + 7.2, tt => feedAfter(tt));
    } else {                            
      F.handT = t; F.itemW = itemPos(); ev(t, 'unfold');
      if (F.gold) at(t + 0.3, tt => { fx({ k: 'glint', t0: tt, dur: 3.2 }); ev(tt, 'gold'); tagW(P('nose'), '金のニンジン！', tt + 0.1, { off: [0, -150], size: 36, dur: 1.8, col: '#b07a10' }); });
      for (let k = 0; k < 3; k++) at(t + (F.gold ? 1.5 : 1.0) + k * 1.0, tt => {
        F.bites = k + 1; react('eat', 0.95, tt, { side: sideToward(BR.x, BR.y + 200) }); ev(tt, 'bite', { n: k, kind: F.kind });
        const q = F.itemW; fx({ k: 'crumbs', t0: tt, w: q, col: F.kind === 'apple' ? ['#f4efe0', '#d9343c', '#f7e9c8'] : F.gold ? ['#ffd65c', '#fff1b0', '#e9b13a'] : ['#f08a2a', '#ffb25c', '#f6c38a'] });
        if (k === 0) tagW(P('nose'), 'シャクッ', tt + 0.05, { off: [-20, -100], size: 34, dur: 1.0 });
      });
      at(t + (F.gold ? 4.2 : 3.7), tt => { F.handHide = tt; ev(tt, 'fold'); });
      at(t + (F.gold ? 4.6 : 4.1), tt => feedAfter(tt));
    }
  }
  function feedAfter(t) {                
    const F = S.feed; let end = t + 0.4;
    if (F.fav) { at(t + 0.1, tt => { react('happy', 2.6, tt); react('nod', 1.4, tt + 0.3); ev(tt, 'yummy'); tagW(P('poll'), 'だいすき！', tt + 0.1, { off: [30, -100], size: 40, dur: 2.0 });
      for (let k = 0; k < 5; k++) at(tt + 0.2 + k * 0.3, t2 => { const p = P('poll'); if (p) fx({ k: 'mini', t0: t2, w: [p[0] + (hash(t2 * 3) - 0.5) * 120, p[1] - 10], r: 22, dx: (hash(t2 * 7) - 0.5) * 70 }); ev(t2, 'heartpop'); }); }); end = t + 2.8; }
    if (F.gold) {                       
      for (let k = 0; k < 3; k++) at(t + 0.3 + k * 0.3, tt => {
        const q = toS(F.itemW || itemPos()), i = Math.min(S.heart, RULE.max - 1); fx({ k: 'fly', t0: tt, x: q[0], y: q[1], i, dur: 0.8 }); ev(tt, 'heart'); S.heart = Math.min(RULE.max, S.heart + 1);
        at(tt + 0.8, t2 => { S.heartShow = Math.max(S.heartShow, i + 1); ev(t2, 'slot', { n: i + 1 }); fx({ k: 'pop', t0: t2, x: SLOT(i)[0], y: SLOT(i)[1] }); });
      });
      at(t + 0.3, tt => tagW(P('poll'), 'なかよし +3', tt, { off: [30, -110], size: 38, dur: 1.8, col: '#c2456f' }));
      end = Math.max(end, t + 2.2);
    }
    const beg = S.demo && S.demo.beg != null ? S.demo.beg : rnd() < 1 / 4;
    if (beg) {                          
      at(end, tt => { S.phase = 'beg'; mark('B', tt); const side = sideToward(BR.x, BR.y + 200); react('beg', 6, tt, { side }); BR.want.look = [side * 0.6, 0.2]; ev(tt, 'beg');
        tagW(P('poll'), 'おかわり…？', tt + 0.2, { off: [30, -100], size: 34, dur: 2.4 }); S.begT = tt; });
      S.holdUntil = Infinity; S.phase = 'feedwait';
    } else { S.phase = 'feedwait'; S.holdUntil = end; at(end, tt => { S.phase = 'feeddone'; }); }
  }
  function begPet(t) {                   
    S.phase = 'feeddone'; BR.reacts = (BR.reacts || []).filter(r => r.k !== 'beg'); BR.want.look = [0, 0];
    react('nod', 1.4, t + 0.1); ev(t, 'rub'); fx({ k: 'mini', t0: t + 0.1, w: (P('poll') || [BR.x, BR.y]).slice(), r: 22, dx: 20 });
    tagW(P('poll'), 'まんぞく', t + 0.3, { off: [30, -100], size: 34, dur: 1.6 }); S.holdUntil = t + 1.9;
  }
  function itemPos() {                   
    const n = P('nose') || [BR.x, BR.y - 200], s = TCHorse.scaleAt(HO, BR.y);
    return [n[0] + Math.cos(BR.dir) * 0.02 * s, n[1] + 0.07 * s];
  }

  
  function season() { const m = (O.month || new Date().getMonth() + 1); return m >= 3 && m <= 5 ? 'spring' : m >= 6 && m <= 8 ? 'summer' : m >= 9 && m <= 11 ? 'autumn' : 'winter'; }
  function pressClean(t) {
    S.press.clean = t; ev(t, 'button');
    if (S.busy || S.phase !== 'idle') return;
    if (!useToken(t, 'clean')) return;
    S.mode = 'clean'; BR.careHold = true; S.holdUntil = Infinity; S.popVal = careLottery();
    const ps = BR.poops || []; let tg = null;
    if (ps.length) { const q = ps.reduce((a, b) => (b.y > a.y ? b : a)); BR.poops = ps.filter(x => x !== q); tg = { type: 'poop', x: q.x, y: q.y, img: q.img || 0, w: q.w || 0.42, gold: !!q.gold }; }
    else {                              
      const cx = BR.stand ? W / 2 : clamp(FRONT.x + (BR.x < FRONT.x ? 170 : -170), 260, 792), cy = BR.stand ? H * 0.82 : FRONT.y - 20, ss = season();
      tg = { type: 'leaves', x: cx, y: cy, ss, leaves: Array.from({ length: 11 }, (_, i) => ({ dx: (hash(i * 3.1) - 0.5) * 230, dy: (hash(i * 5.7) - 0.5) * 90, r: hash(i * 7.3) * TAU, s: 0.8 + 0.4 * hash(i * 2.9), c: i % 3 })) };
    }
    S.clean = { t0: t, x: tg.x, y: tg.y, tg, swipes: 0, prog: 0, sniff: tg.type === 'poop' };
    S.clean.pan = { x: tg.x - 120, y: tg.y + 6 };
    const z = BR.stand ? 1 : 1.7, hw = W / (2 * z), hh = H / (2 * z);
    if (z > 1) { S.phase = 'zoomin'; setZoom(t, { z, cx: clamp(tg.x - 20, hw, W - hw), cy: clamp(tg.y - 90, hh, H - hh) }, 0.9); ev(t, 'zoomin'); }
    else cleanStart(t);
    if (!BR.stand) { const side = sideToward(tg.x, tg.y); BR.want.look = [side * 0.6, -0.1]; }
  }
  function cleanStart(t) {
    const C = S.clean; S.phase = 'clean'; mark('C', t); C.toolT = t; ev(t, 'unfold'); at(t + 0.2, tt => ev(tt, 'unfold'));
    if (C.tg.gold) at(t + 0.2, tt => { tagW([C.x, C.y], '金のうんち！', tt, { off: [0, -120], size: 36, dur: 1.8, col: '#b07a10' }); ev(tt, 'gold'); });
  }
  function sweep(t) {                    
    const C = S.clean; C.swipes++; ev(t, 'sweep', { n: C.swipes });
    fx({ k: 'dust', t0: t, w: [lerp(C.x, C.pan.x + 30, C.swipes / 3), C.y] });
    const nose = P('nose'), br = S.finger;
    if (!C.nibbled && !BR.stand && nose && br && Math.hypot(nose[0] - br[0], nose[1] - br[1]) < 300 && (S.demo && S.demo.nibble != null ? S.demo.nibble : rnd() < 1 / 4) && C.swipes === 2) {
      C.nibbled = true; at(t + 0.1, tt => { react('nibble', 1.6, tt, { side: sideToward(br[0], br[1]) }); ev(tt, 'nibble'); tagW(P('nose'), 'もぐっ？', tt + 0.3, { off: [0, -100], size: 34, dur: 1.3 }); });
    }
    if (C.swipes >= 3) {
      at(t + 0.35, tt => { C.inPan = true; ev(tt, 'inpan'); });
      at(t + 0.8, tt => { C.foldT = tt; ev(tt, 'fold'); });
      at(t + 1.3, tt => { fx({ k: 'kira', t0: tt, w: [C.x, C.y] }); ev(tt, 'kira'); C.flowerT = tt + 0.2; tagW([C.x, C.y], 'きれい！', tt + 0.3, { off: [0, -130], size: 38, dur: 1.8 }); });
      if (C.tg.gold) at(t + 2.2, tt => { S.high = 5; S.highBump = tt; fx({ k: 'luck', t0: tt, dur: 2.6 }); ev(tt, 'luck'); });
      S.holdUntil = t + (C.tg.gold ? 5.0 : 3.4); S.phase = 'cleanwait'; at(S.holdUntil - 0.01, tt => { if (S.phase === 'cleanwait') S.phase = 'cleandone'; });
    }
  }

  
  function pressPet(t) {
    S.press.pet = t; ev(t, 'button');
    if (S.busy || S.phase !== 'idle') return;
    if (t < S.coolUntil) { fx({ k: 'tagUI', t0: t, x: BTN.pet[0] + 40, y: BTN.pet[1] - 150, txt: `あと ${Math.ceil(S.coolUntil - t)}秒`, size: 36, dur: 1.4 }); ev(t, 'wait'); return; }
    S.mode = 'pet'; BR.careHold = true; S.holdUntil = Infinity;
    if (BR.mode === 'sleep' || BR.sl > 0.001) { S.mode = null; BR.careHold = false; return; }      
    if (BR.stand) { BR.reacts = []; S.phase = 'pet'; S.petIdle = t; mark('A', t); mark('R', t); ev(t, 'ready2'); return; }      
    const fr = front(); if (Math.abs(BR.y - fr.y) < 36 && Math.abs(BR.x - fr.x) < (fr.big ? 50 : 280) && Math.abs(Math.sin(BR.dir)) < 0.4) arrived(t);
    else approach(t);
  }
  function pressCall(t, kind) {
    S.press.call = t; ev(t, 'button');
    if (S.busy || S.phase !== 'idle' || BR.sl > 0.001) return;
    kind = kind || ['come', 'turn', 'amae'][Math.floor(rnd() * 3) % 3];
    S.mode = 'call'; S.callKind = kind; BR.careHold = true; S.holdUntil = Infinity; ev(t, 'call', { kind });
    fx({ k: 'notes', t0: t });
    if (BR.stand) { BR.reacts = []; callArrive(t + 0.2); return; }       
    if (kind === 'turn') {             
      if (BR.mode === 'walk') BR.mode = 'idle';
      const want = Math.cos(BR.dir) >= 0 ? 0.6 : Math.PI - 0.6;
      if (Math.abs(angDiff(BR.dir, want)) > 0.25) { S.route = []; S.turnAfter = true; S.turnTarget = want; S.phase = 'approach'; }
      else callArrive(t + 0.25);
    } else approach(t);
  }
  function callArrive(t) {
    S.phase = 'callact'; BR.mode = 'idle'; BR.until = Math.max(BR.until, t + 6);
    const side = sideToward(BR.x, BR.y + 200);
    if (BR.stand) {                    
      if (S.callKind === 'come') { at(t, tt => { react('nod', 1.8, tt); react('happy', 2.2, tt); ev(tt, 'nod'); tagW(P('poll'), 'ぶるるっ', tt + 0.2, { off: [60, -60] }); }); S.holdUntil = t + 2.6; }
      else if (S.callKind === 'turn') { at(t, tt => { BR.want.look = [0.75, 0.05]; }); at(t + 0.9, tt => { BR.want.look = [0, 0.28]; ev(tt, 'turn'); tagW(P('poll'), '！', tt + 0.4, { off: [60, -60], size: 44 }); }); S.holdUntil = t + 3.6; }
      else { at(t, tt => { react('nuzzle', 3.4, tt, { side: 1 }); react('happy', 3.4, tt); ev(tt, 'amae'); tagW(P('poll'), 'すりすり', tt + 0.4, { off: [70, -60], dur: 2.0 }); });
        for (let k = 0; k < 4; k++) at(t + 0.5 + k * 0.62, tt => { const p = P('poll'); if (p) fx({ k: 'mini', t0: tt, w: [p[0] + (hash(tt * 3) - 0.5) * 90, p[1] - 10], r: 22, dx: (hash(tt * 7) - 0.5) * 60 }); ev(tt, 'heartpop'); });
        S.holdUntil = t + 4.0; }
      return;
    }
    if (S.callKind === 'come') {       
      at(t + 0.15, tt => { react('nod', 1.6, tt); react('swish', 2.0, tt + 0.3); ev(tt, 'nod'); tagW(P('poll'), 'ぶるるっ', tt + 0.2, { off: [30, -90] }); BR.want.look = [side * 0.5, 0.15]; });
      S.holdUntil = t + 2.6;
    } else if (S.callKind === 'turn') {  
      at(t, tt => { BR.want.look = [side * 1.0, 0.32]; ev(tt, 'turn'); });
      at(t + 0.7, tt => { tagW(P('poll'), '！', tt, { off: [20, -96], size: 44 }); react('swish', 1.8, tt); });
      S.holdUntil = t + 3.4;
    } else {                           
      at(t + 0.1, tt => { react('nuzzle', 3.4, tt, { side }); react('happy', 3.4, tt); BR.want.look = [side * 0.55, 0.05]; ev(tt, 'amae'); tagW(P('poll'), 'すりすり', tt + 0.4, { off: [30, -96], dur: 2.0 }); });
      for (let k = 0; k < 4; k++) at(t + 0.5 + k * 0.62, tt => { const p = P('poll'); if (p) fx({ k: 'mini', t0: tt, w: [p[0] + (hash(tt * 3) - 0.5) * 60, p[1] - 20], r: 22, dx: (hash(tt * 7) - 0.5) * 60 }); ev(tt, 'heartpop'); });
      S.holdUntil = t + 4.0;
    }
  }

  
  function startSession(t, x, y, z) {
    S.ses = { t0: t, n: 0, dist: 0, zone: z.zone, down: false, last: [x, y], upT: null };
    S.hand = { t0: t, hideT: null };
    ev(t, 'unfold');
    if (O.tod === 'morning' && !S.greeted) { S.greeted = true; at(t + 0.35, tt => { react('nod', 1.5, tt); ev(tt, 'nod'); }); }      
  }
  function stroke(t, x, y) {
    S.ses.n++; S.petIdle = t; ev(t, 'rub', { n: S.ses.n });
    fx({ k: 'mini', t0: t, w: [x + (hash(t * 7) - 0.5) * 24, y - 14], r: 19, dx: (hash(t * 3) - 0.5) * 40 });
    if (S.ses.n >= RULE.strokes) complete(t, x, y);
  }
  function complete(t, x, y) {
    const z = S.ses.zone, side = sideToward(x, y), slow = O.tod === 'evening' ? 1.35 : 1;
    const ZR = { head: ['nuzzle', 2.6, 'すりすり'], neck: ['swish', 2.4, 'ふりふり'], back: ['stretch', 4.6, 'ぐーっ'], nose: ['sneeze', 1.5, 'ぷしゅっ'] };
    let [rk, rd, rt] = ZR[z] || ZR.neck;
    const rare = S.demo && S.demo.rare != null ? S.demo.rare : rnd() < 1 / 20;
    if (rare) { rk = 'tilt'; rd = 1.9; rt = '？'; }
    rd *= slow;
    at(t + 0.25, tt => {
      react(rk, rd, tt, { side }); ev(tt, rk);
      const hp = rk === 'sneeze' ? P('nose') : rk === 'swish' ? P('rump') : rk === 'stretch' ? P('withers') : P('poll');
      tagW(hp || [x, y], rt, tt, { off: rk === 'swish' ? [-40, -60] : [26, -96], dur: 1.5 * slow });
      if (rk === 'sneeze' && hp) fx({ k: 'bits', t0: tt + 0.62, w: hp.slice() });
    });
    let end = t + 0.25 + rd;
    if (O.tod === 'evening') { at(end - 0.6, tt => { react('calm', 3.6, tt, { side }); ev(tt, 'calm'); tagW(P('poll'), 'ふぅ〜', tt + 0.4, { off: [36, -90], size: 34, dur: 2.0, rot: 0.06 }); }); end += 3.0; }
    if (O.stageNo <= 2) { at(end - 0.3, tt => { react('frisk', 2.2, tt, { side }); ev(tt, 'frisk'); tagW(P('poll'), 'るんっ', tt + 0.2, { off: [30, -96], dur: 1.4, rot: -0.08 }); }); end += 1.9; }
    if (O.tod === 'night') {
      at(end - 0.4, tt => { react('yawn', 2.0, tt); ev(tt, 'yawn'); tagW(P('poll'), 'ふわぁ…', tt + 0.3, { off: [36, -96], size: 34, dur: 1.8, rot: 0.05 }); });
      at(end + 1.7, tt => { Object.assign(BR, { mode: 'sleep', until: tt + 600, sleepT: tt, sl: 0, rise: 0, doze: 0, lieDoneT: 0, lieDur: null, flop: null }); ev(tt, 'lie'); });
      end += 3.6;
    }
    
    S.got = S.got.filter(q => t - q < 60);
    if (S.got.length >= RULE.perMin) { at(t + 0.5, tt => { fx({ k: 'note', t0: tt, txt: 'ハートは 1分に 5こまで', dur: 2.6 }); ev(tt, 'nope'); }); }
    else {
      S.got.push(t); const i = Math.min(S.heart, RULE.max - 1), q = toS([x, y - 24]);
      fx({ k: 'fly', t0: t + 0.15, x: q[0], y: q[1], i, dur: 0.8 }); ev(t + 0.15, 'heart');
      S.heart = Math.min(RULE.max, S.heart + 1);
      at(t + 0.95, tt => { S.heartShow = Math.max(S.heartShow, i + 1); ev(tt, 'slot', { n: i + 1 }); fx({ k: 'pop', t0: tt, x: SLOT(i)[0], y: SLOT(i)[1] }); });
      if (S.heart >= RULE.max) { S.busy = true; at(t + 1.45, lottery); }
    }
    S.coolUntil = t + RULE.cool; S.coolFrom = t; S.readyT = S.coolUntil;
    S.hand.hideT = t + 0.55; at(t + 0.55, tt => ev(tt, 'fold'));
    S.holdUntil = end + 0.5; S.ses.done = true;
  }
  
  function lottery(t) {
    const win = S.demo && S.demo.win != null ? S.demo.win : rnd() < RULE.win;
    S.lot = { t0: t, win }; ev(t, 'max'); S.holdUntil = Infinity;
    at(t + 0.9, tt => { react('gather', 1.0, tt); ev(tt, 'gather'); });
    if (win) {
      at(t + 1.7, tt => { react('hop', 2.4, tt); for (let k = 0; k < 2; k++) ev(tt + 0.1 + 1.12 * k, 'frisk', { n: k }); fx({ k: 'burst', t0: tt + 0.35, w: (P('withers') || [BR.x, BR.y - 200]).slice() }); });      
      at(t + 4.1, tt => { fx({ k: 'unlock', t0: tt, dur: 2.6 }); ev(tt, 'unlock'); });
      at(t + 4.6, tt => { S.stockBump = tt; S.stock = Math.min(RULE.stockMax, S.stock + RULE.unlock); fx({ k: 'plus', t0: tt, txt: '+' + RULE.unlock }); ev(tt, 'stock'); });
      at(t + 2.6, tt => { S.drainT = tt; });
      at(t + 6.6, tt => { S.busy = false; S.lot = null; S.holdUntil = tt + 0.3; });
    } else {
      at(t + 1.7, tt => { Object.assign(BR, { mode: 'sleep', until: tt + 2.4 + 2.1 + 1.7, sleepT: tt, sl: 0, rise: 0, doze: 0, lieDoneT: 0, lieDur: 2.4, flop: tt }); ev(tt, 'flop'); });
      at(t + 3.9, tt => { tagW(P('withers') || [BR.x, BR.y], 'ごろん', tt, { off: [20, -110], size: 40, dur: 2.0, rot: -0.06 }); ev(tt, 'goron'); });
      at(t + 3.3, tt => { S.drainT = tt; });
      at(t + 8.1, tt => { S.busy = false; S.lot = null; S.holdUntil = tt + 0.2; });
    }
  }
  
  function input(kind, x, y, t) {
    if (S.phase === 'beg' && kind === 'down' && zoneAt(x, y)) { begPet(t); S.finger = [x, y]; S.begHand = t; return; }
    if (S.mode === 'clean' && S.phase === 'clean') {         
      const C = S.clean; S.finger = [x, y];
      if (kind === 'down') { C.down = true; C.last = [x, y]; C.dist = 0; }
      else if (kind === 'move' && C.down) { const dx = x - C.last[0], dy = y - C.last[1]; C.last = [x, y]; const toward = (C.pan.x - C.x) >= 0 ? dx : -dx; if (toward > 0) C.dist += toward * S.zoom.z; if (C.dist >= 70 && !C.counted) { C.counted = true; sweep(t); } }
      else if (kind === 'up') { C.down = false; C.counted = false; C.dist = 0; }
      return;
    }
    if (kind === 'down') {
      if (S.ses && !S.ses.done) { S.ses.down = true; S.ses.last = [x, y]; S.ses.dist = 0; S.ses.counted = false; S.ses.sdir = null; S.finger = [x, y]; return; }
      if (S.phase !== 'pet' || S.busy) return;
      const z = zoneAt(x, y); if (!z) return;
      startSession(t, x, y, z); S.ses.down = true; S.finger = [x, y]; S.petIdle = t;
    } else if (kind === 'move') {
      S.finger = [x, y]; const s = S.ses; if (!s || s.done || !s.down) return;
      const dx = x - s.last[0], dy = y - s.last[1], d = Math.hypot(dx, dy); s.last = [x, y]; if (d < 0.01) return;
      
      if (s.sdir && (dx * s.sdir[0] + dy * s.sdir[1]) / d < -0.3) { s.dist = 0; s.counted = false; }
      s.sdir = [dx / d, dy / d];
      const z = zoneAt(x, y); if (z) { s.dist += d * S.zoom.z; s.zone = z.zone; }
      if (s.dist >= RULE.strokeLen && !s.counted) { s.counted = true; stroke(t, x, y); }
    } else if (kind === 'up') { if (S.ses) { S.ses.down = false; S.ses.upT = t; S.ses.dist = 0; S.ses.counted = false; S.ses.sdir = null; } }
  }

  
  
  const SPOT = {
    neckA: () => mixP(P('poll'), P('withers'), 0.3), neckB: () => mixP(P('poll'), P('withers'), 0.74),
    headA: () => mixP(P('poll'), P('eye'), 0.1), headB: () => mixP(P('eye'), P('nose'), 0.45),
    backA: () => mixP(P('withers'), P('rump'), 0.12), backB: () => mixP(P('withers'), P('rump'), 0.66),
    noseA: () => mixP(P('eye'), P('nose'), 0.3), noseB: () => mixP(P('eye'), P('nose'), 1.0),
    awayR: () => { const n = P('nose'), b = P('withers'); return toW(n && b && n[0] > b[0] ? [W * 0.2, H * 0.8] : [W * 0.8, H * 0.8]); },     
    brA: () => { const C = S.clean; if (!C) return null; const p = cleanTgPos(), d = C.x >= C.pan.x ? 1 : -1; return [p[0] + 150 * d, p[1] + 4]; },      
    brB: () => { const C = S.clean; if (!C) return null; const p = cleanTgPos(), d = C.x >= C.pan.x ? 1 : -1; return [p[0] + 14 * d, p[1] + 4]; },
  };
  
  function strokes(u0, A, B, n, ds, dr) {
    ds = ds || 0.6; dr = dr || 0.34; const out = []; let u = u0;
    for (let i = 0; i < n; i++) { out.push([u, u + ds, A, B, true]); u += ds; if (i < n - 1) { out.push([u, u + dr, B, A, false]); u += dr; } }
    return out;
  }
  const PET3 = (A, B, ds, dr, u0) => { u0 = u0 || 0.25; const st = strokes(u0 + 0.7, A, B, 3, ds || 0.58, dr || 0.33), e = st[st.length - 1][1]; return [[u0, u0 + 0.7, 'awayR', A, false], ...st, [e + 0.1, e + 1.0, B, 'awayR', false]]; };
  const DEMOS = {
    
    pet_a: { press: [[1.0, 'pet'], ['Z+1.4', 'pet']], cap: [[0.2, 'A+0.3', '「撫でる」を押すと 手前に 来るよ'], ['A+0.3', 'R+3.0', '近くで ズーム → 指で なぞってね'], ['R+3.0', 'Z-0.2', '3回 なでると なかよしハート +1'], ['Z-0.2', 'Z+4.4', '撫でたあとは 7秒 なでられない']],
      path: [[0.25, 0.95, 'awayR', 'neckA', false], [0.95, 2.3, 'neckA', 'neckA', true], ...strokes(2.3, 'neckA', 'neckB', 3, 0.6, 0.34), [4.3, 5.3, 'neckB', 'awayR', false]], greeted: false, end: 'Z+4.6' },
    
    pet_b: { front: 1, heart: 1, got: [-20], greeted: true, cap: [[0.2, 'R+5.6', '頭を なでると → すりすり']], path: PET3('headA', 'headB', 0.55, 0.32), end: 'R+5.8' },
    pet_d: { front: 1, heart: 2, got: [-25, -14], greeted: true, cap: [[0.2, 'R+8.0', '背中を なでると → ぐーっと のび']], path: PET3('backA', 'backB', 0.6, 0.34), end: 'R+8.2' },
    pet_e: { front: 1, heart: 3, got: [-30, -20, -10], greeted: true, cap: [[0.2, 'R+5.0', '鼻を なでると → ぷしゅっ']], path: PET3('noseA', 'noseB', 0.5, 0.3), end: 'R+5.2' },
    
    pet_f: { front: 1, heart: 5, got: [-50, -41, -30, -19, -8], greeted: true, cap: [[0.2, 'R+6.0', 'ハートは 1分に 5こまで']], path: PET3('neckA', 'neckB'), end: 'R+6.2' },
    
    pet_g: { front: 1, heart: 9, got: [], greeted: true, win: false, cap: [[0.2, 'R+3.4', 'ハートが 10こに なると…'], ['R+3.4', 'R+13.0', '抽選（1/66）→ ハズレは ごろん']], path: PET3('neckA', 'neckB'), end: 'R+13.2' },
    pet_h: { front: 1, heart: 9, got: [], greeted: true, win: true, cap: [[0.2, 'R+3.4', 'ハートが 10こに なると…'], ['R+3.4', 'R+11.2', '当たり → ぴょん！ お世話 5回 解放']], path: PET3('neckA', 'neckB'), end: 'R+11.4' },
    
    pet_i: { front: 1, heart: 2, got: [-30, -15], greeted: true, cap: [[0.2, 'R+9.6', '夕方は ゆったり よりかかる']], path: PET3('neckA', 'neckB', 0.7, 0.4), end: 'R+9.8' },
    pet_j: { front: 1, heart: 3, got: [-30, -15], greeted: true, cap: [[0.2, 'R+13.0', '夜は あくびを して ねむる']], path: PET3('neckA', 'neckB', 0.7, 0.4), end: 'R+13.2' },
    pet_k: { front: 1, heart: 2, got: [-30, -15], greeted: true, cap: [[0.2, 'R+7.2', '小さい ころは はしゃぐ']], path: PET3('neckA', 'neckB', 0.5, 0.3), end: 'R+7.4' },
    pet_l: { front: 1, heart: 2, got: [-30, -15], greeted: true, rare: true, cap: [[0.2, 'R+5.4', 'たまに（1/20）首を かしげる']], path: PET3('headA', 'headB', 0.55, 0.32), end: 'R+5.6' },
    
    call_a: { press: [[0.9, 'call', 'come']], cap: [[0.2, 'Z+0.4', '呼ぶ：近づいて くる']], end: 'Z+0.6' },
    call_b: { press: [[0.9, 'call', 'turn']], cap: [[0.2, 'Z+0.4', '呼ぶ：振り向く']], end: 'Z+0.6' },
    call_c: { press: [[0.9, 'call', 'amae']], cap: [[0.2, 'Z+0.4', '呼ぶ：甘える']], end: 'Z+0.6' },
    
    feed_a: { press: [[0.8, 'feed'], [2.3, 'pick', 'esa']], pt: null, beg: false, cap: [[0.2, 2.7, 'ごはん：エサ・リンゴ・ニンジンから えらぶ'], [2.7, 'Z-0.2', 'エサ → バケツから もぐもぐ（3回で からっぽ）']], end: 'Z+0.6' },
    feed_b: { press: [[0.6, 'feed'], [1.9, 'pick', 'apple']], pt: 100, beg: false, cap: [[0.2, 'F+0.2', 'リンゴ・ニンジン → 手から 3口'], ['F+0.2', 'F+3.8', 'シャクッ・シャクッ・シャクッ'], ['F+3.8', 'Z+0.1', '今日の 好物だと 大よろこび'], ['Z+0.1', 'Z+2.4', '当たり → ピロン']], end: 'Z+2.5' },
    feed_c: { heart: 2, got: [], press: [[0.6, 'feed'], [1.9, 'pick', 'carrot']], gold: true, pt: null, beg: true, pathBase: 'B', path: [[0.7, 1.3, 'awayR', 'headA', false], [1.3, 1.45, 'headA', 'headA', true], [1.45, 2.2, 'headA', 'awayR', false]],
      cap: [[0.2, 'F+0.4', 'ニンジンは 1/30で 金のニンジン'], ['F+0.4', 'B-0.2', '金のニンジン → なかよし +3'], ['B-0.2', 'Z+0.2', 'おかわりの目 → なでると まんぞく']], end: 'Z+0.6' },
    feed_d: { press: [[0.6, 'feed'], [1.9, 'pick', 'carrot']], gold: false, pt: null, beg: false, cap: [[0.2, 'F+0.2', 'ニンジン → 手から 3口'], ['F+0.2', 'Z+0.2', '先から シャクッ・シャクッ・シャクッ']], end: 'Z+0.6' },
    ban_k: { rt: [6.4, 6.7], cap: [], end: 10.6 },          
    ban_m: { rt: [6.4, 6.7], cap: [], end: 10.6 },
    
    clean_a: { poop: [770, 1240, 0], nibble: true, pt: null, press: [[0.8, 'clean']], pathBase: 'C', path: [[0.15, 0.6, 'brA', 'brA', false], ...strokes(0.6, 'brA', 'brB', 3, 0.5, 0.36)],
      cap: [[0.2, 'C+0.5', 'おそうじ：うんちを ほうきで はく'], ['C+0.5', 'C+3.5', '3回 はくと ちりとりへ（ときどき かじられる）'], ['C+3.5', 'Z2+0.2', 'きれいに なると 花が さく → くんくん']], end: 'Z2+0.4' },
    clean_b: { pt: 200, month: 11, press: [[0.8, 'clean']], pathBase: 'C', path: [[0.15, 0.6, 'brA', 'brA', false], ...strokes(0.6, 'brA', 'brB', 3, 0.5, 0.36)],
      cap: [[0.2, 'C+3.8', 'うんちが ない 時は 落ち葉（季節で かわる）'], ['C+3.8', 'Z+0.1', 'きれい！'], ['Z+0.1', 'Z+2.4', '当たり → ピロン']], end: 'Z+2.5' },
    guide: { press: [[0.8, 'help']], guideEnd: 15.8, cap: [], end: 16.8 },
    clean_c: { poop: [700, 1250, 2, true], pt: null, press: [[0.8, 'clean']], pathBase: 'C', path: [[0.15, 0.6, 'brA', 'brA', false], ...strokes(0.6, 'brA', 'brB', 3, 0.5, 0.36)],
      cap: [[0.2, 'C+3.4', '金のうんち（うんちの 1/20）'], ['C+3.4', 'Z2+0.2', '運がついた！ 高確ゾーン（お世話 5回）']], end: 'Z2+0.4' },
  };
  function tu(v) {                     
    if (typeof v === 'number') return v;
    const m = /^([A-Z][0-9]?)([+-][\d.]+)?$/.exec(v); const b = S.marks[m[1]]; return b == null ? Infinity : b + Number(m[2] || 0);
  }
  function demoFinger(u) {             
    const D = S.demo, R = S.marks[D.pathBase || 'R']; if (R == null || !D.path) return null; const v = u - R; let cur = null;
    for (const sg of D.path) if (v >= sg[0]) cur = sg;
    if (!cur) return null;
    const [u0, u1, A, B, down] = cur, k = clamp((v - u0) / (u1 - u0), 0, 1);
    if (v > u1 + 0.5) return null;                                       
    if (A === B) { if (cur.hold == null) cur.hold = SPOT[A](); return cur.hold ? { p: cur.hold.slice(), down: down && v < u1 } : null; }      
    const a = SPOT[A](), b = SPOT[B](); if (!a || !b) return null;
    const e = down ? easeIO(k) : easeOut(k), p = mixP(a, b, e);
    if (!down && k > 0 && k < 1) p[1] -= 22 / S.zoom.z * Math.sin(Math.PI * k);      
    return { p, down: down && v < u1 };
  }

  
  
  
  
  
  const B3 = { yaw: 0.31, rimK: 0.25, feedR: 0.88, feedH: 0.62, inner: [[1.0, 0.43], [1.2, 0.46], [1.4, 0.5], [1.6, 0.53], [1.8, 0.55], [2.0, 0.52], [2.15, 0.48]] };      
  function innerR(yp) { const T = B3.inner; if (yp <= T[0][0]) return T[0][1]; for (let i = 1; i < T.length; i++) if (yp <= T[i][0]) { const [y0, r0] = T[i - 1], [y1, r1] = T[i]; return lerp(r0, r1, (yp - y0) / (y1 - y0)); } return T[T.length - 1][1]; }
  function place3(n0, e0, p0, n1, ds) {
    if (!n0 || !e0 || !p0 || !n1) return null;
    const R = n0[1] + B3.rimK * (e0[1] - n0[1]);
    return { cx: n0[0] * 0.86 + p0[0] * 0.14, cz: n0[2] * 0.86 + p0[2] * 0.14, R, sB: R / 2.15, top0: n0[1] + 0.012, top1: n1[1] + 0.012, ds };
  }
  function props3(t) {
    const F = S.feed, b = F && F.bucket, q = F && F.b3; if (!b || !q || !PROPS) return null;
    const op = b.hideT != null ? 1 - sm((t - b.hideT) / 0.45) : backOut((t - b.t0) / 0.45); if (op <= 0.01) return null;
    const M = TCHorse.M, ox = 0.86 + 0.14 * clamp(op, 0, 1.2), oy = Math.max(0.02, op);
    const mB = M.mul(M.tr(q.cx, 0, q.cz), M.mul(M.ry(B3.yaw), M.sc(q.sB * ox, q.sB * oy, q.sB * ox)));
    const out = [{ P: PROPS.bucket, m: mB, sh: [q.cx, q.cz, 0.8 * q.sB * ox, 0.8 * clamp(op, 0, 1)] }];
    if (PROPS.feed) {
      const d = q.ds.reduce((a, s) => a + sm((t - s) / 0.45), 0) / q.ds.length;          
      const top = lerp(q.top0, q.top1, d) * oy, rf0 = B3.feedR * innerR(1.75) * q.sB;      
      const hf = B3.feedH * rf0 * (1 - 0.6 * d) * oy, base = top - hf, rf = Math.min(rf0, B3.feedR * innerR(base / q.sB) * q.sB) * ox;
      out.push({ P: PROPS.feed, m: M.mul(M.tr(q.cx, base, q.cz), M.mul(M.ry(0.7), M.sc(rf / 2.65, hf / 2.15, rf / 2.65))) });
    }
    return out;
  }
  async function loadProps() {          
    if (!HO || !HO.gl || typeof TCHorse === 'undefined' || !TCHorse.createProp) return null;
    const one = async nm => {
      const meta = await fetch(AP(`tc_items/${nm}.json`)).then(r => { if (!r.ok) throw new Error(nm); return r.json(); });
      const bin = await fetch(AP(`tc_items/${meta.bin || nm + '.bin'}`)).then(r => { if (!r.ok) throw new Error(nm); return r.arrayBuffer(); });
      const im = f => f ? new Promise(ok => { const i = new Image(); i.onload = () => ok(i); i.onerror = () => ok(null); i.src = AP(`tc_items/${f}`); }) : Promise.resolve(null);
      const [texImg, nrmImg] = await Promise.all([im(meta.tex), im(meta.ntex)]);
      return TCHorse.createProp(HO.gl, meta, bin, { texImg, nrmImg });
    };
    try { const [b3, f3] = await Promise.all([one('tc_prop_bucket'), one('tc_prop_feed').catch(() => null)]); return { bucket: b3, feed: f3 }; } catch (e) { return null; }
  }
  function bucketArt(x, y, k, level, op, legH) {      
    if (op <= 0.01) return;
    g.save(); g.translate(x, y); g.scale(1, op); g.lineWidth = 0.8;
    const sw = 0.5 * k, lh = (legH != null ? legH : 0.3) * k, bh = 0.42 * k, tw = 0.5 * k, bw = 0.38 * k;
    g.fillStyle = 'rgba(40,20,5,0.22)'; g.beginPath(); g.ellipse(0, 0, sw * 0.62, sw * 0.16, 0, 0, TAU); g.fill();
    for (const sx of [-1, 1]) { pf([[sx * sw * 0.36 - 4, -lh], [sx * sw * 0.36 + 4, -lh], [sx * sw * 0.42 + 4, 0], [sx * sw * 0.42 - 4, 0]], sx < 0 ? '#9c6a3c' : '#7e5330'); }      
    pf([[-sw / 2, -lh - 0.06 * k], [sw / 2, -lh - 0.06 * k], [sw / 2, -lh], [-sw / 2, -lh]], '#b98552'); pf([[-sw / 2, -lh], [sw / 2, -lh], [sw / 2, -lh + 6], [-sw / 2, -lh + 6]], '#8e6238');      
    const y0 = -lh - 0.06 * k, y1 = y0 - bh;
    pf([[-bw / 2, y0], [0, y0], [0, y1], [-tw / 2, y1]], '#d49a5c'); pf([[0, y0], [bw / 2, y0], [tw / 2, y1], [0, y1]], '#b9793f');      
    for (const f of [0.2, 0.75]) { const yy = lerp(y0, y1, f), hw = lerp(bw, tw, f) / 2; pf([[-hw - 1, yy - 4], [hw + 1, yy - 4], [hw + 1, yy + 4], [-hw - 1, yy + 4]], '#8d8f96'); pf([[0, yy - 4], [hw + 1, yy - 4], [hw + 1, yy + 4], [0, yy + 4]], '#6f7178'); }
    g.lineWidth = 1.2; for (let q = -2; q <= 2; q++) line([q * bw / 6, y0], [q * tw / 6, y1], 'rgba(90,50,20,0.25)');
    g.fillStyle = '#7a4a22'; g.beginPath(); g.ellipse(0, y1, tw / 2, tw * 0.16, 0, 0, TAU); g.fill();       
    if (level > 0) {                                   
      const hh = [0, 0.05, 0.1, 0.16][level] * k;
      g.fillStyle = '#e2b858'; g.beginPath(); g.ellipse(0, y1 - hh * 0.3, tw * 0.44, tw * 0.13, 0, 0, TAU); g.fill();
      pf([[-tw * 0.4, y1], [-tw * 0.15, y1 - hh], [tw * 0.12, y1 - hh * 0.8], [tw * 0.4, y1]], '#f0cf73'); pf([[tw * 0.12, y1 - hh * 0.8], [tw * 0.4, y1], [0, y1 + 2]], '#d6aa4a');
      for (let i = 0; i < 9; i++) { const gx = (hash(i * 3.3) - 0.5) * tw * 0.7, gy = y1 - hh * (0.2 + 0.6 * hash(i * 7.7)); pf([[gx - 4, gy], [gx, gy - 3], [gx + 4, gy], [gx, gy + 3]], i % 2 ? '#fff0b8' : '#c99a3c'); }
    }
    g.restore();
  }
  const APPLE_C = typeof document !== 'undefined' ? document.createElement('canvas') : null;
  function appleArt(x, y, r, bites, a, flip) {         
    if (!apple || !apple.naturalWidth || a <= 0.01) return;
    const w = r * 2, h = w * apple.naturalHeight / apple.naturalWidth, c = APPLE_C; c.width = Math.ceil(w) + 4; c.height = Math.ceil(h) + 4; const q = c.getContext('2d');
    q.clearRect(0, 0, c.width, c.height); q.drawImage(apple, 2, 2, w, h);
    const nb = Math.min(3, bites | 0);
    if (nb > 0) {
      const B = [[1.0, 0.45, 0.13], [0.98, 0.66, 0.15], [0.86, 0.56, 0.19]];          
      q.globalCompositeOperation = 'source-atop'; q.fillStyle = '#fff2d6';
      for (let i = 0; i < nb; i++) { const [bx, by, br] = B[i]; polyP(q, 2 + w * bx, 2 + h * by, w * (br + 0.035), 11, i * 0.8); q.fill(); }
      q.globalCompositeOperation = 'destination-out'; q.fillStyle = '#000';
      for (let i = 0; i < nb; i++) { const [bx, by, br] = B[i]; polyP(q, 2 + w * bx, 2 + h * by, w * br, 11, i * 0.8); q.fill(); }
      q.globalCompositeOperation = 'source-over';
    }
    g.save(); g.globalAlpha *= a; g.translate(x, y); if (flip) g.scale(-1, 1); g.drawImage(c, -w / 2 - 2, -h / 2 - 2); g.restore();
  }
  
  const CAR = { tip: [8.8, 498.9], u: [0.6852, -0.7283], len: 411.5, wp: [3.6, 26.2, 48.1, 68.6, 84.9, 102.6, 120.2, 133.7, 141.6, 129.4, 31.9] };     
  const carW = f => { const i = clamp(f, 0, 0.9999) * 10, k = Math.floor(i); return lerp(CAR.wp[k], CAR.wp[k + 1], i - k); };
  const CAR_C = {};
  function carrotCanvas(bites, gold) {
    const im = gold ? carrotG : carrot; if (!im || !im.naturalWidth) return null;
    const nb = Math.min(3, bites | 0), key = (gold ? 'g' : 'n') + nb; if (CAR_C[key]) return CAR_C[key];
    const c = document.createElement('canvas'); c.width = im.naturalWidth; c.height = im.naturalHeight; const q = c.getContext('2d'); q.drawImage(im, 0, 0);
    if (nb > 0) {
      const [ux, uy] = CAR.u, nx = -uy, ny = ux, dc = CAR.len * 0.27 * nb, w = carW(dc / CAR.len), rim = 9;
      const cut = (o, grow) => {           
        const bx = CAR.tip[0] + ux * (dc + o), by = CAR.tip[1] + uy * (dc + o);
        q.beginPath(); q.moveTo(bx + nx * 500, by + ny * 500); q.lineTo(bx + nx * 500 - ux * 1200, by + ny * 500 - uy * 1200); q.lineTo(bx - nx * 500 - ux * 1200, by - ny * 500 - uy * 1200); q.lineTo(bx - nx * 500, by - ny * 500); q.closePath(); q.fill();
        for (let j = -1; j <= 1; j++) { polyP(q, bx + nx * j * w * 0.32 + ux * w * 0.02, by + ny * j * w * 0.32 + uy * w * 0.02, w * 0.24 + grow, 9, j * 0.7 + nb); q.fill(); }
      };
      q.globalCompositeOperation = 'source-atop'; q.fillStyle = gold ? '#fff0ad' : '#ffc684'; cut(rim, rim * 0.6);
      q.globalCompositeOperation = 'destination-out'; q.fillStyle = '#000'; cut(0, 0);
      q.globalCompositeOperation = 'source-over';
    }
    return (CAR_C[key] = c);
  }
  function carrotHeld(qx, qy, side, L, bites, gold, a) {   
    const c = carrotCanvas(bites, gold); if (!c || a <= 0.01) return;
    const nb = Math.min(3, bites | 0), dc = CAR.len * 0.27 * nb, px = CAR.tip[0] + CAR.u[0] * dc, py = CAR.tip[1] + CAR.u[1] * dc;
    const s = L / CAR.len, th = Math.atan2(-0.27, 0.96) - Math.atan2(CAR.u[1], CAR.u[0]);
    g.save(); g.globalAlpha *= a; g.translate(qx, qy); g.scale(side, 1); g.rotate(th); g.scale(s, s); g.drawImage(c, -px, -py); g.restore();
  }
  function broomArt(x, y, k, rot, a) {                 
    if (a <= 0.01) return;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot); g.lineWidth = 0.8;
    const bw = 0.34 * k, bh = 0.26 * k, hl = 0.95 * k;
    g.fillStyle = 'rgba(40,20,5,0.18)'; g.beginPath(); g.ellipse(4, 4, bw * 0.6, 7, 0, 0, TAU); g.fill();
    pf([[-4, -bh - hl], [4, -bh - hl], [5, -bh], [-5, -bh]], '#b07a46'); pf([[0, -bh - hl], [4, -bh - hl], [5, -bh], [0, -bh]], '#8c5c32');       
    pf([[-bw * 0.32, -bh], [bw * 0.32, -bh], [bw / 2, 0], [-bw / 2, 0]], '#f2cd62'); pf([[0, -bh], [bw * 0.32, -bh], [bw / 2, 0], [0, 0]], '#d9ad43');      
    pf([[-bw * 0.34, -bh - 6], [bw * 0.34, -bh - 6], [bw * 0.33, -bh + 6], [-bw * 0.33, -bh + 6]], '#d9534f');       
    g.lineWidth = 1.6; for (let q = -3; q <= 3; q++) line([q * bw * 0.08, -bh + 8], [q * bw * 0.14, -2], 'rgba(120,80,20,0.35)');
    g.restore();
  }
  function panArt(x, y, k, dirX, a, fold) {            
    if (a <= 0.01 || fold >= 0.999) return;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.scale(dirX * (1 - fold), 1 - 0.3 * fold); g.lineWidth = 0.8;
    const w = 0.42 * k, d = 0.18 * k, hw = 0.2 * k;
    g.fillStyle = 'rgba(40,20,5,0.2)'; g.beginPath(); g.ellipse(0, 4, w * 0.62, 9, 0, 0, TAU); g.fill();
    pf([[-w * 0.1, -hw * 0.5], [w * 0.5, -d * 0.4], [w * 0.5, d * 0.4], [-w * 0.1, hw * 0.5]], '#7ec3d9');     
    pf([[-w * 0.5, -hw], [-w * 0.1, -hw * 0.5], [-w * 0.1, hw * 0.5], [-w * 0.5, hw * 0.2]], '#5aa7c4');     
    pf([[-w * 0.5, -hw], [-w * 0.1, -hw * 0.5], [w * 0.5, -d * 0.4], [w * 0.36, -d * 0.62]], '#9bd3e6');
    pf([[-w * 0.5, -hw * 0.3], [-w * 0.95, -hw * 0.75], [-w * 0.95, -hw * 0.55], [-w * 0.5, -hw * 0.1]], '#3f86a6');     
    g.restore();
  }
  function leafArt(x, y, sz, rot, ss, c, a) {
    if (a <= 0.01) return;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot); g.lineWidth = 0.6;
    if (ss === 'autumn') {                             
      const col = ['#e2552d', '#f08a2a', '#c9402a'][c], R = sz, P5 = [];
      for (let i = 0; i < 10; i++) { const an = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? R * 0.42 : R; P5.push([Math.cos(an) * rr, Math.sin(an) * rr * 0.62]); }
      pf(P5, col); pf([[0, 0], ...P5.slice(0, 6)], tone(col, 1.12)); line([0, 0], [0, R * 0.7], 'rgba(90,30,10,0.4)');
    } else if (ss === 'spring') { const col = ['#ffc0d4', '#ffd7e2', '#f7a8c2'][c]; g.scale(1, 0.62); pf([[0, -sz], [sz * 0.7, -sz * 0.2], [sz * 0.3, sz * 0.7], [0, sz * 0.45], [-sz * 0.3, sz * 0.7], [-sz * 0.7, -sz * 0.2]], col); pf([[0, -sz], [sz * 0.7, -sz * 0.2], [0, sz * 0.45]], tone(col, 1.08)); }
    else if (ss === 'summer') { const col = ['#e8c96a', '#d9b452', '#f2dc8c'][c]; pf([[-sz, -2], [sz, -4], [sz, 1], [-sz, 3]], col); }
    else { g.fillStyle = ['#ffffff', '#f2f6fb', '#e8eef6'][c]; g.beginPath(); g.ellipse(0, 0, sz * 0.8, sz * 0.45, 0, 0, TAU); g.fill(); }
    g.restore();
  }
  function flowerArt(x, y, sz, c, a) {                 
    if (a <= 0.01 || sz <= 0.5) return;
    const col = ['#ff9cbc', '#ffd65c', '#ffffff', '#c9a8ff'][c % 4];
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.lineWidth = 0.6;
    pf([[0, 0], [-3, sz * 1.6], [3, sz * 1.6]], '#5fae5a');
    for (let i = 0; i < 5; i++) { const an = -Math.PI / 2 + i * TAU / 5; g.save(); g.rotate(an); pf([[0, 0], [sz * 0.5, -sz * 0.35], [sz, 0], [sz * 0.5, sz * 0.35]], i % 2 ? col : tone(col, 0.92)); g.restore(); }
    g.fillStyle = '#ffcf4a'; g.beginPath(); g.arc(0, 0, sz * 0.28, 0, TAU); g.fill();
    g.restore();
  }
  function poopArt(q, x, y, w, gold, a) {             
    const im = POOP[q % Math.max(1, POOP.length)]; if (!im || !im.naturalWidth || a <= 0.01) return;
    const h = w * im.naturalHeight / im.naturalWidth;
    g.save(); g.globalAlpha *= a; g.fillStyle = 'rgba(40,20,5,0.2)'; g.beginPath(); g.ellipse(x, y, w * 0.4, w * 0.12, 0, 0, TAU); g.fill();
    if (gold) {
      const c = APPLE_C; c.width = Math.ceil(w) + 2; c.height = Math.ceil(h) + 2; const q2 = c.getContext('2d'); q2.clearRect(0, 0, c.width, c.height); q2.drawImage(im, 1, 1, w, h);
      q2.globalCompositeOperation = 'source-atop'; q2.fillStyle = 'rgba(255,200,60,0.62)'; q2.fillRect(0, 0, c.width, c.height); q2.globalCompositeOperation = 'source-over';
      g.drawImage(c, x - w / 2 - 1, y - h * 0.9 - 1);
    } else g.drawImage(im, x - w / 2, y - h * 0.9, w, h);
    g.restore();
  }
  function cleanTgPos() { const C = S.clean; return [lerp(C.x, C.pan.x + 34, C.progS || 0), C.y]; }
  function drawCare(t) {
    const z = S.zoom.z;
    
    for (const q of (BR.poops || [])) if (q.gold) { const p = toS([q.x, q.y]); for (let i = 0; i < 3; i++) { const v = ((t * 0.6 + i / 3) % 1); star(p[0] + (hash(i * 3) - 0.5) * 60 * z, p[1] - 30 * z - 40 * z * v, 9 * z * Math.sin(Math.PI * v), v * 2, 0.9); } }
    
    const FA = S.flowersAt || (S.clean && S.clean.flowerT ? { x: S.clean.x, y: S.clean.y, t0: S.clean.flowerT } : null);
    if (FA && t >= FA.t0) for (let i = 0; i < 7; i++) { const an = i * TAU / 7 + 0.4, rr = 90 + 40 * hash(i * 1.7), p = toS([FA.x + Math.cos(an) * rr * 1.3, FA.y + Math.sin(an) * rr * 0.5]); const v = (t - FA.t0 - i * 0.12) / 0.5; if (v > 0) flowerArt(p[0], p[1], 15 * z * backOut(v), i, 1); }
    
    const F = S.feed;
    if (F && F.bucket) { const b = F.bucket, p = toS([b.x, b.y]), k = TCHorse.scaleAt(HO, b.y) * z, op = b.hideT != null ? 1 - sm((t - b.hideT) / 0.45) : backOut((t - b.t0) / 0.45);
      paperSquare(p[0], p[1] - 0.3 * k, 30 * z * (b.hideT != null ? sm((t - b.hideT - 0.3) / 0.2) * (1 - sm((t - b.hideT - 0.5) / 0.2)) : (1 - sm((t - b.t0 - 0.25) / 0.2))), t, 1);
      if (!F.b3) bucketArt(p[0], p[1], k, b.level, Math.max(0, op), b.lh); }
    if (F && F.handT != null && F.itemW) {
      const q = toS(F.itemW), k = TCHorse.scaleAt(HO, BR.y) * z, uo = (t - F.handT) / 0.5, uc = F.handHide != null ? (t - F.handHide) / 0.5 : -1;
      const open = uc >= 0 ? 1 - sm(uc / 0.6) : backOut((uo - 0.3) / 0.6), a = uc >= 0 ? 1 - sm((uc - 0.4) / 0.4) : 1;
      const n = P('nose'), w2 = P('withers'), side = n && w2 && n[0] > w2[0] ? 1 : -1;
      if (F.kind === 'apple') {         
        const ax = q[0] + side * 0.14 * k; hand(ax + side * 0.04 * k, q[1] + 0.16 * k, 62, side * 0.3, 1, a, Math.max(0, open)); appleArt(ax, q[1], 0.2 * k, F.bites, a * sm(uo / 0.6), side > 0);
      } else {                         
        const L = 0.7 * k, len = L * (1 - 0.27 * Math.min(3, F.bites)), dx = side * 0.96, dy = -0.27, T = [q[0] + dx * len, q[1] + dy * len];
        const Hp = mixP(T, q, 0.3); hand(Hp[0], Hp[1] + 0.13 * k, 62, side * 0.25, 1, a, Math.max(0, open));
        carrotHeld(q[0], q[1], side, L, F.bites, F.gold, a * sm(uo / 0.6));
      }
    }
    
    const C = S.clean;
    if (C) {
      const tgt = (C.swipes || 0) / 3; C.progS = (C.progS || 0) + (tgt - (C.progS || 0)) * 0.18;
      const k = TCHorse.scaleAt(HO, C.y) * z, dirX = C.x >= C.pan.x ? 1 : -1, tp = toS(cleanTgPos()), pp = toS([C.pan.x, C.pan.y]);
      const ft = C.foldT != null ? sm((t - C.foldT) / 0.5) : 0, op = C.toolT != null ? backOut((t - C.toolT) / 0.45) : 0;
      if (C.toolT != null) { paperSquare(pp[0], pp[1] - 20 * z, 26 * z * (1 - sm((t - C.toolT - 0.2) / 0.2)), t, 1); panArt(pp[0], pp[1], k, dirX, Math.max(0, Math.min(1, op)), ft); }
      if (C.tg.type === 'poop' && !(C.inPan && ft > 0.2)) { const w = C.tg.w * TCHorse.scaleAt(HO, C.y) * z * (C.inPan ? 0.7 : 1); poopArt(C.tg.img, tp[0], tp[1] - (C.inPan ? 8 * z : 0), w, C.tg.gold, 1 - ft);
        if (C.tg.gold) for (let i = 0; i < 3; i++) { const v = ((t * 0.6 + i / 3) % 1); star(tp[0] + (hash(i * 3) - 0.5) * 60 * z, tp[1] - 30 * z - 40 * z * v, 9 * z * Math.sin(Math.PI * v), v * 2, 0.9); } }
      if (C.tg.type === 'leaves') for (const L of C.tg.leaves) { const sp = toS([C.x + L.dx, C.y + L.dy]), e = C.progS || 0, x = lerp(sp[0], pp[0] + 30 * z + L.dx * 0.1 * z, e), y = lerp(sp[1], pp[1] - 6 * z + L.dy * 0.08 * z, e); leafArt(x, y, 22 * L.s * z, L.r + e * 2, C.tg.ss, L.c, 1 - ft); }
      if (C.toolT != null && C.foldT == null) { const f = S.finger ? toS(S.finger) : toS([C.x + 150, C.y]); broomArt(f[0], f[1], k, dirX * 0.45 + 0.05 * Math.sin(t * 3), Math.max(0, Math.min(1, op))); }
      else if (C.foldT != null) { const f = S.finger ? toS(S.finger) : toS([C.x + 150, C.y]); broomArt(f[0], f[1], k, dirX * 0.45, 1 - ft); }
    }
  }
  
  function coinArt(x, y, r) {
    const fc = ['#f6d47e', '#eec86a', '#e2b654', '#d8aa49', '#d3a344', '#dbad4e', '#e8bf5f', '#f2cc72'];
    for (let i = 0; i < 8; i++) { const a0 = -Math.PI / 2 - Math.PI / 8 + i * Math.PI / 4, a1 = a0 + Math.PI / 4; pf([[x, y], [x + Math.cos(a0) * r, y + Math.sin(a0) * r], [x + Math.cos(a1) * r, y + Math.sin(a1) * r]], fc[i]); }
    g.strokeStyle = 'rgba(140,90,30,0.5)'; g.lineWidth = 3; g.beginPath();
    for (let i = 0; i <= 8; i++) { const a = -Math.PI / 2 - Math.PI / 8 + i * Math.PI / 4, px = x + Math.cos(a) * r * 0.74, py = y + Math.sin(a) * r * 0.74; i ? g.lineTo(px, py) : g.moveTo(px, py); }
    g.stroke(); label('P', x, y + 2, r * 1.05, '#fff6dc', '#8a5a1c', 7);
  }
  function pointPop(val, u) {
    const D = 2.0; if (u < 0 || u > D) return;
    const PX = W / 2, PY = 720, a = 1 - sm((u - D + 0.35) / 0.35), rise = 43 * (1 - Math.pow(1 - clamp(u / 1.6, 0, 1), 2)), F = 2.7;
    const n = val >= 300 ? 10 : val >= 200 ? 8 : 6, cols = ['#f2c24f', '#f4a39b', '#a6d58f', '#9cc6ec', '#f6dc8c'];
    for (let i = 0; i < n; i++) { const v = u - 0.04; if (v < 0 || v > 0.85) continue; const th = i * TAU / n + 0.35 + 0.3 * hash(i + val), sp = (120 + 60 * hash(i * 3 + val)) * F;
      const x = PX + Math.cos(th) * (40 * F + sp * v) * 1.25, y = PY - rise + Math.sin(th) * (24 * F + sp * v * 0.7) + 160 * F * v * v;
      g.save(); g.globalAlpha *= a * (1 - sm((v - 0.5) / 0.35)); g.translate(x, y); g.rotate(v * 7 + i); g.scale(F, F); pf([[-6, -4], [6, -4], [0, 6]], cols[i % cols.length]); pf([[0, -4], [6, -4], [0, 6]], 'rgba(0,0,0,0.14)'); g.restore(); }
    const s = backOut(u / 0.3), rot = -0.07 * Math.exp(-u * 6) * Math.cos(u * 18);
    g.save(); g.globalAlpha *= a * sm(u / 0.12); g.translate(PX, PY + 8 * F * (1 - sm(u / 0.3)) - rise); g.rotate(rot); g.scale(s * F, s * F); g.lineWidth = 0.4;
    const w = 182, h = 66, c = 15;
    pf([[-w / 2 + 5, -h / 2 + 7], [w / 2 + 5, -h / 2 + 7], [w / 2 + 5, h / 2 + 7], [-w / 2 + 5, h / 2 + 7]], 'rgba(0,0,0,0.22)');
    pf([[-w / 2, -h / 2], [w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2, h / 2], [-w / 2, h / 2]], '#fff4d6');
    pf([[-w / 2, 0], [w / 2, 0], [w / 2, h / 2], [-w / 2, h / 2]], '#f7e6bf'); pf([[w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2 - c, -h / 2 + c]], '#e2c78e');
    g.scale(1 / F, 1 / F); coinArt((-w / 2 + 34) * F, 0, 20 * F);
    label(val + 'P', 22 * F, -10 * F, 30 * F, '#f3b631', '#5b3412', 7 * F); label('GET！', 22 * F, 18 * F, 18 * F, '#fffaf0', '#5b3412', 5 * F);
    g.restore();
  }
  
  function drawChooser(t) {
    const C = S.chooser; if (!C) return;
    const items = [['esa', 'エサ'], ['apple', 'リンゴ'], ['carrot', 'ニンジン']];
    items.forEach(([kd, txt], i) => {
      const v = (t - C.t0 - i * 0.07) / 0.35; if (v <= 0) return;
      const picked = C.pick === kd, gone = C.pick && !picked, pv = C.pickT != null ? (t - C.pickT) / 0.45 : 0;
      const x = 270 + i * 256, y = 1262, s = backOut(v) * (picked ? 1 + 0.12 * Math.sin(Math.PI * clamp(pv, 0, 1)) : 1) * (gone ? 1 - sm(pv) : 1), a = gone ? 1 - sm(pv) : picked ? 1 - sm((pv - 0.7) / 0.3) : 1;
      if (s <= 0.01 || a <= 0.01) return;
      g.save(); g.globalAlpha *= a; g.translate(x, y); g.scale(s, s);
      panel(-108, -120, 216, 230, 22);
      if (picked) { g.strokeStyle = '#f2b63c'; g.lineWidth = 7; g.strokeRect(-104, -116, 208, 222); }
      if (kd === 'esa') { if (bucket && bucket.naturalWidth) g.drawImage(bucket, -64, -72, 128, 128 * bucket.naturalHeight / bucket.naturalWidth); else bucketArt(0, 52, 230, 3, 1); } else if (kd === 'apple') appleArt(0, -10, 56, 0, 1); else if (carrot && carrot.naturalWidth) g.drawImage(carrot, -58, -76, 116, 116 * carrot.naturalHeight / carrot.naturalWidth);
      label(txt, 0, 84, 34, '#7a4520');
      if (kd === S.fav) { heart(80, -96, 22, 0.1, 1); label('好物', 60, -60, 24, '#c2456f', '#fff8ec', 6); }
      g.restore();
    });
    const v = (t - C.t0) / 0.3; if (v > 0 && !C.pick) { g.save(); g.globalAlpha *= sm(v); g.font = `700 34px ${FONT}`; const w = g.measureText('どれを あげる？').width + 50; g.fillStyle = 'rgba(40,24,10,0.6)'; g.beginPath(); g.roundRect(W / 2 - w / 2, 1080, w, 58, 29); g.fill(); label('どれを あげる？', W / 2, 1110, 34, '#fff8ea'); g.restore(); }
  }

  
  function pre(t, dt) {
    if (S.t0 == null) S.t0 = t;
    const u = t - S.t0;
    if (S.demo && S.demo.rt) { const R = S.demo.rt; if (u >= R[0] && !R.a) { R.a = 1; S.rtReq = true; } if (u >= R[1] && !R.b) { R.b = 1; S.rtReq = false; } }
    bannerStep(t);
    
    if (S.zB) {
      const k = easeIO((t - S.zT0) / S.zDur); S.zoom = { z: lerp(S.zA.z, S.zB.z, k), cx: lerp(S.zA.cx, S.zB.cx, k), cy: lerp(S.zA.cy, S.zB.cy, k) };
      if (k >= 1) { S.zB = null;
        if (S.phase === 'zoomin') { if (S.mode === 'feed') feedStart(t); else if (S.mode === 'clean') cleanStart(t); else { S.phase = 'pet'; S.petIdle = t; mark('R', t); ev(t, 'ready2'); } }
        else if (S.phase === 'zoomout') release(t); }
    }
    
    if (S.demo) {
      for (const pr of (S.demo.press || [])) if (!pr.done && u >= tu(pr[0])) { pr.done = true; if (pr[1] === 'help') { S.press.help = t; S.guide = { t0: t }; ev(t, 'button'); ev(t + 0.1, 'paper'); } else if (pr[1] === 'pet') pressPet(t); else if (pr[1] === 'feed') pressFeed(t); else if (pr[1] === 'pick') pick(t, pr[2]); else if (pr[1] === 'clean') pressClean(t); else pressCall(t, pr[2]); }
      const f = demoFinger(u), was = S.fdown || false;
      if (f) {
        if (f.down && !was) input('down', f.p[0], f.p[1], t); else if (f.down) input('move', f.p[0], f.p[1], t); else if (was) input('up', f.p[0], f.p[1], t);
        else S.finger = f.p;
        S.fdown = f.down;
      }
      if (S.demo.end && u >= tu(S.demo.end)) S.demoDone = true;
      if (S.guide && typeof TCGuide !== 'undefined') {          
        const D = S.demo, gu = t - S.guide.t0, end = (D.guideEnd || 16) - 0.6;
        if (!TCGuide.el) TCGuide.open(g.canvas.parentNode);
        TCGuide.set(gu < end ? sm(gu / 0.45) : 1 - sm((gu - end) / 0.4)); TCGuide.scroll(sm((gu - 1.6) / (end - 3.2)));
        if (gu >= end + 0.4 && !S.guide.closed) { S.guide.closed = true; ev(t, 'paper'); }
      }
    }
    S.sched.sort((a, b) => a.t - b.t);
    while (S.sched.length && S.sched[0].t <= t) S.sched.shift().fn(t);
    if (BR.careHold && !S.grazeOK) BR.want.graze = 0;          
    
    if (S.phase === 'approach' && BR.mode === 'walk' && S.route && S.route.length && BR.tgt && Math.hypot(BR.x - BR.tgt[0], (BR.y - BR.tgt[1]) / 0.5) < 80) nextLeg(t);      
    if (S.phase === 'approach' && BR.mode === 'idle') {
      if (S.route && S.route.length) nextLeg(t);
      else if (S.turnAfter) {           
        S.turnAfter = false; const want = S.turnTarget != null ? S.turnTarget : Math.cos(BR.dir) >= 0 ? 0.12 : Math.PI - 0.12; S.turnTarget = null;
        Object.assign(BR, { mode: 'turn', turnTo: want, until: t + 30 });
      } else arrived(t);
    }
    
    if (S.ses && !S.ses.done && S.finger) {
      const side = sideToward(S.finger[0], S.finger[1]), zone = S.ses.zone, mag = zone === 'head' || zone === 'nose' ? 0.35 : 0.85;
      BR.want.look = [side * mag, zone === 'back' ? 0.05 : 0.12];
    }
    if (S.ses && S.ses.done && S.hand && S.hand.hideT != null && t > S.hand.hideT + 0.7) { S.ses = null; S.hand = null; }
    if (S.ses && !S.ses.done && !S.ses.down && S.ses.upT != null && t - S.ses.upT > 2.2) { S.hand.hideT = t; ev(t, 'fold'); S.ses.done = true; S.holdUntil = t + 0.8; }      
    
    if (!S.busy && t > S.holdUntil && (S.phase === 'pet' && !S.ses || S.phase === 'callact' || S.phase === 'feeddone' || S.phase === 'cleandone')) { S.holdUntil = Infinity; endCare(t); }
    if (S.afterSniff && BR.mode === 'idle') { S.afterSniff = false; react('sniff', 2.2, t, { side: 0 }); react('swish', 2.2, t + 1.2); ev(t, 'sniff'); tagW(P('nose'), 'くんくん', t + 0.3, { off: [0, -100], size: 32, dur: 1.4 }); S.holdUntil = t + 3.2; }
    if (S.mode === 'after' && !S.afterSniff && t > S.holdUntil) { S.mode = null; S.phase = 'idle'; BR.careHold = false; BR.until = t + 2; mark('Z2', t); }
    if (S.phase === 'pet' && !S.ses && !S.busy && S.holdUntil === Infinity && t - S.petIdle > 6) endCare(t);
    if (S.readyT != null && t >= S.readyT) { ev(S.readyT, 'ready'); S.readyT = null; S.readyPop = t; }
    if (S.drainT != null && t > S.drainT + RULE.max * 0.07 + 0.2) { S.heart = 0; S.heartShow = 0; S.drainT = null; }
    S.stockShow += clamp(S.stock - S.stockShow, -dt * 6, dt * 6);
    const pp = props3(t); if (pp) BR.props = pp; else if (BR.props) BR.props = null;      
  }
  function post(t) {
    const cs = S.cs || O.cs || 1; g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, g.canvas.width, g.canvas.height); g.setTransform(cs, 0, 0, cs, 0, 0);      
    g.lineJoin = 'round'; g.lineCap = 'round';
    drawBanner(t);
    drawCare(t);
    drawUI(t);
    drawChooser(t);
    
    if (S.hand) {
      const hs = S.hand, f = toS(S.finger || [W / 2, H / 2]);
      const uo = (t - hs.t0) / 0.5, uc = hs.hideT != null ? (t - hs.hideT) / 0.5 : -1;
      let open = uc >= 0 ? 1 - sm(uc / 0.6) : backOut((uo - 0.38) / 0.62), sq = uc >= 0 ? sm((uc - 0.35) / 0.25) * (1 - sm((uc - 0.7) / 0.3)) : (1 - sm((uo - 0.45) / 0.3)) * backOut(uo / 0.4);
      if (uo < 0.38) open = 0;
      const press = S.ses && S.ses.down && !S.ses.done ? 1 : 0;
      hs.press = (hs.press == null ? 0 : hs.press) + (press - (hs.press || 0)) * 0.3;
      const n = P('nose'), b = P('withers'), rot = (n && b && n[0] > b[0] ? 0.5 : -0.5) + 0.06 * Math.sin(t * 1.3);      
      paperSquare(f[0] + 20 * Math.sign(-rot), f[1] + 32, 34 * sq, 0.8 * (1 - sq) + t * 0.5, Math.min(1, sq * 2));
      hand(f[0], f[1], 62 * (O.handK || 1), rot, hs.press, 1, Math.max(0, open));
    }
    if (S.begHand != null && t - S.begHand < 1.1) { const f = toS(S.finger || [W / 2, H / 2]), u2 = (t - S.begHand) / 1.1; hand(f[0], f[1], 62, -0.4, u2 < 0.5 ? 1 : 0, 1 - sm((u2 - 0.75) / 0.25), backOut(u2 / 0.25)); }
    drawFx(t);
    drawCaption(t);
  }
  
  
  
  async function special(kind) {        
    if (!kind) { if (S.ban) S.ban.hideT = S.lastT || 0; return; }
    BANNER = new Image(); BANNER.src = AP(`tc_items/tc_banner_${kind}.webp`); try { await BANNER.decode(); } catch (e) { }
    S.ban = { kind, showT: null, hideT: null, shown: false };
  }
  function roulette(on) { S.rtReq = !!on; }      
  function setHorse(horse, brain) { HO = horse; BR = brain; S.phase = 'idle'; S.mode = null; S.ses = null; S.hand = null; S.feed = null; S.clean = null; S.chooser = null; S.zoom = { z: 1, cx: W / 2, cy: H / 2 }; S.zB = null; }
  
  function uiHit(x, y) {
    if (S.chooser && !S.chooser.pick) { const items = ['esa', 'apple', 'carrot']; for (let i = 0; i < 3; i++) { const cx = 270 + i * 256; if (Math.abs(x - cx) < 110 && y > 1262 - 122 && y < 1262 + 112) return 'pick:' + items[i]; } }
    if (Math.hypot(x - HELP[0], y - HELP[1]) < 48) return 'help';
    for (const k of ['pet', 'feed', 'clean', 'call']) if (Math.hypot(x - BTN[k][0], y - BTN[k][1]) < BTN_R + 10) return k;
    return null;
  }
  function press(t, what) {
    if (what === 'pet') pressPet(t); else if (what === 'feed') pressFeed(t); else if (what === 'clean') pressClean(t); else if (what === 'call') pressCall(t);
    else if (what === 'help') { S.press.help = t; ev(t, 'button'); ev(t + 0.05, 'paper'); if (O.onHelp) O.onHelp(); }
    else if (what && what.startsWith('pick:')) pick(t, what.slice(5));
  }
  function pointer(kind, x, y, t) {        
    if (kind === 'down') { const h = uiHit(x, y); S.uiDown = h; if (h) return; }
    if (kind === 'up' && S.uiDown) { const h = uiHit(x, y); if (h === S.uiDown) press(t, h); S.uiDown = null; return; }
    if (S.uiDown) return;
    const w = toW([x, y]); input(kind, w[0], w[1], t);
  }
  function bannerStep(t) {
    const B = S.ban; if (!B) return;
    if (B.showT == null && B.hideT == null) B.showT = t + 0.6;
    if (S.rtReq != null) {
      if (S.rtReq && !S.rtOn) { S.rtOn = true; if (B.hideT == null) { B.hideT = t; ev(t, 'banout'); } }
      else if (!S.rtReq && S.rtOn) { S.rtOn = false; B.showT = t + 0.3; B.hideT = null; B.shown = false; }
      S.rtReq = null;
    }
    if (!B.shown && B.hideT == null && B.showT != null && t >= B.showT) { B.shown = true; ev(t, 'banin', { kind: B.kind }); }
  }
  const BAN_W = 860; let BAN_TOP = 172;      
  function bannerVisible() { const B = S.ban; return !!(B && B.hideT == null && B.showT != null); }
  function drawBanner(t) {
    const B = S.ban, im = BANNER; if (!B || !im || !im.naturalWidth || B.showT == null) return;
    const w = BAN_W, h = w * im.naturalHeight / im.naturalWidth, cx = W / 2, cy = BAN_TOP + h / 2, ui = t - B.showT;
    let k, a, dy;
    if (B.hideT != null) { const v = (t - B.hideT) / 0.38; if (v >= 1) return; k = 1 - 0.12 * sm(v); a = 1 - sm(v); dy = -70 * v * v; }
    else { if (ui < 0) return; const v = ui / 0.62; k = 0.72 + 0.28 * backOut(v); a = sm(v / 0.35); dy = -90 * (1 - easeOut(v)); }
    const bob = 4 * Math.sin(TAU * ui / 3.4), sway = 0.007 * Math.sin(TAU * ui / 4.6);
    g.save(); g.globalAlpha *= a; g.translate(cx, cy + dy + bob); g.rotate(sway); g.scale(k, k); g.drawImage(im, -w / 2, -h / 2, w, h); g.restore();
    if (B.hideT == null && ui > 0.25 && ui < 2.4) {                 
      const col = B.kind === 'kamisama' ? '#fff2bf' : '#f6dcff';
      for (let i = 0; i < 7; i++) { const v = (ui - 0.25 - i * 0.16) / 1.0; if (v > 0 && v < 1) star(cx + (hash(i * 7.3 + 1) - 0.5) * w * 0.92, BAN_TOP + h * (0.1 + 0.8 * hash(i * 3.1 + 2)) + bob, 22 * Math.sin(Math.PI * v), v * 1.4, 0.95, col); }
    }
  }
  function drawCaption(t) {
    if (!S.demo || !S.demo.cap) return; const u = t - S.t0;
    for (const [a0, b0, txt] of S.demo.cap) {
      const a = tu(a0), b = tu(b0); if (a === Infinity) continue;
      const k = sm((u - a) / 0.25) * (b === Infinity ? 1 : 1 - sm((u - b + 0.25) / 0.25)); if (k <= 0) continue;
      g.save(); g.globalAlpha *= k; g.font = `700 40px ${FONT}`; const w = g.measureText(txt).width + 64;
      const cy0 = bannerVisible() ? BAN_TOP + 262 : 186;      
      g.fillStyle = 'rgba(40,24,10,0.6)'; g.beginPath(); g.roundRect(W / 2 - w / 2, cy0, w, 74, 37); g.fill();
      label(txt, W / 2, cy0 + 38, 40, '#fff8ea'); g.restore();
    }
  }
  function drawUI(t) {
    
    const gx = 26, gy = 34, gw = 600, gh = 126;
    panel(gx, gy, gw, gh, 24);
    const pulse = S.lot ? 1 + 0.06 * Math.sin(TAU * 0.9 * (t - S.lot.t0)) * (1 - sm((t - S.lot.t0 - 2.2) / 0.6)) : 1;
    heart(gx + 62, gy + gh / 2 + 4, 36 * pulse, -0.06, 1);
    label('なかよし', gx + 128, gy + 36, 32, '#7a4520', null, 0, 'left');
    label(`${S.heartShow}/10`, gx + gw - 30, gy + 36, 32, '#c2456f', null, 0, 'right');
    const dr = S.drainT != null ? t - S.drainT : -1;
    for (let i = 0; i < RULE.max; i++) {
      const [x, y] = SLOT(i); heartSlot(x, y, 17);
      if (i < S.heartShow) {
        let a = 1, r = 17;
        if (dr >= 0) { const q = (dr - (RULE.max - 1 - i) * 0.07) / 0.25; a = 1 - sm(q); r = 17 * (1 + 0.3 * Math.sin(Math.PI * clamp(q, 0, 1))); }
        if (S.lot && dr < 0) r = 17 * (1 + 0.1 * Math.sin(TAU * 0.9 * (t - S.lot.t0) - i * 0.5));
        heart(x, y, r, 0, a);
      }
    }
    
    const sx = W - 26 - 296, sy = 44, sw = 296, shh = 106; panel(sx, sy, sw, shh, 20);
    const bu = S.stockBump != null ? (t - S.stockBump) / 0.5 : 2, bs = bu < 1 ? 1 + 0.12 * Math.sin(Math.PI * bu) : 1;
    label('お世話', sx + 24, sy + 36, 28, '#7a4520', null, 0, 'left');
    g.save(); g.translate(sx + sw - 118, sy + 70); g.scale(bs, bs); label(String(Math.round(S.stockShow)), 0, 0, 50, '#3f7f3a', '#fff8ec', 6); g.restore();
    label('/20', sx + sw - 54, sy + 76, 28, '#9a7a55');
    
    
    if (S.stockDrop != null) { const v = (t - S.stockDrop) / 1.2; if (v < 1) label('−1', O.dropX || sx + sw - 60, sy + shh + 26 + 30 * easeOut(v), 40, '#b0445f', '#fff8ec', 7); }
    if (S.high > 0) {                  
      const hb = S.highBump != null ? (t - S.highBump) / 0.5 : 2, hs = hb < 1 ? 1 + 0.15 * Math.sin(Math.PI * hb) : 1;
      g.save(); g.translate(sx + sw / 2, O.hiY || sy + shh + 44); g.scale(hs, hs); panel(-130, -30, 260, 60, 14); label(`高確ゾーン あと${S.high}回`, 0, 2, 28, '#c2456f'); g.restore();
    }
    
    { const [hx, hy] = HELP, pq = S.press.help != null ? (t - S.press.help) / 0.35 : 9, ps = pq < 1 ? 1 - 0.1 * Math.sin(Math.PI * pq) : 1;
      g.save(); g.translate(hx, hy); g.scale(ps, ps); g.fillStyle = 'rgba(40,20,5,0.22)'; g.beginPath(); g.arc(3, 5, 40, 0, TAU); g.fill();
      g.fillStyle = '#fff8ec'; g.beginPath(); g.arc(0, 0, 40, 0, TAU); g.fill(); g.strokeStyle = '#e5cfa8'; g.lineWidth = 3; g.beginPath(); g.arc(0, 0, 38.5, 0, TAU); g.stroke();
      label('？', 0, 2, 44, '#8a5a2a'); g.restore(); }
    
    const items = [['pet', '撫でる'], ['feed', 'ごはん'], ['clean', 'おそうじ'], ['call', '呼ぶ']];
    items.forEach(([k, txt]) => {
      const [x, y] = BTN[k], r = BTN_R, pq = S.press[k] != null ? (t - S.press[k]) / 0.35 : 9, ps = pq < 1 ? 1 - 0.1 * Math.sin(Math.PI * pq) : 1;
      g.save(); g.translate(x, y); g.scale(ps, ps); g.translate(-x, -y);
      g.fillStyle = 'rgba(40,20,5,0.22)'; g.beginPath(); g.arc(x + 4, y + 7, r, 0, TAU); g.fill();
      g.fillStyle = '#fff8ec'; g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill(); g.fillStyle = '#f6e8cf'; g.beginPath(); g.arc(x, y, r, 0.15 * Math.PI, 0.85 * Math.PI); g.fill();
      g.strokeStyle = '#e5cfa8'; g.lineWidth = 3; g.beginPath(); g.arc(x, y, r - 1.5, 0, TAU); g.stroke();
      if (k === 'pet') { handPath(); const [hx0, hy0, hx1, hy1] = HAND_BB, s_ = 34, r_ = -0.5, cx_ = (hx0 + hx1) / 2 * s_, cy_ = (hy0 + hy1) / 2 * s_;      
        hand(x - (Math.cos(r_) * cx_ - Math.sin(r_) * cy_), y - 4 - (Math.sin(r_) * cx_ + Math.cos(r_) * cy_), s_, r_, 1, 1, 1); }
      else if (k === 'feed') { const im_ = bucket && bucket.naturalWidth ? bucket : apple; if (im_ && im_.naturalWidth) { const w_ = 96, h_ = w_ * im_.naturalHeight / im_.naturalWidth; g.drawImage(im_, x - w_ / 2, y - 4 - h_ / 2, w_, h_); } }      
      else if (k === 'clean') { g.save(); g.translate(x, y); g.rotate(0.5); g.lineWidth = 0.8; pf([[-5, -50], [5, -50], [5, 8], [-5, 8]], '#c98d55'); pf([[-24, 8], [24, 8], [32, 42], [-32, 42]], '#f0c75e'); pf([[0, 8], [24, 8], [32, 42], [0, 42]], '#d9ad43'); g.lineWidth = 2; for (let q = -2; q <= 2; q++) line([q * 9, 14], [q * 12, 40], 'rgba(120,80,20,0.35)'); g.restore(); }
      else { g.save(); g.translate(x, y - 4); g.lineWidth = 0.8; pf([[-34, -26], [34, -26], [34, 18], [-6, 18], [-20, 34], [-18, 18], [-34, 18]], '#9fd0f0'); pf([[0, -26], [34, -26], [34, 18], [0, 18]], '#86c0e6'); label('♪', 0, -4, 40, '#ffffff'); g.restore(); }
      if (pq < 1.6) { const q = clamp(pq / 1.6, 0, 1); g.strokeStyle = `rgba(255,248,236,${0.75 * (1 - q)})`; g.lineWidth = 6; g.beginPath(); g.arc(x, y, r + 6 + 30 * easeOut(q), 0, TAU); g.stroke(); }
      g.restore();
      label(txt, x, y + r + 34, 30, '#fff8ea', 'rgba(60,35,15,0.85)', 7);
      
      if (k === 'pet' && t < S.coolUntil) {
        const rem = (S.coolUntil - t) / RULE.cool;
        g.save(); g.fillStyle = 'rgba(60,40,25,0.45)'; g.beginPath(); g.moveTo(x, y); g.arc(x, y, r, -Math.PI / 2, -Math.PI / 2 + TAU * rem); g.closePath(); g.fill();
        g.strokeStyle = '#ff9cbc'; g.lineWidth = 8; g.beginPath(); g.arc(x, y, r + 8, -Math.PI / 2, -Math.PI / 2 + TAU * rem); g.stroke(); g.restore();
        label(String(Math.ceil(S.coolUntil - t)), x, y + 2, 54, '#ffffff', 'rgba(60,35,15,0.9)', 8);
      }
      if (k === 'pet' && S.readyPop != null) { const q = (t - S.readyPop) / 0.6; if (q < 1) { g.save(); g.strokeStyle = `rgba(255,156,188,${0.7 * (1 - q)})`; g.lineWidth = 6; g.beginPath(); g.arc(x, y, r + 8 + 26 * easeOut(q), 0, TAU); g.stroke(); g.restore(); } }
    });
  }
  function drawFx(t) {
    S.fx = S.fx.filter(f => t - f.t0 < (f.dur || 3) + 1.5);
    const z = S.zoom.z;
    for (const f of S.fx) {
      const u = t - f.t0; if (u < 0) continue;
      if (f.k === 'mini') {            
        const d = 1.0; if (u > d) continue; const k = u / d, q = toS(f.w), s = Math.sqrt(z);
        heart(q[0] + f.dx * s * easeOut(k), q[1] - 70 * s * easeOut(k), f.r * s * backOut(k / 0.3), 0.12 * Math.sin(u * 6), 1 - sm((k - 0.6) / 0.4));
      } else if (f.k === 'fly') {       
        const d = f.dur, [tx, ty] = SLOT(f.i), k = u / d; if (k > 1) continue;
        const c = [lerp(f.x, tx, 0.5) + 120, Math.min(f.y, ty) - 160], e = easeIO(clamp((k - 0.25) / 0.75, 0, 1));
        const p = [(1 - e) * (1 - e) * f.x + 2 * (1 - e) * e * c[0] + e * e * tx, (1 - e) * (1 - e) * (f.y - 30) + 2 * (1 - e) * e * c[1] + e * e * ty];
        const r = k < 0.25 ? 34 * backOut(k / 0.25) : lerp(34, 17, e);
        heart(p[0], p[1], r, 0.2 * Math.sin(u * 9) * (1 - e), 1);
      } else if (f.k === 'pop') {      
        const d = 0.6; if (u > d) continue;
        for (let i = 0; i < 6; i++) { const a = i * TAU / 6 + 0.3, rr = 18 + 30 * easeOut(u / d); star(f.x + Math.cos(a) * rr, f.y + Math.sin(a) * rr, 7 * (1 - u / d), u * 3, 1 - sm((u / d - 0.5) / 0.5), i % 2 ? '#ffb3cb' : '#f5d06a'); }
      } else if (f.k === 'tag') {      
        const d = f.dur; if (u > d) continue; const q = toS(f.w), s = Math.sqrt(z), o = f.off || [0, -100], sz = f.size * Math.min(1.25, s);
        g.font = `700 ${sz}px ${FONT}`; const hw = (g.measureText(f.txt).width + sz * 1.0) / 2 + 14;      
        tag(clamp(q[0] + o[0] * s, hw, W - hw), Math.max(290, q[1] + o[1] * s - 26 * easeOut(u / d)), f.txt, sz, 1 - sm((u - d + 0.35) / 0.35), backOut(u / 0.28), f.rot, f.col);
      } else if (f.k === 'tagUI') {
        const d = f.dur; if (u > d) continue;
        tag(f.x, f.y - 26 * easeOut(u / d), f.txt, f.size, 1 - sm((u - d + 0.35) / 0.35), backOut(u / 0.28), 0);
      } else if (f.k === 'note') {     
        const d = f.dur; if (u > d) continue;
        tag(26 + 300, 34 + 126 + 56, f.txt, 32, 1 - sm((u - d + 0.4) / 0.4), backOut(u / 0.28), 0, '#b0445f');
      } else if (f.k === 'bits') {     
        const d = 0.9; if (u > d) continue;
        const L = HO.last, zx = L ? L.V[0] * L.view.W : 1, zy = L ? -L.V[1] * L.view.H : 0, n = Math.hypot(zx, zy) || 1, fxv = zx / n, fyv = zy / n, q = toS(f.w), s = Math.sqrt(z);
        for (let i = 0; i < 7; i++) {
          const a = (hash(i * 5.1) - 0.5) * 1.3, vx = fxv * Math.cos(a) - fyv * Math.sin(a), vy = fxv * Math.sin(a) + fyv * Math.cos(a), sp = (70 + 70 * hash(i * 2.3)) * s;
          const x = q[0] + vx * sp * easeOut(u / d), y = q[1] + vy * sp * easeOut(u / d) + 30 * s * (u / d) * (u / d);
          g.save(); g.globalAlpha *= 1 - sm((u / d - 0.4) / 0.6); g.translate(x, y); g.rotate(u * 6 + i); g.scale(s, s); g.lineWidth = 0.6; pf([[-7, -5], [7, -5], [0, 7]], i % 2 ? '#ffffff' : '#f3e9d8'); g.restore();
        }
      } else if (f.k === 'burst') {    
        const d = 1.9; if (u > d) continue; const p = toS(f.w), s = Math.sqrt(z);
        for (let i = 0; i < 12; i++) {
          const a = -Math.PI / 2 + (i - 5.5) * 0.24 + (hash(i) - 0.5) * 0.2, sp = (260 + 120 * hash(i * 3.3)) * s, k = easeOut(u / d);
          const x = p[0] + Math.cos(a) * sp * k, y = p[1] - 40 + Math.sin(a) * sp * k + 120 * (u / d) * (u / d), al = 1 - sm((u / d - 0.55) / 0.45);
          if (i % 3 === 2) star(x, y, 14 * s * backOut(u / 0.3), u * 2 + i, al); else heart(x, y, (i % 2 ? 18 : 24) * s * backOut(u / 0.3), 0.3 * Math.sin(u * 5 + i), al);
        }
      } else if (f.k === 'notes') {    
        const d = 1.6; if (u > d) continue; const [bx, by] = BTN.call, tg = toS([BR.x, BR.y - 200]);
        for (let i = 0; i < 3; i++) {
          const v = clamp((u - i * 0.18) / (d - 0.4), 0, 1); if (v <= 0) continue; const e = easeOut(v);
          const x = lerp(bx, tg[0], e * 0.55) + 26 * Math.sin(v * 7 + i * 2), y = lerp(by - 70, tg[1], e * 0.55) - 30 * i;
          g.save(); g.globalAlpha *= 1 - sm((v - 0.6) / 0.4); label(i === 1 ? '♫' : '♪', x, y, 54 - i * 6, '#ffffff', 'rgba(60,110,160,0.85)', 7); g.restore();
        }
      } else if (f.k === 'unlock') {   
        const d = f.dur; if (u > d) continue; unlockTag(u, d);
      } else if (f.k === 'crumbs') {   
        const d = 0.8; if (u > d) continue; const q = toS(f.w), s2 = Math.sqrt(z);
        for (let i = 0; i < 8; i++) { const an = -Math.PI / 2 + (hash(i * 2.3 + f.t0) - 0.5) * 2.6, sp = (60 + 70 * hash(i * 4.1)) * s2, x = q[0] + Math.cos(an) * sp * easeOut(u / d), y = q[1] + Math.sin(an) * sp * easeOut(u / d) + 90 * s2 * (u / d) * (u / d);
          g.save(); g.globalAlpha *= 1 - sm((u / d - 0.5) / 0.5); g.translate(x, y); g.rotate(u * 8 + i); g.scale(s2, s2); g.lineWidth = 0.6; pf([[-5, -4], [5, -4], [0, 5]], f.col[i % f.col.length]); g.restore(); }
      } else if (f.k === 'dust') {     
        const d = 0.7; if (u > d) continue; const q = toS(f.w), s2 = z;
        for (let i = 0; i < 6; i++) { const x = q[0] - (20 + 60 * hash(i * 1.9)) * s2 * easeOut(u / d), y = q[1] - (6 + 30 * hash(i * 3.7)) * s2 * easeOut(u / d), r = (10 + 10 * hash(i)) * s2 * (0.6 + 0.6 * u / d);
          g.save(); g.globalAlpha *= 0.35 * (1 - u / d); g.fillStyle = '#e8d2a8'; g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill(); g.restore(); }
      } else if (f.k === 'kira') {     
        const d = 1.0; if (u > d) continue; const q = toS(f.w);
        for (let i = 0; i < 4; i++) { const v = (u - i * 0.12) / 0.7; if (v <= 0 || v >= 1) continue; star(q[0] + (hash(i * 5.1) - 0.5) * 140 * z, q[1] - (10 + 50 * hash(i * 2.2)) * z, 18 * z * Math.sin(Math.PI * v), v, 0.95, '#fff2bf'); }
      } else if (f.k === 'glint') {    
        const d = f.dur; if (u > d || !S.feed || !S.feed.itemW) continue; const q = toS(S.feed.itemW);
        for (let i = 0; i < 4; i++) { const v = ((u * 0.8 + i / 4) % 1); star(q[0] + (hash(i * 3.3) - 0.5) * 120 * z, q[1] + (hash(i * 7.1) - 0.5) * 120 * z, 12 * z * Math.sin(Math.PI * v), v * 2, 0.9 * (1 - sm((u - d + 0.4) / 0.4))); }
      } else if (f.k === 'luck') {     
        const d = f.dur; if (u > d) continue; const a = 1 - sm((u - d + 0.4) / 0.4), s2 = backOut(u / 0.3);
        g.save(); g.globalAlpha *= a; g.translate(W / 2, 640); g.scale(s2, s2);
        panel(-300, -110, 600, 220, 40); label('運がついた！', 0, -36, 70, '#f3b631', '#5b3412', 14); label('高確ゾーン（お世話 5回）', 0, 52, 40, '#c2456f', '#fff8ec', 8);
        g.restore();
        for (let i = 0; i < 6; i++) { const v = (u - i * 0.15) / 0.8; if (v > 0 && v < 1) star(W / 2 + (hash(i * 9.1) - 0.5) * 640, 640 + (hash(i * 4.4) - 0.5) * 260, 22 * Math.sin(Math.PI * v), v, a); }
      } else if (f.k === 'pointpop') {
        pointPop(f.v, u);
      } else if (f.k === 'plus') {
        const d = 1.6; if (u > d) continue;
        label(f.txt, W - 26 - 296 + 150, 44 + 140 + 30 - 40 * easeOut(u / d), 44, '#3f7f3a', '#fff8ec', 7);
      }
    }
  }
  function unlockTag(u, d) {
    const PX = W / 2, PY = 640, a = 1 - sm((u - d + 0.35) / 0.35), rise = 40 * (1 - Math.pow(1 - clamp(u / 1.6, 0, 1), 2));
    const s = backOut(u / 0.3), rot = -0.07 * Math.exp(-u * 6) * Math.cos(u * 18);
    for (const [sx, sy, d0] of [[-250, -80, 0.12], [262, 70, 0.24], [-180, 96, 0.36]]) { const v = (u - d0) / 0.6; if (v > 0 && v < 1) star(PX + sx, PY - rise + sy, 24 * Math.sin(Math.PI * v), v * 1.2, a); }
    g.save(); g.globalAlpha *= a * sm(u / 0.12); g.translate(PX, PY + 20 * (1 - sm(u / 0.3)) - rise); g.rotate(rot); g.scale(s, s);
    const w = 560, h = 190, c = 40; g.lineWidth = 0.8;
    pf([[-w / 2 + 12, -h / 2 + 18], [w / 2 + 12, -h / 2 + 18], [w / 2 + 12, h / 2 + 18], [-w / 2 + 12, h / 2 + 18]], 'rgba(0,0,0,0.22)');
    pf([[-w / 2, -h / 2], [w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2, h / 2], [-w / 2, h / 2]], '#fff4d6');
    pf([[-w / 2, 0], [w / 2, 0], [w / 2, h / 2], [-w / 2, h / 2]], '#f7e6bf');
    pf([[w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2 - c, -h / 2 + c]], '#e2c78e');
    g.lineWidth = 2.5; line([-w / 2, 0], [w / 2, 0], 'rgba(160,110,50,0.3)');
    heart(-w / 2 + 96, 4, 58, -0.08, 1);
    label('お世話 5回', 54, -30, 72, '#3f8f3a', '#5b3412', 14);
    label('解放！', 54, 48, 56, '#fffaf0', '#5b3412', 12);
    g.restore();
  }

  async function init(o) {
    O = Object.assign({ cs: 1, tod: 'morning', stageNo: 5 }, o); HO = o.horse; BR = o.brain; rnd = o.rnd || Math.random;
    if (O.banTop) BAN_TOP = O.banTop;
    g = o.canvas.getContext('2d'); S.on = true;
    apple = new Image(); apple.src = AP('tc_items/tc_item_apple.webp'); try { await apple.decode(); } catch (e) { }
    bucket = new Image(); bucket.src = AP('tc_items/tc_item_bucket.webp'); try { await bucket.decode(); } catch (e) { }      
    if (o.props !== false) PROPS = await loadProps();      
    carrot = new Image(); carrot.src = AP('tc_items/tc_item_carrot.webp'); carrotG = new Image(); carrotG.src = AP('tc_items/tc_item_carrot_gold.webp');      
    try { await Promise.all([carrot.decode(), carrotG.decode()]); } catch (e) { }
    const bk = O.bg === 'divine' ? 'kamisama' : O.bg === 'abyss' ? 'maboroshi' : null;      
    if (bk) await special(bk);
    for (const f of ['tc_poop1.webp', 'tc_poop2.webp', 'tc_poop3.webp']) { const im = new Image(); im.src = AP(f); try { await im.decode(); POOP.push(im); } catch (e) { } }
    try { await document.fonts.load(`700 40px ${FONT}`); } catch (e) { }
    if (o.demo && DEMOS[o.demo]) {
      const D = DEMOS[o.demo]; S.demo = D;
      S.heart = S.heartShow = D.heart || 0; S.got = (D.got || []).map(q => q + 1.5); S.greeted = !!D.greeted; S.stock = S.stockShow = D.stock != null ? D.stock : 3;
      if (D.month) O.month = D.month;
      if (D.poop) { const [px, py, im, gold] = D.poop; BR.poops = [{ x: px, y: py, img: im, t0: -10, h0: 1.05, w: [0.3, 0.5, 0.42][im] * (HO.opt.stage || 1), gold: !!gold }]; }
      if (D.front) {                   
        const cw = o.canvas.width, ch = o.canvas.height, k = cw / W; TCHorse.draw(HO, BR, 0, { W: cw, H: ch, k, ox: 0, oy: 0 });
        S.zoom = zoomFor(); S.mode = 'pet'; S.phase = 'pet'; BR.careHold = true; S.holdUntil = Infinity; S.marks.R = 0.35; S.marks.A = 0;
      }
    } else if (o.demo === 'free') {         
      const el = o.canvas; el.style.touchAction = 'none';
      const pos = e => { const r = el.getBoundingClientRect(); return [(e.clientX - r.left) * W / r.width, (e.clientY - r.top) * H / r.height]; };
      const hitBtn = q => Object.keys(BTN).find(k => Math.hypot(q[0] - BTN[k][0], q[1] - BTN[k][1]) < BTN_R + 10);
      el.addEventListener('pointerdown', e => { const q = pos(e), b = hitBtn(q); if (b === 'pet') return pressPet(S.lastT || 0); if (b === 'call') return pressCall(S.lastT || 0); const p = toW(q); el.setPointerCapture(e.pointerId); input('down', p[0], p[1], S.lastT || 0); });
      el.addEventListener('pointermove', e => { const p = toW(pos(e)); input('move', p[0], p[1], S.lastT || 0); });
      el.addEventListener('pointerup', e => { const p = toW(pos(e)); input('up', p[0], p[1], S.lastT || 0); });
    }
    window.__events = () => S.ev;
    window.__careDone = () => !!S.demoDone;
  }
  return { init, pre: (t, dt) => { S.lastT = t; pre(t, dt); }, post, input, pointer, press, pressPet, pressCall, special, roulette, setHorse, view: () => S.zoom, get on() { return S.on; }, S, DEMOS, RULE };
})();

;




const TCGuide = (() => {
  const CSS = `
#tcg{position:absolute;inset:0;z-index:20;display:flex;align-items:flex-end;justify-content:center;pointer-events:auto;font-family:"BIZ UDPGothic",BIZ,"Hiragino Sans","Noto Sans CJK JP",sans-serif}
#tcg .bk{position:absolute;inset:0;background:rgba(30,18,6,.45);opacity:0;transition:none}
#tcg .sh{position:relative;width:calc(100% - 20px);height:86%;margin-bottom:10px;background:#fff8ec;border-radius:18px 18px 14px 14px;box-shadow:0 6px 18px rgba(0,0,0,.35);overflow:hidden;transform:translateY(105%)}
#tcg .hd{display:flex;align-items:center;justify-content:space-between;padding:12px 14px 10px;background:linear-gradient(#f6e3bf,#efd6a8);border-bottom:2px solid #e2c48e}
#tcg .hd b{font-size:17px;color:#6b3f1d;letter-spacing:.04em}
#tcg .x{width:30px;height:30px;border-radius:50%;background:#fff8ec;border:2px solid #d9b77c;color:#8a5a2a;font-size:17px;line-height:26px;text-align:center}
#tcg .bd{position:absolute;top:56px;left:0;right:0;bottom:0;overflow:hidden}
#tcg .in{padding:10px 14px 40px}
#tcg .sec{background:#fffdf7;border:1.5px solid #ead7b2;border-radius:12px;padding:10px 12px 9px;margin:0 0 10px;box-shadow:0 2px 0 #f0e2c4}
#tcg h3{display:flex;align-items:center;gap:8px;margin:0 0 6px;font-size:15px;color:#6b3f1d}
#tcg h3 i{flex:none;width:24px;height:24px;border-radius:50%;font-style:normal;font-size:13px;line-height:24px;text-align:center;color:#fff;background:#d9a443}
#tcg p{margin:3px 0;font-size:12.5px;line-height:1.55;color:#5a3a1c}
#tcg p b{color:#c2456f}
#tcg table{width:100%;border-collapse:collapse;margin:4px 0 2px;font-size:12.5px;color:#5a3a1c}
#tcg td{padding:4px 6px;border-bottom:1px dashed #ead7b2}
#tcg td:first-child{width:64px;font-weight:700;color:#b06a12;text-align:center;background:#fff4dc;border-radius:6px}
#tcg tr:last-child td{border-bottom:0}
#tcg .pt{font-weight:700;color:#3f7f3a}
#tcg .rt{font-weight:700;color:#c2456f}
#tcg .tk{font-weight:700;color:#b07a10}
#tcg .note{font-size:11px;color:#8a6a48}
#tcg .hh{margin:8px 0 2px;font-weight:700;color:#6b3f1d}
`;
  const SEC = [
    ['ト', '#d9a443', 'お世話トークン', `<p>・<b>10分ごとに1つ</b>たまる（最大<b>20こ</b>）</p><p>・「ごはん」「おそうじ」で1つ使う</p><p>・「撫でる」「呼ぶ」はトークンなしでできる</p>`],
    ['P', '#e0a020', 'お世話でポイントGETチャンス', `<p>ごはん・おそうじのたびに抽選！当たりはお世話のあとに出るよ</p>
      <table><tr><td>1/85</td><td><span class="pt">100P</span> GET</td></tr><tr><td>1/99</td><td><span class="pt">200P</span> GET</td></tr><tr><td>1/121</td><td><span class="pt">300P</span> GET</td></tr>
      <tr><td>1/1000</td><td><span class="rt">ルーレット</span>（800P か 1600P）</td></tr><tr><td>1/2000</td><td><span class="rt">ルーレット</span>（1600P か 3200P）</td></tr><tr><td>1/3600</td><td><span class="rt">ルーレット</span>（3200P か 6400P）</td></tr>
      <tr><td>1/2400</td><td><span class="tk">チケット</span>（壁紙 or 結果ボード・1〜3枚）</td></tr></table>
      <p class="note">チケットは 1/8で3枚・1/3で2枚・そのほかは1枚</p>`],
    ['撫', '#e86a92', '撫でる → なかよしハート', `<p>・3回なでると<b>ハート＋1</b></p><p>・撫でたあとは<b>7秒</b>おやすみ・ハートは<b>1分に5こ</b>まで</p>
      <p>・ハート<b>10こ</b>で抽選（<b>1/66</b>）</p><p>　当たり → <b>ぴょん！</b> お世話トークン<b>×5</b></p><p>　ハズレ → ごろん</p>`],
    ['呼', '#5aa7c4', '呼ぶ', `<p>・「近づいてくる」「振り向く」「甘える」のどれか（1/3ずつ）</p>`],
    ['食', '#e07a3a', 'ごはん', `<p>・エサ・リンゴ・ニンジンから選ぶ</p><p>・<b>今日の好物</b>だと大よろこび</p><p>・<b>金のニンジン</b>（ニンジンの1/30）→ なかよしハート<b>＋3</b></p>`],
    ['掃', '#6aa86a', 'おそうじ', `<p>・うんちは2分ごとに<b>1/7</b>で出る</p><p>・ほうきで3回はくとピカピカ（うんちがない時は落ち葉）</p><p>・<b>金のうんち</b>（うんちの1/20）→ 運がついた！<b>高確ゾーン</b>（お世話5回）</p>`],
    ['★', '#8a62c8', '2分ごとのチャンス', `<p>・<b>高確ゾーン</b> 1/50（お世話5回のあいだ当たりやすい）</p><p>・<b>幻の馬</b> 1/245・<b>神様馬</b> 1/399 がやってくる</p>`],
    ['降', '#7a4ab0', '幻の馬・神様馬がいるあいだ', `<p>やってくると フィールドがかわって、お世話の当たりが かわるよ（いるのは<b>10分</b>）</p>
      <p class="hh">🌙 幻の馬</p>
      <table><tr><td>1/300</td><td><span class="rt">ルーレット</span>（800P か 1600P）</td></tr><tr><td>1/500</td><td><span class="rt">ルーレット</span>（1600P か 3200P）</td></tr><tr><td>1/1000</td><td><span class="rt">ルーレット</span>（3200P か 6400P）</td></tr></table>
      <p class="hh">✨ 神様馬</p>
      <table><tr><td>1/85</td><td><span class="rt">ルーレット</span>（2000P か 4000P）</td></tr><tr><td>1/99</td><td><span class="rt">ルーレット</span>（5000P か 10000P）</td></tr><tr><td>1/121</td><td><span class="rt">ルーレット</span>（10000P か 20000P）</td></tr></table>
      <p class="note">いるあいだは この表だけ（いつものポイント・チケットは出ないよ）</p>`],
    ['育', '#b07a46', '育つ・色がかわる', `<p>・お世話 <b>50・100・150・200・250回</b>で大きく育つ</p><p>・<b>300回</b>で次の色の子に（ブラウン → まだら → ブラック → ホワイト → 肌色）</p>`],
    ['時', '#4a6aa8', '時間でかわるフィールド', `<p>・朝 7:00〜15:59・夕方 16:00〜18:59・夜 19:00〜6:59</p>`],
  ];
  let root = null, inner = null, body = null, t0 = null;
  function build(el) {
    if (!document.getElementById('tcg-css')) { const st = document.createElement('style'); st.id = 'tcg-css'; st.textContent = CSS; document.head.appendChild(st); }
    root = document.createElement('div'); root.id = 'tcg';
    root.innerHTML = `<div class="bk"></div><div class="sh"><div class="hd"><b>トレーニングセンターの説明書</b><div class="x">✕</div></div><div class="bd"><div class="in">` +
      SEC.map(([ic, col, tt, html]) => `<div class="sec"><h3><i style="background:${col}">${ic}</i>${tt}</h3>${html}</div>`).join('') + `</div></div></div>`;
    el.appendChild(root); inner = root.querySelector('.in'); body = root.querySelector('.bd');
    root.querySelector('.x').addEventListener('click', () => close(true));
    root.querySelector('.bk').addEventListener('click', () => close(true));
    body.style.overflowY = 'auto';
  }
  let anim = null, onClose = null;
  function tween(a, b, dur, done) {           
    if (anim) cancelAnimationFrame(anim); const t0 = performance.now();
    const f = () => { const u = Math.min(1, (performance.now() - t0) / (dur * 1000)); set(a + (b - a) * u); if (u < 1) anim = requestAnimationFrame(f); else { anim = null; if (done) done(); } };
    anim = requestAnimationFrame(f);
  }
  function open(el, opt) {
    if (!root) build(el); root.style.display = 'flex';
    if (opt && opt.anim) { onClose = opt.onClose || null; body.scrollTop = 0; set(0.001); tween(0, 1, 0.35); } else set(1);
  }
  function set(k) {                    
    if (!root) return; const e = 1 - Math.pow(1 - Math.max(0, Math.min(1, k)), 3);
    root.querySelector('.sh').style.transform = `translateY(${(1 - e) * 105}%)`; root.querySelector('.bk').style.opacity = String(e);
    root.style.display = k <= 0.001 ? 'none' : 'flex';
  }
  function scroll(f) { if (body) body.scrollTop = Math.max(0, Math.min(1, f)) * (body.scrollHeight - body.clientHeight); }
  function close(a) { if (a && root && root.style.display !== 'none') tween(1, 0, 0.3, () => { if (onClose) { const f = onClose; onClose = null; f(); } }); else set(0); }
  function isOpen() { return !!root && root.style.display !== 'none'; }
  return { open, set, scroll, close, isOpen, get el() { return root; } };
})();

;






const TCFX = (() => {
  const W = 390, H = 614, TAU = Math.PI * 2;
  const AP = p => (typeof window.TC_ASSET === 'function' ? window.TC_ASSET(p) : p);
  const SANS = '"Hiragino Sans", "BIZ UDPGothic", "Noto Sans CJK JP", sans-serif', SERIF = '"Hiragino Mincho ProN", "Noto Serif CJK JP", serif';
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x)), sm = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
  const smoother = x => { x = clamp(x, 0, 1); return x * x * x * (x * (x * 6 - 15) + 10); };
  const backOut = x => { x = clamp(x, 0, 1); const c = 1.6; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  const easeOut = x => 1 - Math.pow(1 - clamp(x, 0, 1), 3);
  const mod = (x, m) => ((x % m) + m) % m;
  function hash(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }
  const IMC = {};
  const img = s => IMC[s] || (IMC[s] = new Promise(ok => { const i = new Image(); i.onload = () => ok(i); i.onerror = () => ok(null); i.src = AP(s); }));
  let g = null, PX = 1;
  function poly(pts, fill) { g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]); g.closePath(); g.fillStyle = fill; g.fill(); }
  function line(x0, y0, x1, y1, col, lw) { g.strokeStyle = col; g.lineWidth = lw; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); }
  function label(txt, x, y, size, fill, edge, ew, font) {
    g.font = `900 ${size}px ${font || SANS}`; g.textAlign = 'center'; g.textBaseline = 'middle';
    if (edge) { g.lineJoin = 'round'; g.lineWidth = ew; g.strokeStyle = edge; g.strokeText(txt, x, y); }
    g.fillStyle = fill; g.fillText(txt, x, y);
  }
  
  function play(cv, o, draw, sound) {
    return new Promise(done => {
      const q = cv.getContext('2d'); const st = { t0: performance.now(), tap: null, end: null, closeAt: null, last: 0 };
      const now = () => (performance.now() - st.t0) / 1000;
      const onTap = e => { if (e) { e.preventDefault(); e.stopPropagation(); } st.tapReq = true; };
      cv.classList.add('on'); cv.addEventListener('pointerdown', onTap);
      let raf = 0;
      const fr = () => {
        const u = now();
        if (st.tapReq) { st.tapReq = false; if (st.tap == null && u > (o.tapMin || 0.8)) st.tap = u; else if (st.end != null && u > st.end + 0.6 && st.closeAt == null) st.closeAt = u; }
        if (st.tap == null && u > 30) st.tap = u;                       
        if (st.end != null && st.closeAt == null && u > st.end + 3.0) st.closeAt = u;
        PX = cv.width / W; g = q; g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, cv.width, cv.height); g.setTransform(PX, 0, 0, PX, 0, 0);
        const fade = st.closeAt != null ? 1 - sm((u - st.closeAt) / 0.5) : 1;
        g.globalAlpha = fade; const r = draw(u, st); g.globalAlpha = 1;
        if (sound) sound(u, st, st.last);
        st.last = u;
        if (r && r.end != null && st.end == null) st.end = r.end;
        if (st.closeAt != null && u > st.closeAt + 0.52) { cv.removeEventListener('pointerdown', onTap); g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, cv.width, cv.height); cv.classList.remove('on'); done(); return; }
        raf = requestAnimationFrame(fr);
      };
      raf = requestAnimationFrame(fr);
    });
  }
  const se = (o, name, gain, lag) => { try { if (o.se) o.se(name, gain, lag); } catch (e) {   } };
  const DIMR = { morning: 0.42, evening: 0.38, night: 0.26, abyss: 0.26, divine: 0.36 };      

  
  const RT_STYLE = {
    normal: { glow: [255, 196, 92], hglow: null, chev: ['#e0434a', '#bf2f36', '#fff1d6'], n: 1, star: ['#f6d36e', '#d9a43c'], gem: '#d8333a', tap: ['#d23b30', '#b52f27', '#f0c25a'], card: ['#22603a', '#1a4f2f', '#f0c25a', '#c8922f'], conf: ['#f3c55a', '#d8333a', '#2f7a46', '#fff1c9'], line: 'rgba(255,248,230,0.55)' },
    maboroshi: { glow: [176, 98, 245], hglow: [440, 380], chev: ['#f3ecfa', '#cdb8e2', '#9a4fc8'], n: 2, star: ['#f2f0f6', '#a9a3b8'], gem: null, tap: ['#9a33bf', '#7f2a9f', '#e6e1ee'], card: ['#8e2db2', '#74229a', '#ebe7f2', '#a9a3b8'], conf: ['#d9b3f0', '#a63cc9', '#f0edf6', '#7f2a9f'], line: 'rgba(255,250,255,0.6)' },
    kamisama: { glow: [255, 212, 118], hglow: [440, 380], chev: ['#ffd85e', '#e3a83a', '#fff4cf'], n: 2, star: ['#f8d672', '#d4a03a'], gem: null, tap: ['#cd3030', '#ad2626', '#f3c95e'], card: ['#c93030', '#a82626', '#f3c95e', '#c8922f'], conf: ['#f6d06a', '#cd3030', '#fff3cf', '#e6a93a'], line: 'rgba(255,248,230,0.55)' },
  };
  const K = H / 1536, OX = (W - 1024 * K) / 2;            
  let GEO = null;
  async function rtLoad(th) {
    if (!GEO) { try { GEO = await fetch(AP('tc_rt_geom.json')).then(r => r.json()); } catch (e) { GEO = null; } }
    const I = {}; await Promise.all(['plate', 'knob', 'stick', 'ptr'].map(async p => { I[p] = await img(`rt_${th}_${p}.webp`); }));
    return I;
  }
  function rtAngle(r, u) {
    const off = (hash(r.a + r.b + r.win) - 0.5) * 0.9, fin = r.win * Math.PI + off;
    if (r.S0 == null || u < r.S0) return 0;
    const p = clamp((u - r.S0) / (r.S1 - r.S0), 0, 1), e = 1 - Math.pow(1 - p, 2.5);
    const turns = 2 + mod(fin, TAU) / TAU; return fin - turns * TAU * (1 - e);
  }
  function leverK(r, u) {
    let down = 0; const HIT = r.HIT;
    if (HIT != null && u >= HIT && u < HIT + 0.09) down = sm((u - HIT) / 0.09);
    else if (HIT != null && u >= HIT + 0.09) { const v = u - HIT - 0.09; down = Math.max(-0.3, Math.exp(-v * 7) * Math.cos(v * 14)); }
    const th = 1.1 * down; return { c: Math.cos(th), s: Math.sin(th) };
  }
  function drawSprite(im, P, sx, sy, ax, ay) { if (!im) return; g.save(); g.translate(ax, ay); g.scale(sx, sy); g.drawImage(im, P.x - ax, P.y - ay, P.w, P.h); g.restore(); }
  function drawLever(r, I, Gm, u) {
    const L = leverK(r, u), [px, py] = Gm.pivot, [kx, ky] = Gm.knob;
    drawSprite(I.stick, Gm.parts.stick, 1 + 0.1 * L.s, Math.max(0.35, L.c), px, py);
    const nx = px + (kx - px) * L.c, ny = py + (ky - py) * L.c, ks = 1 + 0.16 * L.s;
    if (!I.knob) return;
    const P = Gm.parts.knob; g.save(); g.translate(nx, ny); g.scale(ks, ks); g.drawImage(I.knob, P.x - kx, P.y - ky, P.w, P.h); g.restore();
    if (r.HIT != null && u > r.HIT && u < r.HIT + 0.3) {
      const q = (u - r.HIT) / 0.3, R = Gm.knob[2] * ks; g.save(); g.globalAlpha *= 1 - q; g.lineCap = 'round';
      for (let i = 0; i < 8; i++) { const a = -Math.PI / 2 + i * Math.PI / 4, r0 = R + 18 + 22 * q; line(nx + Math.cos(a) * r0, ny + Math.sin(a) * r0, nx + Math.cos(a) * (r0 + 26), ny + Math.sin(a) * (r0 + 26), '#fff3c4', 7); }
      g.restore();
    }
  }
  function drawFace(r, Gm, ang, glowK) {
    const st = RT_STYLE[r.th], [cx, cy] = Gm.c, R = Gm.r;
    g.save(); g.translate(cx, cy);
    g.save(); g.beginPath(); g.arc(0, 0, R + 2, 0, TAU); g.clip();
    g.save(); g.rotate(ang);
    const N = 18;
    for (let i = 0; i < 2; i++) {
      const a0 = -Math.PI + i * Math.PI, cols = Gm.face[i];
      for (let j = 0; j < N; j++) { const s0 = a0 + j * Math.PI / N, s1 = s0 + Math.PI / N; g.fillStyle = cols[j % 2]; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, R + 4, s0 - 0.002, s1 + 0.002); g.closePath(); g.fill(); }
      for (let j = 1; j < N; j++) { const s = a0 + j * Math.PI / N; line(0, 0, Math.cos(s) * (R + 4), Math.sin(s) * (R + 4), j % 2 ? 'rgba(255,255,255,0.18)' : 'rgba(0,0,0,0.07)', 1.4); }
      if (i === r.win && glowK > 0) { g.save(); g.globalAlpha *= 0.32 * glowK; g.fillStyle = '#fffbe8'; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, R + 4, a0, a0 + Math.PI); g.closePath(); g.fill(); g.restore(); }
    }
    line(-R - 4, 0, R + 4, 0, st.line, 5); line(-R - 4, 2.5, R + 4, 2.5, 'rgba(0,0,0,0.12)', 2);
    g.restore();
    const sh = g.createRadialGradient(0, 0, R * 0.25, 0, 0, R + 2);
    sh.addColorStop(0, 'rgba(255,250,235,0.07)'); sh.addColorStop(0.72, 'rgba(0,0,0,0)'); sh.addColorStop(1, 'rgba(40,15,0,0.26)');
    g.fillStyle = sh; g.fillRect(-R - 4, -R - 4, 2 * R + 8, 2 * R + 8);
    g.restore();
    for (let i = 0; i < 2; i++) {                 
      const phi = -Math.PI / 2 + i * Math.PI + ang, v = Math.abs(Math.sin(phi));
      const d = R * (0.57 + 0.07 * (1 - v)); let fs = R * 0.37 * (0.68 + 0.32 * v);
      const x = Math.cos(phi) * d, y = Math.sin(phi) * d, txt = (i ? r.b : r.a) + 'P';
      g.font = `900 ${fs}px ${SERIF}`; const tw = g.measureText(txt).width, mw = R * 1.36; if (tw > mw) fs *= mw / tw;
      g.save(); g.shadowColor = 'rgba(0,0,0,0.35)'; g.shadowOffsetY = 5 * K * PX; g.shadowBlur = 6 * K * PX;
      label(txt, x, y, fs, '#fff4dc', Gm.edge, fs * 0.22, SERIF); g.restore();
      label(txt, x, y, fs, '#fff6e4', Gm.edge, fs * 0.15, SERIF);
    }
    g.save(); g.rotate(ang);                       
    const Ro = R * 0.27, Ri = R * 0.1;
    for (let i = 0; i < 8; i++) {
      const a = -Math.PI / 2 + i * Math.PI / 4, al = a - Math.PI / 8, ar = a + Math.PI / 8;
      const T = [Math.cos(a) * Ro, Math.sin(a) * Ro], Lp = [Math.cos(al) * Ri, Math.sin(al) * Ri], Rp = [Math.cos(ar) * Ri, Math.sin(ar) * Ri];
      poly([[0, 0], Lp, T], st.star[0]); poly([[0, 0], T, Rp], st.star[1]);
    }
    for (let i = 0; i < 8; i++) {
      const a = -Math.PI / 2 + Math.PI / 8 + i * Math.PI / 4, al = a - Math.PI / 8, ar = a + Math.PI / 8, r2 = Ro * 0.55;
      poly([[0, 0], [Math.cos(al) * Ri, Math.sin(al) * Ri], [Math.cos(a) * r2, Math.sin(a) * r2]], st.star[1]); poly([[0, 0], [Math.cos(a) * r2, Math.sin(a) * r2], [Math.cos(ar) * Ri, Math.sin(ar) * Ri]], st.star[0]);
    }
    if (st.gem) { const q = Ri * 0.85; poly([[0, -q], [q * 0.8, 0], [0, q], [-q * 0.8, 0]], st.gem); poly([[0, -q], [q * 0.8, 0], [0, 0]], 'rgba(255,255,255,0.28)'); }
    g.restore();
    g.restore();
  }
  function drawGlow(r, Gm, u) {
    const st = RT_STYLE[r.th], [cx, cy] = Gm.c, R = Gm.r * 1.22, [cr, cg, cb] = st.glow;
    const rg = g.createRadialGradient(cx, cy, R * 0.3, cx, cy, R * 1.55);
    rg.addColorStop(0, `rgba(${cr},${cg},${cb},0.42)`); rg.addColorStop(0.5, `rgba(${cr},${cg},${cb},0.2)`); rg.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
    g.fillStyle = rg; g.fillRect(cx - R * 1.6, cy - R * 1.6, R * 3.2, R * 3.2);
    g.save(); g.translate(cx, cy); g.rotate(0.04 * u);
    for (let i = 0; i < 16; i++) {
      const a = i * TAU / 16, w = 0.07, lg = g.createRadialGradient(0, 0, R * 0.8, 0, 0, R * 1.7);
      lg.addColorStop(0, `rgba(${cr},${cg},${cb},0.10)`); lg.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
      g.fillStyle = lg; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, R * 1.7, a - w, a + w); g.closePath(); g.fill();
    }
    g.restore();
    if (st.hglow) {
      const [hx, hy] = st.hglow, hr = 400, hg = g.createRadialGradient(hx, hy, 40, hx, hy, hr);
      hg.addColorStop(0, `rgba(${cr},${cg},${cb},0.38)`); hg.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
      g.fillStyle = hg; g.fillRect(hx - hr, hy - hr, hr * 2, hr * 2);
    }
  }
  function drawChev(r, Gm, u) {
    const k = sm(u / 0.5) * (r.HIT != null ? 1 - sm((u - r.HIT) / 0.2) : 1); if (k <= 0) return;
    const st = RT_STYLE[r.th], [cx, cy] = Gm.chev, bob = 7 * Math.sin((u - 0.5) * TAU * 1.0);
    g.save(); g.globalAlpha *= k;
    for (let i = 0; i < st.n; i++) {
      const y = cy + bob + (st.n === 2 ? (i - 0.5) * 36 : 0), q = st.n === 2 ? 0.95 : 1.25;
      const V = [[-32, -16], [0, 12], [32, -16], [20, -28], [0, -10], [-20, -28]].map(([x, yy]) => [cx + x * q, y + yy * q]);
      g.save(); g.shadowColor = 'rgba(0,0,0,0.3)'; g.shadowBlur = 6 * K * PX; g.shadowOffsetY = 3 * K * PX;
      g.beginPath(); V.forEach((p, j) => j ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.closePath(); g.fillStyle = st.chev[2]; g.fill(); g.restore();
      const S = [[-32, -16], [0, 12], [32, -16], [20, -28], [0, -10], [-20, -28]].map(([x, yy]) => [cx + x * q * 0.78, y + 2 + yy * q * 0.78]);
      poly([S[0], S[1], S[4], S[5]], st.chev[0]); poly([S[1], S[2], S[3], S[4]], st.chev[1]);
    }
    g.restore();
  }
  function drawTap(r, Gm, u) {
    const k = sm((u - 1.0) / 0.3) * (r.HIT != null ? 1 - sm((u - r.HIT) / 0.15) : 1); if (k <= 0) return;
    const st = RT_STYLE[r.th], cx = Math.min(Gm.chev[0], 856), cy = Gm.chev[1], y = cy - (r.th === 'normal' ? 84 : 108) + 4 * Math.sin((u - 1.0) * 2 * Math.PI * 0.9);
    g.save(); g.globalAlpha *= k; g.translate(cx, y); const s = 1 + 0.03 * Math.sin((u - 1.0) * 5); g.scale(s, s);
    const w = 250, h = 100, c = 22;
    poly([[-w / 2 + 8, -h / 2 + 12], [w / 2 + 8, -h / 2 + 12], [w / 2 + 8, h / 2 + 12], [-w / 2 + 8, h / 2 + 12]], 'rgba(0,0,0,0.25)');
    poly([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]], st.tap[2]);
    poly([[-w / 2 + 7, -h / 2 + 7], [w / 2 - 7, -h / 2 + 7], [w / 2 - 7, 0], [-w / 2 + 7, 0]], st.tap[0]);
    poly([[-w / 2 + 7, 0], [w / 2 - 7, 0], [w / 2 - 7, h / 2 - 7], [-w / 2 + 7, h / 2 - 7]], st.tap[1]);
    poly([[w / 2 - c - 7, -h / 2 + 7], [w / 2 - 7, -h / 2 + 7], [w / 2 - 7, -h / 2 + 7 + c]], 'rgba(255,255,255,0.3)');
    label('タップ', 0, 3, 66, '#fff6e2', '#3a160c', 15);
    g.restore();
  }
  function drawGet(r, Gm, val, k) {
    if (k <= 0) return;
    const st = RT_STYLE[r.th], [x0, y0, x1, y1] = Gm.bottom, cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, w = x1 - x0, h = y1 - y0, s = backOut(k);
    g.save(); g.globalAlpha *= sm(k * 2); g.translate(cx, cy); g.scale(s, s);
    const e = 70, hh = h * 0.42;
    for (const sg of [-1, 1]) {
      const xa = sg * (w / 2 - e), xb = sg * (w / 2);
      poly([[xa, -hh + 18], [xb, -hh + 18], [xb - sg * 26, 18], [xb, hh + 18], [xa, hh + 18]], st.card[3]);
      poly([[sg * (w / 2 - e), hh], [sg * (w / 2 - e - 24), hh + 18], [sg * (w / 2 - e), hh + 18]], 'rgba(0,0,0,0.35)');
    }
    const pw = w - 2 * e + 10;
    poly([[-pw / 2 + 10, -hh + 12], [pw / 2 + 10, -hh + 12], [pw / 2 + 10, hh + 12], [-pw / 2 + 10, hh + 12]], 'rgba(0,0,0,0.25)');
    poly([[-pw / 2, -hh], [pw / 2, -hh], [pw / 2, hh], [-pw / 2, hh]], st.card[2]);
    poly([[-pw / 2 + 8, -hh + 8], [pw / 2 - 8, -hh + 8], [pw / 2 - 8, 0], [-pw / 2 + 8, 0]], st.card[0]);
    poly([[-pw / 2 + 8, 0], [pw / 2 - 8, 0], [pw / 2 - 8, hh - 8], [-pw / 2 + 8, hh - 8]], st.card[1]);
    g.font = `900 86px ${SERIF}`; const w1 = g.measureText(val + 'P').width; g.font = `900 58px ${SANS}`; const w2 = g.measureText('GET！！！').width;
    const gap = 16, tot = w1 + gap + w2, sc = Math.min(1, (pw - 50) / tot), xa = -tot / 2;
    g.scale(sc, sc);
    label(val + 'P', xa + w1 / 2, 4, 86, '#ffd65c', '#3a1a08', 15, SERIF);
    label('GET！！！', xa + w1 + gap + w2 / 2, 8, 58, '#fff6e2', '#3a1a08', 12);
    g.restore();
  }
  function confetti(cols, t, k, w, h) {
    if (k <= 0) return;
    for (let i = 0; i < 46; i++) {
      const x0 = hash(i) * (w + 76) - 40, sp = 110 + 130 * hash(i + 7), y = -60 + (t * sp + hash(i + 3) * 420) % (h + 104), sw = 36 * Math.sin(t * (1 + hash(i + 5)) + i);
      g.save(); g.globalAlpha *= 0.9 * k; g.translate(x0 + sw, y); g.rotate(t * (1 + 2 * hash(i + 9)) + i);
      poly([[0, -15], [9, 0], [0, 15], [-9, 0]], cols[i % cols.length]); poly([[0, -15], [9, 0], [0, 0]], 'rgba(255,255,255,0.25)');
      g.restore();
    }
  }
  async function roulette(cv, o) {
    const th = RT_STYLE[o.th] ? o.th : 'normal', I = await rtLoad(th);
    if (!GEO || !GEO[th]) return;
    const Gm = GEO[th], r = { th, a: o.a, b: o.b, win: o.win ? 1 : 0, HIT: null, S0: null, S1: null }, dim = DIMR[o.bg] != null ? DIMR[o.bg] : 0.4;
    let tickIdx = null;
    se(o, 'tc_se_unfold.m4a', 1, 0);
    await play(cv, o, (u, st) => {
      if (st.tap != null && r.HIT == null) { r.HIT = st.tap; r.S0 = r.HIT + 0.05; r.S1 = r.S0 + 3.5; }
      const app = sm(u / 0.45);
      g.save(); g.globalAlpha *= app; g.fillStyle = `rgba(16,10,6,${dim})`; g.fillRect(0, 0, W, H); g.restore();
      g.save(); g.globalAlpha *= app;
      const z = 1 + 0.03 * (1 - sm(u / 0.6)); g.translate(W / 2, H / 2); g.scale(z, z); g.translate(-W / 2, -H / 2);
      g.translate(OX, 0); g.scale(K, K);
      drawGlow(r, Gm, u);
      if (I.plate) g.drawImage(I.plate, 0, 0, 1024, 1536);
      const ang = rtAngle(r, u);
      drawFace(r, Gm, ang, r.S1 != null ? sm((u - r.S1 - 0.1) / 0.4) : 0);
      const P = Gm.parts.ptr; if (I.ptr) g.drawImage(I.ptr, P.x, P.y, P.w, P.h);
      drawLever(r, I, Gm, u); drawChev(r, Gm, u); drawTap(r, Gm, u);
      if (r.S1 != null && u > r.S1 + 0.4) {
        const v = u - r.S1 - 0.4; g.save(); g.setTransform(PX, 0, 0, PX, 0, 0); g.globalAlpha = app * (st.closeAt != null ? 1 - sm((u - st.closeAt) / 0.5) : 1); confetti(RT_STYLE[th].conf, v, sm(v / 0.4), W, H); g.restore();
        drawGet(r, Gm, r.win ? r.b : r.a, v / 0.45);
      }
      g.restore();
      return { end: r.S1 != null ? r.S1 + 1.2 : null };
    }, (u, st, last) => {
      if (r.HIT != null && last < r.HIT && u >= r.HIT) se(o, 'tc_se_rt_lever.m4a', 1, 0);
      if (r.S0 != null && u >= r.S0 && u <= r.S1 + 0.05) {          
        const steps = 6, a0 = Math.max(r.S0, last);
        for (let k = 1; k <= steps; k++) {
          const uu = a0 + (u - a0) * k / steps, idx = Math.floor((rtAngle(r, uu) + Math.PI / 2) / (Math.PI / 8));
          if (tickIdx != null && idx !== tickIdx) se(o, 'tc_se_rt_tick.m4a', 0.9, Math.max(0, uu - u + 1 / 30));
          tickIdx = idx;
        }
      }
      if (r.S1 != null && last < r.S1 + 0.02 && u >= r.S1 + 0.02) se(o, 'tc_se_rt_stop.m4a', 1, 0);
      if (r.S1 != null && last < r.S1 + 0.4 && u >= r.S1 + 0.4) se(o, 'tc_se_rt_confirm.m4a', 1, 0);
    });
  }

  
  const IW = 1086, IH = 1448, TKK = Math.max(W / IW, H / IH), TOX = (W - IW * TKK) / 2, TOY = (H - IH * TKK) / 2;
  const FALL0 = 0.35, FALL = 0.26, LAND = FALL0 + FALL, TAPSHOW = LAND + 0.7, OPEN = 1.25, HOLD = 0.35, REVEAL = 0.95;
  const TKPOS = { 1: [[0, 0, 0, 1.0]], 2: [[-168, -0.1, 14, 0.78], [168, 0.1, 14, 0.78]], 3: [[-248, -0.2, 50, 0.66], [0, 0, 0, 0.7], [248, 0.2, 50, 0.66]] };
  function goldLight(u, k, beamW, open) {
    if (k <= 0) return;
    const cx = IW / 2, cy = 700, br = (0.86 + 0.14 * Math.sin(TAU * u / 2.4)) * k;
    g.save(); g.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 14; i++) {
      const a = i / 14 * TAU + u * 0.05, w = 0.06 + 0.04 * hash(i), L = 1300, gr = g.createRadialGradient(cx, cy, 40, cx, cy, L);
      gr.addColorStop(0, `rgba(255,220,120,${0.16 * br})`); gr.addColorStop(1, 'rgba(255,200,90,0)');
      g.fillStyle = gr; g.beginPath(); g.moveTo(cx, cy); g.arc(cx, cy, L, a - w, a + w); g.closePath(); g.fill();
    }
    const bw = beamW, gb = g.createLinearGradient(cx - bw * 2.2, 0, cx + bw * 2.2, 0);
    gb.addColorStop(0, 'rgba(255,190,80,0)'); gb.addColorStop(0.32, `rgba(255,210,110,${0.28 * br})`); gb.addColorStop(0.5, `rgba(255,250,225,${0.75 * br})`); gb.addColorStop(0.68, `rgba(255,210,110,${0.28 * br})`); gb.addColorStop(1, 'rgba(255,190,80,0)');
    g.fillStyle = gb; g.fillRect(cx - bw * 2.2, 180 - open * 300, bw * 4.4, 1100 + open * 600);
    const gc = g.createRadialGradient(cx, cy, 10, cx, cy, 420 + 600 * open);
    gc.addColorStop(0, `rgba(255,248,215,${0.55 * br})`); gc.addColorStop(0.4, `rgba(255,214,120,${0.22 * br})`); gc.addColorStop(1, 'rgba(255,190,80,0)');
    g.fillStyle = gc; g.fillRect(0, 0, IW, IH);
    for (let i = 0; i < 34; i++) {
      const sp = 40 + 60 * hash(i + 3), x = 120 + hash(i) * 846 + 30 * Math.sin(u * 0.7 + i), y = IH + 40 - ((u * sp + hash(i + 9) * IH) % (IH + 80));
      const tw = 0.55 + 0.45 * Math.sin(u * (0.8 + hash(i + 5)) + i), rr = 3 + 4 * hash(i + 7), gp = g.createRadialGradient(x, y, 0, x, y, rr * 4);
      gp.addColorStop(0, `rgba(255,240,190,${0.85 * tw * k})`); gp.addColorStop(1, 'rgba(255,200,90,0)');
      g.fillStyle = gp; g.beginPath(); g.arc(x, y, rr * 4, 0, TAU); g.fill();
    }
    g.restore();
  }
  function dust(v) {
    if (v < 0 || v > 2.2) return;
    g.save();
    for (let i = 0; i < 44; i++) {
      const s = i % 2 ? 1 : -1, base = i < 26 ? 1185 : IH - 10;
      const x0 = IW / 2 + s * (20 + hash(i) * (i < 26 ? 470 : 560)), vx = s * (90 + 280 * hash(i + 4)), up = 80 + 220 * hash(i + 8);
      const e = 1 - Math.pow(1 - Math.min(1, v / 1.8), 3.0), x = x0 + vx * e, y = base - up * e - 18 * hash(i + 6);
      const rr = (55 + 90 * hash(i + 2)) * (0.4 + 1.1 * e), a = 0.78 * Math.min(1, v / 0.06) * (1 - sm((v - 0.5) / 1.6));
      const c = i % 3 === 0 ? '168,132,88' : i % 3 === 1 ? '140,104,64' : '196,166,122';
      const gp = g.createRadialGradient(x, y, 0, x, y, rr); gp.addColorStop(0, `rgba(${c},${a})`); gp.addColorStop(0.55, `rgba(${c},${a * 0.55})`); gp.addColorStop(1, `rgba(${c},0)`);
      g.fillStyle = gp; g.beginPath(); g.arc(x, y, rr, 0, TAU); g.fill();
    }
    for (let i = 0; i < 18; i++) {
      const s = i % 2 ? 1 : -1, x = IW / 2 + s * (80 + hash(i + 30) * 420) + s * (120 + 200 * hash(i + 31)) * Math.min(1, v / 0.9), y = 1190 - (260 * hash(i + 32)) * Math.min(1, v / 0.9) + 520 * Math.pow(Math.min(1, v / 0.9), 2);
      const a = 1 - sm((v - 0.6) / 0.4); if (a <= 0) continue;
      g.save(); g.globalAlpha *= a * 0.85; g.translate(x, y); g.rotate(v * 6 + i); poly([[-7, -5], [6, -6], [8, 4], [-5, 6]], i % 2 ? '#8a6a44' : '#b08a5c'); g.restore();
    }
    g.restore();
  }
  function tkTap(u, k) {
    if (k <= 0) return;
    g.save(); g.globalAlpha *= k; g.translate(IW / 2, 1268 + 8 * Math.sin(u * TAU * 0.9)); const s = (1 + 0.03 * Math.sin(u * 5)) * (0.7 + 0.3 * backOut(k)); g.scale(s, s);
    const w = 340, h = 132, c = 28;
    poly([[-w / 2 + 9, -h / 2 + 14], [w / 2 + 9, -h / 2 + 14], [w / 2 + 9, h / 2 + 14], [-w / 2 + 9, h / 2 + 14]], 'rgba(0,0,0,0.3)');
    poly([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]], '#7a4a12');
    poly([[-w / 2 + 8, -h / 2 + 8], [w / 2 - 8, -h / 2 + 8], [w / 2 - 8, 0], [-w / 2 + 8, 0]], '#e9b13a');
    poly([[-w / 2 + 8, 0], [w / 2 - 8, 0], [w / 2 - 8, h / 2 - 8], [-w / 2 + 8, h / 2 - 8]], '#d1952a');
    poly([[w / 2 - c - 8, -h / 2 + 8], [w / 2 - 8, -h / 2 + 8], [w / 2 - 8, -h / 2 + 8 + c]], 'rgba(255,255,255,0.3)');
    label('タップ', 0, 4, 88, '#fff6e2', '#3a1a08', 17);
    g.restore();
  }
  let TBACK = null;
  function ticketArt(im, x, y, s, rot, sx, a) {
    if (a <= 0 || s <= 0.01 || !im) return;
    const w = 430, h = w * im.naturalHeight / im.naturalWidth;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot); g.scale(s * Math.abs(sx), s);
    if (sx >= 0) { g.save(); g.shadowColor = 'rgba(40,20,0,0.35)'; g.shadowBlur = 12 * TKK * s * PX; g.shadowOffsetX = 10 * TKK * s * PX; g.shadowOffsetY = 16 * TKK * s * PX; g.drawImage(im, -w / 2, -h / 2, w, h); g.restore(); }
    else {
      if (!TBACK) { TBACK = document.createElement('canvas'); TBACK.width = im.naturalWidth; TBACK.height = im.naturalHeight; const q = TBACK.getContext('2d'); q.drawImage(im, 0, 0); q.globalCompositeOperation = 'source-atop'; q.fillStyle = 'rgba(214,150,40,0.92)'; q.fillRect(0, 0, TBACK.width, TBACK.height); }
      g.drawImage(TBACK, -w / 2, -h / 2, w, h);
    }
    g.restore();
  }
  function getTag(n, v) {
    if (v <= 0) return;
    const s = backOut(v / 0.3), rot = -0.05 * Math.exp(-v * 6) * Math.cos(v * 18);
    g.save(); g.globalAlpha *= sm(v / 0.12); g.translate(IW / 2, 1110); g.rotate(rot); g.scale(s, s);
    const w = 760, h = 230, c = 46;
    poly([[-w / 2 + 14, -h / 2 + 20], [w / 2 + 14, -h / 2 + 20], [w / 2 + 14, h / 2 + 20], [-w / 2 + 14, h / 2 + 20]], 'rgba(0,0,0,0.25)');
    poly([[-w / 2, -h / 2], [w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2, h / 2], [-w / 2, h / 2]], '#fff4d6');
    poly([[-w / 2, 0], [w / 2, 0], [w / 2, h / 2], [-w / 2, h / 2]], '#f7e6bf');
    poly([[w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2 - c, -h / 2 + c]], '#e2c78e');
    g.strokeStyle = 'rgba(160,110,50,0.3)'; g.lineWidth = 3; g.beginPath(); g.moveTo(-w / 2, 0); g.lineTo(w / 2, 0); g.stroke();
    label(`チケット ×${n}`, 0, -40, 84, '#f3b631', '#5b3412', 16);
    label('GET！', 0, 56, 70, '#fffaf0', '#5b3412', 14);
    g.restore();
  }
  function sparkle(x, y, r, a) {
    if (a <= 0 || r <= 0) return;
    g.save(); g.globalCompositeOperation = 'lighter'; g.globalAlpha *= a; g.translate(x, y);
    const k = 0.22; poly([[0, -r], [r * k, -r * k], [r, 0], [r * k, r * k], [0, r], [-r * k, r * k], [-r, 0], [-r * k, -r * k]], 'rgba(255,240,190,0.9)');
    g.restore();
  }
  async function ticket(cv, o) {
    const [closed, open_, tk] = await Promise.all([img('tk_door_closed.webp'), img('tk_door_open.webp'), img('tk_ticket.webp')]);
    const n = Math.max(1, Math.min(3, o.n | 0)), pos = TKPOS[n], dim = (DIMR[o.bg] != null ? DIMR[o.bg] : 0.4) + 0.08;
    const T = { tap: null, get0: null };
    await play(cv, Object.assign({ tapMin: TAPSHOW }, o), (u, st) => {
      if (st.tap != null && T.tap == null) T.tap = Math.max(st.tap, TAPSHOW);
      const uo = T.tap != null ? u - T.tap : -1, get0 = T.tap != null ? T.tap + OPEN + HOLD + 0.55 : null;
      g.fillStyle = `rgba(18,10,4,${dim * sm(u / 0.45)})`; g.fillRect(0, 0, W, H);
      const p = clamp((u - FALL0) / FALL, 0, 1), q = (u - LAND) / 0.3;
      const yOff = u < LAND ? -H * (1 - p * p) : -10 * Math.sin(Math.PI * clamp(q, 0, 1)) * (1 - clamp(q, 0, 1));
      const zoom = uo > 0 ? (uo < OPEN + HOLD ? 1 + 0.08 * smoother(uo / (OPEN + HOLD)) : 1 + 0.08 * (1 - smoother((uo - OPEN - HOLD) / REVEAL))) : 1;
      const opened = uo >= OPEN + HOLD * 0.5;
      if (u >= FALL0) {
        g.save(); g.translate(W / 2, H / 2 + yOff); g.scale(zoom, zoom); g.translate(-W / 2, -H / 2);
        const im = opened ? open_ : closed; if (im) g.drawImage(im, TOX, TOY, IW * TKK, IH * TKK);
        g.save(); g.translate(TOX, TOY); g.scale(TKK, TKK);
        const lk = opened ? 0.75 + 0.25 * sm((uo - OPEN - HOLD - REVEAL * 0.3) / 0.8) : sm((u - LAND - 0.1) / 0.6);
        const ow = uo > 0 && !opened ? smoother(uo / OPEN) : 0;
        goldLight(u, lk, 34 + 520 * Math.pow(ow, 2.2), ow);
        if (u >= LAND) dust(u - LAND);
        g.restore(); g.restore();
      }
      g.save(); g.translate(TOX, TOY); g.scale(TKK, TKK);
      tkTap(u - TAPSHOW, sm((u - TAPSHOW) / 0.3) * (uo >= 0 ? 1 - sm(uo / 0.18) : 1));
      if (uo >= 0 && uo < 0.6) { g.save(); g.strokeStyle = `rgba(255,246,210,${0.8 * (1 - uo / 0.6)})`; g.lineWidth = 10; g.beginPath(); g.arc(IW / 2, 1268, 60 + 260 * easeOut(uo / 0.6), 0, TAU); g.stroke(); g.restore(); }
      g.restore();
      const wh = uo < 0 ? 0 : uo < OPEN ? Math.pow(smoother(uo / OPEN), 1.6) : uo < OPEN + HOLD ? 1 : 1 - smoother((uo - OPEN - HOLD) / REVEAL);
      if (wh > 0) { g.fillStyle = `rgba(255,251,236,${wh})`; g.fillRect(0, 0, W, H); }
      if (get0 != null) {
        const gu = u - get0;
        if (gu > -0.2) {
          g.save(); g.translate(TOX, TOY); g.scale(TKK, TKK);
          confettiTk(gu, sm(gu / 0.5));
          pos.forEach(([dx, rot, dy, sc], i) => {
            const v = gu - i * 0.28; if (v < 0) return;
            const e = easeOut(v / 0.75), x = IW / 2 + dx * e, y = 760 - 60 * e + dy * e, s = (0.15 + 0.85 * backOut(v / 0.75)) * sc, sx = Math.cos(Math.max(0, 1 - v / 0.75) * Math.PI * 2);
            ticketArt(tk, x, y + 6 * Math.sin((v - 0.75) * 2.2), s, rot * e, sx, sm(v / 0.15));
            for (let j = 0; j < 4; j++) { const w2 = v - 0.75 - j * 0.45; if (w2 > 0 && w2 < 0.9) sparkle(x + (hash(i * 7 + j) - 0.5) * 300 * sc, y + (hash(i * 3 + j + 1) - 0.5) * 170 * sc, 22 * Math.sin(Math.PI * w2 / 0.9), 0.9); }
          });
          getTag(n, gu - 0.75 - 0.28 * (pos.length - 1));
          g.restore();
        }
      }
      return { end: get0 != null ? get0 + 0.75 + 0.28 * (pos.length - 1) + 0.6 : null };
    }, (u, st, last) => {
      const cross = x => last < x && u >= x;
      if (cross(FALL0)) se(o, 'tc_se_tk_fall.m4a', 1, 0);
      if (cross(LAND)) se(o, 'tc_se_tk_land.m4a', 1, 0);
      if (cross(TAPSHOW)) se(o, 'tc_se_tk_tapshow.m4a', 1, 0);
      if (T.tap != null) {
        const tt = T.tap, get0 = tt + OPEN + HOLD + 0.55;
        if (cross(tt)) { se(o, 'tc_se_tk_tap.m4a', 1, 0); se(o, 'tc_se_tk_open.m4a', 1, 0); }
        if (cross(tt + OPEN)) se(o, 'tc_se_tk_white.m4a', 1, 0);
        if (cross(tt + OPEN + HOLD)) se(o, 'tc_se_tk_reveal.m4a', 1, 0);
        pos.forEach((_, i) => { if (cross(get0 + i * 0.28)) se(o, 'tc_se_tk_ticket.m4a', 1, 0); });
        if (cross(get0 + 0.75 + 0.28 * (pos.length - 1))) se(o, 'tc_se_tk_get.m4a', 1, 0);
      }
    });
  }
  function confettiTk(t, k) {
    if (k <= 0) return; const cols = ['#ffd65c', '#fff2bf', '#f4a39b', '#f2c24f', '#ffe9a8'];
    for (let i = 0; i < 40; i++) {
      const x0 = hash(i) * (IW + 80) - 40, sp = 90 + 110 * hash(i + 7), y = -60 + (t * sp + hash(i + 3) * 420) % (IH + 120), sw = 30 * Math.sin(t * (1 + hash(i + 5)) + i);
      g.save(); g.globalAlpha *= 0.9 * k; g.translate(x0 + sw, y); g.rotate(t * (1 + 2 * hash(i + 9)) + i);
      poly([[0, -15], [9, 0], [0, 15], [-9, 0]], cols[i % cols.length]); poly([[0, -15], [9, 0], [0, 0]], 'rgba(255,255,255,0.25)');
      g.restore();
    }
  }
  function preload(th) { rtLoad(th || 'normal'); ['tk_door_closed.webp', 'tk_door_open.webp', 'tk_ticket.webp'].forEach(img); }
  return { roulette, ticket, preload };
})();
window.TCFX = TCFX;

;





const TCPlan = (() => {
  const PK = 'tengel.plan', MINS = [20, 15, 10, 8, 5];
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const pad = n => String(n).padStart(2, '0');
  const today = () => { const d = new Date(); return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); };
  const jaDate = s => { const [y, m, d] = String(s).split('-').map(Number); return `${y}年${m}月${d}日`; };
  const WD = ['日', '月', '火', '水', '木', '金', '土'];
  const wday = s => { const [y, m, d] = String(s).split('-').map(Number); return WD[new Date(y, m - 1, d).getDay()]; };
  let P = null, root = null, edit = null, auth = '', host = null;
  function load() {
    try { P = JSON.parse(localStorage.getItem(PK) || 'null'); } catch (e) { P = null; }
    if (!P || !Array.isArray(P.races)) P = { v: 1, on: false, races: [] };
    const td = today(), n0 = P.races.length;
    P.races = P.races.filter(r => r && r.date && r.date >= td);          
    if (P.races.length !== n0) save(true);
  }
  function save(quiet) {
    try { localStorage.setItem(PK, JSON.stringify(P)); } catch (e) {   }
    if (!quiet) resync();
  }
  function resync() { try { if (typeof window.syncNotify === 'function') window.syncNotify(); } catch (e) {   } }
  const N = () => window.TengelNative && window.TengelNative.notify ? window.TengelNative : null;
  async function authState() { try { const n = N(); if (!n) return ''; const r = await n.notify('status'); return (r && r.auth) || ''; } catch (e) { return ''; } }
  const css = `
#tcPlan{--tcpf:"BIZ UDPGothic","Hiragino Sans",sans-serif;position:absolute;inset:0;z-index:60;display:flex;flex-direction:column;background:rgba(30,18,6,.55);padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom);font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif;color:#5a3a1c;touch-action:pan-y}
#tcPlan .pp{position:relative;margin:8px auto;width:calc(100% - 16px);max-width:540px;flex:1 1 auto;min-height:0;display:flex;flex-direction:column;background:#fff8ec;border-radius:18px;box-shadow:0 8px 24px rgba(0,0,0,.4);overflow:hidden}
#tcPlan .ph{flex:none;display:flex;align-items:center;gap:8px;padding:8px 10px 8px 12px;background:linear-gradient(#f6e3bf,#efd6a8);border-bottom:2px solid #e2c48e}
#tcPlan .ph img{height:40px;max-width:60%;object-fit:contain}
#tcPlan .ph .sp{flex:1}
#tcPlan .bx{flex:none;height:36px;padding:0 14px;border-radius:18px;border:2px solid #d9b77c;background:#fff8ec;color:#7a4520;font:700 14px/1 var(--tcpf)}
#tcPlan .pb{flex:1 1 auto;min-height:0;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:12px 12px 24px}
#tcPlan .board{background:#7a5232;border-radius:14px;padding:10px;box-shadow:inset 0 0 0 3px #5e3d22,inset 0 0 0 6px #9a6a40}
#tcPlan .cork{background:#e9d3a4 repeating-linear-gradient(45deg,rgba(150,110,60,.07) 0 6px,transparent 6px 12px);border-radius:8px;padding:12px 10px 14px;min-height:120px}
#tcPlan .bdt{text-align:center;font-size:22px;font-weight:700;color:#5b3412;letter-spacing:.04em;margin:2px 0 2px}
#tcPlan .bsub{text-align:center;font-size:14px;font-weight:700;color:#8a5a2a;margin:0 0 10px}
#tcPlan .dh{margin:14px 2px 6px;font-size:14px;font-weight:700;color:#5b3412;border-bottom:2px dashed rgba(91,52,18,.35);padding-bottom:3px}
#tcPlan .rc{position:relative;background:#fffdf7;border-radius:6px;padding:10px 10px 9px 12px;margin:0 0 10px;box-shadow:0 3px 0 rgba(90,55,20,.25);border-left:6px solid #e0a020}
#tcPlan .rc::before{content:"";position:absolute;top:-6px;left:50%;width:14px;height:14px;margin-left:-7px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#ff9cbc,#c2456f);box-shadow:0 1px 2px rgba(0,0,0,.35)}
#tcPlan .rt{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
#tcPlan .tm{font-size:22px;font-weight:700;color:#c2456f;font-variant-numeric:tabular-nums}
#tcPlan .nm{font-size:16px;font-weight:700;color:#5a3a1c;word-break:break-all}
#tcPlan .mt{font-size:12.5px;color:#8a6a48;margin-top:2px}
#tcPlan .ch{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;align-items:center}
#tcPlan .ch .lb{flex:none;white-space:nowrap;font-size:12px;color:#8a6a48;margin-right:2px}
#tcPlan .nb{min-width:52px;height:30px;border-radius:15px;border:2px solid #d9b77c;background:#fff;color:#8a5a2a;font:700 12.5px/1 var(--tcpf);padding:0 8px}
#tcPlan .nb[aria-pressed="true"]{background:#e0a020;border-color:#c98a10;color:#fff}
#tcPlan .nb:disabled{opacity:.45}
#tcPlan .ra{display:flex;gap:8px;justify-content:flex-end;margin-top:8px}
#tcPlan .sb{height:30px;padding:0 12px;border-radius:15px;border:2px solid #d9b77c;background:#fff8ec;color:#7a4520;font:700 12.5px/1 var(--tcpf)}
#tcPlan .sb.del{border-color:#e7a3b4;color:#b0445f}
#tcPlan .add{display:block;width:100%;height:46px;margin:12px 0 0;border-radius:23px;border:0;background:#c2456f;color:#fff;font:700 16px/1 var(--tcpf);box-shadow:0 3px 0 #8f2f4f}
#tcPlan .empty{text-align:center;color:#8a6a48;font-size:13.5px;padding:18px 6px 8px;line-height:1.6}
#tcPlan .nt{display:flex;align-items:center;gap:10px;background:#fffdf7;border:1.5px solid #ead7b2;border-radius:12px;padding:10px 12px;margin:0 0 12px}
#tcPlan .nt .tx{flex:1;font-size:13px;line-height:1.5}
#tcPlan .nt .tx b{display:block;font-size:15px;color:#5b3412}
#tcPlan .sw{flex:none;width:58px;height:32px;border-radius:16px;border:0;background:#cdbb9a;position:relative;padding:0}
#tcPlan .sw::after{content:"";position:absolute;top:3px;left:3px;width:26px;height:26px;border-radius:50%;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.3);transition:left .15s}
#tcPlan .sw[aria-checked="true"]{background:#3f9f5a}#tcPlan .sw[aria-checked="true"]::after{left:29px}
#tcPlan .warn{font-size:12px;color:#b0445f;margin-top:4px}
#tcPlan .fm{background:#fffdf7;border:1.5px solid #ead7b2;border-radius:12px;padding:12px}
#tcPlan .fm h3{margin:0 0 8px;font-size:16px;color:#5b3412}
#tcPlan .fm label{display:block;font-size:12.5px;color:#8a6a48;margin:10px 0 4px}
#tcPlan .fm input{width:100%;box-sizing:border-box;height:42px;border-radius:10px;border:1.5px solid #d9b77c;background:#fff;color:#5a3a1c;font:700 16px/1 var(--tcpf);padding:0 10px}
#tcPlan .fm .row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
#tcPlan .ocr{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;height:44px;border-radius:12px;border:2px dashed #c98a10;background:#fff4d6;color:#8a5a12;font:700 15px/1 var(--tcpf)}
#tcPlan .om{font-size:12.5px;color:#3f7f3a;margin-top:6px;min-height:1em}
#tcPlan .fa{display:flex;gap:10px;margin-top:14px}
#tcPlan .fa button{flex:1;height:44px;border-radius:22px;font:700 15px/1 var(--tcpf)}
#tcPlan .fa .ok{border:0;background:#c2456f;color:#fff;box-shadow:0 3px 0 #8f2f4f}
#tcPlan .fa .ng{border:2px solid #d9b77c;background:#fff8ec;color:#7a4520}
`;
  function build(el) {
    if (!document.getElementById('tcPlanCss')) { const s = document.createElement('style'); s.id = 'tcPlanCss'; s.textContent = css; document.head.appendChild(s); }
    root = document.createElement('div'); root.id = 'tcPlan'; root.setAttribute('role', 'dialog'); root.setAttribute('aria-modal', 'true'); root.setAttribute('aria-label', '作戦会議');
    root.innerHTML = `<div class="pp"><div class="ph"><img src="tc_icon_plan.webp" alt="作戦会議"><span class="sp"></span><button type="button" class="bx" data-p="close">とじる</button></div><div class="pb"></div></div><input type="file" accept="image/*" hidden data-p="file">`;
    el.appendChild(root);
    root.addEventListener('click', onClick);
    root.querySelector('[data-p=file]').addEventListener('change', onFile);
  }
  function chipRow(r) {
    return `<div class="ch"><span class="lb">通知</span>` + MINS.map(m => `<button type="button" class="nb" data-p="nt" data-id="${esc(r.id)}" data-m="${m}" aria-pressed="${(r.notify || []).includes(m)}"${P.on ? '' : ' disabled'}>${m}分前</button>`).join('') + '</div>';
  }
  function paint() {
    if (!root) return; const b = root.querySelector('.pb');
    if (edit) { b.innerHTML = formHtml(); return; }
    const td = today(), list = P.races.slice().sort((a, c) => (a.date + a.time).localeCompare(c.date + c.time));
    const off = auth === 'denied';
    let h = `<div class="nt"><div class="tx"><b>通知 ${P.on ? 'オン' : 'オフ'}</b>オンに すると、レースごとに えらんだ 時間（20・15・10・8・5分前）に お知らせするよ${off && P.on ? '<div class="warn">iPhone の 通知が オフに なってるよ。iPhone の「設定」→「通知」→「テンゲル」で 通知を 許可してね</div>' : ''}</div>`
      + `<button type="button" class="sw" role="switch" aria-checked="${!!P.on}" aria-label="通知" data-p="on"></button></div>`;
    h += `<div class="board"><div class="cork"><div class="bdt">${jaDate(td)}（${wday(td)}）</div><div class="bsub">お気に入りレース一覧</div>`;
    if (!list.length) h += '<div class="empty">まだ 予約した レースは ないよ<br>下の「＋ レースを予約」から 入れてね</div>';
    let cur = '';
    list.forEach(r => {
      if (r.date !== cur) { cur = r.date; if (r.date !== td) h += `<div class="dh">${jaDate(r.date)}（${wday(r.date)}）</div>`; }
      const meta = [r.venue ? esc(r.venue) : '', r.r ? esc(r.r) + 'R' : '', r.n ? esc(r.n) + '頭' : '', r.dist ? esc(r.dist) + 'm' : ''].filter(Boolean).join('・');
      h += `<div class="rc"><div class="rt"><span class="tm">${esc(r.time || '--:--')}</span><span class="nm">${esc(r.name || 'レース')}</span></div>${meta ? `<div class="mt">${meta}</div>` : ''}${chipRow(r)}`
        + `<div class="ra"><button type="button" class="sb" data-p="edit" data-id="${esc(r.id)}">直す</button><button type="button" class="sb del" data-p="del" data-id="${esc(r.id)}">消す</button></div></div>`;
    });
    h += `<button type="button" class="add" data-p="add">＋ レースを予約</button></div></div>`;
    b.innerHTML = h;
  }
  function formHtml() {
    const r = edit;
    return `<div class="fm"><h3>${r._new ? 'レースを予約' : 'レースを直す'}</h3>`
      + `<button type="button" class="ocr" data-p="ocr">📷 画像から読み取る</button><div class="om" aria-live="polite">${esc(r._msg || '')}</div>`
      + `<label>レース名</label><input data-f="name" type="text" maxlength="40" value="${esc(r.name || '')}" placeholder="例）〇〇特別" autocomplete="off">`
      + `<div class="row2"><div><label>日付</label><input data-f="date" type="date" value="${esc(r.date || today())}"></div><div><label>発走時間</label><input data-f="time" type="time" value="${esc(r.time || '')}"></div></div>`
      + `<div class="row2"><div><label>出走頭数</label><input data-f="n" type="number" inputmode="numeric" min="2" max="18" value="${esc(r.n || '')}" placeholder="例）12"></div><div><label>距離（m）</label><input data-f="dist" type="number" inputmode="numeric" min="800" max="4000" step="100" value="${esc(r.dist || '')}" placeholder="例）1600"></div></div>`
      + `<div class="fa"><button type="button" class="ng" data-p="cancel">やめる</button><button type="button" class="ok" data-p="save">保存</button></div></div>`;
  }
  function readForm() {
    if (!root || !edit) return; const v = k => { const i = root.querySelector(`[data-f="${k}"]`); return i ? i.value.trim() : ''; };
    edit.name = v('name'); edit.date = v('date') || today(); edit.time = v('time'); edit.n = v('n') ? Math.round(+v('n')) : ''; edit.dist = v('dist') ? Math.round(+v('dist')) : '';
  }
  async function onFile(e) {
    const f = e.target.files && e.target.files[0]; e.target.value = ''; if (!f || !edit) return;
    readForm(); edit._msg = '読み取り中…'; paint();
    try {
      const s = window.claude && window.claude.use ? await window.claude.use('sample') : null;
      if (!s || !s.json) throw new Error('none');
      const d = await s.json('', { images: [f] });
      const got = [];
      if (d.rname) { edit.name = d.rname; got.push('レース名'); }
      if (d.n) { edit.n = +d.n; got.push('頭数'); }
      if (d.dist) { edit.dist = +d.dist; got.push('距離'); }
      if (d.start) { edit.time = String(d.start).padStart(5, '0'); got.push('発走時間'); }
      if (d.date && /^\d{4}-\d{2}-\d{2}$/.test(d.date) && d.date >= today()) edit.date = d.date;
      if (d.venue) edit.venue = d.venue; if (d.r) edit.r = +d.r;
      edit._msg = got.length ? `読み取ったよ（${got.join('・')}）。ちがう 所は 直してね` : '読み取れなかったよ。手で 入れてね';
    } catch (er) { edit._msg = '読み取れなかったよ。手で 入れてね'; }
    paint();
  }
  async function onClick(e) {
    const a = e.target.closest('[data-p]'); if (!a) { if (e.target === root) close(); return; }
    const k = a.dataset.p;
    if (k === 'close') { close(); return; }
    if (k === 'on') {
      if (!P.on) {
        const n = N(); let ok = true;
        if (n) { try { const r = await n.notify('permission'); auth = (r && r.auth) || auth; ok = !!(r && (r.granted || r.auth === 'authorized' || r.auth === 'provisional')); } catch (er) { ok = false; } }
        P.on = true; save(); if (!ok) auth = 'denied';
      } else { P.on = false; save(); }
      paint(); return;
    }
    if (k === 'nt') {
      const r = P.races.find(x => x.id === a.dataset.id); if (!r) return; const m = +a.dataset.m;
      r.notify = (r.notify || []).includes(m) ? r.notify.filter(x => x !== m) : (r.notify || []).concat(m).sort((x, y) => y - x);
      save(); paint(); return;
    }
    if (k === 'add') { edit = { _new: true, id: 'p' + Date.now().toString(36), date: today(), time: '', name: '', n: '', dist: '', notify: [] }; paint(); root.querySelector('.pb').scrollTop = 0; return; }
    if (k === 'edit') { const r = P.races.find(x => x.id === a.dataset.id); if (!r) return; edit = Object.assign({}, r); paint(); root.querySelector('.pb').scrollTop = 0; return; }
    if (k === 'del') { const r = P.races.find(x => x.id === a.dataset.id); if (!r) return; if (!confirm(`「${r.name || 'レース'}」を 消す？`)) return; P.races = P.races.filter(x => x.id !== r.id); save(); paint(); return; }
    if (k === 'cancel') { edit = null; paint(); return; }
    if (k === 'ocr') { readForm(); root.querySelector('[data-p=file]').click(); return; }
    if (k === 'save') {
      readForm(); const r = edit;
      if (!r.name && !r.time) { r._msg = 'レース名か 発走時間を 入れてね'; paint(); return; }
      if (r.date < today()) { r._msg = '今日より 前の 日は 入れられないよ'; paint(); return; }
      const out = { id: r.id, date: r.date, time: r.time, name: r.name, n: r.n || '', dist: r.dist || '', venue: r.venue || '', r: r.r || '', notify: r.notify || [] };
      const i = P.races.findIndex(x => x.id === r.id); if (i >= 0) P.races[i] = out; else P.races.push(out);
      edit = null; save(); paint(); return;
    }
  }
  async function open(el) {
    host = el; load();
    if (!root) build(el); else if (root.parentNode !== el) el.appendChild(root);
    edit = null; root.style.display = 'flex'; paint();
    auth = await authState(); paint();
  }
  function close() { if (root) root.style.display = 'none'; edit = null; }
  function isOpen() { return !!root && root.style.display !== 'none'; }
  return { open, close, isOpen };
})();
window.TCPlan = TCPlan;

;






const TCApp = (() => {
  const W = 1052, H = 1657;
  const SK = 'tengel.tc';
  const COLORS = ['brown', 'madara', 'black', 'white', 'hada'];
  const COLOR_JA = { brown: 'ブラウン', madara: 'まだら', black: 'ブラック', white: 'ホワイト', hada: '肌色' };
  const BIG = 1.7;                                    
  const TOKEN_MIN = 10, TOKEN_MAX = 20;               
  const TICK = 120;                                   
  const VISIT_MIN = 10;                               
  const HIGH_N = 5, HIGH_X = 4;                       
  const P_POOP = 1 / 7, P_GOLD = 1 / 20, P_HIGH = 1 / 50, P_MAB = 1 / 245, P_KAMI = 1 / 399;
  const PRIZES = [                                    
    [1 / 3600, { k: 'rt', tier: 'kamisama' }], [1 / 2400, { k: 'tk' }], [1 / 2000, { k: 'rt', tier: 'maboroshi' }], [1 / 1000, { k: 'rt', tier: 'normal' }],
    [1 / 121, { k: 'pt', v: 300 }], [1 / 99, { k: 'pt', v: 200 }], [1 / 85, { k: 'pt', v: 100 }]];
  const RT = { normal: [800, 1600], maboroshi: [1600, 3200], kamisama: [3200, 6400] };
  
  const PRIZES_VISIT = {
    maboroshi: [[1 / 1000, { k: 'rt', tier: 'maboroshi', v: [3200, 6400] }], [1 / 500, { k: 'rt', tier: 'maboroshi', v: [1600, 3200] }], [1 / 300, { k: 'rt', tier: 'maboroshi', v: [800, 1600] }]],
    kamisama: [[1 / 121, { k: 'rt', tier: 'kamisama', v: [10000, 20000] }], [1 / 99, { k: 'rt', tier: 'kamisama', v: [5000, 10000] }], [1 / 85, { k: 'rt', tier: 'kamisama', v: [2000, 4000] }]] };
  const AP = p => String(p).split('/').pop();         
  window.TC_ASSET = AP;

  
  const DEF = () => ({ v: 1, color: 0, cares: 0, total: 0, stock: 5, stockAt: Date.now(), heart: 0, high: 0, tickets: 0, fav: null, poops: [], visit: null, snd: true, gen: 1 });
  let st = null, dirty = false, saveAt = 0;
  function load() { try { const s = JSON.parse(localStorage.getItem(SK) || 'null'); st = Object.assign(DEF(), s && s.v === 1 ? s : {}); } catch (e) { st = DEF(); } }
  function save() { dirty = false; try { localStorage.setItem(SK, JSON.stringify(st)); } catch (e) { } }
  const touch = () => { dirty = true; };
  function stageOf(c) { return c < 50 ? 1 : c < 100 ? 2 : c < 150 ? 3 : c < 200 ? 4 : 5; }
  function scaleOf(c) { return c < 50 ? 0.6 : c < 100 ? 0.7 : c < 150 ? 0.8 : c < 200 ? 0.88 : c < 250 ? 0.94 : 1.0; }      
  function tod(d) { const h = (d || new Date()).getHours(); return h >= 7 && h < 16 ? 'morning' : h >= 16 && h < 19 ? 'evening' : 'night'; }
  function today() { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  
  
  
  
  function tnow() {
    const n = Date.now(), s0 = +st.seen || 0;
    if (n > s0) { st.seen = n; if (n > (tnow.saved || 0) + 60000) { tnow.saved = n; touch(); } }
    return Math.max(n, s0);
  }
  function accrue(now) {                              
    if (st.stock >= TOKEN_MAX) { st.stockAt = now; return 0; }
    const n = Math.floor((now - st.stockAt) / (TOKEN_MIN * 60000)); if (n <= 0) return 0;
    const add = Math.min(n, TOKEN_MAX - st.stock); st.stock += add; st.stockAt = st.stock >= TOKEN_MAX ? now : st.stockAt + n * TOKEN_MIN * 60000; touch(); return add;
  }

  
  const SND = (() => {
    let ac = null, master = null, bed = null, want = null, on = true;
    const cache = {};
    const AMB = { morning: 'tc_amb_morning.m4a', evening: 'tc_amb_evening.m4a', night: 'tc_amb_night.m4a', abyss: 'tc_bgm_abyss.m4a', divine: 'tc_bgm_divine.m4a' };
    function buf(f) { if (!cache[f]) cache[f] = fetch(AP(f)).then(r => { if (!r.ok) throw new Error('no ' + f); return r.arrayBuffer(); }).then(b => new Promise((ok, ng) => { const q = ac.decodeAudioData(b, ok, ng); if (q && q.catch) q.catch(() => { }); })); return cache[f]; }
    function unlock() { try { if (!ac) { const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return; ac = new AC(); master = ac.createGain(); master.gain.value = on ? 1 : 0; master.connect(ac.destination); } if (ac.state === 'suspended') ac.resume(); } catch (e) { } }
    async function field(name) {
      want = name; if (!ac) return; if (bed && bed.name === name) return;
      const old = bed; bed = null;
      if (old) { try { const n = ac.currentTime; old.g.gain.cancelScheduledValues(n); old.g.gain.setValueAtTime(old.g.gain.value, n); old.g.gain.linearRampToValueAtTime(0, n + 2); old.s.stop(n + 2.1); } catch (e) { } }
      const f = AMB[name]; if (!f) return; let b; try { b = await buf(f); } catch (e) { return; }
      if (want !== name || (bed && bed.name === name)) return;
      const s = ac.createBufferSource(); s.buffer = b; s.loop = true;
      const g = ac.createGain(); g.gain.setValueAtTime(0, ac.currentTime); g.gain.linearRampToValueAtTime(1, ac.currentTime + 2);
      s.connect(g); g.connect(master); s.start(); bed = { s, g, name };
    }
    async function se(name, gain, at) {
      if (!ac || !on) return; let b; try { b = await buf(name); } catch (e) { return; }
      try { const s = ac.createBufferSource(); s.buffer = b; const g = ac.createGain(); g.gain.value = gain == null ? 1 : gain; s.connect(g); g.connect(master); s.start(ac.currentTime + Math.max(0, at || 0)); return s; } catch (e) { }
    }
    function stopAll() { if (bed) { try { bed.s.stop(); } catch (e) { } bed = null; } want = null; if (ac && ac.state === 'running') { try { ac.suspend(); } catch (e) { } } }
    function setOn(v) { on = !!v; if (master) master.gain.value = on ? 1 : 0; }
    function preload(list) { if (!ac) return; list.forEach(f => buf(f).catch(() => { })); }
    return { unlock, field, se, stopAll, setOn, preload, get ac() { return ac; } };
  })();
  
  const SE_VAR = { slot: e => 'slot_' + Math.max(1, Math.min(10, e.n || 1)), bite: e => 'bite_' + (e.kind === 'apple' ? 'apple' : 'carrot'), banin: e => 'banin_' + (e.kind === 'maboroshi' ? 'maboroshi' : 'kamisama') };
  const SE_SKIP = { ready2: 'ready', zoomout: 'zoomin', feedstart: null };
  function onCareEvent(e) {
    if (e.k === 'token') { st.cares += 1; st.total = (st.total || 0) + 1; touch(); later.push(() => growCheck()); }      
    let nm = SE_VAR[e.k] ? SE_VAR[e.k](e) : (e.k in SE_SKIP ? SE_SKIP[e.k] : e.k);
    if (!nm) return;
    const lag = Math.max(0, e.t - clock());
    SND.se('tc_se_' + nm + '.m4a', 1, lag);
  }

  
  let ov = null, stage = null, cvGL = null, cvOv = null, cvFx = null, field = null, gl = null, built = false;
  let HO = null, BR = null, horseKey = '', raf = 0, running = false, tBase = 0, lastT = null, lastDraw = 0, nextTick = 0, later = [], busy = false;
  const clock = () => (performance.now() - tBase) / 1000 + 1.5;
  const css = `
#tcOv{position:fixed;inset:0;z-index:90;display:none;flex-direction:column;align-items:center;background:#2a1d12;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom);-webkit-user-select:none;user-select:none;touch-action:none;font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif}
#tcOv.on{display:flex}
#tcOv .tch{width:100%;max-width:560px;box-sizing:border-box;display:flex;align-items:center;gap:8px;padding:6px 10px;height:58px;flex:none}
#tcOv .tcbk{flex:none;height:40px;padding:0 12px;border-radius:20px;border:2px solid #d9b77c;background:#fff8ec;color:#7a4520;font:700 15px/1 "BIZ UDPGothic","Hiragino Sans",sans-serif;display:flex;align-items:center;gap:4px}
#tcOv .tcsp{flex:1 1 auto}
#tcOv .tcst .tcpl{position:absolute;right:2.47%;top:9.1%;width:25%;border:0;padding:0;margin:0;background:none;-webkit-tap-highlight-color:transparent;transition:transform .12s}
#tcOv .tcst .tcpl:active{transform:scale(.94)}
#tcOv .tcpl img{display:block;width:100%;height:auto;pointer-events:none;filter:drop-shadow(0 3px 4px rgba(0,0,0,.35))}
#tcOv .tcsd{flex:none;width:40px;height:40px;border-radius:50%;border:2px solid #d9b77c;background:#fff8ec;font-size:18px;line-height:1;padding:0}
#tcOv .tctk{flex:none;height:30px;padding:0 9px;border-radius:15px;background:#fff4d6;border:2px solid #e2c48e;color:#8a5a12;font:700 13px/26px "BIZ UDPGothic",sans-serif;white-space:nowrap}
#tcOv .tcwr{position:relative;flex:1 1 auto;min-height:0;width:100%;display:flex;align-items:center;justify-content:center;overflow:hidden}
#tcOv .tcbg{position:absolute;inset:-24px;background:#2a1d12 center/cover no-repeat;filter:blur(16px) brightness(.62) saturate(1.1);transform:scale(1.06)}
#tcOv .tcst{position:relative;flex:none;overflow:hidden;touch-action:none;box-shadow:0 0 0 1px rgba(0,0,0,.25),0 6px 24px rgba(0,0,0,.35)}
#tcOv .tcst canvas{position:absolute;left:0;top:0;width:100%;height:100%;display:block}
#tcOv .tcst .tcfx{display:none}#tcOv .tcst .tcfx.on{display:block}
#tcOv .tcmsg{white-space:pre-line;position:absolute;left:50%;top:44%;transform:translate(-50%,-50%);background:#fff8ec;border:2px solid #e2c48e;border-radius:16px;padding:14px 18px;color:#6b3f1d;font:700 16px/1.5 "BIZ UDPGothic",sans-serif;text-align:center;box-shadow:0 6px 18px rgba(0,0,0,.35);max-width:80%;z-index:30;pointer-events:none;opacity:0;transition:opacity .3s}
#tcOv .tcmsg.on{opacity:1}
#tcOv .tcld{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#fff8ec;font:700 16px "BIZ UDPGothic",sans-serif;background:#2a1d12;z-index:40}
`;
  function build() {
    if (built) return; built = true;
    const s = document.createElement('style'); s.id = 'tcCss'; s.textContent = css; document.head.appendChild(s);
    ov = document.createElement('div'); ov.id = 'tcOv'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'トレーニングセンター');
    ov.innerHTML = `<div class="tch"><button type="button" class="tcbk" data-tc="back" aria-label="もどる">← もどる</button>`
      + `<span class="tcsp"></span>`
      + `<span class="tctk" hidden></span><button type="button" class="tcsd" data-tc="snd" aria-label="音"></button></div>`
      + `<div class="tcwr"><div class="tcbg"></div><div class="tcst"><canvas class="tcgl"></canvas><canvas class="tco"></canvas><button type="button" class="tcpl" data-tc="plan" aria-label="作戦会議"><img src="${AP('tc_icon_plan.webp')}" alt="作戦会議"></button><canvas class="tcfx"></canvas><div class="tcmsg" aria-live="polite"></div><div class="tcld">トレーニングセンター…</div></div></div>`;
    document.body.appendChild(ov);
    stage = ov.querySelector('.tcst'); cvGL = ov.querySelector('.tcgl'); cvOv = ov.querySelector('.tco'); cvFx = ov.querySelector('.tcfx');
    ov.addEventListener('click', e => {
      const b = e.target.closest('[data-tc]'); if (!b) return; SND.unlock();
      if (b.dataset.tc === 'back') close();
      else if (b.dataset.tc === 'plan') { if (window.TCPlan) { SND.se('tc_se_button.m4a'); window.TCPlan.open(ov); } }
      else if (b.dataset.tc === 'snd') { st.snd = !st.snd; touch(); SND.setOn(st.snd); paintHead(); }
    });
    const pt = (e, kind) => {
      if (busy || !TCCare.on) return; const r = stage.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width * W, y = (e.clientY - r.top) / r.height * H;
      TCCare.pointer(kind, x, y, clock());
    };
    stage.addEventListener('pointerdown', e => { SND.unlock(); if (e.target === cvOv || e.target === cvGL) { try { stage.setPointerCapture(e.pointerId); } catch (x) { } pt(e, 'down'); } });
    stage.addEventListener('pointermove', e => { if (e.buttons || e.pointerType === 'touch') pt(e, 'move'); });
    stage.addEventListener('pointerup', e => pt(e, 'up'));
    stage.addEventListener('pointercancel', e => pt(e, 'up'));
    window.addEventListener('resize', () => { if (running) layout(); });
    document.addEventListener('visibilitychange', () => { if (!ov.classList.contains('on')) return; if (document.hidden) pause(); else resume(); });
  }
  function paintHead() {
    const b = ov.querySelector('.tcsd'); b.textContent = st.snd ? '🔊' : '🔇'; b.setAttribute('aria-label', st.snd ? '音：オン（押すと けす）' : '音：オフ（押すと 出す）');
    const tk = ov.querySelector('.tctk'); tk.hidden = !(st.tickets > 0); tk.textContent = `🎫 ${st.tickets}`;
    tk.setAttribute('aria-label', `チケット ${st.tickets}枚（設定の 着せ替えで 壁紙の 解放に 使えるよ）`);
  }
  function layout() {
    const vw = window.innerWidth, r = ov.getBoundingClientRect(), head = 58;
    const cs = getComputedStyle(ov), padT = parseFloat(cs.paddingTop) || 0, padB = parseFloat(cs.paddingBottom) || 0;
    const avail = (r.height || window.innerHeight) - padT - padB - head;
    const w = Math.max(200, Math.min(vw, avail * W / H)), h = w * H / W;
    stage.style.width = w + 'px'; stage.style.height = h + 'px';
    const dpr = Math.min(window.devicePixelRatio || 1, W / w);
    const pw = Math.round(w * dpr), ph = Math.round(pw * H / W);
    for (const c of [cvGL, cvOv, cvFx]) if (c.width !== pw || c.height !== ph) { c.width = pw; c.height = ph; }
    if (window.TCCare && TCCare.S) TCCare.S.cs = pw / W;
    return pw / W;
  }
  function msg(txt, sec) {
    const m = ov.querySelector('.tcmsg'); m.textContent = txt; m.classList.add('on');
    clearTimeout(msg._t); msg._t = setTimeout(() => m.classList.remove('on'), (sec || 2.6) * 1000);
  }

  
  const STANCE_KAMI = { bodyW: 0.64, topOut: 0.04, hoofZ: { FL: -0.3, FR: 0.3, HL: -0.26, HR: 0.26 } };      
  function horseSpec() {
    if (st.visit) {
      return st.visit.kind === 'kamisama'
        ? { key: 'kamisama', name: 'tc_horse_bk_kamisama', stage: BIG, eyeGlow: 'gold', lift: 0.14, stance: STANCE_KAMI, glowK: 0.45, glowR: 0.7, light: 'divine' }
        : { key: 'maboroshi', name: 'tc_horse_bk_maboroshi', stage: BIG, eyeGlow: 'purple', light: 'abyss' };
    }
    const c = COLORS[st.color % COLORS.length], s = stageOf(st.cares);
    return { key: c + s + ':' + scaleOf(st.cares), name: `tc_horse_bk_${c}_s${s}`, stage: scaleOf(st.cares) };
  }
  const hcache = {};
  async function loadHorse(sp) {
    if (hcache[sp.key]) return hcache[sp.key];
    const meta = await fetch(AP(sp.name + '.json')).then(r => r.json());
    const bin = await fetch(AP(meta.bin || (sp.name + '.bin'))).then(r => r.arrayBuffer());
    const img = s => s ? new Promise(ok => { const im = new Image(); im.onload = () => ok(im); im.onerror = () => ok(null); im.src = AP(s); }) : Promise.resolve(null);
    const [texImg, nrmImg, ...poopImgs] = await Promise.all([img(meta.tex), img(meta.ntex), img('tc_poop1.webp'), img('tc_poop2.webp'), img('tc_poop3.webp')]);
    const h = TCHorse.create(gl, meta, bin, { base: 175, stage: sp.stage, texImg, nrmImg, eyeGlow: sp.eyeGlow || null, lift: sp.lift || 0, poopImgs: poopImgs.filter(Boolean), stance: sp.stance || null, glowK: sp.glowK || null, glowR: sp.glowR || null });
    hcache[sp.key] = h; return h;
  }
  async function useHorse(first) {
    const sp = horseSpec(); if (sp.key === horseKey && HO) return;
    const h = await loadHorse(sp);
    const nb = TCHorse.brain({ tod: tod(), force: [], stand: false }); nb.rnd = Math.random;
    if (BR) { nb.x = BR.x; nb.y = BR.y; nb.dir = BR.dir; } else { nb.x = 470 + Math.random() * 120; nb.y = 1080 + Math.random() * 90; nb.dir = Math.random() * Math.PI * 2; }
    if (sp.light) nb.light = sp.light;
    nb.poops = (st.poops || []).map(q => Object.assign({ t0: -10, h0: 1.05 }, q));
    HO = h; BR = nb; horseKey = sp.key;
    if (TCCare.on) TCCare.setHorse(HO, BR);
    if (!first && TCCare.on) TCCare.special(st.visit ? st.visit.kind : null);
  }
  function growCheck() {                               
    const s0 = stageOf(st.cares - 1), s1 = stageOf(st.cares), k0 = scaleOf(st.cares - 1), k1 = scaleOf(st.cares);
    if (st.cares >= 300) {
      st.color = (st.color + 1) % COLORS.length; st.cares = 0; st.gen = (st.gen || 1) + 1; touch();
      msg(`🎉 お世話 300回！\n${COLOR_JA[COLORS[st.color]]}の 子が やってきたよ`, 3.6); if (!st.visit) useHorse();
      return;
    }
    if (s1 !== s0 || k1 !== k0) { msg(`🎉 お世話 ${st.cares}回！ 大きく 育ったよ`, 3.2); if (!st.visit) useHorse(); }
  }

  
  function fieldName() { return st.visit ? (st.visit.kind === 'kamisama' ? 'divine' : 'abyss') : tod(); }
  async function syncField() {
    const f = fieldName();
    if (field.field !== f) { await field.setField(f); }
    paintBg(f); SND.field(f);
  }
  function paintBg(f) {                                 
    const bg = ov && ov.querySelector('.tcbg'); if (!bg || bg.dataset.f === f) return;
    bg.dataset.f = f; bg.style.backgroundImage = `url("${AP(`tc_field_${f}.webp`)}")`;
  }
  function chance(t) {
    const r = Math.random(), now = Date.now();
    if (!st.visit && !busy) {
      if (r < P_KAMI) return startVisit('kamisama');
      if (r < P_KAMI + P_MAB) return startVisit('maboroshi');
    }
    if (Math.random() < P_HIGH) { const S = TCCare.S; S.high = HIGH_N; S.highBump = t; S.fx.push({ k: 'luck', t0: t, dur: 2.6 }); SND.se('tc_se_luck.m4a'); st.high = HIGH_N; touch(); }
    if (Math.random() < P_POOP && BR && BR.mode !== 'sleep' && (BR.poops || []).length < 3) BR.poopReq = true;
    void now;
  }
  async function startVisit(kind) {
    st.visit = { kind, until: tnow() + VISIT_MIN * 60000, el: 0 }; touch(); save();
    await useHorse(); await syncField();
    msg(kind === 'kamisama' ? '✨ 神様馬が やってきた！' : '🌙 幻の馬が やってきた！', 3.0);
  }
  async function endVisit() {
    st.visit = null; touch(); save();
    await useHorse(); await syncField();
    msg('また 来てね… と 帰って いったよ', 2.6);
  }
  function lottery() {                                 
    const S = TCCare.S, hi = S.high > 0, k = hi ? HIGH_X : 1;
    if (hi) { S.high -= 1; S.highBump = clock(); st.high = S.high; touch(); }
    const r = Math.random(); let a = 0, tab = st.visit ? PRIZES_VISIT[st.visit.kind] || PRIZES : PRIZES;
    for (const [p, z] of tab) { a += p * k; if (r < a) return Object.assign({}, z, z.k === 'tk' ? { n: tkCount() } : {}); }
    return null;
  }
  function tkCount() { const r = Math.random(); return r < 1 / 8 ? 3 : r < 1 / 8 + 1 / 3 ? 2 : 1; }
  async function onPrize(z) {                           
    if (z.k === 'pt') { grant(z.v, 'トレーニングセンターの お世話'); return; }
    if (busy || !window.TCFX) return;
    busy = true; TCCare.roulette(true);
    try {
      if (z.k === 'rt') {
        const [a, b] = z.v || RT[z.tier] || RT.normal, win = Math.random() < 0.5 ? 0 : 1;
        await TCFX.roulette(cvFx, { th: z.tier, a, b, win, bg: fieldName(), se: SND.se });
        grant(win ? b : a, 'トレーニングセンターの ルーレット');
      } else if (z.k === 'tk') {
        const n = z.n || 1;
        await TCFX.ticket(cvFx, { n, bg: fieldName(), se: SND.se });
        st.tickets = (st.tickets || 0) + n; touch(); save(); paintHead();
        msg(`🎫 チケット ${n}枚 GET！\n設定の「着せ替え」で 壁紙の 解放に 使えるよ`, 3.6);
      }
    } finally { busy = false; TCCare.roulette(false); }
  }
  function grant(v, what) {
    const w = window.TengelWallet;
    if (w && typeof w.grant === 'function') w.grant('tc-' + Date.now().toString(36) + '-' + Math.floor(Math.random() * 1e6).toString(36), v, what).catch(() => { });
  }

  
  function frame(now) {
    raf = requestAnimationFrame(frame);
    if (now - lastDraw < 1000 / 31) return;         
    lastDraw = now;
    const t = clock(), dt = lastT == null ? 1 / 30 : Math.max(0, Math.min(0.1, t - lastT)); lastT = t;
    const ms = Date.now(), gms = tnow();
    if (accrue(gms) > 0 && TCCare.on) { const S = TCCare.S; S.stock = st.stock; S.stockShow = st.stock; S.stockBump = t; }
    if (t >= nextTick) { nextTick = t + TICK; if (t > 3) chance(t); }
    if (BR && !st.visit) BR.tod = tod();
    if (st.visit) st.visit.el = (+st.visit.el || 0) + dt;                                       
    if (st.visit && (gms > st.visit.until || st.visit.el >= VISIT_MIN * 60) && !busy) endVisit();
    else if (!busy && field.field && field.field !== fieldName() && !frame._sw) { frame._sw = true; syncField().finally(() => { frame._sw = false; }); }
    while (later.length) { try { later.shift()(); } catch (e) { } }
    if (!HO || !BR) return;
    const ZV = TCCare.on ? TCCare.view() : null;
    field.render(t, ZV);
    const cvv = gl.canvas, kk = cvv.width / W, Z = ZV ? ZV.z : 1, ZX = ZV ? ZV.cx : W / 2, ZY = ZV ? ZV.cy : H / 2;
    if (TCCare.on) TCCare.pre(t, dt);
    TCHorse.step(HO, BR, t, dt, BR.rnd);
    TCHorse.draw(HO, BR, t, { W: cvv.width, H: cvv.height, k: kk * Z, ox: cvv.width / 2 - ZX * kk * Z, oy: cvv.height / 2 - ZY * kk * Z });
    if (TCCare.on) TCCare.post(t);
    
    const S = TCCare.S;
    if (S.stock !== st.stock) { st.stock = S.stock; touch(); }
    if (S.heart !== st.heart) { st.heart = S.heart; touch(); }
    if ((S.high || 0) !== (st.high || 0)) { st.high = S.high || 0; touch(); }
    const ps = (BR.poops || []).map(q => { if (q.gold == null) q.gold = Math.random() < P_GOLD; return { x: Math.round(q.x), y: Math.round(q.y), img: q.img || 0, w: q.w, gold: !!q.gold }; });
    if (JSON.stringify(ps) !== JSON.stringify(st.poops)) { st.poops = ps; touch(); }
    if (dirty && ms - saveAt > 2000) { saveAt = ms; save(); }
  }
  function pause() { running = false; cancelAnimationFrame(raf); SND.stopAll(); if (dirty) save(); }
  function resume() {
    if (running) return; running = true; lastT = null; lastDraw = 0; SND.unlock(); syncField(); raf = requestAnimationFrame(frame);
  }

  
  let ready = null;
  async function init() {
    load(); build(); paintHead(); SND.setOn(st.snd);
    ov.classList.add('on'); const cs = layout();
    field = TCField.create(cvGL); if (!field) throw new Error('webgl');
    gl = field.gl; tBase = performance.now();
    if (!st.fav || st.fav.day !== today()) { st.fav = { day: today(), kind: ['esa', 'apple', 'carrot'][Math.floor(Math.random() * 3)] }; touch(); }
    if (st.visit && (tnow() > st.visit.until || (+st.visit.el || 0) >= VISIT_MIN * 60)) st.visit = null;
    accrue(tnow());
    await Promise.all([useHorse(true), field.setField(fieldName())]); paintBg(fieldName());
    await TCCare.init({ horse: HO, brain: BR, canvas: cvOv, cs, tod: tod(), bg: st.visit ? fieldName() : '', stageNo: stageOf(st.cares),
      lottery, onPrize, onEvent: onCareEvent, banTop: 352, dropX: 726, hiY: 284, onHelp: () => { if (window.TCGuide) TCGuide.open(stage, { anim: true }); } });
    const S = TCCare.S; S.heart = S.heartShow = st.heart || 0; S.stock = S.stockShow = st.stock; S.high = st.high || 0; S.fav = st.fav.kind;
    nextTick = clock() + TICK;
    SND.preload(['tc_se_button.m4a', 'tc_se_unfold.m4a', 'tc_se_rub.m4a', 'tc_se_heart.m4a', 'tc_se_pick.m4a', 'tc_se_chooser.m4a']);
  }
  async function open(opt) {
    SND.unlock();
    try {
      if (!ready) ready = init(); else { load(); ov.classList.add('on'); layout(); const S = TCCare.S; S.heart = S.heartShow = st.heart || 0; S.high = st.high || 0; }
      await ready;
    } catch (e) { ready = null; if (ov) ov.classList.remove('on'); alert('トレーニングセンターを ひらけなかったよ（' + (e && e.message || e) + '）'); return; }
    const ld = ov.querySelector('.tcld'); if (ld) ld.remove();
    paintHead(); layout(); accrue(tnow());
    if (TCCare.on) { const S = TCCare.S; S.stock = S.stockShow = st.stock; }
    resume();
    if (opt && opt.plan && window.TCPlan) window.TCPlan.open(ov);
  }
  function close() {
    if (window.TCPlan && window.TCPlan.isOpen && window.TCPlan.isOpen()) window.TCPlan.close();
    if (window.TCGuide && TCGuide.isOpen && TCGuide.isOpen()) TCGuide.close();
    pause(); save(); if (ov) ov.classList.remove('on');
    try { document.dispatchEvent(new CustomEvent('tengel:tc')); } catch (e) { }      
  }
  
  const tickets = { count: () => { if (!st) load(); return st.tickets || 0; }, use: () => { if (!st) load(); if ((st.tickets || 0) < 1) return false; st.tickets -= 1; save(); if (ov) paintHead(); return true; } };
  return { open, close, tickets, get state() { return st; }, _snd: SND, _t: { lottery, onPrize, PRIZES, PRIZES_VISIT, fieldName, startVisit } };      
})();

;window.TCField = TCField; window.TCCare = TCCare; window.TCGuide = TCGuide; window.TCApp = TCApp;
