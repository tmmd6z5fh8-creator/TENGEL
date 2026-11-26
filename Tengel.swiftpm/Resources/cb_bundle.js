


















































































































































const CBRules = (() => {
  'use strict';
  const NUMS = ['1', '2', '3', '4', '5', '6', '7'], KINDS = NUMS.concat(['k', 'm']);
  const TURNS = 5, HAND = 7, COPIES = 4;      
  const power = (k, rv) => (k === 'k' || k === 'm' ? 0 : rv ? 8 - +k : +k);      
  
  function compare(a, b, rv) {
    if (a === b) return 'clash';
    const pa = power(a, rv), pb = power(b, rv);
    return pa === pb ? 'tie' : pa < pb ? 0 : 1;
  }
  function shuffle(a, rng) {
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rng() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  
  const GEMS = ['m', 'k', '1', '3', '7'], GEM_W = { m: 1, k: 1, '1': 2, '3': 2, '7': 3 }, GEM_HAND = 6;
  const fullSet = () => { const a = []; NUMS.forEach(k => { for (let i = 0; i < COPIES; i++) a.push(k); }); a.push('k', 'm'); return a; };
  const mkP = () => ({ hand: [], set: null, wins: 0, known: [], eff: null, six: null, r7: 0, x7: 0, x3: 0, gems: [], gused: [], gturn: 0 });      
  const count = (hand, k) => hand.reduce((n, c) => n + (c.k === k ? c.tok || 1 : 0), 0);      
  const realN = hand => hand.reduce((n, c) => n + (c.tok ? 0 : 1), 0);                         
  const hasTok = (hand, k) => hand.some(c => c.tok && c.k === k);
  
  function pickW(hand, k, need) {
    const cs = hand.filter(c => c.k === k).sort((a, b) => (b.tok || 0) - (a.tok || 0)), out = []; let n = 0;
    for (const c of cs) { if (n >= need) break; out.push(c); n += c.tok || 1; }
    return n >= need ? out : null;
  }
  const cardEv = c => (c.tok ? { u: c.u, k: c.k, tok: c.tok } : { u: c.u, k: c.k });      
  const idx = (hand, u) => hand.findIndex(c => c.u === u);

  function newGame(rng, opt) {
    rng = rng || Math.random; opt = opt || {};
    const tn = Math.floor(+opt.turns);
    const S = { v: 6, full: !!opt.full, turn: 1, turns: tn >= 1 && tn <= 9 ? tn : TURNS, phase: 'set', uid: 0, deck: [], discard: [], p: [mkP(), mkP()], pend: null, win: null, last: null, res: null, rv: false, step: null, effN: 0 };      
    let rest = fullSet();
    const take = k => { const j = rest.indexOf(k); if (j < 0) throw new Error('card ' + k); rest.splice(j, 1); return k; };
    if (opt.hands) {
      const hs = opt.hands.map(h => h.map(take));
      let dk;
      if (opt.deck) { dk = opt.deck.map(take); shuffle(rest, rng); dk = dk.concat(rest); } else dk = shuffle(rest, rng);
      
      for (let i = 0; i < 2; i++) S.p[i].hand = hs[i].map(k => ({ u: ++S.uid, k }));
      S.deck = dk.slice().reverse().map(k => ({ u: ++S.uid, k }));
    } else if (opt.rig) {
      
      
      const must = [0, 1].map(i => (Array.isArray(opt.rig[i]) ? opt.rig[i] : []).slice(0, HAND).map(take));
      const dk = shuffle(rest, rng), hk = [must[0].slice(), must[1].slice()];
      for (let n = 0; n < HAND; n++) for (let i = 0; i < 2; i++) if (hk[i].length < HAND) hk[i].push(dk.pop());
      hk.forEach(h => shuffle(h, rng));
      const all = hk[0].length + hk[1].length + dk.length, ids = shuffle(Array.from({ length: all }, (_, j) => j + 1), rng); let q = 0;
      for (let i = 0; i < 2; i++) S.p[i].hand = hk[i].map(k => ({ u: ids[q++], k }));
      S.deck = dk.map(k => ({ u: ids[q++], k })); S.uid = all;
    } else {
      S.deck = shuffle(rest, rng).map(k => ({ u: ++S.uid, k }));
      for (let n = 0; n < HAND; n++) for (let i = 0; i < 2; i++) S.p[i].hand.push(S.deck.pop());      
    }
    const gl = Array.isArray(opt.gems) ? opt.gems : [], gu = Array.isArray(opt.gused) ? opt.gused : [];      
    [0, 1].forEach(i => { const g = Array.isArray(gl[i]) ? gl[i] : [], u = Array.isArray(gu[i]) ? gu[i] : []; S.p[i].gems = GEMS.filter(k => g.indexOf(k) >= 0); S.p[i].gused = S.p[i].gems.filter(k => u.indexOf(k) >= 0); });      
    S.gpub = !!opt.gpub;
    S.ev0 = []; startTurn(S, S.ev0);      
    return S;
  }

  const forget = (S, u) => { S.p.forEach(P => { const j = P.known.indexOf(u); if (j >= 0) P.known.splice(j, 1); }); };
  const learn = (P, u) => { if (P.known.indexOf(u) < 0) P.known.push(u); };
  
  const toss = (S, c, by, why) => { forget(S, c.u); S.discard.push(Object.assign({ u: c.u, k: c.k, by: by, why: why, turn: S.turn }, c.tok ? { tok: c.tok } : {})); };      

  
  const unseen = (P, Q) => Q.hand.filter(c => P.known.indexOf(c.u) < 0);
  
  
  
  
  
  function handOf(P, Q) {
    const kn = c => P.known.indexOf(c.u) >= 0;
    return Q.hand.map(c => (kn(c) ? cardEv(c) : { u: c.u, k: null }));
  }
  
  
  const STEPS = ['u5', 'u4'];
  
  function canStep(S, i, st) {
    const P = S.p[i], Q = S.p[1 - i], sc = P.set && !P.set.blind ? P.set.c.k : null;      
    if (st === 'u5') return sc === '5' && P.hand.length >= 1 && S.deck.length >= 1 && P.hand.some(c => dropOk(S, P, c));      
    if (st === 'u4') return sc === '4' && Q.hand.length >= 1;
    return false;
  }
  
  function dropOk(S, P, c) { return !!c && realN(P.hand) - (c.tok ? 0 : 1) >= S.turns - S.turn; }
  
  const can6 = (S, i) => { const P = S.p[i], Q = S.p[1 - i]; return count(P.hand, '6') >= 2 && unseen(P, Q).length >= 1; };
  
  
  const can7r = (S, i) => { const P = S.p[i]; return S.phase === 'set' && !P.set && !S.rv && P.x7 !== S.turn && count(P.hand, '7') >= 4 && realN(P.hand) - (hasTok(P.hand, '7') ? 0 : 1) >= S.turns - S.turn + 1; };      
  
  
  
  const canX7 = (S, i) => { const P = S.p[i]; return S.phase === 'set' && !P.set && P.x7 !== S.turn && P.r7 !== S.turn && count(P.hand, '7') >= 3 && S.deck.length >= 3; };
  
  
  
  const x3Pool = (S, i) => { const P = S.p[i], Q = S.p[1 - i]; return Q.hand.filter(c => !c.tok && P.known.indexOf(c.u) < 0).map(c => c.u); };
  const canX3 = (S, i) => { const P = S.p[i]; return S.phase === 'set' && !P.set && P.x3 !== S.turn && count(P.hand, '3') >= 3 && P.hand.some(c => c.k === '3' && !c.tok) && x3Pool(S, i).length >= 1; };
  
  const can5 = (S, i) => { const P = S.p[i]; return !!P.set && !P.set.blind && P.set.c.k === '5' && P.hand.length >= 1 && S.deck.length >= 1 && P.hand.some(c => dropOk(S, P, c)); };
  
  const canGem = (S, i, g) => { const P = S.p[i]; return S.phase === 'set' && !P.set && GEMS.indexOf(g) >= 0 && P.gems.indexOf(g) >= 0 && P.gused.indexOf(g) < 0 && P.gturn !== S.turn && P.hand.length <= GEM_HAND; };
  
  
  function revWho(S, r) {
    if (r !== 0 && r !== 1) return null;
    const i = 1 - r, P = S.p[i], mk = P.set.c.k, wk = S.p[r].set.c.k;
    const hit = (mk === '1' && (wk === 'k' || wk === 'm')) || (mk === '2' && wk === '1');
    return hit && count(P.hand, mk) >= 2 && realN(P.hand) - (hasTok(P.hand, mk) ? 0 : 1) >= S.turns - S.turn ? i : null;      
  }

  function act(S, i, a, rng) {
    rng = rng || Math.random;
    const ev = [], bad = why => ({ ok: false, why: why, ev: [] });
    if (!S || (i !== 0 && i !== 1) || !a || typeof a !== 'object') return bad('arg');
    if (S.phase === 'end') return bad('end');
    const P = S.p[i], Q = S.p[1 - i];
    if (a.t === 'set') {                                 
      if (S.phase !== 'set' || P.set) return bad('set');
      const j = idx(P.hand, a.u); if (j < 0) return bad('card');
      const c = P.hand.splice(j, 1)[0];
      P.set = { c: c, up: false, blind: false, open: false, at: j };      
      ev.push({ e: 'set', who: i, u: c.u });
      if (S.p[0].set && S.p[1].set) afterSet(S, ev);
      return { ok: true, ev: ev };
    }
    if (a.t === 'gem') {                                 
      if (!canGem(S, i, a.g)) return bad('gem');
      const c = { u: ++S.uid, k: a.g, tok: GEM_W[a.g] };
      P.hand.push(c); P.gused.push(a.g); P.gturn = S.turn;
      if (S.gpub) learn(Q, c.u);                         
      ev.push({ e: 'gem', who: i, g: a.g, c: cardEv(c), pub: !!S.gpub });
      return { ok: true, ev: ev };
    }
    if (a.t === 'x7r') {                                 
      if (!can7r(S, i)) return bad('x7r');
      const sev = pickW(P.hand, '7', 4), drop = sev[0];      
      P.hand.splice(P.hand.indexOf(drop), 1); toss(S, drop, i, '7');
      sev.slice(1).forEach(c => learn(Q, c.u));          
      S.rv = true; P.r7 = S.turn;
      ev.push({ e: 'x7r', who: i, show: sev.map(c => c.u), drop: cardEv(drop) });
      return { ok: true, ev: ev };
    }
    if (a.t === 'x7') {                                  
      if (!canX7(S, i)) return bad('x7');
      P.x7 = S.turn; doX7(S, i, ev, rng);
      return { ok: true, ev: ev };
    }
    if (a.t === 'x3') {                                  
      if (!canX3(S, i)) return bad('x3');
      if (x3Pool(S, i).indexOf(a.pick) < 0) return bad('pick');
      P.x3 = S.turn; doX3(S, i, ev, a.pick);
      return { ok: true, ev: ev };
    }
    if (a.t === 'p6') {                                  
      if (S.phase !== 'six' || !P.six || P.six.done) return bad('p6');
      if (a.pick != null) {
        if (!P.six.can) return bad('e6');
        if (idx(Q.hand, a.pick) < 0 || P.known.indexOf(a.pick) >= 0) return bad('pick');      
        P.six.pick = a.pick;
      }
      P.six.done = true;
      ev.push({ e: 'sixd', who: i });
      if (S.p[0].six.done && S.p[1].six.done) resolveSix(S, ev);
      return { ok: true, ev: ev };
    }
    if (a.t === 'eff') {                                 
      if (S.phase !== 'eff' || !P.eff || P.eff.done) return bad('eff');
      const stp = P.eff.st, w = a.use && typeof a.use === 'object' ? a.use : {};
      if (w.x7r) return bad('e7r');                     
      if (w.p6 != null) return bad('e6');               
      if (w.x7 || w.x3) return bad(w.x7 ? 'e7' : 'e3');      
      const ask = { u5: w.u5 != null, u4: !!w.u4 }, NUM = { u5: 'e5', u4: 'e4' };
      for (const k of STEPS) if (ask[k] && k !== stp) return bad(NUM[k]);      
      if (stp === 'u5' && ask.u5 && !dropOk(S, P, P.hand[idx(P.hand, w.u5)])) return bad('drop');      
      P.eff.use = ask[stp]; P.eff.drop = stp === 'u5' && ask.u5 ? w.u5 : null; P.eff.done = true;
      ev.push({ e: 'effd', who: i });
      if (S.p[0].eff.done && S.p[1].eff.done) resolveStep(S, ev, rng);
      return { ok: true, ev: ev };
    }
    if (a.t === 'swap') {                                
      if (S.phase !== 'swap' || !S.pend || S.pend.who !== i) return bad('swap');
      const j = idx(P.hand, a.u); if (j < 0) return bad('card');
      const old = P.set.c, c = P.hand.splice(j, 1)[0];
      P.hand.push(old);
      P.set = { c: c, up: false, blind: false, open: false, at: j };
      S.pend = null;
      ev.push({ e: 'swap', who: i, u: c.u, back: old.u });
      
      if (can5(S, i)) { S.phase = 'u5'; S.pend = { type: 'u5', who: i }; ev.push({ e: 'ask5', who: i }); return { ok: true, ev: ev }; }
      open(S, ev);
      return { ok: true, ev: ev };
    }
    if (a.t === 'u5') {                                  
      if (S.phase !== 'u5' || !S.pend || S.pend.type !== 'u5' || S.pend.who !== i) return bad('u5');
      if (a.drop == null) ev.push({ e: 'u5skip', who: i });
      else {
        const d = idx(P.hand, a.drop); if (d < 0 || !can5(S, i) || !dropOk(S, P, P.hand[d])) return bad('drop');
        const five = P.set.c, drop = P.hand.splice(d, 1)[0];
        toss(S, five, i, '5'); toss(S, drop, i, '5');
        P.set = { c: S.deck.pop(), up: false, blind: true, open: false };
        ev.push({ e: 'u5', who: i, five: { u: five.u, k: five.k }, drop: cardEv(drop), sw: true });
      }
      S.pend = null;
      open(S, ev);
      return { ok: true, ev: ev };
    }
    if (a.t === 'k') {                                   
      if (S.phase !== 'pre' || !S.pend || S.pend.type !== 'k' || S.pend.who !== i) return bad('k');
      if (a.pick == null) ev.push({ e: 'kskip', who: i });
      else {
        const j = idx(Q.hand, a.pick); if (j < 0 || P.known.indexOf(a.pick) >= 0) return bad('pick');      
        learn(P, Q.hand[j].u);
        ev.push(Object.assign({ e: 'k', who: i, pick: Q.hand[j].u, k: Q.hand[j].k }, S.pend.tok ? { tok: 1 } : {}));
      }
      S.pend = null; S.phase = 'set';
      return { ok: true, ev: ev };
    }
    if (a.t === 'm') {                                   
      if (S.phase !== 'pre' || !S.pend || S.pend.type !== 'm' || S.pend.who !== i) return bad('m');
      if (a.drop == null) ev.push({ e: 'mskip', who: i });
      else {
        if (!Array.isArray(a.drop) || a.drop.length !== 2 || a.drop[0] === a.drop[1]) return bad('drop');
        const j0 = idx(P.hand, a.drop[0]), j1 = idx(P.hand, a.drop[1]); if (j0 < 0 || j1 < 0) return bad('drop');
        const out = [P.hand[j0], P.hand[j1]];
        P.hand = P.hand.filter(c => out.indexOf(c) < 0);
        out.forEach(c => { toss(S, c, i, 'm'); if (S.pend.tok) S.discard[S.discard.length - 1].wt = 1; });      
        const drew = []; while (drew.length < 2 && S.deck.length) drew.push(S.deck.pop());
        drew.forEach(c => P.hand.push(c));
        ev.push(Object.assign({ e: 'm', who: i, drop: out.map(c => ({ u: c.u, k: c.k })), drew: drew.map(c => ({ u: c.u, k: c.k })) }, S.pend.tok ? { tok: 1 } : {}));
      }
      S.pend = null; S.phase = 'set';
      return { ok: true, ev: ev };
    }
    if (a.t === 'rev') {                                 
      if (S.phase !== 'rev' || !S.pend || S.pend.type !== 'rev' || S.pend.who !== i) return bad('rev');
      let r = S.pend.res;
      if (a.use) {
        const k = P.set.c.k, kn = c => (Q.known.indexOf(c.u) >= 0 ? 1 : 0), tk = P.hand.find(c => c.tok && c.k === k);
        let drop, keep = null;
        if (tk) drop = tk;                               
        else {
          const same = P.hand.filter(c => c.k === k).sort((x, y) => kn(y) - kn(x) || x.u - y.u);      
          if (same.length < 2) return bad('rev');
          drop = same[0]; keep = same[1];
        }
        P.hand.splice(P.hand.indexOf(drop), 1); toss(S, drop, i, k);
        if (keep) learn(Q, keep.u);                      
        r = i;
        ev.push({ e: 'rev', who: i, k: k, show: keep ? [drop.u, keep.u] : [drop.u], drop: cardEv(drop), beat: Q.set.c.k });
      } else ev.push({ e: 'revskip', who: i });
      S.pend = null;
      score(S, r, !!a.use);
      ev.push({ e: 'fin', turn: S.turn, res: r, wins: [S.p[0].wins, S.p[1].wins], rev: !!a.use });
      endTurn(S, ev);
      return { ok: true, ev: ev };
    }
    return bad('type');
  }

  
  function afterSet(S, ev) { nextStep(S, ev, -1); }
  
  
  function nextStep(S, ev, from) {
    for (let k = from + 1; k < STEPS.length; k++) {
      const st = STEPS[k], c0 = canStep(S, 0, st), c1 = canStep(S, 1, st);
      if (!c0 && !c1) continue;
      S.phase = 'eff'; S.step = st; S.effN += 1;
      S.p[0].eff = { st: st, can: c0, done: !c0, use: false, drop: null };
      S.p[1].eff = { st: st, can: c1, done: !c1, use: false, drop: null };
      ev.push({ e: 'efft', st: st, has: [c0, c1], first: from < 0 });
      return;
    }
    S.step = null; S.p.forEach(P => { P.eff = null; });
    open(S, ev);
  }
  
  function resolveSix(S, ev) {
    [0, 1].forEach(i => {
      const P = S.p[i], Q = S.p[1 - i], pk = P.six ? P.six.pick : null;
      if (pk == null) { if (P.six && P.six.can) ev.push({ e: 'p6skip', who: i }); return; }      
      const j = idx(Q.hand, pk), six = P.hand.filter(c => c.k === '6').slice(0, 2);
      if (j < 0 || six.length < 2) { ev.push({ e: 'fizz', who: i, k: '6' }); return; }
      six.forEach(c => learn(Q, c.u));                    
      learn(P, Q.hand[j].u);
      ev.push({ e: 'p6', who: i, six: six.map(c => c.u), pick: Q.hand[j].u, k: Q.hand[j].k });
    });
    S.p.forEach(P => { P.six = null; });
    preKM(S, ev);
  }
  
  function doX7(S, i, ev, rng) {
    const P = S.p[i];
    const back = pickW(P.hand, '7', 3);              
    if (!back || S.deck.length < 3) { ev.push({ e: 'fizz', who: i, k: '7' }); return; }
    P.hand = P.hand.filter(c => back.indexOf(c) < 0);
    const drew = [S.deck.pop(), S.deck.pop(), S.deck.pop()];
    drew.forEach(c => P.hand.push(c));
    const tk = back.find(c => c.tok);                 
    back.forEach(c => { if (c.tok) toss(S, c, i, '7'); else { forget(S, c.u); S.deck.push({ u: ++S.uid, k: c.k }); } });      
    shuffle(S.deck, rng);
    ev.push(Object.assign({ e: 'x7', who: i, n: 3, drew: drew.map(c => ({ u: c.u, k: c.k })) }, tk ? { tok: tk.u, drop: cardEv(tk) } : {}));      
  }
  
  
  function doX3(S, i, ev, pickU) {
    const P = S.p[i], Q = S.p[1 - i];
    const three = pickW(P.hand, '3', 3), give = three && three.find(c => !c.tok), take = Q.hand.find(c => c.u === pickU && !c.tok);      
    if (!three || !give || !take) { ev.push({ e: 'fizz', who: i, k: '3' }); return; }
    P.hand.splice(P.hand.indexOf(give), 1); Q.hand.splice(Q.hand.indexOf(take), 1);
    P.hand.push(take); Q.hand.push(give);
    forget(S, give.u); forget(S, take.u);              
    three.filter(c => c !== give).forEach(c => learn(Q, c.u));        
    learn(P, give.u);                                  
    learn(Q, take.u);                                  
    ev.push({ e: 'x3', who: i, three: three.map(c => c.u), give: cardEv(give), take: cardEv(take) });
  }
  
  function resolveStep(S, ev, rng) {
    const st = S.step, U = S.p.map(P => (P.eff && P.eff.use ? P.eff : null));
    if (st === 'u5') [0, 1].forEach(i => {         
      const P = S.p[i]; if (!U[i]) return;
      const d = idx(P.hand, U[i].drop);
      if (d < 0 || !P.set || P.set.blind || P.set.c.k !== '5' || S.deck.length < 1) { ev.push({ e: 'fizz', who: i, k: '5' }); return; }
      const five = P.set.c, drop = P.hand.splice(d, 1)[0];
      toss(S, five, i, '5'); toss(S, drop, i, '5');
      P.set = { c: S.deck.pop(), up: false, blind: true, open: false };
      ev.push({ e: 'u5', who: i, five: { u: five.u, k: five.k }, drop: cardEv(drop) });
    });
    else if (st === 'u4') {                              
      const A = S.p[0], B = S.p[1], f0 = !!U[0] && !A.set.blind && A.set.c.k === '4', f1 = !!U[1] && !B.set.blind && B.set.c.k === '4';
      S.step = null; S.p.forEach(P => { P.eff = null; });
      if (f0 && f1) { A.set.up = B.set.up = true; ev.push({ e: 'first2' }); open(S, ev, true); return; }      
      if (f0 || f1) {
        const w = f0 ? 0 : 1, F = S.p[w], O = S.p[1 - w];
        F.set.up = true;
        ev.push({ e: 'first', who: w });
        if (O.hand.length >= 1) { S.phase = 'swap'; S.pend = { type: 'swap', who: 1 - w }; return; }
      }
      open(S, ev);
      return;
    }
    S.p.forEach(P => { P.eff = null; });
    nextStep(S, ev, STEPS.indexOf(st));
  }
  
  function open(S, ev, d4) {
    const c0 = S.p[0].set.c, c1 = S.p[1].set.c, r = d4 ? 'tie' : compare(c0.k, c1.k, S.rv), cs = [cardEv(c0), cardEv(c1)];      
    S.step = null; S.p.forEach(P => { P.set.up = true; P.set.blind = false; P.set.open = true; P.eff = null; });
    const rv = revWho(S, r);
    if (rv != null) {                                    
      S.phase = 'rev'; S.pend = { type: 'rev', who: rv, res: r };
      ev.push({ e: 'open', turn: S.turn, c: cs, res: r, wins: [S.p[0].wins, S.p[1].wins], rev: rv });
      return;
    }
    score(S, r, false, d4);
    ev.push(Object.assign({ e: 'open', turn: S.turn, c: cs, res: r, wins: [S.p[0].wins, S.p[1].wins] }, d4 ? { d4: true } : {}));
    endTurn(S, ev);
  }
  
  function score(S, r, rev, d4) {
    const c0 = S.p[0].set.c, c1 = S.p[1].set.c;
    if (r === 0 || r === 1) S.p[r].wins += 1;
    S.last = { turn: S.turn, c: [c0.k, c1.k], res: r, rev: !!rev, d4: !!d4 };
    
    S.win = null;
    if ((r === 0 || r === 1) && S.turn < S.turns) { const wc = r === 0 ? c0 : c1, wk = wc.k; if (wk === 'k' || wk === 'm') S.win = Object.assign({ type: wk, who: r }, wc.tok ? { tok: 1 } : {}); }      
  }
  function endTurn(S, ev) {
    S.p.forEach((P, i) => { if (P.set) { toss(S, P.set.c, i, 't'); P.set = null; } P.eff = null; });
    S.pend = null;
    ev.push({ e: 'clear' });
    S.p.forEach((P, i) => {                              
      const gone = P.hand.filter(c => c.tok); if (!gone.length) return;
      P.hand = P.hand.filter(c => !c.tok); gone.forEach(c => forget(S, c.u));
      ev.push({ e: 'tokgone', who: i, u: gone.map(c => c.u), k: gone.map(c => c.k), pub: !!S.gpub });
    });
    const a = S.p[0].wins, b = S.p[1].wins, left = S.turns - S.turn;      
    const early = !S.full && left > 0 && Math.abs(a - b) > left;      
    if (S.turn >= S.turns || early) {
      S.phase = 'end'; S.res = a > b ? 0 : b > a ? 1 : 'draw'; S.win = null; S.early = early ? S.turn : 0;
      ev.push(Object.assign({ e: 'end', wins: [a, b], res: S.res }, early ? { early: S.turn } : {}));      
      return;
    }
    S.turn += 1; S.phase = 'set';
    ev.push({ e: 'turn', n: S.turn });
    startTurn(S, ev);
  }
  
  
  function startTurn(S, ev) {
    S.phase = 'set';
    const c0 = can6(S, 0), c1 = can6(S, 1);
    if (c0 || c1) {
      S.phase = 'six';
      S.p[0].six = { can: c0, done: !c0, pick: null };
      S.p[1].six = { can: c1, done: !c1, pick: null };
      ev.push({ e: 'sixt', has: [c0, c1] });
      return;
    }
    preKM(S, ev);
  }
  
  function preKM(S, ev) {
    S.phase = 'set';
    const w = S.win; S.win = null;
    if (w) {
      const Wn = S.p[w.who], Ls = S.p[1 - w.who];
      if ((w.type === 'k' && unseen(Wn, Ls).length >= 1) || (w.type === 'm' && Wn.hand.length >= 2 && S.deck.length >= 1)) {      
        S.phase = 'pre'; S.pend = Object.assign({ type: w.type, who: w.who }, w.tok ? { tok: 1 } : {});      
        ev.push(Object.assign({ e: 'pre', who: w.who, type: w.type }, w.tok ? { tok: 1 } : {}));
      }
    }
  }

  
  function view(S, i) {
    const P = S.p[i], Q = S.p[1 - i];
    const setOf = (X, mine) => {                         
      if (!X.set) return null;
      const c = X.set.c, o = { u: c.u, k: null, up: X.set.up, blind: X.set.blind, open: !!X.set.open };
      if (mine) o.k = X.set.blind ? null : c.k;
      else if (X.set.up || X.set.open) o.k = c.k;
      if (o.k != null && c.tok) o.tok = c.tok;      
      return o;
    };
    const st = S.phase === 'eff' && P.eff && !P.eff.done && P.eff.can ? P.eff.st : null;      
    const hide5 = S.phase === 'u5' && !!S.pend && S.pend.who !== i;      
    return {
      v: 4, me: i, turn: S.turn, turns: S.turns, phase: hide5 ? 'swap' : S.phase, deckN: S.deck.length, rv: !!S.rv,      
      discard: S.discard.map(d => Object.assign({ k: d.k, mine: d.by === i, why: d.why, turn: d.turn }, d.tok ? { tok: d.tok } : {}, d.wt ? { wt: 1 } : {})),
      my: { hand: P.hand.map(c => Object.assign({ u: c.u, k: c.k, seen: Q.known.indexOf(c.u) >= 0 }, c.tok ? { tok: c.tok } : {})), set: setOf(P, true), wins: P.wins,
        gem: P.gems.length ? { list: P.gems.slice(), used: P.gused.slice(), can: GEMS.filter(g => canGem(S, i, g)), now: P.gturn === S.turn } : null },      
      op: { hand: handOf(P, Q), set: setOf(Q, false), wins: Q.wins, gem: S.gpub && Q.gems.length ? { list: Q.gems.slice(), used: Q.gused.slice() } : null },      
      can: { set: S.phase === 'set' && !P.set, x7r: can7r(S, i), x7: canX7(S, i), x3: canX3(S, i), x3p: canX3(S, i) ? x3Pool(S, i) : [], gem: GEMS.filter(g => canGem(S, i, g)), eff: st ? { e6: false, e7: false, e3: false, e5: st === 'u5', e4: st === 'u4', st: st, n: S.effN } : null,      
        six: S.phase === 'six' && !!P.six && !P.six.done && P.six.can ? { n: S.turn } : null },      
      pend: S.pend ? Object.assign({ type: hide5 ? 'swap' : S.pend.type, mine: S.pend.who === i }, S.pend.tok ? { tok: 1 } : {}) : null,      
      wait: (S.phase === 'set' && !!P.set && !Q.set) || (S.phase === 'eff' && !!P.eff && P.eff.done && !!Q.eff && !Q.eff.done) || (S.phase === 'six' && !!P.six && P.six.done && !!Q.six && !Q.six.done) || (!!S.pend && S.pend.who !== i),
      last: S.last ? { turn: S.last.turn, c: i === 0 ? S.last.c.slice() : [S.last.c[1], S.last.c[0]], res: S.last.res === 0 || S.last.res === 1 ? (S.last.res === i ? 'win' : 'lose') : S.last.res, rev: !!S.last.rev, d4: !!S.last.d4 } : null,
      res: S.phase === 'end' ? (S.res === 'draw' ? 'draw' : S.res === i ? 'win' : 'lose') : null,
      early: S.phase === 'end' && S.early ? S.early : 0      
    };
  }

  
  function evFor(ev, i) {
    return ev.filter(x => !((x.e === 'ask5' || x.e === 'u5skip' || (x.e === 'gem' && !x.pub)) && x.who !== i)).map(x => {      
      const o = { e: x.e };
      if (x.who != null) o.me = x.who === i;
      if (x.e === 'x7') { o.n = x.n; if (x.who === i) o.drew = x.drew; if (x.tok) { o.tok = x.tok; o.drop = x.drop; } }      
      else if (x.e === 'gem') { o.g = x.g; o.c = x.c; }      
      else if (x.e === 'tokgone') { o.u = x.u; if (x.who === i || x.pub) o.k = x.k; }      
      else if (x.e === 'x7r') { o.show = x.show; o.drop = x.drop; }      
      else if (x.e === 'set' || x.e === 'swap') { if (x.who === i) { o.u = x.u; if (x.back != null) o.back = x.back; } }
      else if (x.e === 'efft') { o.mine = x.has[i]; if (x.has[i]) o.st = x.st; o.first = !!x.first; if (x.first) o.other = x.has[1 - i]; }      
      else if (x.e === 'sixt') { o.mine = x.has[i]; o.other = x.has[1 - i]; }      
      else if (x.e === 'p6') { o.six = x.six; o.pick = x.pick; if (x.who === i) o.k = x.k; }
      else if (x.e === 'u5') { o.five = x.five; o.drop = x.drop; }
      else if (x.e === 'x3') { o.three = x.three; o.give = x.give; o.take = x.take; }      
      else if (x.e === 'fizz') o.k = x.k;
      else if (x.e === 'open') { o.turn = x.turn; o.my = x.c[i]; o.op = x.c[1 - i]; o.res = x.res === 0 || x.res === 1 ? (x.res === i ? 'win' : 'lose') : x.res; o.wins = [x.wins[i], x.wins[1 - i]]; if (x.rev != null) o.rev = x.rev === i ? 'me' : 'op'; if (x.d4) o.d4 = true; }      
      else if (x.e === 'rev') { o.k = x.k; o.show = x.show; o.drop = x.drop; o.beat = x.beat; }      
      else if (x.e === 'fin') { o.turn = x.turn; o.res = x.res === i ? 'win' : 'lose'; o.wins = [x.wins[i], x.wins[1 - i]]; o.rev = !!x.rev; }
      else if (x.e === 'pre') { o.type = x.type; if (x.tok) o.tok = 1; }
      else if (x.e === 'k') { o.pick = x.pick; if (x.who === i) o.k = x.k; if (x.tok) o.tok = 1; }      
      else if (x.e === 'm') { o.drop = x.drop; o.n = x.drew.length; if (x.who === i) o.drew = x.drew; if (x.tok) o.tok = 1; }
      else if (x.e === 'turn') o.n = x.n;
      else if (x.e === 'end') { o.wins = [x.wins[i], x.wins[1 - i]]; o.res = x.res === 'draw' ? 'draw' : x.res === i ? 'win' : 'lose'; if (x.early) o.early = x.early; }      
      return o;
    });
  }

  
  function legal(S, i) {
    const v = view(S, i), out = [];
    if (v.can.set) out.push('set');
    if (v.can.x7r) out.push('x7r');                     
    if (v.can.x7) out.push('x7');                       
    if (v.can.x3) out.push('x3');
    if (v.can.gem && v.can.gem.length) out.push('gem');      
    if (v.can.eff) out.push('eff');
    if (v.can.six) out.push('p6');                      
    if (v.pend && v.pend.mine) out.push(v.pend.type);
    return out;
  }

  return { NUMS, KINDS, TURNS, HAND, COPIES, STEPS, GEMS, GEM_W, GEM_HAND, power, compare, shuffle, newGame, act, view, evFor, legal };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = CBRules;

;



























const CBCpu = (() => {
  'use strict';
  const power = (k, rv) => (k === 'k' || k === 'm' ? 0 : rv ? 8 - +k : +k);      
  const byStrong = (hand, rv) => hand.slice().sort((a, b) => power(a.k, rv) - power(b.k, rv) || a.u - b.u);      
  const pick = (a, rng) => a[Math.floor(rng() * a.length)];

  function decide(v, rng) {
    rng = rng || Math.random;
    if (!v || v.phase === 'end') return null;
    const hand = v.my.hand, opHand = v.op.hand, rv = !!v.rv, P = k => power(k, rv), byS = h => byStrong(h, rv);
    if (v.pend && v.pend.mine) {
      if (v.pend.type === 'swap') {
        const s = byS(hand), win = s.filter(c => P(c.k) < P('4'));
        if (win.length) return { t: 'swap', u: win[win.length - 1].u };
        const four = s.find(c => c.k === '4'); if (four) return { t: 'swap', u: four.u };
        const five = s.find(c => c.k === '5'); if (five && hand.length - 1 >= v.turns - v.turn && v.deckN >= 1) return { t: 'swap', u: five.u };      
        return { t: 'swap', u: s[s.length - 1].u };
      }
      if (v.pend.type === 'u5') { const s = byS(hand), tk = hand.find(c => c.tok); return { t: 'u5', drop: tk ? tk.u : s.length ? s[s.length - 1].u : null }; }      
      if (v.pend.type === 'k') {
        const un = opHand.filter(c => c.k == null);
        return { t: 'k', pick: un.length ? pick(un, rng).u : null };
      }
      if (v.pend.type === 'm') {
        const s = byS(hand);
        return { t: 'm', drop: [s[s.length - 1].u, s[s.length - 2].u] };
      }
      if (v.pend.type === 'rev') return { t: 'rev', use: true };      
      return null;
    }
    if (v.can.six) {                                     
      const un = opHand.filter(x => x.k == null);
      return { t: 'p6', pick: un.length ? pick(un, rng).u : null };
    }
    if (v.can.eff) {                                     
      const c = v.can.eff, s = byS(hand);
      if (c.e5) { const weak = hand.find(x => x.tok) || s[s.length - 1]; return { t: 'eff', use: weak ? { u5: weak.u } : {} }; }      
      if (c.e4) return { t: 'eff', use: (v.turn >= v.turns ? true : v.turn >= 2 ? rng() < 0.5 : false) ? { u4: true } : {} };
      return { t: 'eff', use: {} };
    }
    if (v.phase !== 'set' || !v.can.set) return null;
    if (v.can.x7r) return { t: 'x7r' };                 
    if (v.can.x7 && !rv) return { t: 'x7' };            
    if (v.can.x3 && v.can.x3p.length && rng() < (v.turn >= 2 ? 0.55 : 0.35)) return { t: 'x3', pick: pick(v.can.x3p, rng) };      
    const s = byS(hand), left = v.turns - v.turn + 1;          
    const top = s.slice(0, Math.min(left, s.length));
    if (hand.length - 2 >= v.turns - v.turn && hand.length - 1 >= 1 && v.deckN >= 1) {          
      const third = top[top.length - 1], five = s.find(x => x.k === '5');
      if (five && P(third.k) >= P('5')) return { t: 'set', u: five.u };
    }
    const knownOp = opHand.filter(x => x.k != null).map(x => x.k);
    let cand = top.filter(x => x.k === 'k' || x.k === 'm' || knownOp.indexOf(x.k) < 0);
    if (!cand.length) cand = top;
    return { t: 'set', u: pick(cand, rng).u };
  }
  return { decide };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = CBCpu;

;















































const CBNet = (() => {
  'use strict';
  const R = CBRules, PROTO = 14, MAXLEN = 20000;      
  
  const STAKE_MAX = 100;                               
  function stakeOf(k) {
    const e = Math.max(0, Math.min(STAKE_MAX, Math.floor(+(k && k.e) || 0)));
    const w = Math.max(e, Math.min(e * 2, Math.floor(+(k && k.w) || 0)));
    return { e: e, w: e > 0 ? w : 0 };
  }
  
  const gmOf = o => ({ on: !!o && o.on === true });
  const say = (m, k, v) => { try { if (typeof m[k] === 'function') m[k](v); } catch (e) {   } };
  
  const DZID = /^[a-z0-9]{1,12}$/;
  function dzOf(d) {
    const o = { b: '', f: {} };
    if (!d || typeof d !== 'object') return o;
    if (typeof d.b === 'string' && DZID.test(d.b)) o.b = d.b;
    const f = d.f && typeof d.f === 'object' ? d.f : {};
    R.KINDS.forEach(k => { if (Object.prototype.hasOwnProperty.call(f, k) && typeof f[k] === 'string' && DZID.test(f[k])) o.f[k] = f[k]; });
    return o;
  }

  
  
  const SAFE = /^[A-Za-z0-9_-]{0,24}$/, BAD = {}, MIN_SETS = 3;
  let minSets = MIN_SETS;                              
  function clean(v, d) {
    if (v === null || typeof v === 'boolean') return v;
    if (typeof v === 'number') return isFinite(v) && Math.abs(v) <= 1e6 ? v : BAD;
    if (typeof v === 'string') return SAFE.test(v) ? v : BAD;
    if (typeof v !== 'object' || d >= 8) return BAD;
    if (Array.isArray(v)) {
      if (v.length > 64) return BAD;
      const a = [];
      for (let i = 0; i < v.length; i++) { const x = clean(v[i], d + 1); if (x === BAD) return BAD; a.push(x); }
      return a;
    }
    const ks = Object.keys(v), o = {};
    if (ks.length > 48) return BAD;
    for (let i = 0; i < ks.length; i++) {
      const k = ks[i]; if (!SAFE.test(k) || k === '__proto__' || k === 'constructor' || k === 'prototype') return BAD;
      const x = clean(v[k], d + 1); if (x === BAD) return BAD;
      o[k] = x;
    }
    return o;
  }
  const isObj = x => !!x && typeof x === 'object' && !Array.isArray(x);
  
  const viewOk = v => isObj(v) && isObj(v.my) && isObj(v.op) && isObj(v.can) && Array.isArray(v.my.hand) && Array.isArray(v.op.hand) && Array.isArray(v.discard);
  const evOk = ev => Array.isArray(ev) && ev.every(x => isObj(x) && typeof x.e === 'string' && x.e.length > 0);

  
  
  function parent(kind, rng, mkSeat, opt) {
    let S = null, seat = null, n = 0, alive = true;
    const m = { kind: kind, me: 0, onUpdate: null, onState: null, wantAgain: [false, false] };
    function push(ev) {
      n += 1;
      say(m, 'onUpdate', { n: n, ev: R.evFor(ev, 0), view: R.view(S, 0) });
      if (seat) seat.up({ n: n, ev: R.evFor(ev, 1), view: R.view(S, 1) });
    }
    function apply(i, a) {
      if (!alive || !S) return { ok: false, why: 'off' };
      const r = R.act(S, i, a, rng);
      if (r.ok) push(r.ev);
      return { ok: r.ok, why: r.why };
    }
    m.start = () => {                                   
      if (!alive) return;
      S = R.newGame(rng, opt); m.wantAgain = [false, false]; n = 0;
      const ev0 = S.ev0 || []; delete S.ev0;            
      push([{ e: 'deal' }].concat(ev0));
    };
    m.act = a => Promise.resolve(apply(0, a));
    m.setOpt = o => { opt = o; };                     
    m.idle = () => { if (seat && seat.idle) seat.idle(); };
    m.again = () => {                                   
      if (!alive || !S || S.phase !== 'end') return;
      m.wantAgain[0] = true; if (seat && seat.again) seat.again();
      if (m.wantAgain[1]) m.start();
    };
    m.leave = () => { if (!alive) return; alive = false; if (seat) seat.stop(true); };
    m._ = { state: () => S, apply: apply, seatAgain: () => { m.wantAgain[1] = true; if (m.wantAgain[0]) m.start(); else say(m, 'onState', 'again'); }, end: why => { if (!alive) return; alive = false; if (seat) seat.stop(false); say(m, 'onState', why); } };
    seat = mkSeat(m);
    return m;
  }

  
  function cpu(rng, think, opt) {
    rng = rng || Math.random;
    return parent('cpu', rng, m => {
      let last = null, timer = 0, stopped = false;
      const go = () => {
        timer = 0; if (stopped || !last) return;
        const a = CBCpu.decide(last, rng); if (!a) return;
        m._.apply(1, a);
      };
      return {
        up: u => { last = u.view; },
        
        idle: () => { if (stopped || timer || !last || !CBCpu.decide(last, () => 0.5)) return; timer = setTimeout(go, think ? think(last) : 700 + Math.floor(rng() * 900)); },
        again: () => { m.wantAgain[1] = true; },
        stop: () => { stopped = true; clearTimeout(timer); }
      };
    }, opt);
  }

  
  
  function host(link, rng, opt, stake, dz, gm) {
    rng = rng || Math.random;
    const stk = stakeOf(stake), myDz = dzOf(dz), gmv = gmOf(gm);
    const mm = parent('host', rng, m => {
      let hello = false, joined = false, closed = false, want = false;
      const send = o => { if (!closed) link.send(JSON.stringify(o)); };
      
      const deal = m.start; m.start = () => { want = true; if (joined) deal(); };
      link.onText = txt => {
        if (closed || typeof txt !== 'string' || txt.length > MAXLEN) return;
        let o; try { o = JSON.parse(txt); } catch (e) { return; }
        if (!o || typeof o !== 'object') return;
        if (o.t === 'hello') { if (o.v !== PROTO) { send({ t: 'hello', v: PROTO }); m._.end('ver'); return; } if (!hello) { hello = true; m.opDz = dzOf(o.dz); send({ t: 'hello', v: PROTO, stake: stk, dz: myDz, gm: gmv }); say(m, 'onState', 'ready'); } return; }
        if (!hello) return;
        if (o.t === 'join') {                           
          const k = stakeOf(o.stake);
          if (!joined && k.e === stk.e && k.w === stk.w) {
            joined = true;
            if (gmv.on) m.setOpt(Object.assign({}, opt || {}, { gems: [R.GEMS.slice(), R.GEMS.slice()], gpub: true }));      
            say(m, 'onState', 'joined'); if (want) deal();
          }
          return;
        }
        if (o.t === 'bye') { m._.end('bye'); return; }
        if (!joined) return;
        if (o.t === 'act') {                            
          const a = clean(o.a, 0); let r;
          try { r = a === BAD || !isObj(a) ? { ok: false, why: 'arg' } : m._.apply(1, a); } catch (e) { r = { ok: false, why: 'err' }; }
          send({ t: 'ack', id: typeof o.id === 'number' && isFinite(o.id) ? o.id : 0, ok: r.ok, why: r.why });
        } else if (o.t === 'again') m._.seatAgain();
      };
      link.onLost = () => { if (!closed) m._.end('lost'); };
      return {
        up: u => send({ t: 'up', n: u.n, ev: u.ev, view: u.view }),
        again: () => send({ t: 'again' }),
        stop: mine => { if (closed) return; if (mine) send({ t: 'bye' }); closed = true; setTimeout(() => { try { link.close(); } catch (e) {   } }, mine ? 250 : 0); }
      };
    }, opt);
    mm.stake = stk; mm.opDz = null; mm.gm = gmv;
    return mm;
  }

  
  function guest(link, dz) {
    let alive = true, id = 0, hello = false, sets = 0;      
    let joined = false, over = false, again = false;      
    const wait = new Map(), myDz = dzOf(dz);
    const m = { kind: 'guest', me: 1, onUpdate: null, onState: null, stake: null, opDz: null, gm: null };      
    const send = o => { if (alive) link.send(JSON.stringify(o)); };
    const end = why => { if (!alive) return; alive = false; const fs = Array.from(wait.values()); wait.clear(); fs.forEach(f => f({ ok: false, why: 'off' })); try { link.close(); } catch (e) {   } say(m, 'onState', why); };
    link.onText = txt => {
      if (!alive || typeof txt !== 'string' || txt.length > MAXLEN) return;
      let o; try { o = JSON.parse(txt); } catch (e) { return; }
      if (!o || typeof o !== 'object') return;
      if (o.t === 'hello') { if (o.v !== PROTO) end('ver'); else if (!hello) { hello = true; m.stake = stakeOf(o.stake); m.opDz = dzOf(o.dz); m.gm = gmOf(o.gm); say(m, 'onState', 'ready'); say(m, 'onState', 'stake'); } }      
      else if (o.t === 'up') {
        
        const ev = clean(o.ev, 0), view = clean(o.view, 0);
        if (!hello || !joined || ev === BAD || view === BAD || !evOk(ev) || !viewOk(view)) return end('bad');      
        
        
        for (let i = 0; i < ev.length; i++) {
          if (ev[i].e === 'deal') { if (over && !again) return end('bad'); over = false; again = false; sets = 0; }
          else if (ev[i].e === 'end') { if (over || sets < minSets) return end('bad'); over = true; sets = 0; }
        }
        say(m, 'onUpdate', { n: typeof o.n === 'number' && isFinite(o.n) ? o.n : 0, ev: ev, view: view });
      } else if (o.t === 'ack') { const f = wait.get(o.id); if (f) { wait.delete(o.id); f({ ok: o.ok === true, why: typeof o.why === 'string' && SAFE.test(o.why) ? o.why : '' }); } }
      else if (o.t === 'again') say(m, 'onState', 'again');
      else if (o.t === 'bye') end('bye');
    };
    link.onLost = () => end('lost');
    m.start = () => send({ t: 'hello', v: PROTO, dz: myDz });
    m.join = () => { if (hello && m.stake) { joined = true; send({ t: 'join', stake: m.stake }); } };      
    m.act = a => new Promise(ok => {
      if (!alive) return ok({ ok: false, why: 'off' });
      id += 1; wait.set(id, ok);
      if (a && a.t === 'set') sets += 1;               
      send({ t: 'act', id: id, a: a });
    });
    m.idle = () => { };
    m.again = () => { if (over) again = true; send({ t: 'again' }); };
    m.leave = () => { if (!alive) return; send({ t: 'bye' }); alive = false; setTimeout(() => { try { link.close(); } catch (e) {   } }, 250); };
    return m;
  }

  
  
  
  function nativeRoom() {
    const N = window.TengelNative;
    let link = null, done = null, fail = null, onStep = null, live = false;
    function onNative(e) {
      const d = e.detail; if (!d || d.name !== 'room' || !live) return;
      const p = d.payload || {};
      if (p.ev === 'state') {
        if (p.state === 'connected' && done) {
          link = { send: txt => { N.call('room', { op: 'send', data: txt }).catch(() => { }); }, onText: null, onLost: null, close: () => { stop(); } };
          const ok = done; done = fail = null; ok(link);
        } else if (p.state === 'idle' && link) { const l = link; link = null; if (l.onLost) l.onLost(); }
        else if (onStep && (p.state === 'hosting' || p.state === 'searching')) onStep('wait');
        else if (onStep && p.state === 'connecting') onStep('found');
      } else if (p.ev === 'data' && link && link.onText) link.onText(String(p.data || ''));
      else if (p.ev === 'error' && fail) { const ng = fail; done = fail = null; stop(); ng(new Error(p.why || 'room')); }
    }
    function stop() { if (!live) return; live = false; document.removeEventListener('tengel:native', onNative); if (N) N.call('room', { op: 'stop' }).catch(() => { }); }
    return {
      open: (mode, room, step) => new Promise((ok, ng) => {
        if (!N || !window.__NATIVE) return ng(new Error('none'));
        onStep = step || null; done = ok; fail = ng; live = true;
        document.addEventListener('tengel:native', onNative);
        N.call('room', { op: mode === 'host' ? 'host' : 'join', room: String(room) }).then(r => { if (!r || !r.ok) { const f = fail; done = fail = null; stop(); if (f) f(new Error((r && r.why) || 'room')); } })
          .catch(e => { const f = fail; done = fail = null; stop(); if (f) f(e); });
      }),
      cancel: () => { const f = fail; done = fail = null; stop(); if (f) f(new Error('cancel')); }
    };
  }

  return { PROTO, STAKE_MAX, MIN_SETS, stakeOf, dzOf, gmOf, clean: v => { const x = clean(v, 0); return x === BAD ? undefined : x; }, cpu, host, guest, nativeRoom,
    _t: { get minSets() { return minSets; }, set minSets(n) { minSets = Math.max(0, Math.floor(+n || 0)); } } };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = CBNet;

;


















































































































































const CBApp = (() => {
  'use strict';
  const R = CBRules, SK = 'tengel.cb';
  
  
  
  
  
  const TK_BONUS = [[3, 1], [5, 2]];
  const tkBonus = streak => TK_BONUS.reduce((a, t) => a + (streak > 0 && streak % t[0] === 0 ? t[1] : 0), 0);
  
  const COIN = { win: 2, bonus: [[3, 6], [5, 10]], day: 2, day7: 10, max: 9999 };
  const coinBonus = streak => COIN.bonus.reduce((a, t) => a + (streak > 0 && streak % t[0] === 0 ? t[1] : 0), 0);      
  const coinFor = streak => COIN.win + coinBonus(streak);
  const coinHow = () => `コンピュータに 勝つと ${COIN.win}枚（${COIN.bonus.map(t => `${t[0]}連勝 ＋${t[1]}枚`).join('・')}）`;      
  const coinDay = () => `毎日の ログインボーナスで ${COIN.day}枚（7日目 ＋${COIN.day7}枚）`;
  const GK = 'tengel.cbgift';                         
  
  const MS = { cpu: [[3, 30], [5, 60], [6, 90], [7, 120], [8, 150], [9, 200], [10, 300]], fr: [[3, 20], [5, 40], [6, 60], [7, 80], [8, 100], [9, 120], [10, 140]] };
  
  const QMS = [[3, [[3, 30], [5, 60], [6, 90]]], [4, [[3, 50], [5, 100], [6, 150]]], [5, [[3, 90], [5, 180], [6, 270]]]];
  const QMS_K = QMS.reduce((a, t) => a.concat(t[1].map(w => `g${t[0]}w${w[0]}`)), []);
  const MS_WHO = { cpu: 'コンピュータ', fr: '友達バトル', q: '決戦調査' }, MS_ALL = MS.cpu.length + MS.fr.length + QMS_K.length;
  const nowD = () => (typeof CBApp._now === 'function' ? CBApp._now() : new Date(window.TengelClock ? window.TengelClock.now() : Date.now()));      
  const monthKey = d => { const x = d || nowD(); return x.getFullYear() + '-' + String(x.getMonth() + 1).padStart(2, '0'); };
  const COINI = '<img class="cbci" src="cb_coin.webp" alt="">';      
  const STAKE_CHIPS = [0, 1, 2, 3, 5, 10, 20, 30, 50, 100];      
  const NAMES = { k: '神様馬', m: '幻の馬' };
  
  
  const GEMS = { m: { n: '幻影のアメジスト', t: '幻の馬トークン' }, k: { n: '日輪の黄金石', t: '神様馬トークン' }, 1: { n: '双炎のルビー', t: '1トークン' }, 3: { n: '双葉のエメラルド', t: '3トークン' }, 7: { n: '三峰の翡翠', t: '7トークン' } };
  const GEM_SLOT = [[7.99, 11.24, 16.55, 69.38], [25.44, 11.24, 15.93, 69.38], [42.13, 11.24, 15.65, 69.38], [59.1, 11.24, 15.37, 69.38], [75.93, 11.24, 16.55, 69.38]];      
  const gemPic = g => `cb_gm_${g}.webp`;
  const nameOf = k => (typeof k === 'string' && k.length === 2 && k[0] === 't' && GEMS[k[1]] ? GEMS[k[1]].t : NAMES[k] || String(k));      
  const TOKP = { m: 'tm', k: 'tk', 1: 't1', 3: 't3', 7: 't7' }, tokP = k => TOKP[k] || 't' + k;      
  const kmN = (k, tok) => (k === 'k' ? '神様馬' : '幻の馬') + (tok ? 'トークン' : '');      
  const picK = c => (!c || c.k == null ? null : c.tok ? tokP(c.k) : c.k);      
  const headOf = w => (w > 1 ? `（1枚で ${w}頭分）` : '');
  
  
  const BACK_COST = 300;      
  const FACES = [['k', 'ka', '朱の鳥居'], ['k', 'kb', '天空の神殿'], ['m', 'ma', '三日月の幻'], ['m', 'mb', '紅い雷'], ['1', '1a', '炎の輪'], ['1', '1b', '赤銅の鎧'], ['2', '2a', '月夜の黒馬'], ['2', '2b', '銀の鎧'],
    ['3', '3a', '水晶の間'], ['3', '3b', '星の遺跡'], ['4', '4a', '雷の城'], ['4', '4b', '青の広間'], ['5', '5a', '炎の城'], ['5', '5b', '琥珀の洞窟'], ['6', '6a', '赤の書庫'], ['6', '6b', '紅玉の天文台'], ['7', '7a', '疾風の草原'], ['7', '7b', '翡翠の馬'],      
    
    ['k', 'kr', '聖光の神馬', 'r'], ['m', 'mr', '紫の水鏡', 'r'], ['1', '1r', '暁の凱旋門', 'r'], ['2', '2r', '黒き日食', 'r'], ['3', '3r', '碧水の森', 'r'], ['4', '4r', '蒼晶の跳躍', 'r'], ['5', '5r', '金色の大橋', 'r'], ['6', '6r', '紅き満月', 'r'], ['7', '7r', '翠玉の輝き', 'r'],
    ['k', 'ksr', '白金の聖殿', 'sr'], ['m', 'msr', '紫電の魔城', 'sr'], ['1', '1sr', '真紅の宮廷', 'sr'], ['2', '2sr', '黒曜の大階段', 'sr'], ['3', '3sr', '碧玉の温室', 'sr'], ['4', '4sr', '月光のテラス', 'sr'], ['5', '5sr', '黄金の宝殿', 'sr'], ['6', '6sr', '雲上の図書館', 'sr'], ['7', '7sr', '天空の楽園', 'sr']]
    .map(([k, id, name, r]) => ({ k: k, id: id, name: name, r: r || 'n', c: `cb_fc_${id}_c.webp`, s: `cb_fc_${id}_s.webp` }));
  
  
  
  
  const PACK = { cost: 112, size: 5, lot: 230, ranges: [['n', 0, 68], ['r', 69, 160], ['gr', 161, 183], ['sr', 184, 219], ['gsr', 220, 229]] };
  const GROUP = { n: 'ノーマル', r: 'レア（1〜7）', gr: '神様馬・幻の馬の レア', sr: '超レア（1〜7）', gsr: '神様馬・幻の馬の 超レア' };
  const RAR = { n: 'ノーマル', r: 'レア', sr: '超レア' }, RARS = { n: 'N', r: 'R', sr: 'SR' };
  const PKH_MAX = 100;      
  const BACKS = [['sky', '天馬の光'], ['star', '星座の馬'], ['ice', '氷の結晶'], ['wa', '和の墨絵'], ['ori', '折り紙の馬'], ['crown', '王冠の紋章'], ['heart', 'ハートの2頭']]
    .map(([id, name]) => ({ k: null, id: id, name: name, c: `cb_bk_${id}_c.webp`, s: `cb_bk_${id}_s.webp`, d: `cb_bk_${id}_d.webp`, cost: BACK_COST }));
  
  const BOARD_COST = 300;
  
  const BOARDS = [['marble', '白亜の宮殿', 1], ['frost', '蒼氷の宮', 1], ['sakura', '桜の舞踏会', 1], ['violet', '紫月の夜', 1], ['crimson', '紅蓮の闘技場', 1], ['starry', '黄金の星空', 1], ['steam', '歯車の工房', 1]]
    .map(([id, name, dl]) => ({ id: id, name: name, b: `cb_bd_${id}.webp`, s: `cb_bd_${id}_s.webp`, cost: BOARD_COST, dl: !!dl }));
  const boardNow = () => (st && st.board ? BOARDS.find(d => d.id === st.board) || null : null);      
  const DZ_KINDS = ['k', 'm', '1', '2', '3', '4', '5', '6', '7'];
  
  
  const selOf = side => { const o = side === 'op' && match && match.kind !== 'cpu' ? match.opDz || { b: '', f: {} } : null; return o ? { back: o.b || '', face: o.f || {} } : { back: st ? st.back : '', face: st ? st.face : {} }; };
  const backNow = side => { const id = selOf(side).back; return id ? BACKS.find(b => b.id === id) || null : null; };
  const faceNow = (k, side) => { const id = selOf(side).face[k]; return id ? FACES.find(f => f.id === id && f.k === k) || null : null; };
  
  const pic = (k, big, side) => { const d = k == null ? backNow(side) : faceNow(k, side); return d ? d[big ? 'c' : 's'] : 'cb_' + (big ? 'c' : 's') + (k == null ? 'b' : k) + '.webp'; };
  const deckPic = () => { const b = backNow(); return b ? b.d : 'cb_deck.webp'; };      
  const power = R.power;
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  let SPEED = 1, GEN = 0;                              
  
  const clk = { manual: false, now: 0, q: [] };
  function later(fn, ms) { if (!clk.manual) return setTimeout(fn, ms); const o = { at: clk.now + Math.max(0, ms), fn: fn }; clk.q.push(o); return o; }
  function unlater(h) { if (h && typeof h === 'object') { const i = clk.q.indexOf(h); if (i >= 0) clk.q.splice(i, 1); } else clearTimeout(h); }
  function tick(ms) {
    clk.now += ms; let n = 0;
    for (;;) { const due = clk.q.filter(o => o.at <= clk.now).sort((a, b) => a.at - b.at)[0]; if (!due) break; clk.q.splice(clk.q.indexOf(due), 1); due.fn(); n++; }
    return n;
  }
  
  
  const T = ms => { const g = GEN; return new Promise(ok => later(() => { if (g === GEN) ok(); }, Math.max(0, ms * SPEED))); };
  const reduce = () => !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);      

  
  let st = null;
  const DEF = () => ({ v: 1, streak: 0, win: 0, lose: 0, draw: 0, bgm: null, se: null, coin: 0, stake: null, backs: [], faces: [], back: '', face: {}, boards: [], board: '', ms: null, gifts: [], pkh: [], packs: 0, q: null, rg: null });      
  let lostStake = 0;                                   
  let lostMs = '';                                     
  let lostLive = -1;                                   
  let giftGot = 0, giftFull = false;                   
  function load() {
    try { const s = JSON.parse(localStorage.getItem(SK) || 'null'); st = Object.assign(DEF(), s && s.v === 1 ? s : {}); } catch (e) { st = DEF(); }
    ['streak', 'win', 'lose', 'draw'].forEach(k => { st[k] = Math.max(0, Math.floor(+st[k] || 0)); });
    delete st.owe;      
    ['bgm', 'se'].forEach(k => { st[k] = st[k] === true || st[k] === false ? st[k] : null; });      
    delete st.fx;                                      
    st.coin = Math.max(0, Math.min(COIN.max, Math.floor(+st.coin || 0)));      
    
    const m0 = st.ms && typeof st.ms === 'object' ? st.ms : {}, g0 = m0.got && typeof m0.got === 'object' ? m0.got : {};
    const gotOf = kd => (Array.isArray(g0[kd]) ? g0[kd] : []).map(x => Math.floor(+x)).filter((x, i, a) => MS[kd].some(t => t[0] === x) && a.indexOf(x) === i).sort((a, b) => a - b);
    const cnt = x => Math.max(0, Math.min(9999, Math.floor(+x || 0)));
    st.ms = { m: typeof m0.m === 'string' && /^\d{4}-\d{2}$/.test(m0.m) ? m0.m : monthKey(), cpu: cnt(m0.cpu), fr: cnt(m0.fr), got: { cpu: gotOf('cpu'), fr: gotOf('fr'), q: (Array.isArray(g0.q) ? g0.q : []).filter((x, i, a) => QMS_K.indexOf(x) >= 0 && a.indexOf(x) === i) }, live: m0.live === 'cpu' || m0.live === 'fr' || m0.live === 'qc' ? m0.live : '' };
    
    const q0 = st.q && typeof st.q === 'object' ? st.q : {};
    st.q = { m: typeof q0.m === 'string' && /^\d{4}-\d{2}$/.test(q0.m) ? q0.m : monthKey(), clr: Math.max(0, Math.min(QN, Math.floor(+q0.clr || 0))) };
    { const t0 = st.qt && typeof st.qt === 'object' ? st.qt : null; st.qt = t0 && isFinite(+t0.n) && isFinite(+t0.at) ? { n: Math.max(0, Math.min(QT.max, Math.floor(+t0.n))), at: +t0.at } : null; }      
    if (st.ms.live === 'qc') { st.ms.live = ''; lostQ = true; save(); }      
    
    delete st.gq;
    { const r0 = st.rg && typeof st.rg === 'object' ? st.rg : {}; st.rg = { on: r0.on === true }; }      
    
    if (st.ms.live) { if (st.ms[st.ms.live] > 0) lostMs = st.ms.live; st.ms[st.ms.live] = 0; st.ms.live = ''; lostLive = st.streak; st.lose += 1; st.streak = 0; save(); }
    msRoll();
    
    const bids = BACKS.map(b => b.id), fids = FACES.map(f => f.id);
    st.backs = Array.isArray(st.backs) ? st.backs.filter((x, i, a) => bids.indexOf(x) >= 0 && a.indexOf(x) === i) : [];
    st.faces = Array.isArray(st.faces) ? st.faces.filter((x, i, a) => fids.indexOf(x) >= 0 && a.indexOf(x) === i) : [];
    st.back = st.backs.indexOf(st.back) >= 0 ? st.back : '';
    const fc = {}, f0 = st.face && typeof st.face === 'object' ? st.face : {};
    DZ_KINDS.forEach(k => { const id = f0[k]; if (st.faces.indexOf(id) >= 0 && FACES.some(f => f.id === id && f.k === k)) fc[k] = id; });
    st.face = fc;
    
    st.pkh = Array.isArray(st.pkh) ? st.pkh.filter(h => h && typeof h.id === 'string' && Array.isArray(h.cards) && h.cards.length === PACK.size && h.cards.every(id => fids.indexOf(id) >= 0) && PACK.ranges.some(t => t[0] === h.g))
      .map(h => ({ id: h.id, t: Math.floor(+h.t || 0), g: h.g, k: Math.floor(+h.k || 0), cards: h.cards.slice(), nw: Array.isArray(h.nw) ? h.cards.map((x, i) => !!h.nw[i]) : h.cards.map(() => false), v: !!h.v })).slice(-PKH_MAX) : [];
    st.packs = Math.max(st.pkh.length, Math.min(1e9, Math.floor(+st.packs || 0)));
    const dids = BOARDS.map(d => d.id);                
    st.boards = Array.isArray(st.boards) ? st.boards.filter((x, i, a) => dids.indexOf(x) >= 0 && a.indexOf(x) === i) : [];
    st.board = st.boards.indexOf(st.board) >= 0 ? st.board : '';
    
    const k = st.stake; st.stake = null;
    if (k && typeof k === 'object' && Math.floor(+k.e) > 0) { lostStake = Math.floor(+k.e); save(); }
    st.gifts = Array.isArray(st.gifts) ? st.gifts.filter((x, i, a) => typeof x === 'string' && a.indexOf(x) === i).slice(-60) : [];      
    takeGift();
  }
  
  
  function takeGift() {
    if (!st) return 0;
    let g = null; try { g = JSON.parse(localStorage.getItem(GK) || 'null'); } catch (e) { g = null; }
    const list = g && typeof g === 'object' && Array.isArray(g.list) ? g.list : [];
    let want = 0;
    list.forEach(x => {
      const id = x && typeof x.id === 'string' ? x.id : '', c = Math.max(0, Math.min(COIN.max, Math.floor(+(x && x.c) || 0)));
      if (!id || !(c > 0) || st.gifts.indexOf(id) >= 0) return;
      st.gifts.push(id); want += c;
    });
    if (!want) return 0;
    st.gifts = st.gifts.slice(-60);
    const c0 = st.coin; addCoin(want); save();
    giftGot += st.coin - c0; if (st.coin - c0 < want) giftFull = true;
    return st.coin - c0;
  }
  const addCoin = n => { st.coin = Math.max(0, Math.min(COIN.max, st.coin + Math.floor(+n || 0))); };
  function save() { try { localStorage.setItem(SK, JSON.stringify(st)); } catch (e) {   } }
  
  function saveOk() { try { const s = JSON.stringify(st); localStorage.setItem(SK, s); return localStorage.getItem(SK) === s; } catch (e) { return false; } }      
  
  
  function msRoll() {
    const k = monthKey(); if (k <= st.ms.m) return false;
    st.ms = { m: k, cpu: 0, fr: 0, got: { cpu: [], fr: [], q: [] }, live: st.ms.live }; save(); return true;
  }
  
  function msWin(kind) {
    msRoll(); const s = st.ms, out = []; s[kind] = Math.min(9999, s[kind] + 1);
    MS[kind].forEach(t => { if (s[kind] >= t[0] && s.got[kind].indexOf(t[0]) < 0) { s.got[kind].push(t[0]); out.push({ k: kind, n: t[0], c: t[1] }); } });
    return out;
  }
  const msKind = m => (m && m.kind === 'cpu' ? 'cpu' : 'fr');      
  const msQ = () => (Array.isArray(st.ms.got.q) ? st.ms.got.q : (st.ms.got.q = []));      
  const msDone = () => st.ms.got.cpu.length + st.ms.got.fr.length + msQ().length;
  
  function qmsWin(r) {
    const left = R.GEMS.length - (r.gu ? r.gu.length : 0), got = msQ(), out = [];
    QMS.forEach(t => t[1].forEach(w => { const k = `g${t[0]}w${w[0]}`; if (r.won >= w[0] && left >= t[0] && got.indexOf(k) < 0) { got.push(k); out.push({ k: 'q', g: t[0], n: w[0], c: w[1] }); } }));
    return out;
  }
  
  
  
  
  async function settle(res) {
    if (qRun) return qSettle(res);                     
    let coin = 0, cb = 0, tk = 0, pot = null, ms = []; const cpu = !!match && match.kind === 'cpu', k = st.stake, mk = msKind(match);
    st.ms.live = '';
    if (res === 'win') { st.win += 1; st.streak += 1; if (cpu) { coin = COIN.win; cb = coinBonus(st.streak); tk = tkBonus(st.streak); } ms = msWin(mk); }
    else if (res === 'lose') { st.lose += 1; st.streak = 0; msRoll(); st.ms[mk] = 0; }
    else { st.draw += 1; msRoll(); }
    if (k) { pot = { e: k.e, w: k.w, add: res === 'win' ? k.w : res === 'draw' ? k.e : 0 }; st.stake = null; }
    const msc = ms.reduce((a, x) => a + x.c, 0), want = coin + cb + (pot ? pot.add : 0) + msc, c0 = st.coin; addCoin(want);
    save();
    const tkGot = tk ? qtAdd(tk) : 0;      
    return { res: res, cpu: cpu, streak: st.streak, coin: coin, cb: cb, tk: tk, tkGot: tkGot, tks: tk ? qtNow().n : 0, pot: pot, coins: st.coin, full: st.coin - c0 < want, ms: ms, msc: msc, mk: mk, mst: st.ms[mk] };
  }
  
  function msLive() { if (!match) return; msRoll(); st.ms.live = qRun ? 'qc' : msKind(match); save(); }      
  
  
  
  function payStake() {
    const k = match && match.stake; st.stake = null;
    if (k && k.e > 0 && st.coin >= k.e) { st.coin -= k.e; st.stake = { e: k.e, w: k.w }; }
    save();
  }

  
  
  
  
  
  
  const SE = ['deal', 'set', 'flip', 'win', 'lose', 'even', 'magic', 'tap', 'fanfare', 'over', 'join', 'appear', 'hit', 'qwin1', 'qwin2', 'qwin3', 'coin', 'unlock'];      
  const snd = { ac: null, buf: {} };
  const AS = (() => { try { return !!(navigator.audioSession && 'type' in navigator.audioSession); } catch (e) { return false; } })();
  const appSound = () => { try { const g = window.TengelFx && window.TengelFx.get ? window.TengelFx.get() : null; return g ? g.sound !== false : true; } catch (e) { return true; } };
  const seOn = () => (st && st.se != null ? st.se : appSound());
  const bgmOn = () => (st && st.bgm != null ? st.bgm : appSound() && (AS || !!CBApp._as));
  function actx() {
    if (!snd.ac) { const C = window.AudioContext || window.webkitAudioContext; if (C) { try { snd.ac = new C(); } catch (e) { snd.ac = null; } } }
    const c = snd.ac;
    if (c && c.state !== 'running' && c.resume) { try { const q = c.resume(); if (q && q.catch) q.catch(() => { }); } catch (e) {   } }
    return c;
  }
  function se(name, gain) {
    if (!seOn()) return;
    const c = actx(); if (!c || SE.indexOf(name) < 0) return;
    const f = 'cb_se_' + name + '.m4a';
    if (!snd.buf[name]) snd.buf[name] = fetch(f).then(r => (r.ok ? r.arrayBuffer() : null)).then(b => (b ? new Promise(ok => { try { const q = c.decodeAudioData(b, ok, () => ok(null)); if (q && q.catch) q.catch(() => ok(null)); } catch (e) { ok(null); } }) : null)).catch(() => null);
    snd.buf[name].then(b => { if (!b || !seOn()) return; try { const s = c.createBufferSource(), g = c.createGain(); s.buffer = b; g.gain.value = gain == null ? 1 : gain; s.connect(g); g.connect(c.destination); s.start(0); } catch (e) {   } });
  }
  
  
  
  
  
  
  
  const BGMS = { main: { file: 'cb_bgm.m4a', pre: 0.5, len: 34 * 3 * 60 / 76, vol: 0.42, fin: 1.4, fout: 0.45 },      
    quest: { file: 'cb_qbgm.m4a', pre: 0.5, len: 16 * 4 * 60 / 132, vol: 0.40, fin: 0.9, fout: 0.6 } };      
  
  
  
  let BGM = BGMS.main;
  const bg = { raw: null, buf: null, dec: null, cur: null, tau: 0, gone: false, want: false, trk: 'main', taus: {} };      
  
  const bgLp = (B, dur) => (B.ls == null ? { ls: B.pre / 2, le: B.pre / 2 + B.len, at: B.pre } : { ls: B.ls, le: Math.min(B.le, dur || Infinity), at: B.at || 0 });
  
  const bgOk = (B, b) => (B.ls == null ? b.duration > B.len + B.pre : b.duration > B.ls + 0.5 && (B.le === Infinity || b.duration >= B.le - 0.02));
  function bgmLoad() {
    if (bg.buf || bg.gone) return Promise.resolve(bg.buf);
    if (bg.dec) return bg.dec;
    const c = actx(); if (!c || typeof fetch !== 'function') return Promise.resolve(null);
    const B = BGM;                                     
    if (!bg.raw) bg.raw = fetch(B.file).then(r => (r.ok ? r.arrayBuffer() : null)).catch(() => null);
    const dec = bg.raw.then(b => (b ? new Promise(ok => { try { const q = c.decodeAudioData(b.slice(0), ok, () => ok(null)); if (q && q.catch) q.catch(() => ok(null)); } catch (e) { ok(null); } }) : null)).then(b => {
      if (BGM !== B) return null;
      bg.dec = null;
      if (b && bgOk(B, b)) bg.buf = b; else if (!b) { bg.gone = true; bg.raw = null; } else bg.gone = true;
      return bg.buf;
    });
    bg.dec = dec;
    return dec;
  }
  
  const bgmPos = () => bgWrap(bg.cur && snd.ac ? bg.tau + Math.max(0, snd.ac.currentTime - bg.cur.t0) : bg.tau);
  function bgWrap(t) {
    if (BGM.ls == null) return t % BGM.len;
    const L = bgLp(BGM, bg.buf ? bg.buf.duration : 0), x = L.at + t;
    return (x < L.le || L.le === Infinity ? x : L.ls + (x - L.ls) % (L.le - L.ls)) - L.at;
  }
  function bgmStart() {
    const c = snd.ac; if (!c || bg.cur || !bg.buf) return;
    try {
      const s = c.createBufferSource(), g = c.createGain(), n = c.currentTime, L = bgLp(BGM, bg.buf.duration);
      s.buffer = bg.buf; s.loop = true; s.loopStart = L.ls; s.loopEnd = L.le;
      let off = L.at + bg.tau; if (off >= L.le) off = L.ls + (off - L.ls) % (L.le - L.ls);
      g.gain.setValueAtTime(0, n); g.gain.linearRampToValueAtTime(BGM.vol, n + BGM.fin);
      s.connect(g); g.connect(c.destination); s.start(0, off); bg.cur = { s: s, g: g, t0: n, off: off };
    } catch (e) { bg.cur = null; }
  }
  function bgmStop(fade) {
    if (!bg.cur || !snd.ac) return;
    const o = bg.cur, n = snd.ac.currentTime; bg.tau = bgmPos(); bg.cur = null;
    try { o.g.gain.cancelScheduledValues(n); o.g.gain.setValueAtTime(o.g.gain.value, n); o.g.gain.linearRampToValueAtTime(0, n + fade); o.s.stop(n + fade + 0.05); }
    catch (e) { try { o.s.stop(); } catch (e2) {   } }
    setTimeout(() => { try { o.s.disconnect(); o.g.disconnect(); } catch (e) {   } }, (fade + 0.3) * 1000);
  }
  
  function bgmSync() {
    const want = !!ov && ov.classList.contains('on') && !document.hidden && bgmOn() && !!bg.trk;
    bg.want = want;
    if (!want) { bgmStop(BGM.fout); return; }
    if (bg.cur) return;
    if (!actx()) return;
    bgmLoad().then(b => { if (b && bg.want && !bg.cur) bgmStart(); });
  }
  
  
  function bgmTrack(t, lv) {
    const B = t === 'field' ? QBG[lv - 1] || null : t === 'quest' || t === 'main' ? BGMS[t] : null;
    t = B ? t : '';
    if (t === bg.trk && t !== 'field') return bgmSync();
    if (bg.cur) bgmStop(BGM.fout);
    if (bg.trk && bg.trk !== 'field') bg.taus[bg.trk] = bg.tau;
    bg.trk = t;
    if (B && B !== BGM) { BGM = B; bg.buf = null; bg.raw = null; bg.dec = null; bg.gone = false; }
    bg.tau = t === 'field' ? 0 : t ? bg.taus[t] || 0 : bg.tau;
    bgmSync();
  }
  
  function soundRest() {
    bgmSync();
    setTimeout(() => {
      if (ov && ov.classList.contains('on')) return;
      bg.buf = null; bg.gone = false;
      try { if (snd.ac && snd.ac.state === 'running') { const q = snd.ac.suspend(); if (q && q.catch) q.catch(() => { }); } } catch (e) {   }
    }, (BGM.fout + 0.4) * 1000);
  }

  
  const css = `
#cbOv{position:fixed;inset:0;z-index:90;display:none;color:#f6ead2;font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;-webkit-tap-highlight-color:transparent;overflow:hidden;touch-action:manipulation}
#cbOv.on{display:block}
#cbOv button{font-family:inherit;-webkit-tap-highlight-color:transparent;color:inherit}
#cbOv img{-webkit-user-drag:none;user-select:none;pointer-events:none}
#cbOv .cbbg{position:absolute;inset:0;overflow:hidden;background:radial-gradient(95% 52% at 4% 4%,rgba(96,128,196,.30) 0%,rgba(52,74,132,.13) 42%,rgba(20,28,56,0) 72%),radial-gradient(120% 62% at 50% 40%,#1c1a22 0%,#100f17 52%,#06060b 100%)}
#cbOv .cbbg::after{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,rgba(0,0,0,0) 0 46px,rgba(0,0,0,.18) 46px 47px,rgba(190,210,255,.025) 47px 48px);opacity:.9}
#cbOv .cbfire{position:absolute;inset:0;pointer-events:none;background:radial-gradient(88% 46% at 100% 76%,rgba(255,138,44,.34) 0%,rgba(214,84,18,.15) 40%,rgba(120,40,8,0) 72%);will-change:opacity;animation:cbfire 5.6s ease-in-out infinite}
#cbOv .cbboard .cbfire{background:radial-gradient(62% 88% at 100% 82%,rgba(255,150,56,.26) 0%,rgba(226,96,24,.10) 45%,rgba(140,50,10,0) 74%);animation-duration:4.3s;animation-delay:-1.7s}
@keyframes cbfire{0%{opacity:.78}17%{opacity:.92}29%{opacity:.82}46%{opacity:1}61%{opacity:.84}78%{opacity:.95}100%{opacity:.78}}
#cbOv .cbboard.cust .cbfire{display:none}
#cbOv .cbboard.dl .cbdeck{left:61.34%}
#cbOv .cbs{position:absolute;inset:0;display:none;flex-direction:column;box-sizing:border-box;padding:var(--sat,env(safe-area-inset-top)) 0 var(--sab,env(safe-area-inset-bottom));max-width:480px;margin:0 auto}
#cbOv .cbs.on{display:flex}
#cbOv .gold{font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-weight:400;background:linear-gradient(180deg,#fff3c4 0%,#ffd76a 38%,#e2a83e 62%,#9c6410 100%);-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent;filter:drop-shadow(0 2px 2px rgba(0,0,0,.6))}
#cbOv .cbb{display:block;box-sizing:border-box;min-height:48px;border-radius:24px;border:1.5px solid #f7d27c;background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206;font-weight:700;font-size:16px;line-height:1.25;padding:8px 18px;box-shadow:0 3px 0 #7a4c0c,0 6px 12px rgba(0,0,0,.4)}
#cbOv .cbb:active{transform:translateY(2px);box-shadow:0 1px 0 #7a4c0c,0 3px 6px rgba(0,0,0,.4)}
#cbOv .cbb.dk{background:linear-gradient(180deg,#3a2616,#22150b);color:#ffe7b0;border-color:#c9a35a;box-shadow:0 3px 0 #0d0703,0 6px 12px rgba(0,0,0,.4)}
#cbOv .cbb.sm{min-height:38px;border-radius:19px;font-size:13.5px;padding:5px 14px;box-shadow:0 2px 0 #7a4c0c,0 4px 8px rgba(0,0,0,.35)}
#cbOv .cbb.dk.sm{box-shadow:0 2px 0 #0d0703,0 4px 8px rgba(0,0,0,.35)}
#cbOv .cbb:disabled{opacity:.45}
#cbOv .cbb small{display:block;font-weight:400;font-size:11.5px;opacity:.85}

#cbOv .cbmenu{align-items:center;justify-content:center;gap:10px;padding-left:22px;padding-right:22px;text-align:center}
#cbOv .cbmenu .lg{width:min(58vw,230px);height:auto;aspect-ratio:1;filter:drop-shadow(0 8px 14px rgba(0,0,0,.55))}
#cbOv .cbmenu h1{margin:0;font-size:30px;line-height:1.15;letter-spacing:.04em}
#cbOv .cbmenu h1 small{display:block;font-size:13px;letter-spacing:.3em;margin-bottom:2px}
#cbOv .cbmenu .rec{font-size:12.5px;color:#d9c08c;line-height:1.6;margin:0 0 4px}
#cbOv .cbmenu .rec b{color:#ffe2a0}
#cbOv .cbmenu .btns{display:flex;flex-direction:column;gap:10px;width:100%;max-width:300px}
#cbOv .cbmenu .row{display:flex;gap:10px}#cbOv .cbmenu .row .cbb{flex:1 1 0;padding-left:6px;padding-right:6px}
#cbOv .cbx{position:absolute;left:12px;top:calc(var(--sat,env(safe-area-inset-top)) + 8px);z-index:2}

#cbOv .cbroom{align-items:center;justify-content:flex-start;gap:12px;padding-left:22px;padding-right:22px;text-align:center;overflow-y:auto}#cbOv .cbroom>h2{margin-top:auto}#cbOv .cbroom>:last-child{margin-bottom:auto}      /* 第4.197版：決戦宝石の ぶん 長い ときは スクロール（短い ときは まん中） */
#cbOv .cbroom h2{margin:0;font-size:22px}
#cbOv .cbroom p{margin:0;font-size:13.5px;line-height:1.7;color:#e6d3a6}
#cbOv .cbroom .num{font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-size:56px;letter-spacing:.14em;line-height:1.1;color:#ffe9a8;text-shadow:0 3px 0 #7a4c0c,0 6px 14px rgba(0,0,0,.6);padding-left:.14em}
#cbOv .cbroom .num.in{display:flex;justify-content:center;gap:10px;letter-spacing:0;padding-left:0}
#cbOv .cbroom .num.in span{display:block;width:52px;height:68px;line-height:68px;border-radius:12px;background:rgba(0,0,0,.35);border:1.5px solid rgba(255,226,160,.4);box-sizing:border-box}
#cbOv .cbroom .num.in span.cur{border-color:#ffd27a;box-shadow:0 0 10px rgba(255,210,90,.5)}
#cbOv .cbroom .stt{min-height:24px;font-weight:700;color:#ffe2a0;font-size:14.5px}
#cbOv .cbroom .hint{font-size:12px;color:#bfa873;line-height:1.65;max-width:320px}
#cbOv .cbkeys{display:grid;grid-template-columns:repeat(3,64px);gap:8px;justify-content:center}
#cbOv .cbkeys button{height:50px;border-radius:14px;border:1.5px solid #c9a35a;background:linear-gradient(180deg,#3a2616,#22150b);color:#ffe9a8;font-size:22px;font-weight:700}
#cbOv .cbkeys button:active{background:#5a3b1c}
#cbOv .cbkeys button[data-key=go]{font-size:17px}
#cbOv .cbkeys button[data-key=go]:not(:disabled){background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206;border-color:#f7d27c}
#cbOv .cbkeys button:disabled{opacity:.4}
#cbOv .cbspin{display:inline-block;width:18px;height:18px;border-radius:50%;border:3px solid rgba(255,226,160,.25);border-top-color:#ffd27a;animation:cbsp .9s linear infinite;vertical-align:-3px;margin-right:6px}
@keyframes cbsp{to{transform:rotate(360deg)}}

#cbOv .cbmidw{flex:1 1 auto;min-height:0;display:flex;flex-direction:column}
#cbOv .cbtop{flex:none;height:44px;display:flex;align-items:center;gap:8px;padding:0 10px}
#cbOv .cbtop .cbturn{flex:1 1 auto;text-align:center;font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-size:17px;letter-spacing:.08em;color:#ffe9a8;text-shadow:0 2px 0 rgba(0,0,0,.6)}
#cbOv .cbtop .cbturn small{font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif;font-size:11px;letter-spacing:0;color:#d9c08c;margin-left:6px}
#cbOv .cbwho{display:flex;align-items:center;justify-content:center;gap:8px;height:22px;font-size:12.5px;color:#e6d3a6}
#cbOv .cbwho b{color:#ffe9a8;font-size:13px}
#cbOv .cbpips{display:inline-flex;gap:4px}
#cbOv .cbpips i{width:13px;height:13px;border-radius:50%;box-sizing:border-box;border:1.5px solid #c9a35a;background:rgba(0,0,0,.35)}
#cbOv .cbpips i.on{background:radial-gradient(circle at 35% 30%,#fff6cf,#ffd24d 45%,#b97a10);border-color:#ffe9a8;box-shadow:0 0 6px rgba(255,210,90,.75)}
#cbOv .cbopp{flex:0 1 118px;min-height:62px;display:flex;flex-direction:column;justify-content:flex-end;padding-bottom:2px}
#cbOv .cbohand{flex:1 1 auto;min-height:0;display:flex;align-items:flex-end;justify-content:center;padding:0 8px}
#cbOv .cbohand .cbc{width:var(--ow,40px);margin-left:calc(var(--ow,40px) * -.28)}
#cbOv .cbohand .cbc:first-child{margin-left:0}
#cbOv .cbc{position:relative;flex:none;display:block;aspect-ratio:2/3;border:0;padding:0;margin:0;background:none;border-radius:6.5% / 4.3%;filter:drop-shadow(0 2px 3px rgba(0,0,0,.5))}
#cbOv .cbc img{display:block;width:100%;height:100%}
#cbOv .cbc .eye{position:absolute;right:-3px;top:-5px;width:20px;height:20px;border-radius:50%;background:#1b1209;border:1.5px solid #ffd27a;box-shadow:0 1px 3px rgba(0,0,0,.6)}
#cbOv .cbc .eye::before{content:"";position:absolute;left:3px;right:3px;top:6px;height:5px;border-radius:50%;border:1.5px solid #ffd27a}
#cbOv .cbc .eye::after{content:"";position:absolute;left:7px;top:7.5px;width:3px;height:3px;border-radius:50%;background:#ffd27a}
#cbOv .cbhand .cbc .eye{right:auto;left:calc(60% - 23px)}
#cbOv .cbboard{position:relative;flex:none;width:100%;margin-top:auto;aspect-ratio:1672/941;-webkit-mask-image:linear-gradient(180deg,transparent 0,#000 7%,#000 93%,transparent 100%);mask-image:linear-gradient(180deg,transparent 0,#000 7%,#000 93%,transparent 100%)}
#cbOv .cbboard>img{position:absolute;inset:0;width:100%;height:100%;display:block}
#cbOv .cbdeck{position:absolute;left:67.2%;top:25.5%;width:9.8%;aspect-ratio:360/426}
#cbOv .cbdeck img{width:100%;height:100%;display:block;filter:drop-shadow(0 3px 4px rgba(0,0,0,.5))}
#cbOv .cbn{position:absolute;min-width:18px;height:18px;box-sizing:border-box;padding:0 4px;border-radius:9px;background:#1b1209;border:1.5px solid #ffd27a;color:#ffe9a8;font-size:10.5px;font-weight:700;line-height:15px;text-align:center}
#cbOv .cbdeck .cbn{right:-7px;top:-6px}
#cbOv .cbdis{position:absolute;left:23.5%;top:29.5%;width:15.5%;height:43%;border:0;padding:0;background:none}
#cbOv .cbdis .pl{position:absolute;left:19%;top:27%;width:62%;aspect-ratio:2/3;transform:rotate(-7deg);border-radius:6.5% / 4.3%;filter:drop-shadow(0 2px 3px rgba(0,0,0,.55))}
#cbOv .cbdis .pl img{display:block;width:100%;height:100%;border-radius:inherit}
#cbOv .cbdis .cbn{right:0;top:21%}
#cbOv .cbgear{position:absolute;left:80.6%;top:60.2%;width:13.4%;height:19.5%;border:0;padding:0;background:none;border-radius:50%}
#cbOv .cbslot{position:absolute;left:43.5%;width:12.8%;aspect-ratio:2/3}
#cbOv .cbslot.op{top:1.6%}
#cbOv .cbslot.my{top:41.4%}
#cbOv .cbslot .cbc{width:100%}
#cbOv .cbslot .tag{position:absolute;left:50%;bottom:-7px;transform:translateX(-50%);white-space:nowrap;font-size:9px;font-weight:700;line-height:13px;padding:0 5px;border-radius:7px;background:#1b1209;border:1px solid #c9a35a;color:#ffe2a0}
#cbOv .cbslot .mk{position:absolute;left:-6px;top:-7px;min-width:19px;height:19px;padding:0 3px;box-sizing:border-box;border-radius:10px;background:#1b1209;border:1.5px solid #ffd27a;color:#ffe2a0;font-style:normal;font-size:11px;font-weight:800;line-height:16px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.6)}
#cbOv .cbglow{position:absolute;left:39.6%;top:41.4%;width:20.8%;height:23%;border-radius:12% / 18%;pointer-events:none;box-shadow:0 0 0 2px rgba(255,226,130,.85),0 0 16px 4px rgba(255,210,90,.55);opacity:0;transition:opacity .3s}
#cbOv .cbglow.on{opacity:1;animation:cbgl 1.8s ease-in-out infinite alternate}
@keyframes cbgl{from{box-shadow:0 0 0 2px rgba(255,226,130,.7),0 0 10px 2px rgba(255,210,90,.35)}to{box-shadow:0 0 0 2px rgba(255,240,180,.95),0 0 18px 5px rgba(255,210,90,.6)}}
#cbOv .cbmsg{flex:none;height:44px;box-sizing:border-box;overflow:hidden;display:flex;align-items:center;justify-content:center;text-align:center;white-space:pre-line;font-size:13.5px;font-weight:700;line-height:1.35;color:#fff1cf;padding:2px 12px;text-shadow:0 1px 2px rgba(0,0,0,.7)}
#cbOv .cbme{flex:none;margin-top:auto}
#cbOv .cbhand{flex:0 1 190px;min-height:104px;display:flex;align-items:center;justify-content:center;padding:14px 6px 4px;box-sizing:border-box}
#cbOv .cbhand .cbc{width:var(--cw,70px);margin-left:var(--ov,4px);transition:transform .16s ease-out}
#cbOv .cbhand .cbc:first-child{margin-left:0}
#cbOv .cbhand .cbc.sel{transform:translateY(-12px);filter:drop-shadow(0 0 8px rgba(255,214,110,.95)) drop-shadow(0 4px 5px rgba(0,0,0,.5))}
#cbOv .cbhand .cbc.off{filter:brightness(.55) drop-shadow(0 2px 3px rgba(0,0,0,.5))}
#cbOv .cbhand .cbc.new{animation:cbin .4s ease-out both}
@keyframes cbin{from{transform:translateY(-30px) scale(.8);opacity:0}to{transform:none;opacity:1}}
#cbOv .cbc.tg::after,#cbOv .cbc.src::after,#cbOv .cbc.fl::after{content:"";position:absolute;inset:-2px;border-radius:inherit;pointer-events:none}
#cbOv .cbc.tg::after{box-shadow:0 0 0 2px rgba(255,238,170,.95),0 0 14px 4px rgba(255,198,64,.85);animation:cbtg .85s ease-in-out infinite alternate}
#cbOv .cbc.src::after{box-shadow:0 0 0 2px rgba(255,224,140,.9),0 0 10px 2px rgba(255,186,60,.5)}
#cbOv .cbc.fl::after{box-shadow:0 0 0 3px rgba(255,248,210,1),0 0 22px 8px rgba(255,208,90,.95);animation:cbfl 1.6s ease-out var(--fld,0s) both}
#cbOv .cbhand .cbc.tg{transform:translateY(-5px)}
#cbOv .cbtl{flex:none;display:inline-flex;align-items:center;gap:4px;margin-left:6px;padding:0 7px 0 6px;height:20px;border-radius:10px;background:rgba(20,12,4,.72);border:1px solid rgba(255,226,160,.55);color:#ffe9a8;font-size:12px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums;white-space:nowrap}
#cbOv .cbtl[hidden]{display:none}
#cbOv .cbtl i{position:relative;flex:none;width:28px;height:5px;border-radius:3px;background:rgba(255,226,160,.2);overflow:hidden}
#cbOv .cbtl i::after{content:"";position:absolute;left:0;top:0;bottom:0;width:calc(var(--p,1) * 100%);border-radius:inherit;background:linear-gradient(90deg,#e2a83e,#ffe07a)}
#cbOv .cbtl .n::after{content:"秒";font-size:9.5px;margin-left:1px;opacity:.85}
#cbOv .cbtl.lo{border-color:rgba(255,128,96,.95);color:#ffb59c}
#cbOv .cbtl.lo i::after{background:linear-gradient(90deg,#d8452e,#ff8a5c)}
#cbOv .cbmod .cbtl.mt{margin:0;height:26px;padding:0 11px 0 9px;font-size:14.5px;border-radius:13px}
#cbOv .cbmod .cbtl.mt i{width:46px;height:6px}
@keyframes cbtg{from{opacity:.45}to{opacity:1}}
@keyframes cbfl{0%{opacity:0}14%{opacity:1}100%{opacity:0}}
#cbOv .cbuse.on .cd{animation:cbusg .9s ease-in-out infinite alternate}
@keyframes cbusg{from{filter:drop-shadow(0 4px 8px rgba(0,0,0,.6)) drop-shadow(0 0 2px rgba(255,222,120,.55))}to{filter:drop-shadow(0 4px 8px rgba(0,0,0,.6)) drop-shadow(0 0 11px rgba(255,212,84,1))}}
@media (prefers-reduced-motion:reduce){#cbOv .cbc.tg::after,#cbOv .cbuse.on .cd{animation:none}}
#cbOv .cbact{flex:none;height:48px;overflow:hidden;display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:nowrap;padding:4px 10px 6px;box-sizing:border-box}
#cbOv .cbact .cbb{flex:0 1 auto;white-space:nowrap}

#cbOv .cbfly{position:absolute;inset:0;pointer-events:none;z-index:5}
#cbOv .cbfl{position:absolute;border-radius:6.5% / 4.3%;will-change:transform;filter:drop-shadow(0 4px 6px rgba(0,0,0,.5))}
#cbOv .cbban{position:absolute;left:0;right:0;top:38%;z-index:6;text-align:center;pointer-events:none;opacity:0;transform:scale(.8);transition:opacity .22s,transform .22s}
#cbOv .cbban.on{opacity:1;transform:none}
#cbOv .cbban .bd{padding:6px 0 8px;background:linear-gradient(90deg,rgba(0,0,0,0),rgba(10,6,3,.86) 16%,rgba(10,6,3,.86) 84%,rgba(0,0,0,0))}
#cbOv .cbban b{display:inline-block;font-size:34px;line-height:1.2;letter-spacing:.06em}
#cbOv .cbban small{display:block;font-size:13px;font-weight:700;color:#fff1cf;margin-top:2px;text-shadow:0 1px 3px #000;white-space:pre-line;line-height:1.45}

#cbOv .cbmod{position:absolute;inset:0;z-index:8;display:none;flex-direction:column;align-items:center;justify-content:center;gap:10px;box-sizing:border-box;padding:calc(var(--sat,env(safe-area-inset-top)) + 10px) 16px calc(var(--sab,env(safe-area-inset-bottom)) + 12px);background:rgba(8,5,2,.8);text-align:center}
#cbOv .cbmod.on{display:flex}
#cbOv .cbmod h3{margin:0;font-size:18px;line-height:1.35}
#cbOv .cbmod p{margin:0;font-size:13.5px;line-height:1.65;color:#f0dfb6;max-width:330px}
#cbOv .cbmod .big{width:min(62vw,calc((100vh - 330px) * .6667),250px);aspect-ratio:2/3;border-radius:6.5% / 4.3%;filter:drop-shadow(0 10px 18px rgba(0,0,0,.6))}
#cbOv .cbmod .big img{width:100%;height:100%;display:block}
#cbOv .cbmod .col{display:flex;flex-direction:column;gap:9px;width:100%;max-width:310px}
#cbOv .cbmod .rowb{display:flex;gap:9px;width:100%;max-width:330px}#cbOv .cbmod .rowb .cbb{flex:1 1 0}
#cbOv .cbmod .pick{display:flex;justify-content:center;gap:8px;flex-wrap:wrap}
#cbOv .cbmod .pick .cbc{width:min(17vw,74px)}
#cbOv .cbmod .pick .cbc.knw{filter:brightness(.5)}
#cbOv .cbmod.cbdm{background:rgba(8,5,2,.95)}
#cbOv .cbmod.cbask{gap:11px;background:rgba(8,5,2,.9)}
#cbOv .cbmod.cbask h3{font-size:22px}
#cbOv .cbmod.cbask .big{width:min(52vw,calc((100vh - 410px) * .6667),220px)}
#cbOv .cbmod .askq{font-size:14px;line-height:1.6;color:#f0dfb6}
#cbOv .cbmod p,#cbOv .cbmsg,#cbOv .cbtoast,#cbOv .cbend .gift,#cbOv .cbhelp .bd{word-break:keep-all;overflow-wrap:anywhere}
#cbOv .cbmod .askq b{display:block;font-size:20px;line-height:1.4;color:#ffe9a8}
#cbOv .cbmod .askq .nw{white-space:nowrap}
#cbOv .cbb.lg{min-height:58px;border-radius:29px;font-size:19px;padding:8px 10px}
#cbOv .cbmod .three{display:flex;justify-content:center;gap:8px}
#cbOv .cbmod .three .cbc{width:min(24vw,104px)}
#cbOv .cbmod .three.four{gap:6px}#cbOv .cbmod .three.four .cbc{width:min(19vw,84px)}
#cbOv .cbmod .rvord{font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-size:21px;letter-spacing:.06em;color:#9ff0c0;text-shadow:0 2px 0 rgba(0,0,0,.6)}
#cbOv .cbmod .rvord small{display:block;font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif;font-size:12px;letter-spacing:0;color:#d9c08c;margin-top:2px}
#cbOv .cbturn small.rv{display:inline-block;margin-left:8px;padding:1px 8px;border-radius:10px;background:linear-gradient(180deg,#1f7a46,#0f4a2a);border:1px solid #7be0a5;color:#e8fff1;font-size:11px;letter-spacing:0;line-height:1.5;vertical-align:2px}
#cbOv .cbuse{position:absolute;left:50%;top:40%;z-index:7;width:min(calc(100% - 24px),390px);box-sizing:border-box;transform:translate(-50%,-50%) scale(.9);opacity:0;pointer-events:none;transition:opacity .22s,transform .22s}
#cbOv .cbuse.on{opacity:1;transform:translate(-50%,-50%);pointer-events:auto}
#cbOv .cbuse .in{display:flex;align-items:center;gap:12px;padding:11px 14px 11px 11px;border-radius:16px;background:linear-gradient(180deg,rgba(52,33,15,.97),rgba(22,13,6,.97));border:2px solid #c9a35a;box-shadow:0 10px 28px rgba(0,0,0,.6),inset 0 0 0 1px rgba(255,226,160,.18),inset 0 1px 0 rgba(255,240,200,.18)}
#cbOv .cbuse .cd{position:relative;flex:none;width:62px;aspect-ratio:2/3;filter:drop-shadow(0 4px 8px rgba(0,0,0,.6))}
#cbOv .cbuse .cd img{position:absolute;left:0;top:0;width:100%;height:100%;display:block}
#cbOv .cbuse .cd.two{width:80px;aspect-ratio:auto;height:98px}
#cbOv .cbuse .cd.two img{width:62px;height:93px}
#cbOv .cbuse .cd.two img+img{left:18px;top:5px;transform:rotate(7deg)}
#cbOv .cbuse .tx{flex:1 1 auto;min-width:0;display:flex;flex-direction:column;align-items:flex-start;gap:2px;text-align:left}
#cbOv .cbuse .who{font-size:11.5px;font-weight:700;line-height:19px;padding:0 9px;border-radius:10px;white-space:nowrap}
#cbOv .cbuse.me .who{background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206}
#cbOv .cbuse.op .who{background:#3a1c10;border:1px solid #ffb38a;color:#ffd9c4;line-height:17px}
#cbOv .cbuse.both .who{background:#1b1209;border:1px solid #c9a35a;color:#ffe2a0;line-height:17px}
#cbOv .cbuse .tx b{font-size:22px;line-height:1.2;margin-top:1px}
#cbOv .cbuse .tx em{font-style:normal;font-size:15px;font-weight:700;line-height:1.3;color:#ffe9a8}
#cbOv .cbuse .tx small{font-size:12.5px;line-height:1.5;color:#f0dfb6;word-break:keep-all;overflow-wrap:anywhere}
#cbOv .cbdl{width:100%;max-width:340px;max-height:56vh;overflow:auto;-webkit-overflow-scrolling:touch;box-sizing:border-box;padding:2px 4px 6px}
#cbOv .cbdl h4{margin:12px 0 6px;font-size:14px;line-height:1.3;color:#ffe2a0;text-align:left;border-left:4px solid #e2a83e;padding-left:8px}
#cbOv .cbdl h4:first-child{margin-top:2px}
#cbOv .cbdl .none{font-size:12.5px;color:#bfa873;text-align:left;padding-left:12px}
#cbOv .cbdl .row{display:flex;align-items:center;gap:10px;padding:6px 8px;margin:5px 0;border-radius:12px;background:rgba(255,236,190,.06);border:1px solid rgba(255,226,160,.22)}
#cbOv .cbdl .row>b{flex:none;width:62px;font-size:12.5px;line-height:1.3;color:#ffe9a8;text-align:left}
#cbOv .cbdl .row>b small{display:block;font-size:10.5px;font-weight:400;color:#d9c08c}
#cbOv .cbdl .pr{flex:1 1 0;min-width:0;display:flex;flex-direction:column;align-items:center;gap:4px;font-size:11px;line-height:1.2;color:#e6d3a6}
#cbOv .cbdl .cs{display:flex;justify-content:center;gap:6px}
#cbOv .cbdl .cbc{width:46px}
#cbOv .cbdl .cbc img{pointer-events:none}
#cbOv .cbvs{display:flex;align-items:flex-start;justify-content:center;gap:14px;width:100%}
#cbOv .cbvs .sd{display:flex;flex-direction:column;align-items:center;gap:6px;width:min(40vw,160px);transition:transform .35s ease-out,filter .35s,opacity .35s}
#cbOv .cbvs .sd span{font-size:13px;font-weight:700;color:#ffe2a0}
#cbOv .cbvs .sd.wn{transform:scale(1.06)}
#cbOv .cbvs .sd.ls{transform:scale(.92);filter:brightness(.5)}
#cbOv .cbvs .mid{align-self:center;font-size:22px}
#cbOv .cbflip{width:100%;aspect-ratio:2/3;perspective:700px}
#cbOv .cbflip .in{position:relative;width:100%;height:100%;transform-style:preserve-3d;transition:transform .5s cubic-bezier(.3,.6,.3,1)}
#cbOv .cbflip.up .in{transform:rotateY(180deg)}
#cbOv .cbflip img{position:absolute;inset:0;width:100%;height:100%;display:block;backface-visibility:hidden;-webkit-backface-visibility:hidden;border-radius:6.5% / 4.3%;filter:drop-shadow(0 8px 12px rgba(0,0,0,.55))}
#cbOv .cbflip img.fc{transform:rotateY(180deg)}
#cbOv .cbres{min-height:52px;font-size:38px;line-height:1.15;opacity:0;transform:scale(.6);transition:opacity .25s,transform .3s cubic-bezier(.3,1.5,.5,1)}
#cbOv .cbres.on{opacity:1;transform:none}
#cbOv .cbres small{display:block;font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif;font-size:13.5px;font-weight:700;color:#fff1cf;-webkit-text-fill-color:#fff1cf;letter-spacing:0;margin-top:2px}
#cbOv .cbmod.cbend{background:rgba(8,5,2,.9)}
#cbOv .cbend h3{font-size:40px;line-height:1.15}
#cbOv .cbend .sc{font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-size:26px;color:#ffe9a8;letter-spacing:.08em}
#cbOv .cbend .sc small{font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif;font-size:12px;color:#d9c08c;letter-spacing:0;display:block}
#cbOv .cbend .gift{min-height:204px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;font-size:14px;line-height:1.6;color:#fff1cf}
#cbOv .cbend .gift b{color:#ffe07a;font-size:17px}
@keyframes cbget{from{transform:scale(.5);opacity:0}to{transform:none;opacity:1}}
#cbOv .cbtoast{position:absolute;left:50%;top:calc(var(--sat,env(safe-area-inset-top)) + 54px);z-index:9;transform:translate(-50%,-8px);width:max-content;max-width:86%;box-sizing:border-box;padding:9px 16px;border-radius:16px;background:rgba(20,12,6,.94);border:1.5px solid #c9a35a;color:#fff1cf;font-size:13.5px;font-weight:700;line-height:1.5;text-align:center;white-space:pre-line;box-shadow:0 6px 16px rgba(0,0,0,.5);opacity:0;pointer-events:none;transition:opacity .2s,transform .2s}
#cbOv .cbtoast.on{opacity:1;transform:translate(-50%,0)}

#cbOv .cbhelp{padding-left:0;padding-right:0}
#cbOv .cbhelp .hd{flex:none;height:48px;display:flex;align-items:center;gap:8px;padding:0 12px}
#cbOv .cbhelp .hd b{flex:1;text-align:center;font-size:17px;color:#ffe9a8;margin-right:64px}
#cbOv .cbhelp .bd{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;padding:4px 18px 26px;font-size:13.5px;line-height:1.75;color:#f0dfb6}
#cbOv .cbhelp h4{display:flex;align-items:center;gap:8px;margin:24px 0 8px;font-size:16px;color:#ffe2a0;scroll-margin-top:6px}
#cbOv .cbhelp h4::before{content:attr(data-n);flex:none;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206;font-size:14px;font-weight:700;box-shadow:0 1px 3px rgba(0,0,0,.5)}
#cbOv .cbhelp .hhero{margin:6px 0 4px;padding:12px 8px 10px;border-radius:16px;background:radial-gradient(120% 90% at 50% 0%,rgba(255,214,120,.16),rgba(255,214,120,.03));border:1px solid rgba(255,226,160,.3)}
#cbOv .cbhelp .hlead{margin:0 0 8px;text-align:center;font-weight:700;color:#ffe9a8;font-size:13.5px;line-height:1.5}
#cbOv .cbhelp .hpts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:4px}
#cbOv .cbhelp .hpt{display:flex;flex-direction:column;align-items:center;text-align:center;gap:1px;min-width:0}
#cbOv .cbhelp .hpt b{font-size:14.5px;color:#ffe07a;line-height:1.3}
#cbOv .cbhelp .hpt span{font-size:10.5px;line-height:1.35;color:#e8d3a4}
#cbOv .cbhelp .hpic{height:56px;width:100%;display:flex;align-items:center;justify-content:center}
#cbOv .cbhelp .hturns{gap:3px;flex-wrap:wrap;align-content:center}
#cbOv .cbhelp .hturns i{flex:none;font-style:normal;width:19px;height:19px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10.5px;font-weight:700;color:#3a2206;background:linear-gradient(180deg,#ffe9a8,#e2a83e);box-shadow:0 1px 3px rgba(0,0,0,.5)}
#cbOv .cbhelp .hfan img{flex:none;width:24px;height:36px;margin-left:-13px;border-radius:2px;filter:drop-shadow(0 1px 2px rgba(0,0,0,.7))}
#cbOv .cbhelp .hfan img:first-child{margin-left:0}
#cbOv .cbhelp .hvs img{flex:none;width:32px;height:48px;filter:drop-shadow(0 1px 2px rgba(0,0,0,.6))}
#cbOv .cbhelp .hvs em{font-style:normal;font-weight:700;color:#ff9b6a;margin:0 3px;font-size:11.5px}
#cbOv .cbhelp .htoc{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;margin:12px 0 2px}
#cbOv .cbhelp .htoc button{min-height:38px;border-radius:12px;border:1px solid rgba(255,226,160,.4);background:rgba(255,236,190,.08);color:#ffe9a8;font:inherit;font-size:13px;font-weight:700;text-align:left;padding:4px 10px}
#cbOv .cbhelp .hcd{position:relative;flex:none;display:flex;flex-direction:column;align-items:center;gap:2px;padding:0;margin:0;border:0;background:none;color:inherit;font:inherit}
#cbOv .cbhelp .hcd img{display:block;width:100%;height:auto;aspect-ratio:2/3;filter:drop-shadow(0 2px 4px rgba(0,0,0,.6))}
#cbOv .cbhelp .hcd small{width:100%;text-align:center;font-size:10.5px;line-height:1.25;color:#ffe9a8}
#cbOv .cbhelp .hrank{margin:6px 0 4px;padding:10px 4px;border-radius:14px;background:rgba(255,236,190,.05);border:1px solid rgba(255,226,160,.2)}
#cbOv .cbhelp .hrk{display:flex;align-items:flex-start;justify-content:center;gap:2px;margin:4px 0}
#cbOv .cbhelp .hrk .hcd{width:min(17vw,64px)}
#cbOv .cbhelp .hrk0{position:relative;padding-top:20px}
#cbOv .cbhelp .hrk0 .hcd{width:min(22vw,84px)}
#cbOv .cbhelp .hrk>i{flex:none;font-style:normal;color:#e2a83e;font-weight:700;font-size:14px;align-self:center;margin-top:-14px}
#cbOv .cbhelp .hrk>i.eq{color:#ffe07a;font-size:18px}
#cbOv .cbhelp .hcrown{position:absolute;left:50%;top:0;transform:translateX(-50%);padding:0 10px;border-radius:10px;background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206;font-size:11.5px;font-weight:700;line-height:18px;white-space:nowrap}
#cbOv .cbhelp .hdir{display:flex;align-items:center;gap:6px;margin:8px 10px 4px;font-size:11px;color:#d9c08c}
#cbOv .cbhelp .hdir i{flex:1;height:2px;position:relative;background:linear-gradient(90deg,#ffe07a,rgba(255,224,122,.15))}
#cbOv .cbhelp .hdir i::after{content:"";position:absolute;right:-2px;top:-4px;border:5px solid transparent;border-left:7px solid rgba(255,224,122,.45)}
#cbOv .cbhelp .hnote{margin:6px 0}
#cbOv .cbhelp .hsteps{display:flex;flex-direction:column;gap:8px;margin:6px 0}
#cbOv .cbhelp .hst{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:12px;background:rgba(255,236,190,.05);border:1px solid rgba(255,226,160,.18)}
#cbOv .cbhelp .hst .hpic{flex:none;width:100px;height:54px}
#cbOv .cbhelp .hst .hturns{gap:2px;flex-wrap:nowrap}
#cbOv .cbhelp .hst .hturns i{width:17px;height:17px;font-size:10px}
#cbOv .cbhelp .hst p{margin:0;flex:1;min-width:0;font-size:12.5px;line-height:1.6}
#cbOv .cbhelp .hscore b{font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-weight:400;font-size:26px;color:#ffe07a}
#cbOv .cbhelp .hscore i{font-style:normal;color:#d9c08c;margin:0 4px}
#cbOv .cbhelp .hflow{list-style:none;margin:6px 0;padding:0;display:flex;flex-direction:column;gap:8px}
#cbOv .cbhelp .hflow li{display:flex;gap:10px;align-items:flex-start;margin:0}
#cbOv .cbhelp .hflow li>i{flex:none;font-style:normal;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#3a2410;border:1.5px solid #e2a83e;color:#ffe9a8;font-weight:700;font-size:13px;margin-top:2px}
#cbOv .cbhelp .hflow li>div>b{display:block;color:#ffe9a8;font-size:14px}
#cbOv .cbhelp .hflow span{display:block;font-size:12.5px;line-height:1.6}
#cbOv .cbhelp .hflow span b{color:#ffe9a8}
#cbOv .cbhelp .hsub{margin:4px 0 8px;font-size:12.5px;line-height:1.65}
#cbOv .cbhelp .hglow{color:#ffe07a;text-shadow:0 0 8px rgba(255,200,70,.9)}
#cbOv .cbhelp .hring{color:#ffe2a0;border:1px solid rgba(255,224,140,.9);border-radius:4px;padding:0 3px}
#cbOv .cbhelp .hef{display:flex;gap:10px;align-items:flex-start;margin:8px 0;padding:10px;border-radius:14px;background:rgba(255,236,190,.06);border:1px solid rgba(255,226,160,.24)}
#cbOv .cbhelp .hef>.hcd{width:72px}
#cbOv .cbhelp .hefr{flex:1;min-width:0}
#cbOv .cbhelp .hefr>b{display:block;color:#ffe9a8;font-size:14.5px;line-height:1.4}
#cbOv .cbhelp .hwhen{display:inline-block;margin:4px 0 2px;padding:0 8px;border-radius:9px;background:#3a2410;border:1px solid #c9a35a;color:#ffd98a;font-size:11px;font-weight:700;line-height:18px}
#cbOv .cbhelp .hneed{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:4px 0}
#cbOv .cbhelp .hmany{display:flex}
#cbOv .cbhelp .hmany img{flex:none;width:22px;height:33px;margin-left:-8px;filter:drop-shadow(0 1px 2px rgba(0,0,0,.6))}
#cbOv .cbhelp .hmany img:first-child{margin-left:0}
#cbOv .cbhelp .hneed em{font-style:normal;font-size:11.5px;color:#e8d3a4}
#cbOv .cbhelp .hefr p{margin:2px 0 0;font-size:12.5px;line-height:1.65}
#cbOv .cbhelp .hefr small{color:#d9c08c;font-size:11px}
#cbOv .cbhelp .hord{margin:10px 0;padding:10px 12px;border-radius:12px;border:1px dashed rgba(255,226,160,.45)}
#cbOv .cbhelp .hord>b{color:#ffe9a8}
#cbOv .cbhelp .hord ol{list-style:none;margin:4px 0 0;padding:0}
#cbOv .cbhelp .hord li{display:flex;align-items:center;gap:8px;margin:3px 0;font-size:12.5px}
#cbOv .cbhelp .hord li i{flex:none;font-style:normal;width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#e2a83e;color:#3a2206;font-size:11px;font-weight:700}
#cbOv .cbhelp .hwhere{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;margin:6px 0}
#cbOv .cbhelp .hwhere>div{padding:8px 10px;border-radius:12px;font-size:11.5px;line-height:1.55}
#cbOv .cbhelp .hwhere>div>b{display:block;font-size:13.5px}
#cbOv .cbhelp .hwhere span b{color:#fff3c4}
#cbOv .cbhelp .hwhere .ok{background:rgba(120,200,140,.12);border:1px solid rgba(140,220,160,.55)}
#cbOv .cbhelp .hwhere .ok>b{color:#b8f0c4}
#cbOv .cbhelp .hwhere .no{grid-column:1/-1;display:flex;align-items:center;justify-content:center;gap:8px;background:rgba(255,120,100,.08);border:1px solid rgba(255,150,120,.4)}
#cbOv .cbhelp .hwhere .no>b{display:inline;color:#ffc2a8}
#cbOv .cbhelp .hcase{position:relative;width:100%;max-width:430px;margin:6px auto 10px;aspect-ratio:1100/185}
#cbOv .cbhelp .hcase>img{position:absolute;inset:0;width:100%;height:100%;display:block;filter:drop-shadow(0 4px 8px rgba(0,0,0,.55))}
#cbOv .cbhelp .hcase>span{position:absolute;display:flex;align-items:center;justify-content:center}
#cbOv .cbhelp .hcase>span img{height:92%;width:auto;max-width:96%;object-fit:contain;filter:drop-shadow(0 2px 3px rgba(0,0,0,.65))}
#cbOv .cbhelp .hgms{display:flex;flex-direction:column;gap:6px}
#cbOv .cbhelp .hgm{display:flex;align-items:center;gap:8px;padding:6px 10px;border-radius:12px;background:rgba(255,236,190,.05);border:1px solid rgba(255,226,160,.18)}
#cbOv .cbhelp .hgm .gm{flex:none;width:40px;height:40px;object-fit:contain;filter:drop-shadow(0 2px 3px rgba(0,0,0,.6))}
#cbOv .cbhelp .hgm>i{flex:none;font-style:normal;color:#c9a35a;font-size:11px}
#cbOv .cbhelp .hgm .hcd{width:38px}
#cbOv .cbhelp .hgm>div{min-width:0}
#cbOv .cbhelp .hgm b{display:block;color:#ffe9a8;font-size:13.5px;line-height:1.35}
#cbOv .cbhelp .hgm span{font-size:12px;color:#e8d3a4}
#cbOv .cbhelp .hgm em{font-style:normal;margin-left:6px;padding:0 6px;border-radius:8px;background:#3a2410;border:1px solid #c9a35a;color:#ffd98a;font-size:10.5px;white-space:nowrap}
#cbOv .cbhelp .hdt{margin:6px 0;border-radius:12px;border:1px solid rgba(255,226,160,.25);background:rgba(255,236,190,.04)}
#cbOv .cbhelp .hdt summary{list-style:none;cursor:pointer;padding:10px 12px;font-weight:700;color:#ffe9a8;display:flex;align-items:center;justify-content:space-between;gap:8px}
#cbOv .cbhelp .hdt summary::-webkit-details-marker{display:none}
#cbOv .cbhelp .hdt summary::after{content:"＋";flex:none;color:#e2a83e}
#cbOv .cbhelp .hdt[open] summary::after{content:"－"}
#cbOv .cbhelp .hdt ul{padding:0 12px 10px 1.9em}
#cbOv .cbhelp .hend{margin:16px 0 0;text-align:center;font-size:11.5px;color:#bfa873}
#cbOv .cbhelp ul{margin:0;padding-left:1.2em}#cbOv .cbhelp li{margin:2px 0}
#cbOv .cbmod.cbset{background:rgba(8,5,2,.93)}#cbOv .cbmod.cbset h3{font-size:22px}
#cbOv .cbsws{display:flex;flex-direction:column;gap:8px;width:100%;max-width:320px}
#cbOv .cbsw{display:flex;align-items:center;gap:10px;min-height:54px;box-sizing:border-box;padding:6px 8px 6px 14px;border-radius:16px;background:rgba(255,236,190,.07);border:1px solid rgba(255,226,160,.26);text-align:left}
#cbOv .cbsw>span{flex:1 1 auto;min-width:0;font-size:16px;font-weight:700;color:#ffe9a8;line-height:1.25}
#cbOv .cbsw>span small{display:block;font-size:11.5px;font-weight:400;color:#d9c08c}
#cbOv .cbseg{flex:none;display:flex;border-radius:21px;border:1.5px solid #c9a35a;overflow:hidden;background:#1b1209}
#cbOv .cbseg button{min-width:58px;height:40px;border:0;padding:0 10px;background:none;color:#bfa873;font-size:15px;font-weight:700}
#cbOv .cbseg button.on{background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206}
#cbOv .cbmenu .row.two .cbb{min-height:44px}
#cbOv .cbci{display:inline-block;width:1.35em;height:1.35em;vertical-align:-.32em;margin-right:.25em}
#cbOv .cbcoinl{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:0 2px;margin:0;font-size:13.5px;line-height:1.5;color:#f0dfb6}
#cbOv .cbcoinl b{color:#ffe07a;font-size:17px}
#cbOv .cbcoinl small{flex:0 0 100%;font-size:11.5px;color:#d9c08c}
#cbOv .cbturn small.stk{margin-left:10px;color:#ffe07a;font-size:11.5px}
#cbOv .cbstk{display:flex;flex-direction:column;gap:9px;width:100%;max-width:330px}
#cbOv .cbstk .blk{box-sizing:border-box;padding:9px 12px 11px;border-radius:16px;background:rgba(255,236,190,.07);border:1px solid rgba(255,226,160,.26);text-align:left}
#cbOv .cbstk .blk>b{display:block;font-size:15px;color:#ffe9a8}
#cbOv .cbstk .blk>small{display:block;font-size:11.5px;line-height:1.45;color:#d9c08c;margin-bottom:7px;word-break:keep-all;overflow-wrap:anywhere}
#cbOv .cbstk .chips{display:flex;flex-wrap:wrap;gap:6px}
#cbOv .cbstk .chips button{min-width:44px;height:40px;box-sizing:border-box;border-radius:20px;border:1.5px solid #c9a35a;background:#1b1209;color:#ffe9a8;font-size:15px;font-weight:700;padding:0 8px}
#cbOv .cbstk .chips button.on{background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206;border-color:#f7d27c}
#cbOv .cbstp{display:flex;align-items:center;justify-content:center;gap:14px}
#cbOv .cbstp button{width:48px;height:42px;border-radius:14px;border:1.5px solid #c9a35a;background:linear-gradient(180deg,#3a2616,#22150b);color:#ffe9a8;font-size:20px;font-weight:700;padding:0}
#cbOv .cbstp button:disabled{opacity:.35}
#cbOv .cbstp>b{min-width:74px;text-align:center;font-size:26px;line-height:1;color:#ffe07a}
#cbOv .cbstp>b small{font-size:13px;font-weight:400;color:#d9c08c;margin-left:2px}
#cbOv .cbstkl{margin:0;font-size:14px;color:#f0dfb6}#cbOv .cbstkl b{color:#ffe07a;font-size:16px}
#cbOv .cbtlh{margin:0;font-size:13px;color:#e8d3a4}
#cbOv .cbmod .cbstkv{font-size:16px;line-height:1.5;color:#f0dfb6}
#cbOv .cbmod .cbstkv b{color:#ffe07a;font-size:21px}#cbOv .cbmod .cbstkv i{font-style:normal;color:#c9a35a;margin:0 8px}
#cbOv .cbmod .cbhave b{color:#ffe07a;font-size:16px}#cbOv .cbmod .cbhave strong{color:#ffb38a}
#cbOv .cbmod.cbjoin{background:rgba(8,5,2,.93)}
#cbOv .cbend .gift .cbcl b{color:#ffe07a;font-size:15.5px}
#cbOv .cbend .gift .cbtkl{font-size:13.5px;color:#ffe9a8}
#cbOv .cbdz{padding-left:0;padding-right:0}
#cbOv .cbdz .hd{flex:none;height:48px;display:flex;align-items:center;gap:8px;padding:0 12px}
#cbOv .cbdz .hd b{flex:1;text-align:center;font-size:17px;color:#ffe9a8;margin-right:64px}
#cbOv .cbdz>.cbcoinl{flex:none;margin:0 0 6px}
#cbOv .cbdz .tabs{flex:none;display:flex;gap:4px;margin:0 14px 4px;padding:3px;border-radius:24px;border:1.5px solid #c9a35a;background:#1b1209}
#cbOv .cbdz .tabs button{flex:1 1 0;min-width:0;height:40px;border:0;border-radius:20px;background:none;color:#bfa873;font-size:min(14px,3.75vw);font-weight:700;padding:0 2px;white-space:nowrap}
#cbOv .cbdz .tabs button.on{background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206}
#cbOv .cbdz .bd{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;padding:0 12px 26px}
#cbOv .cbdz h4{display:flex;align-items:baseline;gap:8px;margin:14px 2px 7px;font-size:15px;color:#ffe2a0;border-left:4px solid #e2a83e;padding-left:8px}
#cbOv .cbdz h4 small{font-size:12px;font-weight:400;color:#d9c08c}
#cbOv .cbdz h4 .cbci,#cbOv .dzt .cbci{width:1.25em;height:1.25em;vertical-align:-.3em;margin-right:.12em}
#cbOv .cbdz .tiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
#cbOv .cbdz .tiles.b{grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}
#cbOv .dzt{display:flex;flex-direction:column;align-items:center;gap:3px;min-width:0;padding:6px 4px 7px;border-radius:12px;border:1.5px solid rgba(255,226,160,.22);background:rgba(255,236,190,.06);color:#f0dfb6}
#cbOv .dzt>img{width:100%;max-width:100px;height:auto;aspect-ratio:2/3;display:block;filter:drop-shadow(0 3px 5px rgba(0,0,0,.5))}
#cbOv .dzt span{font-size:12px;line-height:1.3;color:#ffe9a8;text-align:center;word-break:keep-all;overflow-wrap:anywhere}
#cbOv .dzt em{font-style:normal;font-size:11.5px;line-height:1.25;color:#d9c08c}
#cbOv .dzt.on{border-color:#f7d27c;background:rgba(255,214,120,.16);box-shadow:0 0 0 1px #f7d27c inset}
#cbOv .dzt.on em{color:#ffe07a;font-weight:700}
#cbOv .dzt.lk>img{filter:brightness(.6) saturate(.75) drop-shadow(0 3px 5px rgba(0,0,0,.5))}
#cbOv .cbdz .dzn{margin:12px 4px 0;font-size:12px;line-height:1.6;color:#d9c08c}
#cbOv .cbmod.cbdzm{background:rgba(8,5,2,.93)}
#cbOv .cbmod.cbdzm h3 small{display:block;font-size:12.5px;font-weight:400;color:#d9c08c;letter-spacing:.04em}
#cbOv .cbmod .big.sm{width:min(36vw,calc((100vh - 420px) * .6667),150px)}
#cbOv .cbdz .tiles.d{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
#cbOv .cbdz .tiles.d .dzt>img{max-width:none;aspect-ratio:1672/941;border-radius:6px}
#cbOv .cbmod .big.bd{width:min(calc(100vw - 32px),calc((100vh - 300px) * 1.777),420px);aspect-ratio:1672/941;border-radius:10px;overflow:hidden}
#cbOv .cbmod .big.bd.sm{width:min(64vw,calc((100vh - 400px) * 1.777),260px)}
#cbOv .cbmod .cbneed{font-size:12.5px;color:#ffb38a;text-align:center}
/* 第4.189版：カードパック（デザインカスタムの タブ・パックの 絵・開ける 画面・レア度の 印）*/
#cbOv .cbdz .tabs button{font-size:min(14px,3.6vw)}
#cbOv .rr{display:inline-block;padding:1px 7px;border-radius:999px;font-style:normal;font-size:11px;font-weight:700;letter-spacing:.04em;line-height:1.45;white-space:nowrap}
#cbOv .rr.k-n{background:#3b4356;color:#dfe6f3;box-shadow:0 0 0 1px rgba(223,230,243,.35) inset}
#cbOv .rr.k-r{background:linear-gradient(120deg,#bfe6ff,#d6c8ff 50%,#ffd6f2);color:#1d2340}
#cbOv .rr.k-sr{background:linear-gradient(180deg,#fff3c4,#ffd76a 45%,#e2a83e);color:#3a2206;box-shadow:0 0 6px rgba(255,210,90,.55)}
#cbOv .dzt{position:relative}
#cbOv .dzt>.rr{position:absolute;left:3px;top:3px;font-size:10px;padding:0 6px;z-index:1;box-shadow:0 0 0 1.5px rgba(20,12,6,.9),0 2px 4px rgba(0,0,0,.5)}
#cbOv .dzt.r-r:not(.lk)>img{filter:drop-shadow(0 0 5px rgba(190,220,255,.7)) drop-shadow(0 3px 5px rgba(0,0,0,.5))}
#cbOv .dzt.r-sr:not(.lk)>img{filter:drop-shadow(0 0 6px rgba(255,214,110,.85)) drop-shadow(0 3px 5px rgba(0,0,0,.5))}
#cbOv .cbmod .cbneed.pk{color:#f3e2b8}
#cbOv .pkbox{display:flex;flex-direction:column;align-items:center;gap:9px;margin:12px 0 2px;padding:16px 12px 14px;border-radius:16px;border:1.5px solid rgba(255,214,120,.35);background:radial-gradient(110% 80% at 50% 18%,rgba(126,74,196,.3),rgba(20,12,30,0) 70%),rgba(255,236,190,.05)}
#cbOv .pkbox .cbb{width:min(100%,300px)}
#cbOv .pkbox .cbneed{margin:-2px 0 0;font-size:12.5px;line-height:1.55;color:#ffb38a;text-align:center}
#cbOv .pkc0{margin:2px 0 0;font-size:14px;color:#f3e2b8}
#cbOv .pkc0 b{color:#ffe07a;font-size:17px}
#cbOv .pkc0 .cbci{width:1.25em;height:1.25em;vertical-align:-.3em}
#cbOv .pkc1{margin:-4px 0 2px;font-size:12.5px;color:#d9c08c}
#cbOv .pkun{display:flex;align-items:center;gap:10px;margin:12px 0 0;padding:10px 12px;border-radius:14px;border:1.5px solid #ff9f4a;background:rgba(255,140,60,.14);font-size:13.5px;font-weight:700;color:#ffe2b8;line-height:1.45}
#cbOv .pkun span{flex:1 1 auto}#cbOv .pkun .cbb{flex:none;min-height:40px;padding:6px 16px}
#cbOv .cbdz .pkh3{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px;margin:22px 2px 2px;font-size:16.5px;color:#ffe9a8}
#cbOv .cbdz .pkh3 small{font-size:12px;font-weight:400;color:#d9c08c}
#cbOv .pkhl{display:flex;flex-direction:column;gap:6px}
#cbOv .pkhi{display:flex;align-items:center;gap:8px;width:100%;box-sizing:border-box;padding:6px 10px;border-radius:12px;border:1.5px solid rgba(255,226,160,.22);background:rgba(255,236,190,.06);color:#f0dfb6;text-align:left}
#cbOv .pkhi.un{border-color:#ff9f4a;background:rgba(255,140,60,.12)}
#cbOv .pkhi .w{flex:none;width:6.6em;font-size:12px;color:#d9c08c}
#cbOv .pkhi .cs{flex:1 1 auto;display:flex;gap:3px;min-width:0}
#cbOv .pkhi .cs img{width:min(9vw,34px);height:auto;aspect-ratio:2/3}
#cbOv .pkhi .cs img.r-r{filter:drop-shadow(0 0 3px rgba(190,220,255,.9))}#cbOv .pkhi .cs img.r-sr{filter:drop-shadow(0 0 4px rgba(255,214,110,.95))}
#cbOv .pkart{--pw:132px;position:relative;flex:none;width:var(--pw);aspect-ratio:600/1110;filter:drop-shadow(0 10px 16px rgba(0,0,0,.6))}
#cbOv .pkart img{position:absolute;inset:0;width:100%;height:100%;display:block;-webkit-user-drag:none;-webkit-user-select:none;user-select:none}
#cbOv .pkart::after{content:'';position:absolute;inset:0;pointer-events:none;background:linear-gradient(100deg,rgba(255,255,255,0) 40%,rgba(255,246,214,.34) 50%,rgba(255,255,255,0) 60%) no-repeat;background-size:250% 100%;background-position:150% 0;-webkit-mask:url(cb_pack.webp) 0 0/100% 100% no-repeat;mask:url(cb_pack.webp) 0 0/100% 100% no-repeat;animation:pkshn 5s ease-in-out infinite}
@keyframes pkshn{0%,58%{background-position:150% 0}100%{background-position:-50% 0}}
#cbOv .pkart .tp{clip-path:polygon(0 0, 100% 0, 100% 4.5%, 95% 3.9%, 90% 4.5%, 85% 3.9%, 80% 4.5%, 75% 3.9%, 70% 4.5%, 65% 3.9%, 60% 4.5%, 55% 3.9%, 50% 4.5%, 45% 3.9%, 40% 4.5%, 35% 3.9%, 30% 4.5%, 25% 3.9%, 20% 4.5%, 15% 3.9%, 10% 4.5%, 5% 3.9%, 0% 4.5%);-webkit-clip-path:polygon(0 0, 100% 0, 100% 4.5%, 95% 3.9%, 90% 4.5%, 85% 3.9%, 80% 4.5%, 75% 3.9%, 70% 4.5%, 65% 3.9%, 60% 4.5%, 55% 3.9%, 50% 4.5%, 45% 3.9%, 40% 4.5%, 35% 3.9%, 30% 4.5%, 25% 3.9%, 20% 4.5%, 15% 3.9%, 10% 4.5%, 5% 3.9%, 0% 4.5%);transform-origin:96% 4.2%}
#cbOv .pkart .bd{clip-path:polygon(0% 4.5%, 5% 3.9%, 10% 4.5%, 15% 3.9%, 20% 4.5%, 25% 3.9%, 30% 4.5%, 35% 3.9%, 40% 4.5%, 45% 3.9%, 50% 4.5%, 55% 3.9%, 60% 4.5%, 65% 3.9%, 70% 4.5%, 75% 3.9%, 80% 4.5%, 85% 3.9%, 90% 4.5%, 95% 3.9%, 100% 4.5%, 100% 100%, 0 100%);-webkit-clip-path:polygon(0% 4.5%, 5% 3.9%, 10% 4.5%, 15% 3.9%, 20% 4.5%, 25% 3.9%, 30% 4.5%, 35% 3.9%, 40% 4.5%, 45% 3.9%, 50% 4.5%, 55% 3.9%, 60% 4.5%, 65% 3.9%, 70% 4.5%, 75% 3.9%, 80% 4.5%, 85% 3.9%, 90% 4.5%, 95% 3.9%, 100% 4.5%, 100% 100%, 0 100%)}
#cbOv .cbmod .pkart.sm{--pw:96px}
#cbOv .cbmod .pkod{width:min(100%,340px);border-collapse:collapse;font-size:13px;color:#f0dfb6}
#cbOv .cbmod .pkod caption{font-size:12.5px;color:#d9c08c;padding-bottom:4px}
#cbOv .cbmod .pkod th,#cbOv .cbmod .pkod td{padding:6px 6px;border-bottom:1px solid rgba(255,226,160,.2);text-align:left;font-weight:700;vertical-align:top}
#cbOv .cbmod .pkod td{text-align:right;color:#ffe07a;white-space:nowrap}
#cbOv .cbmod .pkod small{display:block;font-size:11px;color:#d9c08c;font-weight:400}
#cbOv .cbmod p.sm{font-size:12px;color:#d9c08c}
#cbOv .cbmod.cbodm{justify-content:flex-start;overflow-y:auto;-webkit-overflow-scrolling:touch}#cbOv .cbmod.cbodm>:first-child{margin-top:auto}#cbOv .cbmod.cbodm>:last-child{margin-bottom:auto}
#cbOv .cbpk{--k:1;align-items:center;background:radial-gradient(90% 55% at 50% 44%,rgba(98,56,160,.42),rgba(0,0,0,0) 72%),#0c0812}
#cbOv .cbpk .pkhd{flex:none;min-height:50px;display:flex;flex-direction:column;align-items:center;justify-content:center}
#cbOv .cbpk .pkhd b{font-size:22px;letter-spacing:.06em}
#cbOv .cbpk .pkhd small{font-size:12px;color:#d9c08c}
#cbOv .cbpk .pkmsg{flex:none;min-height:2.9em;margin:0 16px;display:flex;align-items:center;justify-content:center;text-align:center;white-space:pre-line;font-size:15px;font-weight:700;line-height:1.45;color:#ffe9a8}
#cbOv .cbpk .pkst{position:relative;flex:1 1 auto;min-height:0;width:100%;display:flex;align-items:center;justify-content:center}
#cbOv .cbpk .pkft{flex:none;width:100%;max-width:340px;box-sizing:border-box;padding:6px 16px 14px;display:flex;flex-direction:column;align-items:center;gap:6px}
#cbOv .cbpk .pkft>.cbb{width:100%}
#cbOv .cbpk .pkft .rowb{display:flex;gap:9px;width:100%}#cbOv .cbpk .pkft .rowb .cbb{flex:1 1 0;padding-left:8px;padding-right:8px;font-size:15px}
#cbOv .cbpk .pkft .rowb .cbb small{display:block;font-size:12px;font-weight:700;opacity:.85}#cbOv .cbpk .pkft .rowb .cbb small .cbci{width:1.2em;height:1.2em;vertical-align:-.28em}
#cbOv .cbpk .pkft .cbneed{margin:0;font-size:12px;color:#ffb38a;text-align:center;line-height:1.5}
#cbOv .cbpk .pkart.big{--pw:min(46vw,200px,calc((100vh - 300px) * .44));position:absolute;z-index:5;left:50%;top:50%;margin:calc(var(--pw) * -.925) 0 0 calc(var(--pw) * -.5);cursor:pointer;animation:pkin calc(.5s * var(--k)) cubic-bezier(.2,.9,.3,1.2) both,pkwob calc(2.8s * var(--k)) ease-in-out calc(.7s * var(--k)) infinite;transition:opacity calc(.42s * var(--k)),transform calc(.42s * var(--k))}
@keyframes pkin{from{opacity:0;transform:translateY(-36px) scale(.9)}to{opacity:1;transform:none}}
@keyframes pkwob{0%,80%,100%{transform:none}86%{transform:rotate(-2.2deg)}92%{transform:rotate(2deg)}}
#cbOv .cbpk .pkart.big .tp{transition:transform calc(.38s * var(--k)) cubic-bezier(.45,0,.8,.55),opacity calc(.38s * var(--k)) ease-in}
#cbOv .cbpk .pkart.big.rip{animation:none}
#cbOv .cbpk .pkart.big.rip .tp{transform:translate(9%,-8%) rotate(-16deg);opacity:0}
#cbOv .cbpk .pkart.big.gone{opacity:0;transform:translateY(34%) scale(.9);pointer-events:none;transition-duration:calc(.5s * var(--k));transition-timing-function:ease-in}
#cbOv .cbpk .pkgrid{--cw:min(29vw,128px,calc((100vh - 300px) / 3.1));display:flex;flex-direction:column;align-items:center;gap:16px}
#cbOv .cbpk .pkgrid .row{display:flex;flex-wrap:nowrap;justify-content:center;align-items:flex-start;gap:12px}
#cbOv .pkc{position:relative;width:var(--cw);aspect-ratio:2/3;padding:0;border:0;background:none;perspective:800px;opacity:0;-webkit-tap-highlight-color:transparent}
#cbOv .pkc.got{opacity:1}
#cbOv .pkc .in{position:absolute;inset:0;transform-style:preserve-3d;transition:transform calc(.46s * var(--k)) cubic-bezier(.3,.6,.3,1)}
#cbOv .pkc.up .in{transform:rotateY(180deg)}
#cbOv .pkc .in img{position:absolute;inset:0;width:100%;height:100%;display:block;backface-visibility:hidden;-webkit-backface-visibility:hidden;filter:drop-shadow(0 6px 10px rgba(0,0,0,.55))}
#cbOv .pkc .in .fr{transform:rotateY(180deg)}
#cbOv .pkc .sh{position:absolute;inset:2%;border-radius:6.5% / 4.3%;transform:rotateY(180deg);backface-visibility:hidden;-webkit-backface-visibility:hidden;pointer-events:none;opacity:0;
  background:linear-gradient(115deg,rgba(255,255,255,0) 38%,rgba(255,255,255,.55) 48%,rgba(196,232,255,.4) 53%,rgba(255,255,255,0) 63%);background-size:320% 100%;background-position:100% 0}
#cbOv .pkc.rv .sh{animation:pksw calc(1.2s * var(--k)) ease-in-out 1 both}
@keyframes pksw{0%{opacity:0;background-position:100% 0}14%{opacity:1}100%{opacity:0;background-position:0 0}}
#cbOv .pkc .gl{position:absolute;inset:-3px;border-radius:9% / 6%;opacity:0;pointer-events:none}
#cbOv .pkc.g-r .gl{box-shadow:0 0 14px 4px rgba(170,214,255,.85)}
#cbOv .pkc.g-gr .gl{box-shadow:0 0 14px 4px rgba(214,176,255,.85),0 0 26px 6px rgba(150,220,255,.4)}
#cbOv .pkc.g-sr .gl{box-shadow:0 0 16px 5px rgba(255,210,90,.9)}
#cbOv .pkc.g-gsr .gl{box-shadow:0 0 16px 5px rgba(255,214,110,.92),0 0 30px 8px rgba(255,150,230,.45)}
#cbOv .cbpk.out .pkc.got:not(.g-n):not(.up) .gl{animation:pkgl calc(2.4s * var(--k)) ease-in-out infinite alternate}
@keyframes pkgl{from{opacity:.35}to{opacity:1}}
#cbOv .pkc.up.r-r .gl,#cbOv .pkc.up.r-sr .gl{opacity:.75}
#cbOv .pkc.up:not(.rv).g-r .gl,#cbOv .pkc.up:not(.rv).g-gr .gl,#cbOv .pkc.up:not(.rv).g-sr .gl,#cbOv .pkc.up:not(.rv).g-gsr .gl{opacity:.75}
#cbOv .pkc.up.r-r:not(.g-r):not(.g-gr) .gl{box-shadow:0 0 12px 3px rgba(170,214,255,.8)}
#cbOv .pkc.up.r-sr:not(.g-sr):not(.g-gsr) .gl{box-shadow:0 0 14px 4px rgba(255,210,90,.85)}
#cbOv .pkc .bst{position:absolute;left:50%;top:50%;width:230%;aspect-ratio:1;border-radius:50%;opacity:0;pointer-events:none;transform:translate(-50%,-50%) scale(.2);
  background:radial-gradient(circle,rgba(255,240,180,.8) 0%,rgba(255,206,96,.34) 34%,rgba(255,206,96,0) 68%)}
#cbOv .pkc.rv.g-sr .bst,#cbOv .pkc.rv.g-gsr .bst{animation:pkbst calc(1.1s * var(--k)) ease-out 1 both}
@keyframes pkbst{0%{opacity:0;transform:translate(-50%,-50%) scale(.2)}28%{opacity:.85}100%{opacity:0;transform:translate(-50%,-50%) scale(1.1)}}
#cbOv .pkc>.rr,#cbOv .pkc>.nw,#cbOv .pkc>.hv{position:absolute;z-index:2;opacity:0;transform:scale(.6);transition:opacity calc(.25s * var(--k)) calc(.32s * var(--k)),transform calc(.25s * var(--k)) calc(.32s * var(--k));pointer-events:none}
#cbOv .pkc.up>.rr,#cbOv .pkc.up>.nw,#cbOv .pkc.up>.hv{opacity:1;transform:none}
#cbOv .pkc>.rr{left:-5px;top:-7px;box-shadow:0 0 0 1.5px rgba(20,12,6,.9),0 2px 5px rgba(0,0,0,.5)}
#cbOv .pkc>.nw{right:-5px;top:-7px;padding:1px 7px;border-radius:999px;background:#ff5b6e;color:#fff;font-size:11px;font-weight:700;letter-spacing:.06em;line-height:1.45;box-shadow:0 2px 6px rgba(0,0,0,.45)}
#cbOv .pkc>.hv{left:50%;bottom:-9px;margin-left:-2.9em;width:5.8em;text-align:center;padding:1px 0;border-radius:999px;background:rgba(20,12,6,.92);border:1px solid rgba(255,226,160,.5);color:#d9c08c;font-size:10.5px;font-weight:700;line-height:1.4}
@media (prefers-reduced-motion: reduce){#cbOv .pkart::after{animation:none;opacity:0}#cbOv .cbpk .pkart.big{animation:none;transition:opacity .2s}#cbOv .cbpk .pkart.big.gone{transform:none}#cbOv .cbpk .pkart.big .tp{transition:opacity .15s}#cbOv .cbpk .pkart.big.rip .tp{transform:none}#cbOv .pkc .in{transition:none}#cbOv .cbpk.out .pkc.got:not(.g-n):not(.up) .gl{animation:none;opacity:.8}#cbOv .pkc.rv .sh,#cbOv .pkc.rv .bst{animation:none}}
#cbOv .cbtst{margin:18px 2px 0;padding:10px 10px 12px;border-radius:14px;border:2px dashed #b98a4a;background:rgba(255,244,214,.08)}
#cbOv .cbtst b{display:block;color:#ffe9a8;font-size:14px}#cbOv .cbtst small{display:block;font-size:11.5px;color:#d9c08c;margin:2px 0 8px}
#cbOv .cbtst .r{display:flex;flex-wrap:wrap;gap:6px}
#cbOv .cbmenu .row.two .cbb .msn{white-space:nowrap}
#cbOv .cbms{padding-left:0;padding-right:0}
#cbOv .cbms .hd{flex:none;height:48px;display:flex;align-items:center;gap:8px;padding:0 12px}
#cbOv .cbms .hd b{flex:1;text-align:center;font-size:17px;color:#ffe9a8;margin-right:64px}
#cbOv .cbms>.cbcoinl{flex:none;margin:0 0 4px}
#cbOv .cbms .msm{flex:none;margin:0 0 6px;text-align:center;font-size:14px;font-weight:700;line-height:1.35;color:#ffe2a0}
#cbOv .cbms .msm small{display:block;font-size:11.5px;font-weight:400;color:#d9c08c}
#cbOv .cbms .tabs{flex:none;display:flex;gap:4px;margin:0 14px 4px;padding:3px;border-radius:24px;border:1.5px solid #c9a35a;background:#1b1209}
#cbOv .cbms .tabs button{flex:1 1 0;height:44px;border:0;border-radius:22px;background:none;color:#bfa873;font-size:15px;font-weight:700;line-height:1.2;padding:0 6px}
#cbOv .cbms .tabs button small{display:block;font-size:11px;font-weight:400}
#cbOv .cbms .tabs button.on{background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206}
#cbOv .cbms .bd{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;padding:0 14px 26px}
#cbOv .cbms h4{margin:12px 2px 6px;font-size:15px;color:#ffe2a0;border-left:4px solid #e2a83e;padding-left:8px}
#cbOv .cbms .cur{display:flex;align-items:baseline;justify-content:center;flex-wrap:wrap;gap:0 6px;margin:0 0 8px;font-size:13.5px;color:#f0dfb6}
#cbOv .cbms .cur b{font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-weight:400;font-size:30px;line-height:1.1;color:#ffe07a}
#cbOv .cbms .cur small{flex:0 0 100%;text-align:center;font-size:12px;color:#d9c08c}
#cbOv .cbms .cur .cbci{width:1.2em;height:1.2em;vertical-align:-.25em;margin-right:.1em}
#cbOv .cbms .msl{display:flex;flex-direction:column;gap:6px}
#cbOv .cbms .qmsi{margin:0 2px 4px;font-size:12.5px;line-height:1.6;color:#f0dfb6}
#cbOv .cbms .qmsi b{color:#ffe07a}
#cbOv .cbms .qmsg{display:flex;align-items:center;gap:6px;margin:12px 2px 6px;font-size:14px;color:#ffe2a0}
#cbOv .cbms .qmsg b{color:#ffe07a;font-size:16px}
#cbOv .cbms .qmsg span{display:inline-flex;gap:2px;margin-left:auto}
#cbOv .cbms .qmsg img{width:20px;height:20px;object-fit:contain;filter:drop-shadow(0 1px 2px rgba(0,0,0,.6))}
#cbOv .cbms .qmsg img.u{opacity:.25;filter:grayscale(1) brightness(.7)}
#cbOv .msr{display:grid;grid-template-columns:5.4em 1fr auto;align-items:center;gap:6px;min-height:42px;box-sizing:border-box;padding:4px 12px;border-radius:12px;border:1.5px solid rgba(255,226,160,.2);background:rgba(255,236,190,.05);color:#d9c08c;font-size:14px}
#cbOv .msr .n{font-size:16px;color:#f0dfb6}
#cbOv .msr .c{font-weight:700;color:#f0dfb6}
#cbOv .msr .c .cbci{width:1.3em;height:1.3em;vertical-align:-.3em;margin-right:.15em}
#cbOv .msr em{font-style:normal;font-size:12.5px;font-weight:700}
#cbOv .msr.done{border-color:#f7d27c;background:rgba(255,214,120,.16)}
#cbOv .msr.done .n,#cbOv .msr.done .c{color:#ffe07a}
#cbOv .msr.done em{color:#ffe07a}
#cbOv .msr.next{border-color:#c9a35a;background:rgba(255,236,190,.1)}
#cbOv .msr.next em{color:#ffd9a0}
#cbOv .cbms .note{margin:12px 2px 0;padding:0 0 0 1.2em;font-size:12px;line-height:1.65;color:#d9c08c}
#cbOv .cbend .gift .cbmsn,#cbOv .cbend .gift .cbsbn,#cbOv .qvic .gift .cbmsn{display:inline-flex;align-items:center;flex-wrap:wrap;justify-content:center;gap:0 5px;box-sizing:border-box;max-width:100%;padding:3px 14px 4px;border-radius:16px;border:1.5px solid #ffd76a;background:rgba(255,214,120,.15);font-size:13.5px;line-height:1.5;color:#fff1cf;animation:cbget .45s cubic-bezier(.2,1.4,.4,1) 1 both}
#cbOv .cbend .gift .cbmsn i,#cbOv .cbend .gift .cbsbn i,#cbOv .qvic .gift .cbmsn i{font-style:normal}
#cbOv .cbend .gift .cbmsn b,#cbOv .cbend .gift .cbsbn b,#cbOv .qvic .gift .cbmsn b{color:#ffe07a;font-size:15px}
#cbOv .cbend .gift .cbmsn .cbci,#cbOv .cbend .gift .cbsbn .cbci,#cbOv .qvic .gift .cbmsn .cbci{width:1.25em;height:1.25em;vertical-align:-.28em;margin-right:0}
#cbOv .cbend .gift .cbsbn{border-color:#ff9f4a;background:rgba(255,140,60,.16)}
/* 第4.196版：決戦調査（メニューの ボタン・マップ・エリアの 窓・フィールド・敵HP ゲージ・戦の あいだ・勝利の 演出）*/
#cbOv .cbmenu .cbb.qb{background:linear-gradient(180deg,#8a3aa0,#4a1660);color:#fff0fb;border-color:#e6b4ff;box-shadow:0 3px 0 #22072c,0 6px 12px rgba(0,0,0,.45),0 0 12px rgba(206,130,255,.35)}
#cbOv .cbmenu .cbb.qb small{color:#f3dcff}
#cbOv .cbmenu .cbb.qb:active{box-shadow:0 1px 0 #22072c,0 3px 6px rgba(0,0,0,.4)}
#cbOv .cbqmap{padding-left:0;padding-right:0}
#cbOv .cbqmap .hd{position:relative;flex:none;height:48px;display:flex;align-items:center;gap:8px;padding:0 12px}
#cbOv .cbqmap .hd b{flex:1;text-align:center;font-size:19px;margin-right:64px}
#cbOv .cbqmap .hd .qtt{position:absolute;right:12px;min-width:44px;padding:5px 8px}
#cbOv .cbqmap .hd .qtt[hidden]{display:none}
#cbOv .qmst{flex:none;margin:0 0 4px;text-align:center;font-size:14px;color:#f0dfb6}
#cbOv .qmst b{color:#ffe07a;font-size:17px}
#cbOv .qmw{flex:1 1 auto;min-height:0;display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden}
/* 第4.203版：調査隊切符の ゲージ（マップの すぐ 上・マップと 同じ 幅：qMapLayout。2つ いっしょに まん中に 置く）。絵（数字を 消した ゲージ）＋ うめた こま（左から n こ 分：clip-path）＋ 枚数の 字 ＋ 次の 1枚までの 時間 */
#cbOv .qtg{position:relative;flex:none;display:block;width:96%;aspect-ratio:7.4549;margin:0 0 6px;padding:0;border:0;background:none;container-type:inline-size;-webkit-tap-highlight-color:transparent}
#cbOv .qtg img{position:absolute;inset:0;width:100%;height:100%;display:block;pointer-events:none;-webkit-user-select:none;user-select:none}
#cbOv .qtg .n{position:absolute;right:20.12%;top:30.9%;transform:translateY(-52%);font:700 5.1cqw/1 "Avenir Next","Helvetica Neue","Hiragino Sans",sans-serif;color:#f6e3bf;letter-spacing:.01em;text-shadow:0 .12cqw .3cqw rgba(0,0,0,.75);pointer-events:none}
#cbOv .qtg .rc{position:absolute;right:31.5%;top:30.9%;transform:translateY(-50%);font:700 2.35cqw/1 "BIZ UDPGothic","Hiragino Sans",sans-serif;color:#e8cf98;white-space:nowrap;text-shadow:0 1px 2px rgba(0,0,0,.8);pointer-events:none}
#cbOv .qtg:active{filter:brightness(1.08)}
#cbOv .qpo .qpotk{margin-top:6px;font-size:13px;line-height:1.4;color:#f3dfae}
#cbOv .qpo .qpotk small{display:block;font-size:11.5px;color:#d9c08c}
#cbOv .tki{display:inline-block;height:1.45em;width:auto;vertical-align:-0.42em;margin:0 5px 0 0;filter:drop-shadow(0 1px 1.5px rgba(0,0,0,.6))}
#cbOv .qpo .qpotk b{color:#ffe07a;font-size:16px}
#cbOv .qpo .qpob .cbb small:empty{display:none}
#cbOv .qpo .qpob .cbb small{display:block;font-size:11px;font-weight:700;color:#5a3a10}
#cbOv .qpo .qpob .cbb:disabled{opacity:.62;filter:grayscale(.35)}
#cbOv .cbmod .qtl{margin:4px 0;font-size:14px;color:#ffe9a8}
#cbOv .cbmod .qtl b{font-size:17px}
#cbOv .cbmod .qtl small{display:block;font-size:11.5px;color:#d9c08c}
#cbOv .cbmod .cbb[data-qt] .qtw:empty{display:none}
#cbOv .cbmod .cbb[data-qt]:disabled{opacity:.62;filter:grayscale(.35)}
#cbOv .cbmod.cbqtk .qtkm{display:flex;flex-direction:column;align-items:center;gap:6px;text-align:center}
#cbOv .cbmod.cbqtk .tk{width:100%;max-width:340px;height:auto;filter:drop-shadow(0 6px 14px rgba(0,0,0,.6))}
#cbOv .cbmod.cbqtk h3{margin:2px 0 0}
#cbOv .cbmod.cbqtk p{margin:0;font-size:14px;line-height:1.55;color:#f3dfae}
#cbOv .cbmod.cbqtk .qtkn{font-size:16px;color:#ffe9a8}
#cbOv .cbmod.cbqtk .qtkn b{font-size:24px;color:#ffe07a}
#cbOv .cbmod.cbqtk .qtkr{font-size:14px;font-weight:700;color:#ffd27a}
#cbOv .cbmod.cbqtk .col{width:100%}
#cbOv .qmap{--u:.38px;position:relative;flex:none;border-radius:12px;overflow:hidden;box-shadow:0 8px 22px rgba(0,0,0,.6),0 0 0 1.5px rgba(255,214,120,.35)}
#cbOv .qmap>img{position:absolute;inset:0;width:100%;height:100%;display:block}
#cbOv .qmft{flex:none;margin:6px 0 2px;text-align:center}
#cbOv .qnd{position:absolute;left:calc((var(--x) - 40) * var(--u));top:calc((var(--y) - 40) * var(--u));width:calc(250 * var(--u));height:calc(80 * var(--u));border:0;padding:0;background:none;border-radius:calc(40 * var(--u))}
#cbOv .qnd i{position:absolute;font-style:normal;pointer-events:none}
#cbOv .qnd .ring{left:calc(8 * var(--u));top:calc(8 * var(--u));width:calc(64 * var(--u));height:calc(64 * var(--u));border-radius:50%}
#cbOv .qnd.op .ring{box-shadow:0 0 0 calc(3 * var(--u)) rgba(255,236,150,.95),0 0 calc(22 * var(--u)) calc(8 * var(--u)) rgba(255,200,80,.75);animation:qrg 1.8s ease-in-out infinite alternate}
@keyframes qrg{from{box-shadow:0 0 0 calc(3 * var(--u)) rgba(255,236,150,.8),0 0 calc(12 * var(--u)) calc(4 * var(--u)) rgba(255,200,80,.45)}to{box-shadow:0 0 0 calc(4 * var(--u)) rgba(255,246,190,1),0 0 calc(26 * var(--u)) calc(10 * var(--u)) rgba(255,200,80,.85)}}
#cbOv .qnd.lk::before{content:"";position:absolute;inset:calc(6 * var(--u)) calc(4 * var(--u)) calc(6 * var(--u)) calc(6 * var(--u));border-radius:calc(36 * var(--u));background:rgba(6,4,10,.55)}
#cbOv .qnd .lock{left:calc(16 * var(--u));top:calc(16 * var(--u));width:calc(48 * var(--u));height:calc(48 * var(--u));border-radius:50%;background:rgba(10,8,14,.78) center/56% no-repeat;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23e9d9b0' d='M7 10V7a5 5 0 0 1 10 0v3h1a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1h1zm2 0h6V7a3 3 0 0 0-6 0v3z'/%3E%3C/svg%3E");box-shadow:0 0 0 calc(2 * var(--u)) rgba(233,217,176,.55)}
#cbOv .qnd.nw .lock{animation:qul .9s ease-in .35s both}
@keyframes qul{0%{opacity:1;transform:none}40%{transform:scale(1.18) rotate(-8deg)}100%{opacity:0;transform:scale(1.6) rotate(10deg)}}
#cbOv .qnd.nw::before{animation:qulb .9s ease-in .35s both}
@keyframes qulb{to{opacity:0}}
#cbOv .qnd .stamp{left:calc(2 * var(--u));top:calc(24 * var(--u));padding:calc(3 * var(--u)) calc(7 * var(--u));border-radius:calc(8 * var(--u));border:calc(3 * var(--u)) solid #ff6a5c;color:#ffe6dc;background:rgba(150,16,20,.82);font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-size:calc(24 * var(--u));line-height:1.1;letter-spacing:.06em;transform:rotate(-14deg);box-shadow:0 calc(3 * var(--u)) calc(8 * var(--u)) rgba(0,0,0,.5)}
#cbOv .qnd .go{left:calc(-6 * var(--u));top:calc(-34 * var(--u));padding:calc(3 * var(--u)) calc(12 * var(--u));border-radius:calc(14 * var(--u));background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206;font-size:calc(24 * var(--u));font-weight:800;line-height:1.25;white-space:nowrap;box-shadow:0 calc(3 * var(--u)) calc(8 * var(--u)) rgba(0,0,0,.55);animation:qgo 1.8s ease-in-out infinite alternate}
@keyframes qgo{from{transform:translateY(0)}to{transform:translateY(calc(-5 * var(--u)))}}
#cbOv .cbmod.cbqa{background:rgba(8,5,2,.93)}
#cbOv .cbmod.cbqa h3 small{display:block;font-size:13px;letter-spacing:.2em}
#cbOv .cbmod.cbqa h3{font-size:24px}
#cbOv .qnd.sel .ring{animation:none;box-shadow:0 0 0 calc(4 * var(--u)) #fff6c8,0 0 calc(24 * var(--u)) calc(9 * var(--u)) rgba(255,214,110,.9)}
#cbOv .qnd.sel .go{visibility:hidden}
#cbOv .qpo{position:absolute;z-index:3;left:8px;top:8px;box-sizing:border-box;padding:9px 12px 12px;border-radius:16px;border:1.5px solid rgba(255,214,120,.85);background:linear-gradient(180deg,#4a3218 0%,#2c1b0b 55%,#1e1207 100%);box-shadow:0 12px 26px rgba(0,0,0,.7),0 0 0 1px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,236,180,.22);color:#f0dfb6;text-align:center;transform-origin:var(--tx,50%) 100%;animation:qpoin .18s ease-out both}
#cbOv .qpo.dn{transform-origin:var(--tx,50%) 0;animation-name:qpoind}
@keyframes qpoin{from{opacity:0;transform:translateY(8px) scale(.92)}to{opacity:1;transform:none}}
@keyframes qpoind{from{opacity:0;transform:translateY(-8px) scale(.92)}to{opacity:1;transform:none}}
#cbOv .qpo p{margin:0}
#cbOv .qpo .qpoh{line-height:1.2}
#cbOv .qpo .qpoh small{display:block;margin-bottom:2px;font-size:12px;font-weight:700;letter-spacing:.22em;color:#e9cf96}
#cbOv .qpo .qpoh b{font-size:21px;letter-spacing:.04em}
#cbOv .qpo .qpoi{margin-top:6px;font-size:14px;line-height:1.45}
#cbOv .qpo .qpoi b{color:#ffe07a;font-size:17px}
#cbOv .qpo .qpoi small{display:block;font-size:12.5px;color:#d9c08c}
#cbOv .qpo .qpoi .cbci{width:1.25em;height:1.25em;vertical-align:-.3em}
#cbOv .qpo .qpor{margin-top:6px;padding:4px 8px;border-radius:10px;border:1px solid rgba(255,140,120,.5);background:rgba(120,20,20,.32);font-size:12px;line-height:1.45;color:#ffd9cc}
#cbOv .qpo .qpob{display:flex;gap:8px;margin-top:10px}
#cbOv .qpo .qpob .cbb{flex:1 1 auto;min-width:0;min-height:46px;padding:8px 10px;font-size:15px}
#cbOv .qpo .qpob .cbb.dk{flex:0 0 34%}
#cbOv .qpo .qpob .cbb.dk:only-child{flex:1 1 auto}
#cbOv .qpo .qpot{position:absolute;left:var(--tx,50%);bottom:-8px;width:14px;height:14px;margin-left:-7.75px;background:#1e1207;border-right:1.5px solid rgba(255,214,120,.85);border-bottom:1.5px solid rgba(255,214,120,.85);transform:rotate(45deg);font-style:normal;pointer-events:none}
#cbOv .qpo.dn .qpot{bottom:auto;top:-8px;background:#4a3218;transform:rotate(225deg)}
#cbOv .cbqf{padding:0;max-width:none}
#cbOv .qfw{position:absolute;inset:0;overflow:hidden;background:#000}
#cbOv .qfld{position:absolute;opacity:0;transition:opacity .6s}
#cbOv .cbqf.in .qfld{opacity:1}
#cbOv .qfld>.bg{position:absolute;inset:0;width:100%;height:100%;display:block}
#cbOv .qfld>.qe{position:absolute;display:block;opacity:.001;transform:translate(-50%,-70.42%);transform-origin:50% 70.42%;pointer-events:none;will-change:transform,opacity}
#cbOv .qfld>.qe>img{display:block;width:100%;height:auto}
#cbOv .qfld>.qe>.q2{position:absolute;left:0;top:0;filter:brightness(2.4) blur(3px);opacity:.001;will-change:opacity}
#cbOv .qfld.en>.qe{animation:qein 1s cubic-bezier(.2,.8,.3,1) both}
#cbOv .qfld.en>.qe>.q2{animation:qeg .9s ease-out both}
@keyframes qein{0%{opacity:0;transform:translate(-50%,-70.42%) scale(1.09)}30%{opacity:1}100%{opacity:1;transform:translate(-50%,-70.42%) scale(1)}}
@keyframes qeg{0%{opacity:.9}100%{opacity:0}}
#cbOv .qfld>.qdu{position:absolute;aspect-ratio:3/1;transform:translate(-50%,-62%);border-radius:50%;opacity:0;pointer-events:none;will-change:transform,opacity;background:radial-gradient(closest-side,rgba(232,214,180,.55),rgba(200,180,150,.25) 55%,rgba(200,180,150,0))}
#cbOv .qfld.en>.qdu{animation:qdu 1.3s ease-out .15s both}
@keyframes qdu{0%{opacity:0;transform:translate(-50%,-62%) scale(.5)}25%{opacity:.9}100%{opacity:0;transform:translate(-50%,-62%) scale(1.35)}}
#cbOv .qfld>.qsh{position:absolute;inset:0;pointer-events:none;background:radial-gradient(120% 70% at 50% 60%,rgba(0,0,0,0) 40%,rgba(0,0,0,.35) 100%)}
#cbOv .cbqf .cbx{z-index:4}
#cbOv .qtel{position:absolute;left:0;right:0;top:calc(var(--sat,env(safe-area-inset-top)) + 58px);z-index:3;text-align:center;opacity:0;transform:translateX(-36px);transition:opacity .35s,transform .5s cubic-bezier(.2,.8,.3,1);pointer-events:none}
#cbOv .qtel.on{opacity:1;transform:none}
#cbOv .qtel .bd{padding:10px 8px 12px;background:linear-gradient(90deg,rgba(40,4,8,0),rgba(40,4,8,.86) 12%,rgba(40,4,8,.86) 88%,rgba(40,4,8,0));border-top:1.5px solid rgba(255,190,120,.55);border-bottom:1.5px solid rgba(255,190,120,.55)}
#cbOv .qtel b{display:block;font-size:30px;line-height:1.2;letter-spacing:.06em}
#cbOv .qtel small{display:block;font-size:15px;font-weight:700;line-height:1.45;color:#fff1cf;margin-top:4px;text-shadow:0 1px 3px #000;word-break:keep-all;overflow-wrap:anywhere}
#cbOv .qnm{position:absolute;left:50%;bottom:calc(var(--sab,env(safe-area-inset-bottom)) + 72px);z-index:3;transform:translate(-50%,8px);opacity:0;transition:opacity .35s,transform .35s;padding:5px 20px 6px;border-radius:999px;background:rgba(14,8,4,.82);border:1.5px solid #c9a35a;color:#ffe9a8;font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-size:20px;letter-spacing:.08em;white-space:nowrap;pointer-events:none;box-shadow:0 4px 12px rgba(0,0,0,.5)}
#cbOv .qnm.on{opacity:1;transform:translate(-50%,0)}
#cbOv .qsay{position:absolute;left:12px;right:12px;bottom:calc(var(--sab,env(safe-area-inset-bottom)) + 16px);z-index:3;min-height:112px;box-sizing:border-box;padding:18px 18px 24px;border-radius:16px;background:linear-gradient(180deg,rgba(30,19,9,.9),rgba(12,8,4,.94));border:2px solid #c9a35a;box-shadow:0 0 0 1px rgba(0,0,0,.6) inset,0 8px 20px rgba(0,0,0,.55);opacity:0;transform:translateY(14px);transition:opacity .3s,transform .3s;pointer-events:none}
#cbOv .qsay.on{opacity:1;transform:none}
#cbOv .qsay p{margin:0;font-size:18px;line-height:1.7;font-weight:700;color:#fff6e0;word-break:keep-all;overflow-wrap:anywhere}
#cbOv .qsay .nx{position:absolute;right:16px;bottom:7px;font-style:normal;color:#ffd27a;font-size:13px;animation:qnx 1s ease-in-out infinite}
@keyframes qnx{0%,100%{transform:translateY(0)}50%{transform:translateY(4px)}}
#cbOv .qtap{position:absolute;left:50%;bottom:calc(var(--sab,env(safe-area-inset-bottom)) + 18px);z-index:3;transform:translateX(-50%);opacity:0;transition:opacity .4s;padding:8px 22px;border-radius:999px;background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206;font-size:16px;font-weight:800;white-space:nowrap;pointer-events:none;box-shadow:0 4px 12px rgba(0,0,0,.5)}
#cbOv .qtap.on{opacity:1;animation:qtp 1.4s ease-in-out .4s infinite alternate}
@keyframes qtp{from{transform:translateX(-50%) scale(1)}to{transform:translateX(-50%) scale(1.06)}}
#cbOv .cbgame.qm .cbtop{height:68px;gap:6px;padding:0 8px}
#cbOv .cbgame.qm .cbturn{display:none}
#cbOv .cbgame:not(.qm) .qhp,#cbOv .cbgame:not(.qm) .cbwho .qt{display:none}
#cbOv .cbwho .qt{font-size:11.5px;color:#d9c08c;white-space:nowrap}
#cbOv .qhp{--gh:62px;position:relative;flex:1 1 auto;min-width:0;height:var(--gh);display:flex}
#cbOv .qhp>img{flex:none;height:100%;width:auto;display:block}
#cbOv .qhp>.l{aspect-ratio:526/294}
#cbOv .qhp>.r{aspect-ratio:156/294}
#cbOv .qhp>.m{flex:1 1 auto;min-width:0;background:url(cb_q_hm.webp) 0 0/100% 100% no-repeat}
#cbOv .qhp .qbar{--cl:calc(var(--gh) * .0493);--cr:calc(var(--gh) * .0833);position:absolute;left:calc(var(--gh) * 1.6769);right:calc(var(--gh) * .3963);top:calc(var(--gh) * .3537);height:calc(var(--gh) * .3350);overflow:hidden;-webkit-clip-path:polygon(var(--cl) 0,calc(100% - var(--cr)) 0,100% var(--cr),100% calc(100% - var(--cr)),calc(100% - var(--cr)) 100%,var(--cl) 100%,0 calc(100% - var(--cl)),0 var(--cl));clip-path:polygon(var(--cl) 0,calc(100% - var(--cr)) 0,100% var(--cr),100% calc(100% - var(--cr)),calc(100% - var(--cr)) 100%,var(--cl) 100%,0 calc(100% - var(--cl)),0 var(--cl))}
#cbOv .qhp .qbar>i{position:absolute;left:0;top:0;bottom:0;font-style:normal}
#cbOv .qhp .dmg{width:100%;background:linear-gradient(180deg,#fff8de 0%,#ffe28e 45%,#f2b447 100%);transition:width .7s ease-in .55s}
#cbOv .qhp .fill{width:100%;background:linear-gradient(180deg,rgba(255,236,226,.7) 0,rgba(255,236,226,0) 2px),linear-gradient(180deg,#ff8b74 0%,#ff5248 24%,#e8262f 52%,#b8121f 80%,#860914 100%);transition:width .35s ease-out}
#cbOv .qhp .sg{position:absolute;inset:0}
#cbOv .qhp .sg i{position:absolute;top:0;bottom:0;width:2px;margin-left:-1px;background:rgba(18,8,4,.9)}
#cbOv .qhp .nm{position:absolute;left:calc(var(--gh) * 1.6769 + 8px);right:calc(var(--gh) * .3963 + 6px);top:calc(var(--gh) * .3537);height:calc(var(--gh) * .3350);display:flex;align-items:center;font-size:12px;font-weight:800;color:#fff;text-shadow:0 0 2px #000,0 0 3px #000,0 1px 2px #000;white-space:nowrap;overflow:hidden;letter-spacing:.02em;pointer-events:none}
#cbOv .qhp .fl{position:absolute;left:calc(var(--gh) * .085);top:calc(var(--gh) * .116);width:calc(var(--gh) * .653);height:calc(var(--gh) * .769);border-radius:30% 30% 50% 50%;opacity:0;pointer-events:none;background:radial-gradient(closest-side,rgba(255,255,255,.95),rgba(255,120,90,.6) 60%,rgba(255,80,60,0))}
#cbOv .qhp.hit{animation:qhit .45s ease-out}
#cbOv .qhp.hit .fl{animation:qfl .55s ease-out}
@keyframes qhit{0%{transform:none}15%{transform:translateX(-4px)}30%{transform:translateX(4px)}45%{transform:translateX(-3px)}60%{transform:translateX(2px)}100%{transform:none}}
@keyframes qfl{0%{opacity:.9}100%{opacity:0}}
#cbOv .qhp.ko>.l{filter:grayscale(.55) brightness(.8)}
#cbOv .cbmod.qend .cbb small{display:block;font-weight:400;font-size:11.5px;opacity:.85}
#cbOv .cbmod.qend{background:linear-gradient(180deg,rgba(8,5,2,0) 0,rgba(8,5,2,0) calc(var(--sat,env(safe-area-inset-top)) + 68px),rgba(8,5,2,.9) calc(var(--sat,env(safe-area-inset-top)) + 78px))}      /* 上の 敵HP ゲージは 見えた まま（窓の 中は いつもの こさ）*/
#cbOv .cbmod.qvic{background:rgba(6,4,2,.94);overflow:hidden}
#cbOv .qv{position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;gap:8px;width:100%}
#cbOv .qv>i{position:absolute;pointer-events:none;font-style:normal}
#cbOv .qv .rays{left:50%;top:24%;width:150vmax;height:150vmax;margin:-75vmax 0 0 -75vmax;z-index:-1;opacity:0;background:repeating-conic-gradient(from 0deg,rgba(255,214,110,.16) 0deg 7deg,rgba(255,214,110,0) 7deg 20deg);-webkit-mask-image:radial-gradient(closest-side,#000 18%,transparent 72%);mask-image:radial-gradient(closest-side,#000 18%,transparent 72%);animation:qry 1s ease-out .1s forwards,qrr 24s linear infinite}
#cbOv .qv.t2 .rays{background:repeating-conic-gradient(from 0deg,rgba(255,214,110,.2) 0deg 6deg,rgba(255,150,90,0) 6deg 15deg)}
#cbOv .qv.t3 .rays{background:repeating-conic-gradient(from 0deg,rgba(255,230,140,.24) 0deg 6deg,rgba(210,150,255,.08) 6deg 9deg,rgba(255,150,90,0) 9deg 15deg);animation:qry 1s ease-out .1s forwards,qrr 16s linear infinite}
@keyframes qry{to{opacity:1}}
@keyframes qrr{to{transform:rotate(360deg)}}
#cbOv .qv .glow{left:50%;top:24%;width:120vw;height:120vw;margin:-60vw 0 0 -60vw;z-index:-1;border-radius:50%;opacity:0;background:radial-gradient(closest-side,rgba(255,236,170,.75),rgba(255,190,90,.25) 45%,rgba(255,190,90,0));animation:qgl 1.4s ease-out both}
@keyframes qgl{0%{opacity:0;transform:scale(.3)}25%{opacity:.85}100%{opacity:.35;transform:scale(1)}}
#cbOv .qv .wave{left:50%;top:24%;width:60vw;height:60vw;margin:-30vw 0 0 -30vw;z-index:-1;border-radius:50%;border:3px solid rgba(255,230,150,.85);opacity:0;animation:qwv 1.6s ease-out .2s both}
#cbOv .qv .wave.w2{border-color:rgba(214,170,255,.7);animation-delay:.55s}
@keyframes qwv{0%{opacity:.9;transform:scale(.2)}100%{opacity:0;transform:scale(1.9)}}
#cbOv .qv .en{--ew:min(76vw,calc((100vh - 470px) * 1.3),300px);position:relative;width:var(--ew);height:calc(var(--ew) / 1.3);display:flex;align-items:flex-start;justify-content:center;animation:qen .7s cubic-bezier(.3,1.5,.5,1) both}
#cbOv .qv .en img{height:calc(var(--ew) / 1.3 * 1.42);width:auto;max-width:none;display:block;flex:none;-webkit-mask-image:linear-gradient(180deg,#000 66%,transparent 70.4%);mask-image:linear-gradient(180deg,#000 66%,transparent 70.4%);filter:saturate(.85) brightness(.9)}      /* 絵の 下の 影・うつりこみ（蹄の 線より 下：1/1.42）は 見せない */
#cbOv .qv .stamp{position:absolute;right:-4%;bottom:12%;padding:4px 14px;border-radius:12px;border:3px solid #ff6a5c;background:rgba(150,16,20,.85);color:#ffe6dc;font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-size:26px;line-height:1.15;letter-spacing:.08em;transform:rotate(-14deg);box-shadow:0 4px 12px rgba(0,0,0,.55);animation:qst .45s cubic-bezier(.3,1.6,.5,1) .55s both}
@keyframes qen{from{opacity:0;transform:scale(.7)}to{opacity:1;transform:none}}
@keyframes qst{from{opacity:0;transform:rotate(-14deg) scale(2.2)}to{opacity:1;transform:rotate(-14deg) scale(1)}}
#cbOv .qv h3{margin:2px 0 0;font-size:40px;line-height:1.15;letter-spacing:.06em;animation:qh3 .6s cubic-bezier(.3,1.5,.5,1) .3s both}
#cbOv .qv.t3 h3{font-size:44px}
@keyframes qh3{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}
#cbOv .qv .sub{margin:0;font-size:15px;font-weight:700;color:#fff1cf;text-align:center;line-height:1.5}
#cbOv .qv .sub small{font-size:13px;color:#f3dcff}
#cbOv .qget{display:inline-flex;align-items:center;gap:12px;box-sizing:border-box;min-width:260px;padding:10px 22px 11px 14px;border-radius:22px;border:2.5px solid #ffd76a;background:linear-gradient(180deg,rgba(80,52,14,.95),rgba(40,24,6,.95));box-shadow:0 0 18px rgba(255,200,80,.45),0 6px 14px rgba(0,0,0,.5);opacity:0;transform:scale(.6)}
#cbOv .qget.on{opacity:1;transform:none;transition:opacity .25s,transform .4s cubic-bezier(.3,1.6,.5,1)}
#cbOv .qget .ci{flex:none;width:52px;height:52px;display:block}
#cbOv .qget.on .ci{animation:qci 1s ease-out}
@keyframes qci{0%{transform:rotateY(0)}100%{transform:rotateY(720deg)}}
#cbOv .qget small{display:block;font-size:14px;font-weight:700;color:#ffe9b0;line-height:1.3}
#cbOv .qget b{display:block;font-size:32px;line-height:1.15}
#cbOv .qget.re b{font-size:21px;line-height:1.3}
#cbOv .qv .qg2{min-height:0;opacity:0;transition:opacity .3s;display:flex;flex-direction:column;align-items:center;gap:6px;font-size:14px;color:#fff1cf}
#cbOv .qv .qg2 .cbcl .cbci{width:1.3em;height:1.3em;vertical-align:-.3em}
#cbOv .qv .qg2.on{opacity:1}
#cbOv .qpt{position:absolute;inset:0;z-index:0;pointer-events:none;overflow:hidden}
#cbOv .qpt .cf{position:absolute;top:-6%;width:9px;height:14px;border-radius:2px;background:hsl(calc(var(--h) * 1),85%,62%);opacity:0;animation:qcf 2.8s linear var(--d) forwards}
@keyframes qcf{0%{opacity:0;transform:translate(0,0) rotate(0)}8%{opacity:1}100%{opacity:.9;transform:translate(var(--x),112vh) rotate(var(--r))}}
#cbOv .qpt .cn{position:absolute;top:-8%;width:30px;height:30px;opacity:0;animation:qcn 2.4s cubic-bezier(.4,0,.8,.6) var(--d) forwards}
@keyframes qcn{0%{opacity:0;transform:translateY(0) scale(var(--s)) rotateY(0)}10%{opacity:1}100%{opacity:1;transform:translateY(115vh) scale(var(--s)) rotateY(900deg)}}
@media (prefers-reduced-motion: reduce){#cbOv .qpo,#cbOv .qnd.op .ring,#cbOv .qnd .go,#cbOv .qsay .nx,#cbOv .qtap.on,#cbOv .qv .rays{animation:none}#cbOv .qv .rays{opacity:1}#cbOv .qpt{display:none}#cbOv .qfld.en>.qe{animation:none;opacity:1}#cbOv .qfld.en>.qe>.q2{animation:none;opacity:0}}
/* 第4.197版：決戦宝石（ケースは 手札の 下）・トークンの カード・宝石の 窓・相手の 宝石・部屋の あり／なし */
#cbOv .cbgem{position:relative;flex:none;width:calc(100% - 20px);max-width:430px;margin:0 auto;aspect-ratio:1100/185}
#cbOv .cbgem[hidden],#cbOv .ogem[hidden]{display:none}
#cbOv .cbgem .case{position:absolute;inset:0;width:100%;height:100%;display:block;pointer-events:none;filter:drop-shadow(0 4px 8px rgba(0,0,0,.55))}
#cbOv .cbgem .gs{position:absolute;inset:0}
#cbOv .cbgem .g{position:absolute;padding:0;margin:0;border:0;background:none;border-radius:14%;display:flex;align-items:center;justify-content:center}
#cbOv .cbgem .g img{height:92%;width:auto;max-width:96%;object-fit:contain;filter:drop-shadow(0 2px 3px rgba(0,0,0,.65));transition:opacity .3s,filter .3s,transform .18s}
#cbOv .cbgem .g.can::before{content:"";position:absolute;inset:6% 4%;border-radius:14%;box-shadow:0 0 0 1.5px rgba(255,232,160,.85),0 0 12px 2px rgba(255,214,110,.55);animation:cbgcan 2.4s ease-in-out infinite alternate;pointer-events:none}
@keyframes cbgcan{from{opacity:.55}to{opacity:1}}
#cbOv .cbgem .g.can img{filter:drop-shadow(0 0 6px rgba(255,236,170,.7)) drop-shadow(0 2px 3px rgba(0,0,0,.6))}
#cbOv .cbgem .g.off img{opacity:.8;filter:saturate(.75) drop-shadow(0 2px 3px rgba(0,0,0,.6))}
#cbOv .cbgem .g.used img{opacity:.3;filter:grayscale(.85) brightness(.7)}
#cbOv .cbgem .g:active img{transform:scale(.93)}
#cbOv .cbgem .g.pop img{animation:cbgpop .75s ease-out}
@keyframes cbgpop{0%{transform:scale(1)}35%{transform:scale(1.22);filter:brightness(1.35) drop-shadow(0 0 10px rgba(255,236,170,.9))}100%{transform:scale(1)}}
#cbOv .ogem{display:inline-flex;align-items:center;gap:1px;margin-left:6px;white-space:nowrap}
#cbOv .ogem img{width:17px;height:17px;object-fit:contain;filter:drop-shadow(0 1px 2px rgba(0,0,0,.6))}
#cbOv .ogem img.u{opacity:.3;filter:grayscale(.9) brightness(.8)}
#cbOv .cbhand .cbc.tok img,#cbOv .cbohand .cbc.tok img,#cbOv .cbslot .cbc.tok img{box-shadow:0 0 0 2px rgba(255,232,160,.85),0 0 10px 3px rgba(255,206,100,.55)}
#cbOv .cbhand .cbc.gone{animation:cbtgone .55s ease-in forwards;pointer-events:none}
@keyframes cbtgone{to{opacity:0;transform:translateY(-18px) scale(.86)}}
#cbOv .cbgemq{display:flex;align-items:center;justify-content:center;gap:10px}
#cbOv .cbgemq .gm{width:min(26vw,104px);height:auto;filter:drop-shadow(0 4px 10px rgba(0,0,0,.6))}
#cbOv .cbgemq i{font-style:normal;font-size:22px;color:#ffe07a}
#cbOv .cbgemq .cbc{display:block;width:min(36vw,150px)}#cbOv .cbgemq .cbc img{width:100%;height:auto;display:block;border-radius:6px;box-shadow:0 6px 16px rgba(0,0,0,.55)}
#cbOv .cbmod.cbgemm p small{display:block;margin-top:4px;font-size:12px;color:#d9c08c}
#cbOv .qgl{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:4px 8px;font-size:14px;color:#ffe9a8}#cbOv .qgl b{font-size:17px}#cbOv .qgl span{display:inline-flex;gap:2px}#cbOv .qgl img{width:24px;height:24px;object-fit:contain;filter:drop-shadow(0 1px 2px rgba(0,0,0,.6))}#cbOv .qgl img.u{opacity:.3;filter:grayscale(.9) brightness(.8)}
#cbOv .gl5{display:flex;gap:6px;justify-content:center;margin-top:9px}#cbOv .gl5 img{width:38px;height:38px;object-fit:contain;filter:drop-shadow(0 2px 3px rgba(0,0,0,.6))}
#cbOv .cbstk .blk .cbseg{margin-top:2px;width:max-content}
#cbOv .cbjg{width:100%;max-width:330px;box-sizing:border-box;padding:9px 12px 11px;border-radius:16px;background:rgba(255,236,190,.07);border:1px solid rgba(255,226,160,.26);text-align:left}
#cbOv .cbjg>b{display:block;font-size:15px;color:#ffe9a8}#cbOv .cbjg>small{display:block;font-size:12px;line-height:1.5;color:#d9c08c;word-break:keep-all;overflow-wrap:anywhere}
@media (prefers-reduced-motion: reduce){#cbOv .cbgem .g.can::before{animation:none;opacity:.85}#cbOv .cbgem .g.pop img{animation:none}#cbOv .cbhand .cbc.gone{animation:none;opacity:0}}
@media (max-height:720px){#cbOv .cbmenu .lg{width:min(44vw,168px)}#cbOv .cbmenu{gap:8px}}
@media (max-height:760px){#cbOv .cbmenu .lg{width:min(36vw,132px)}#cbOv .cbmenu{gap:6px}#cbOv .cbmenu .btns{gap:8px}#cbOv .cbmenu .rec{margin:0}}      /* 第4.196版：決戦調査の ボタンが ふえた ぶん */
@media (prefers-reduced-motion: reduce){#cbOv .cbglow.on{animation:none}#cbOv .cbhand .cbc.new{animation:none}#cbOv .cbflip .in{transition:none}#cbOv .cbend .gift .cbmsn,#cbOv .cbend .gift .cbsbn,#cbOv .qvic .gift .cbmsn{animation:none}#cbOv .cbfire{animation:none;opacity:.88}#cbOv .cbuse,#cbOv .cbuse.on{transform:translate(-50%,-50%);transition:opacity .22s}}
`;
  let ov = null, built = false, scr = {}, flyEl = null, modEl = null, toastEl = null, banEl = null, useEl = null;
  const $ = (s, r) => (r || ov).querySelector(s);
  function build() {
    if (built) return; built = true;
    const s = document.createElement('style'); s.id = 'cbCss'; s.textContent = css; document.head.appendChild(s);
    ov = document.createElement('div'); ov.id = 'cbOv'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'TENGERカードバトル');
    ov.innerHTML = '<div class="cbbg"><div class="cbfire"></div></div>'
      + '<section class="cbs cbmenu" data-s="menu"><button type="button" class="cbb dk sm cbx" data-cb="close">← 戻る</button>'
      + '<img class="lg" src="cb_logo.webp" alt=""><h1 class="gold"><small>TENGER</small>カードバトル</h1><p class="rec"></p><p class="cbcoinl"></p>'
      + '<div class="btns"><button type="button" class="cbb" data-cb="cpu">コンピュータと 対戦</button>'
      + '<button type="button" class="cbb qb" data-cb="quest">⚔️ 決戦調査<small class="qsn"></small></button>'
      + '<div class="row"><button type="button" class="cbb" data-cb="host">部屋を 作る<small>友達と 対戦</small></button><button type="button" class="cbb" data-cb="join">部屋に 入る<small>友達と 対戦</small></button></div>'
      + '<div class="row two"><button type="button" class="cbb dk" data-cb="help">遊び方</button><button type="button" class="cbb dk" data-cb="gear">設定<small>BGM・効果音</small></button></div>'
      + '<div class="row two"><button type="button" class="cbb dk" data-cb="ms">🎯ミッション<small class="msn"></small></button><button type="button" class="cbb dk" data-cb="dz">デザインカスタム<small>カードパック・裏・ボード</small></button></div></div></section>'
      + '<section class="cbs cbroom" data-s="room"></section>'
      + '<section class="cbs cbgame" data-s="game">'
      + '<div class="cbtop"><button type="button" class="cbb dk sm" data-cb="quit">やめる</button><div class="cbturn"></div>'
      + '<div class="qhp" role="img"><img class="l" src="" alt=""><i class="m"></i><img class="r" src="cb_q_hr.webp" alt=""><div class="qbar"><i class="dmg"></i><i class="fill"></i><span class="sg"></span></div><b class="nm"></b><i class="fl"></i></div>'
      + '<button type="button" class="cbb dk sm" data-cb="help" aria-label="遊び方">？</button></div>'
      + '<div class="cbmidw"><div class="cbopp"><div class="cbohand"></div><div class="cbwho"><b></b><span class="cbpips" data-p="op"></span><span class="cbtl" data-p="op" hidden><i></i><span class="n"></span></span><span class="ogem" hidden></span><small class="qt"></small></div></div>'
      + '<div class="cbboard"><img src="cb_board.webp" alt=""><div class="cbfire"></div><div class="cbglow"></div>'
      + '<div class="cbdeck"><img src="cb_deck.webp" alt=""><b class="cbn"></b></div>'
      + '<button type="button" class="cbdis" data-cb="discard" aria-label="捨て札を 見る"><span class="pl"></span><b class="cbn"></b></button>'
      + '<div class="cbslot op"></div><div class="cbslot my"></div>'
      + '<button type="button" class="cbgear" data-cb="gear" aria-label="メニュー"></button></div>'
      + '<div class="cbmsg" aria-live="polite"></div>'
      + '<div class="cbme"><div class="cbwho"><b>あなた</b><span class="cbpips" data-p="my"></span><span class="cbtl" data-p="my" hidden><i></i><span class="n"></span></span></div></div>'
      + '<div class="cbhand"></div><div class="cbgem" hidden><img class="case" src="cb_gmcase.webp" alt=""><div class="gs"></div></div><div class="cbact"></div></div></section>'
      + '<section class="cbs cbhelp" data-s="help"></section>'
      + '<section class="cbs cbdz" data-s="dz"></section>'
      + '<section class="cbs cbms" data-s="ms"></section>'
      + '<section class="cbs cbpk" data-s="pk"></section>'
      + '<section class="cbs cbqmap" data-s="qmap"><div class="hd"><button type="button" class="cbb dk sm" data-cb="qx">← 戻る</button><b class="gold">⚔️ 決戦調査</b><button type="button" class="cbb dk sm qtt" data-cb="qtst" aria-label="テスト版の 道具">🧪</button></div><p class="qmst"></p><div class="qmw"><button type="button" class="qtg" data-cb="qtk"><img class="b" src="cb_q_tg.webp" alt="" draggable="false"><img class="f" src="cb_q_tgf.webp" alt="" draggable="false"><b class="n"></b><small class="rc"></small></button><div class="qmap"></div></div><p class="cbcoinl qmft"></p></section>'
      + '<section class="cbs cbqf" data-s="qf"><div class="qfw" data-cb="qtap"><div class="qfld"></div></div><button type="button" class="cbb dk sm cbx" data-cb="qback">← マップ</button>'
      + '<div class="qtel" aria-live="polite"></div><div class="qnm"></div><div class="qsay" aria-live="polite"><p></p><i class="nx" aria-hidden="true">▼</i></div><div class="qtap">▶ タップで バトル開始！</div></section>'
      + '<div class="cbfly"></div><div class="cbban"></div><div class="cbuse" data-cb="useok" aria-live="polite"></div><div class="cbmod" role="dialog" aria-modal="true"></div><div class="cbtoast" aria-live="polite"></div>';
    document.body.appendChild(ov);
    ov.querySelectorAll('.cbs').forEach(e => { scr[e.dataset.s] = e; });
    flyEl = $('.cbfly'); modEl = $('.cbmod'); toastEl = $('.cbtoast'); banEl = $('.cbban'); useEl = $('.cbuse');
    ov.addEventListener('click', onClick);
    document.addEventListener('visibilitychange', () => { if (ov.classList.contains('on')) { bgmSync(); if (document.hidden) qaStop(0.05, true); } });      
    window.addEventListener('resize', () => { if (ov.classList.contains('on')) { layout(); qMapLayout(); qFieldLayout(); } });
    try { if (document.fonts && document.fonts.addEventListener) document.fonts.addEventListener('loadingdone', () => { if (ov.classList.contains('on')) qsRefit(); }); } catch (e) {   }      
    if (window.ResizeObserver) new ResizeObserver(() => { if (ov.classList.contains('on')) layout(); }).observe(scr.game);
  }
  let screen = '';
  function show(name) {
    const was = screen; screen = name; Object.keys(scr).forEach(k => scr[k].classList.toggle('on', k === name)); if (name !== 'game') useOff();
    if (was !== name && toastEl && toastEl.classList.contains('on')) toastPos();      
  }
  let toastT = 0;
  function toast(t, sec, ic) {
    toastEl.textContent = t;
    if (ic) { const i = document.createElement('img'); i.className = 'tki'; i.src = ic; i.alt = ''; toastEl.prepend(i); }      
    toastPos();
    toastEl.classList.add('on');
    unlater(toastT); toastT = later(() => toastEl.classList.remove('on'), (sec || 2.4) * 1000 * Math.max(SPEED, 0.2));
  }
  
  function toastPos() {
    
    const m = screen === 'game' ? $('.cbmsg') : null;
    if (m && m.getBoundingClientRect().height) { const r = m.getBoundingClientRect(), o = ov.getBoundingClientRect(); toastEl.style.top = Math.max(60, r.top - o.top - 6) + 'px'; }
    else if (screen === 'pk') toastEl.style.top = Math.round(ov.getBoundingClientRect().height * 0.13) + 'px';      
    else if (screen === 'dz' || screen === 'ms') toastEl.style.top = Math.round(ov.getBoundingClientRect().height * 0.6) + 'px';      
    else toastEl.style.top = '';
  }
  async function banner(big, small, ms) {
    banEl.innerHTML = `<div class="bd"><b class="gold">${esc(big)}</b>${small ? `<small>${esc(small)}</small>` : ''}</div>`; banEl.classList.add('on');
    await T(ms || 900); banEl.classList.remove('on'); await T(180);
  }
  
  
  
  
  const USE_MS = 1900;
  let useSkip = null;
  function useOf(x) {
    const W = WHO(), yours = x.me ? `${W}の` : 'あなたの';
    if (x.e === 'p6') return { k: '6', t: '6 の 効果', n: '手札を 1枚 見る', d: `6 を 2枚 見せて、${yours} 手札を 1枚 見るよ` };
    if (x.e === 'u5') return { k: '5', t: '5 の 効果', n: '捨てて 山札から セット', d: 'セットした 5 と 手札 1枚を 捨てて、山札から 1枚 伏せて セットするよ' };
    if (x.e === 'x7') return x.tok ? { k: 't7', t: '7 の 効果', n: '3枚 引く', d: '7トークン（3頭分）を 見せて 捨てて、山札から 3枚 引くよ' } : { k: '7', t: '7 の 効果', n: '3枚 交換', d: '7 を 3枚 山札に 戻して、新しく 3枚 引くよ' };      
    if (x.e === 'x7r') return x.drop && x.drop.tok ? { k: 't7', t: '7 の 効果', n: '強さ 逆転', d: '7 を 4枚 ぶん 見せて（7トークンは 3頭分）、トークンを 捨てるよ。この 対戦が 終わる まで、数字の 強さが 逆に なる！' } : { k: '7', t: '7 の 効果', n: '強さ 逆転', d: '7 を 4枚 見せて 1枚 捨てるよ。この 対戦が 終わる まで、数字の 強さが 逆に なる！' };
    if (x.e === 'x3') return { k: '3', t: '3 の 効果', n: '手札を 交換', d: x.three && x.three.length < 3 ? `3トークン（2頭分）と 3 で 3枚 ぶん 見せて、本物の 3 と ${yours} 手札から 選んだ 1枚（裏の カード）を 交換するよ` : `3 を 3枚 見せて、その 1枚と ${yours} 手札から 選んだ 1枚（裏の カード）を 交換するよ` };      
    if (x.e === 'first') return { k: '4', t: '4 の 効果', n: '強制 交換', d: x.me ? `4 を 先に 見せたよ。${W}は セットした カードを 交換するよ` : '4 を 先に 見せたよ。あなたは セットした カードを、手札の 別の カードと 交換してね' };
    if (x.e === 'first2') return { k: '4', t: '4 の 効果', n: '打ち消して ドロー', d: '2人とも 4 の 効果を 使った ので、打ち消しあって この ターンは ドロー（引き分け）だよ', both: true };
    if (x.e === 'k') return { k: x.tok ? tokP('k') : 'k', t: `${kmN('k', x.tok)}の 効果`, n: '手札を 1枚 見る', d: `前の ターンに ${kmN('k', x.tok)}で 勝った ので、${yours} 手札を 1枚 見るよ` };      
    if (x.e === 'm') return { k: x.tok ? tokP('m') : 'm', t: `${kmN('m', x.tok)}の 効果`, n: '捨てて 引き直す', d: `前の ターンに ${kmN('m', x.tok)}で 勝った ので、手札を 2枚 捨てて、山札から ${x.n}枚 引くよ` };
    if (x.e === 'rev') return x.drop && x.drop.tok ? { k: tokP(x.k), t: `${x.k} の 効果`, n: '逆転勝利', d: `場の ${x.k} と ${x.k}トークン（2頭分）で 3枚 ぶん。トークンを 捨てて、${toName(x.beat)} 勝ち！` } : { k: x.k, t: `${x.k} の 効果`, n: '逆転勝利', d: `${x.k} を 3枚（場の 1枚 ＋ 手札の 2枚）見せて、手札の ${x.k} を 1枚 捨てると、${toName(x.beat)} 勝ち！` };      
    return null;
  }
  async function useShow(x) {
    const u = useOf(x); if (!u || !useEl || screen !== 'game') return;
    hush();                                            
    const im = sd => `<img src="${pic(u.k, false, sd)}" alt="" draggable="false">`;
    useEl.className = 'cbuse ' + (u.both ? 'both' : x.me ? 'me' : 'op');
    useEl.innerHTML = `<div class="in"><span class="cd${u.both ? ' two' : ''}">${u.both ? im('my') + im('op') : im(x.me ? 'my' : 'op')}</span><div class="tx">`
      + `<span class="who">${esc(u.both ? 'どちらも 使った！' : x.me ? 'あなたが 使った！' : WHO() + 'が 使った！')}</span><b class="gold">${esc(u.t)}</b><em>${esc(u.n)}</em><small>${esc(u.d)}</small></div></div>`;
    const bd = $('.cbboard').getBoundingClientRect(), o = ov.getBoundingClientRect();
    useEl.style.top = bd.height ? Math.round(bd.top - o.top + bd.height / 2) + 'px' : '';      
    void useEl.offsetWidth; useEl.classList.add('on');
    se('magic');
    await new Promise(ok => { const h = later(() => { useSkip = null; ok(); }, USE_MS * SPEED); useSkip = () => { unlater(h); useSkip = null; ok(); }; });
    useEl.classList.remove('on'); await T(220);
  }
  function useOff() { if (useSkip) useSkip(); if (useEl) useEl.classList.remove('on'); }      

  
  function showMenu() {
    pk = null;      
    qaStop(0.15, true);      
    closeMod(); show('menu'); msRoll();
    const tot = st.win + st.lose + st.draw;
    $('.rec', scr.menu).innerHTML = (tot ? `<b>${st.win}</b>勝 <b>${st.lose}</b>敗 <b>${st.draw}</b>分` + (st.streak > 0 ? `　今 <b>${st.streak}</b>連勝！` : '') + '<br>' : '')
      + `コンピュータに ${TK_BONUS.map(t => `<b>${t[0]}</b>連勝 ごとに 調査隊切符 <b>${t[1]}</b>枚`).join('・')}`;
    $('.cbcoinl', scr.menu).innerHTML = `${COINI}<span>バトルコイン <b>${st.coin}</b>枚</span><small>${coinHow()}<br>${coinDay()}</small>`;
    $('[data-cb=ms] .msn', scr.menu).textContent = `今月 ${msDone()}／${MS_ALL} 達成`;      
    qRoll(); $('[data-cb=quest] .qsn', scr.menu).textContent = st.q.clr >= QN ? `今月は 全部 討伐！（${QN}／${QN}）` : `今月 ${st.q.clr}／${QN} 討伐・次は レベル${qOpen()}`;      
    bgmTrack('main');
    const lw = [];
    if (lostLive >= 0) { lw.push(lostLive > 0 ? `負けに 数えたよ（${lostLive}連勝は 0 に 戻ったよ）` : '負けに 数えたよ'); lostLive = -1; }      
    if (lostStake > 0) { lw.push(`参加コイン ${lostStake}枚は 戻らなかったよ`); lostStake = 0; }
    if (lostQ) { lw.push('決戦調査は 失敗に なったよ'); lostQ = false; }      
    if (lostMs) { lw.push(`ミッションの 連勝（${MS_WHO[lostMs]}）は 0 に 戻ったよ`); lostMs = ''; }
    const tw = lw.length ? ['前の 対戦が 途中で 終わった ので、\n' + lw.join('\n')] : [];
    if (pkUnseen().length && !pkTold) { pkTold = true; tw.push('🎴 開けた パックの 結果は\n「デザインカスタム」→「カードパック」で 見られるよ'); }      
    if (giftGot > 0) { tw.push(`🎁 ログインボーナスの バトルコイン\n${giftGot}枚を 受け取ったよ${giftFull ? `（${COIN.max}枚 まで）` : ''}`); giftGot = 0; giftFull = false; }      
    if (tw.length) toast(tw.join('\n'), (lw.length ? 3.6 + (lw.length - 1) * 1.2 : 2.4) + (tw.length - (lw.length ? 1 : 0)) * 1.2);
    const can = !!(window.__NATIVE && window.TengelNative);
    scr.menu.querySelectorAll('[data-cb=host],[data-cb=join]').forEach(b => { b.disabled = !can; });
  }

  
  
  
  
  
  
  
  
  
  let helpBack = 'menu';
  function showHelp(from) {
    helpBack = from || 'menu'; closeMod();
    const im = (k, cls) => `<img class="${cls || ''}" src="${pic(k)}" alt="${k == null ? '伏せた カード' : esc(nameOf(k))}" draggable="false">`;
    const card = (k, cap, cls) => `<button type="button" class="hcd${cls ? ' ' + cls : ''}" data-cb="hbig" data-k="${esc(k)}" aria-label="${esc(nameOf(k))} の カードを 大きく 見る">${im(k)}${cap ? `<small>${cap}</small>` : ''}</button>`;
    const many = (k, n) => `<span class="hmany">${Array.from({ length: n }, () => im(k)).join('')}</span>`;
    const when = t => `<span class="hwhen">${t}</span>`;
    const ef = (k, title, wh, need, d) => `<div class="hef">${card(k)}<div class="hefr"><b>${title}</b>${when(wh)}${need ? `<div class="hneed">${need}</div>` : ''}<p>${d}</p></div></div>`;
    const sec = (id, n, t) => `<h4 data-h="${id}" data-n="${n}">${t}</h4>`;      
    const turnPips = Array.from({ length: R.TURNS }, (_, i) => `<i>${i + 1}</i>`).join('');
    const gemsCase = '<div class="hcase"><img src="cb_gmcase.webp" alt="決戦宝石の ケース" draggable="false">'
      + R.GEMS.map((g, i) => { const s = GEM_SLOT[i]; return `<span style="left:${s[0]}%;top:${s[1]}%;width:${s[2]}%;height:${s[3]}%"><img src="${gemPic(g)}" alt="${esc(GEMS[g].n)}" draggable="false"></span>`; }).join('') + '</div>';
    const gemRow = g => `<div class="hgm"><img class="gm" src="${gemPic(g)}" alt="" draggable="false"><i aria-hidden="true">▶</i>${card(tokP(g), '', 'tk')}<div><b>${esc(GEMS[g].n)}</b><span>${esc(GEMS[g].t)}${R.GEM_W[g] > 1 ? `<em>${R.GEM_W[g]}頭分</em>` : ''}</span></div></div>`;
    scr.help.innerHTML = '<div class="hd"><button type="button" class="cbb dk sm" data-cb="helpx">← 戻る</button><b>遊び方</b></div><div class="bd">'
      
      + '<div class="hhero"><p class="hlead">TENGERカードバトルは、馬の カードで 戦う ゲームだよ</p><div class="hpts">'
      + `<div class="hpt"><div class="hpic hturns">${turnPips}</div><b>${R.TURNS}ターン</b><span>で 勝負</span></div>`
      + `<div class="hpt"><div class="hpic hfan">${Array.from({ length: R.HAND }, () => `<img src="${pic(null)}" alt="" draggable="false">`).join('')}</div><b>手札 ${R.HAND}枚</b><span>から 1枚ずつ 出す</span></div>`
      + `<div class="hpt"><div class="hpic hvs">${im('1')}<em>VS</em>${im('5')}</div><b>強い 方の 勝ち</b><span>勝った 数が 多い 人の 優勝</span></div>`
      + '</div></div>'
      + '<nav class="htoc" aria-label="もくじ">' + [['st', '① カードの 強さ'], ['rule', '② 勝負の 仕方'], ['flow', '③ 1ターンの 流れ'], ['ef', '④ カードの 効果'], ['gem', '⑤ 決戦宝石'], ['etc', '⑥ そのほか']]
        .map(([h, t]) => `<button type="button" data-cb="hgo" data-h="${h}">${t}</button>`).join('') + '</nav>'
      
      + sec('st', '1', 'カードの 強さ')
      + '<div class="hrank"><div class="hrk hrk0">' + card('k', '神様馬') + '<i class="eq">＝</i>' + card('m', '幻の馬') + '<span class="hcrown">いちばん 強い！</span></div>'
      + '<p class="hdir"><span>強い</span><i></i><span>弱い</span></p>'
      + '<div class="hrk">' + ['1', '2', '3', '4'].map(k => card(k, k === '1' ? '数字の 最強' : '')).join('<i>＞</i>') + '</div>'
      + '<div class="hrk"><i>＞</i>' + ['5', '6', '7'].map(k => card(k, k === '7' ? '一番 弱い' : '')).join('<i>＞</i>') + '</div></div>'
      + '<ul class="hnote"><li>数字は <b>1 が 一番 強くて、7 が 一番 弱い</b>よ</li>'
      + '<li><b>同じ 数字</b>が ぶつかったら「<b>かぶり</b>」＝ <b>どちらも 負け</b>（4 同士で 2人とも 4 の 効果を 使った ときは ドロー）</li>'
      + '<li><b>神様馬 と 幻の馬</b>が ぶつかったら <b>引き分け</b></li>'
      + '<li>7 の 効果（<b>4枚 公開</b>）で <b>強さ 逆転</b>したら、その 対戦が 終わる まで <b>7＞6＞5＞4＞3＞2＞1</b>（神様馬・幻の馬は 一番 強い まま。上に「強さ 逆転中」と 出るよ）</li>'
      + '<li>カードは 全部で <b>30枚</b>：1〜7 が 4枚 ずつ・神様馬 1枚・幻の馬 1枚</li></ul>'
      
      + sec('rule', '2', '勝負の 仕方')
      + '<div class="hsteps">'
      + `<div class="hst"><div class="hpic hfan">${Array.from({ length: R.HAND }, () => `<img src="${pic(null)}" alt="" draggable="false">`).join('')}</div><p><b>手札は ${R.HAND}枚</b>（2人とも 山札から 配られるよ）</p></div>`
      + `<div class="hst"><div class="hpic hturns">${turnPips}</div><p><b>${R.TURNS}ターン</b> 戦うよ。1ターンに <b>1枚ずつ</b> 出すから、<b>${R.HAND - R.TURNS}枚は 使わずに 残る</b>よ（ターンの 間に 山札から 引かない）</p></div>`
      + `<div class="hst"><div class="hpic hvs">${im(null)}<em>VS</em>${im(null)}</div><p>2人とも カードを <b>伏せて セット</b> → 一緒に <b>めくって、強い 方の 勝ち</b></p></div>`
      + `<div class="hst"><div class="hpic hscore"><b>3</b><i>－</i><b>1</b></div><p>${R.TURNS}ターン 終わって <b>勝った 数が 多い 人の 勝ち</b>（同じ なら 同点）。<b>先に 勝ちが 決まったら</b>（3勝した・残りを 全部 勝っても 追いつけない）その ターンで 試合終了</p></div>`
      + '</div>'
      + '<ul class="hnote"><li>相手は <b>コンピュータ</b> か、近くに いる <b>友達</b>（部屋を 作って 対戦）。<b>決戦調査</b>では 強い 敵と 連続で 戦うよ</li></ul>'
      
      + sec('flow', '3', '1ターンの 流れ')
      + '<ol class="hflow">'
      + `<li><i>1</i><div><b>ターンの 始め</b><span>手札に <b>6 が 2枚</b> ある 人は「6 の 効果」・前の ターンに <b>神様馬・幻の馬</b>で 勝った 人は その 効果を 使えるよ</span></div></li>`
      + `<li><i>2</i><div><b>セット</b><span>手札から 1枚 選んで <b>伏せて 出す</b>（自分の カードには 数字の 印・タップで 見られる）。<b>セットしたら もう 変えられない</b>よ。<b>7・3 の 効果</b>と <b>決戦宝石</b>は セットの 前に 使えるよ（使った 後で セットする カードを 選べる）。<b>友達バトルは ${Math.round(SET_LIMIT / 1000)}秒 まで</b>（すぎたら 自動で 1枚）</span></div></li>`
      + `<li><i>3</i><div><b>効果タイム</b><span>2人とも セットしたら、セットした <b>5 → 4</b> の 順に 効果を 使うか 聞かれるよ（1つ 終わってから 次。同じ 効果を 2人とも 使える ときは、2人とも 決めて から 一緒に 出る）</span></div></li>`
      + `<li><i>4</i><div><b>オープン</b><span>2枚 一緒に めくって 勝ち負け。負けた 人は <b>1・2 の 逆転勝利</b>を 使えるかも</span></div></li>`
      + '</ol>'
      
      + sec('ef', '4', 'カードの 効果')
      + '<p class="hsub">効果は <b>使うか 使わないか 自分で 選べる</b>よ。使う ときは、<b class="hglow">選べる カードが 金色に 光る</b>よ（<b class="hring">金の ふち</b>＝その 効果に かかわる カード）。効果で 来た カード・見た カード・見られた カードは 少しの 間 強く 光るよ</p>'
      + ef('k', '神様馬：相手の 手札を 見る', '勝った 次の ターンの 始め', `${many('k', 1)}<em>神様馬で 勝つ</em>`, '相手の 手札を <b>1枚 選んで 見られる</b>よ（まだ 見て いない カードが ある とき）')
      + ef('m', '幻の馬：手札を 入れかえ', '勝った 次の ターンの 始め', `${many('m', 1)}<em>幻の馬で 勝つ</em>`, '手札を <b>2枚 捨てて</b>、山札から <b>2枚 引ける</b>よ')
      + ef('1', '1：逆転勝利', 'オープンの 後', `${many('1', 3)}<em>場の 1 ＋ 手札の 1 が 2枚</em>`, '1 を 出して <b>神様馬・幻の馬に 負けた</b> とき、手札の 1 を 2枚 見せて 1枚 捨てると <b>勝ちに できる</b>よ')
      + ef('2', '2：逆転勝利', 'オープンの 後', `${many('2', 3)}<em>場の 2 ＋ 手札の 2 が 2枚</em>`, '2 を 出して <b>1 に 負けた</b> とき、手札の 2 を 2枚 見せて 1枚 捨てると <b>勝ちに できる</b>よ<br><small>1・2 とも、捨てた 後の 手札が 残りの ターンの 数より 少なく ならない とき だけ</small>')
      + ef('3', '3：3枚 見せて 交換', 'セットの 前', `${many('3', 3)}<em>手札に 3 が 3枚</em>`, '3枚を 見せて、その 1枚と、相手の 手札の <b>裏の カードから 自分で 選んだ 1枚</b>を 交換（何が 来るかは わからない）。もう 見た カードは 選べないよ<br><small>手札に あれば 使える（3 を セットしなくて いい）</small>')
      + ef('4', '4：見せて 強制交換', '効果タイム（いちばん 後）', `${many('4', 1)}<em>4 を セット</em>`, '4 を 先に 見せる かわりに、<b>相手は セットした カードを 手札の 別の カードと 交換</b>しないと いけないよ。<b>2人とも 4 の 効果を 使ったら</b> その ターンは <b>ドロー</b>。交換で 5 を セットしたら、5 の 効果も 使えるよ<br><small>4 は 一番 後：相手が 5 の 効果で 山札から 伏せた カードも 交換に なるよ</small>')
      + ef('5', '5：山札から 伏せて セット', '効果タイム', `${many('5', 1)}<em>5 を セット</em>`, '<b>5 と 手札 1枚を 捨てて</b>、山札から 1枚を <b>伏せて セット</b>。何が 出るかは オープンまで 分からない！<br><small>使った 後の 手札が 残りの ターンの 数より 少なく ならない とき だけ（最後の ターンは、手札が 1枚 あれば 使える）</small>')
      + ef('6', '6：相手の 手札を 見る', 'ターンの 始め', `${many('6', 2)}<em>手札に 6 が 2枚</em>`, '2枚を 相手に 見せて、<b>相手の 手札を 1枚 選んで 見る</b>よ。見てから セットする カードを 選べる。相手の 手札が もう 見た カード だけの ときは 使えないよ')
      + ef('7', '7：3枚 交換・4枚で 強さ 逆転', 'セットの 前', `${many('7', 3)}<em>手札に 7 が 3枚（4枚）</em>`, '<b>【3枚】</b>3枚を 山札に 戻して、新しく <b>3枚 引く</b>よ<br><b>【4枚】</b>4枚 見せて 1枚 捨てると、<b>その 対戦が 終わる まで 強さが 逆</b>（7＞6＞…＞1）<br><small>【3枚】と【4枚】は 1ターンに どちらか 1つ。手札に あれば 使える（7 を セットしなくて いい）</small>')
      + '<div class="hord"><b>効果の 順番</b><ol><li><i>1</i>ターンの 始め：<b>6</b> → 神様馬・幻の馬</li><li><i>2</i>セットの 前：<b>7・3</b>・決戦宝石</li><li><i>3</i>効果タイム：<b>5 → 4</b></li><li><i>4</i>オープンの 後：<b>1・2</b></li></ol></div>'
      + '<ul class="hnote"><li>手札の 数は、6・7・3 は <b>セットする 前</b>、5 は <b>セットした あと</b>の 手札で 数えるよ</li><li>最後の ターンに 神様馬・幻の馬で 勝った ときは、次の ターンが ない ので 効果は ないよ</li><li>効果は 1つ 終わってから 次の 効果を 聞くよ（前の 効果で 変わった 手札で 決められる。例：7 で 引いた 後の 手札で セットする カードを 選ぶ・5 で 捨てる カードを 選ぶ）</li><li>効果を 使うと、ボードの 真ん中に <b>誰が・どの 効果を・何を するか</b>の 札が 出るよ（タップすると すぐ 次へ）</li></ul>'
      
      + sec('gem', '5', '決戦宝石')
      + '<div class="hwhere"><div class="ok"><b>⚔️ 決戦調査</b><span>いつも 使える！<br>1つの 調査（連勝が 続く 間）で 5つを 1回ずつ</span></div>'
      + '<div class="ok"><b>🤝 友達バトル</b><span>部屋を 作る 人が「<b>決戦宝石 あり</b>」に した とき。2人とも 1試合で 5つを 1回ずつ（おたがいの 宝石が 見える）</span></div>'
      + '<div class="no"><b>コンピュータとの 対戦</b><span>使えないよ</span></div></div>'
      + `<p class="hsub">手札の 下の <b>ケース</b>に 宝石が 並ぶよ。タップ →「使う」で、<b>トークンの カード</b>が 手札に 1枚 来るよ</p>${gemsCase}`
      + `<div class="hgms">${R.GEMS.map(gemRow).join('')}</div>`
      + `<ul class="hnote"><li>使えるのは <b>手札が ${R.GEM_HAND}枚 以下</b>・<b>セットの 前</b>・<b>1ターンに 1つ</b></li>`
      + '<li>トークンは <b>その ターン だけ</b>（使わないと ターンの 終わりに 消えるよ）。セットすると その カードと 同じ 強さ（神様馬トークンと 神様馬は かぶり）</li>'
      + '<li>「○頭分」は 手札の 効果の 数え方：1トークンで 1 の 逆転勝利・3トークン ＋ 3 で 3 の 交換・7トークンで 7 の 効果（見せて 捨てて、山札から 3枚 引く）・7トークン ＋ 7 で 4枚 公開。セット・捨てる ときは 1枚</li>'
      + '<li>決戦調査の 敵は 宝石を 使わないよ（あなたが 使った ことも 敵には わからない）</li></ul>'
      
      + sec('etc', '6', 'そのほか')
      + '<details class="hdt"><summary>見た カード・見られた カード</summary><ul><li>効果で 見た 相手の カードは、相手の 手札に ある 間 表で 見えるよ</li><li>相手に 見られた 自分の カードには 目の 印が 付くよ</li><li>セットした カードは <b>裏</b>（4 の 効果で 見せる か、オープン するまで）。相手の 手札は いつも <b>本当の 手札</b>の まま 見えるよ（見た カードを 相手が セットしたら、その カードは 相手の 手札から 消える）</li></ul></details>'
      + '<details class="hdt"><summary>捨て札</summary><ul><li>ボードの「<b>捨て札</b>」を タップすると、捨て札を 見られるよ</li><li><b>終わった ターンの 捨て札</b>（2人が 出した カード）と、<b>効果で 捨てた カード</b>に 分けて 出るよ</li></ul></details>'
      + `<details class="hdt"><summary>ご褒美・調査隊切符</summary><ul><li>コンピュータに 勝つと <b>バトルコイン</b>（下の「バトルコイン」）</li><li>コンピュータに ${TK_BONUS.map(t => `<b>${t[0]}連勝 ごとに 調査隊切符 ${t[1]}枚</b>`).join('・')}（${TK_BONUS.reduce((a, t) => a * t[0], 1)}連勝 など、両方の ときは 両方。調査隊切符は ${QT.max}枚 まで）</li><li>負けると 連勝は 0 に 戻るよ。同点は そのまま。対戦の 途中で やめた・アプリを 閉じた ときも 負けに なるよ</li></ul></details>`
      + `<details class="hdt"><summary>バトルコイン</summary><ul><li><b>コンピュータに 勝つと ${COIN.win}枚</b> もらえるよ。連勝すると ボーナス：${COIN.bonus.map(t => `<b>${t[0]}連勝 ごとに ＋${t[1]}枚</b>`).join('・')}（${COIN.bonus.reduce((a, t) => a * t[0], 1)}連勝 など、両方の ときは 両方）</li>`
      + `<li><b>毎日の ログインボーナス</b>でも <b>${COIN.day}枚</b>（<b>7日目は ＋${COIN.day7}枚</b>）もらえるよ。<b>買う ことは できない</b>よ</li>`
      + '<li>友達と 対戦する 部屋を 作る とき、<b>参加コイン</b>と <b>勝者の 獲得コイン</b>（参加コインの 2倍 まで）を 決められるよ</li><li>部屋に 入る 人は、同じ 数の 参加コインを 持って いないと 入れないよ</li>'
      + '<li>2人とも 初めに 参加コインを 出す。<b>勝った 人は、テンゲルから 獲得コインを プレゼントで もらえる</b>。同点は 参加コインが 戻る</li><li><b>途中で やめると、参加コインは 戻らない</b>（つながりが 切れた ときは 戻るよ）</li><li>相手が 途中で やめた とき：あなたが カードを 3回 出した 後 なら 獲得コインを もらえる。その 前なら 参加コインが 戻るよ</li></ul></details>'
      + `<details class="hdt"><summary>デザインカスタム</summary><ul><li>メニューの「<b>デザインカスタム</b>」で、カードの <b>表</b>・<b>裏</b>と <b>プレイボード</b>の デザインを 変えられるよ</li>`
      + `<li><b>カードの 表</b>は <b>カードパック</b>で 集めるよ：1パック <b>バトルコイン ${PACK.cost}枚</b>・<b>${PACK.size}枚</b>入り（ノーマル ${PACK.size - 1}枚 ＋ くじの 1枚）</li>`
      + `<li>くじの 1枚：<b>レア 2パックに 1枚</b>・<b>超レア 5パックに 1枚</b>（どちらも 神様馬・幻の馬を 含む）・<b>神様馬／幻の馬の レア 10パックに 1枚</b>・<b>神様馬／幻の馬の 超レア 23パックに 1枚</b>（どれも 平均。詳しい 確率は カードパックの「出る 確率」）</li>`
      + '<li>新しい カードは 持って いる カードに 入るよ（同じ カードが 出ても、数は 増えないよ）。開けた パックは「パックの 記録」で もう 1回 見られるよ</li>'
      + `<li>カードの 裏 <b>${BACK_COST}枚</b>・プレイボード <b>${BOARD_COST}枚</b>は バトルコインで 1つずつ 解放できるよ。いつもの デザインは 初めから 使えるよ</li>`
      + '<li>コンピュータと 対戦する ときは、コンピュータの カード（裏・表）も あなたが 選んだ デザインに なるよ</li><li>友達と 対戦する ときは、<b>あなたの カードは あなたの デザイン</b>・<b>友達の カードは 友達が 選んだ デザイン</b>で 出るよ（山札は あなたの 裏）</li><li>プレイボードは、あなたの 画面に 出るよ（友達と 対戦する ときも、あなたの 画面は あなたが 選んだ ボード）</li></ul></details>'
      + `<details class="hdt"><summary>⚔️ 決戦調査</summary><ul><li>メニューの「<b>決戦調査</b>」：<b>エリア 1〜${QN}</b> の 敵と 戦う クエストだよ。マップの エリアを タップ →「決戦調査に 行く」</li>`
      + '<li>フィールドで 敵が 出たら、タップで カードバトル。<b>いつもの ルール</b>で 戦うよ（上の 敵HP ゲージが、勝つ たびに 減る）</li>'
      + `<li>敵ごとに 決まった <b>連勝</b>で 討伐！ バトルコインが もらえるよ：${QUEST.map(q => `Lv${q.lv} ${q.w}連勝 <b>${q.c}枚</b>`).join('・')}</li>`
      + '<li>討伐すると <b>次の エリアが 開く</b>よ。負けたら その エリアを <b>1戦目から やり直し</b>。同点は <b>同じ 戦を やり直し</b>（HP は そのまま）</li>'
      + '<li>強い 敵は、決まった 戦で <b>手札に 必ず 強い カード</b>を 持って いるよ（その 戦の 始めに 知らせるよ）</li>'
      + '<li>討伐した エリアにも <b>もう 一度 調査に 行ける</b>よ。<b>討伐の バトルコインは 毎月 1回目 だけ</b>（2回目からは なし）</li>'
      + '<li>もらえるのは 討伐の バトルコインと、<b>決戦調査ミッション</b>（決戦宝石を 残して 連続勝利）の バトルコイン。いつもの 勝ち負け・連勝（調査隊切符の ボーナス）・いつもの ミッションには 数えないよ</li>'
      + '<li>戦の 途中で やめる・アプリを 閉じると 調査 失敗。<b>毎月 1日に リセット</b>（討伐した エリアも 最初から）</li>'
      + `<li>${TKI}<b>調査隊切符</b>：エリアに <b>挑戦する とき 1枚</b>（1戦目の はじめ）。<b>連勝中は 使わない</b>（「第○戦へ」・同点の やり直し）。負けて「もう 一度 挑戦」する とき・次の エリアに 行く とき（例：レベル3 → レベル4）は また 1枚。<b>${QTM()}分で 1枚</b> たまって、<b>${QT.max}枚 まで</b>。0枚の ときは 挑戦 できないよ（マップの 上の ゲージで 枚数と 次の 1枚 までの 時間が わかるよ）</li></ul></details>`
      + `<details class="hdt"><summary>ミッション</summary><ul><li>メニューの「<b>ミッション</b>」：<b>コンピュータに 連続勝利</b>・<b>友達バトルで 連続勝利</b>・<b>決戦調査</b>（決戦宝石を 残して 連続勝利）で バトルコインが もらえるよ</li>`
      + `<li>コンピュータ：${MS.cpu.map(t => `${t[0]}連勝 <b>${t[1]}枚</b>`).join('・')}</li><li>友達バトル：${MS.fr.map(t => `${t[0]}連勝 <b>${t[1]}枚</b>`).join('・')}</li>`
      + `<li>決戦調査（1つの 調査で 数える・宝石を ○個 以上 残せば 達成）：${QMS.map(t => `宝石 ${t[0]}個 残し ${t[1].map(w => `${w[0]}連勝 <b>${w[1]}枚</b>`).join('・')}`).join('／')}</li>`
      + '<li>達成した ときに、その場で もらえるよ（受け取りは いらない）。<b>毎月 1日に リセット</b>（達成も 連勝も 0 に 戻る）</li>'
      + '<li>負けると その 連勝は 0 に 戻るよ（途中で やめた・対戦の 途中で アプリを 閉じた ときも 同じ）。同点は そのまま。友達が 途中で 部屋を 出た・つながりが 切れた ときは 数えないよ</li><li>コンピュータ・友達バトル・決戦調査は 別に 数えるよ（決戦調査の 勝ち負けは いつもの ミッションに 数えない）</li></ul></details>'
      + '<details class="hdt"><summary>音（設定）</summary><ul><li>ボードの 右下の <b>歯車</b>（メニューでは「設定」）を 押すと、<b>BGM</b>・<b>効果音</b>を オン／オフ できるよ</li></ul></details>'
      + '<details class="hdt"><summary>友達と 対戦（部屋）</summary><ul><li>1人が「部屋を 作る」→ 出て きた <b>部屋番号（4桁）</b>を 友達に 教える</li><li>友達は「部屋に 入る」で その 番号を 入れる</li><li><b>近くに いる 友達</b>と、iPhone 同士で 直接 つながるよ（インターネットは 使わない）。2人とも Wi‑Fi か Bluetooth を オンに してね</li><li>初めて 使う とき「ローカルネットワーク」の 確認が 出たら「許可」を 押してね</li>'
      + `<li>⏱ 友達バトルは、カードを セットする までの 時間が <b>${Math.round(SET_LIMIT / 1000)}秒</b>（名前の よこに 自分と 友達の のこりが 出るよ）。すぎたら 手札から <b>自動で 1枚 セット</b>（タップして 開いて いた カード・なければ ランダム）。相手の 4 の 効果で <b>交換する カードを 選ぶ ときも ${Math.round(SET_LIMIT / 1000)}秒</b>。カードの 動きや 効果の 札が 出て いる 間は 時計が 止まるよ。<b>自動で 出した カードの 効果は 使わない</b>よ。ほかの「効果を 使う？」には 時間の 決まりは ないよ</li>`
      + '<li>2人とも 同じ 版の アプリで 遊んでね（版が ちがうと「アプリの 版が ちがう」と 出るよ）</li></ul></details>'
      + '<p class="hend">カードの 絵を タップすると 大きく 見られるよ</p>'
      + '</div>';
    show('help');
  }

  
  
  
  
  let dzTab = 'p', dzAt = 0;
  const DZ_GUARD = 450;
  const testOn = () => !!(window.__TEST && window.CBTest);      
  const dzLabel = k => NAMES[k] || k + ' の カード';
  const dzFind = id => FACES.find(f => f.id === id) || BACKS.find(b => b.id === id) || null;
  const dzOwn = d => !d || (d.k ? st.faces : st.backs).indexOf(d.id) >= 0;      
  const rrChip = d => (d && d.k ? `<i class="rr k-${d.r}" aria-hidden="true">${RARS[d.r]}</i>` : '');      
  const dzUsed = (kind, id) => (kind ? st.face[kind] || '' : st.back) === (id || '');
  const dzWhat = kind => (kind ? dzLabel(kind) + 'の 表' : 'カードの 裏');
  
  function dzGet(kind, id) {
    if (kind && DZ_KINDS.indexOf(kind) < 0) return undefined;
    if (!id) return null;
    const d = dzFind(id); return d && (d.k || null) === (kind || null) ? d : undefined;
  }
  function dzTile(kind, d) {
    const id = d ? d.id : '', used = dzUsed(kind, id), own = dzOwn(d);
    const img = d ? d.s : kind ? 'cb_s' + kind + '.webp' : 'cb_sb.webp';
    const em = used ? '使って いる' : own ? '持って いる' : d.k ? 'パックで 出る' : `${COINI}${d.cost}枚`;
    const lab = (d ? d.name + (d.k ? '・' + RAR[d.r] : '') : 'いつもの') + '・' + em.replace(/<[^>]+>/g, '');
    return `<button type="button" class="dzt${used ? ' on' : ''}${own ? '' : ' lk'}${d && d.k ? ' r-' + d.r : ''}" data-cb="dzi" data-id="${id}" data-ck="${kind || ''}" aria-label="${esc(lab)}"><img src="${img}" alt="" draggable="false">${rrChip(d)}<span>${esc(d ? d.name : 'いつもの')}</span><em>${em}</em></button>`;
  }
  function showDz(tab) {
    const same = !tab || tab === dzTab, b0 = $('.bd', scr.dz), y = same && b0 && screen === 'dz' ? b0.scrollTop : 0;
    if (tab) dzTab = tab;
    closeMod();
    const body = dzTab === 'p'
      ? pkTab()
      : dzTab === 'd'
      ? `<h4>プレイボード<small>1つ ${COINI}${BOARD_COST}枚</small></h4><div class="tiles d">${bdTile(null)}${BOARDS.map(bdTile).join('')}</div>`
        + '<p class="dzn">選んだ プレイボードは、あなたの 画面の 対戦で 出るよ。友達と 対戦する ときも、あなたの 画面は あなたの ボード（友達の 画面は 友達が 選んだ ボード）</p>'
      : dzTab === 'b'
      ? `<h4>カードの 裏<small>1つ ${COINI}${BACK_COST}枚</small></h4><div class="tiles b">${dzTile(null, null)}${BACKS.map(d => dzTile(null, d)).join('')}</div>`
        + '<p class="dzn">選んだ 裏は、あなたの 画面の 山札・あなたの 伏せた カードに 出るよ。コンピュータの 手札も この 裏。友達と 対戦する ときは、友達の カードは 友達が 選んだ 裏に なるよ</p>'
      : DZ_KINDS.map(k => { const fs = FACES.filter(f => f.k === k); return `<h4>${esc(dzLabel(k))}<small>持って いる ${fs.filter(f => dzOwn(f)).length}／${fs.length}</small></h4><div class="tiles">${dzTile(k, null)}${fs.map(f => dzTile(k, f)).join('')}</div>`; }).join('')
        + '<p class="dzn">表の デザインは「カードパック」で 集めるよ（N＝ノーマル・R＝レア・SR＝超レア）。選んだ デザインは、あなたの カードに 出るよ（手札・めくった とき・捨て札）。コンピュータの カードも この デザイン。友達と 対戦する ときは、友達の カードは 友達が 選んだ デザインに なるよ</p>';
    scr.dz.innerHTML = '<div class="hd"><button type="button" class="cbb dk sm" data-cb="dzx">← 戻る</button><b>デザインカスタム</b></div>'
      + `<p class="cbcoinl">${COINI}<span>バトルコイン <b>${st.coin}</b>枚</span></p>`
      + '<div class="tabs" role="tablist">' + [['p', 'カードパック'], ['f', '表'], ['b', '裏'], ['d', 'ボード']].map(([t, l]) => `<button type="button" role="tab" data-cb="dztab" data-t="${t}" class="${dzTab === t ? 'on' : ''}" aria-selected="${dzTab === t}">${l}</button>`).join('') + '</div>'
      + `<div class="bd">${body}${testOn() ? window.CBTest.html() : ''}</div>`;
    show('dz');
    const b1 = $('.bd', scr.dz); if (b1) b1.scrollTop = y;
  }
  
  function dzItem(kind, id) {
    const d = dzGet(kind, id); if (d === undefined) return;
    const used = dzUsed(kind, id), own = dzOwn(d), big = d ? d.c : kind ? 'cb_c' + kind + '.webp' : 'cb_cb.webp';
    let btns;
    if (used) btns = '<button type="button" class="cbb" disabled>使って いるよ</button>';
    else if (own) btns = `<button type="button" class="cbb" data-cb="dzuse" data-id="${id || ''}" data-ck="${kind || ''}">この デザインを 使う</button>`;
    else if (d.k) btns = `<p class="cbneed pk">カードパックで 出るよ（${esc(GROUP[pkGroupOf(d)])}）</p>${dzTab === 'p' ? '' : '<button type="button" class="cbb" data-cb="dztab" data-t="p">カードパックへ</button>'}`;      
    else if (st.coin >= d.cost) btns = `<button type="button" class="cbb" data-cb="dzopen" data-id="${d.id}" data-ck="${kind || ''}">${COINI}バトルコイン ${d.cost}枚で 解放</button>`;
    else btns = `<button type="button" class="cbb" disabled>${COINI}バトルコイン ${d.cost}枚で 解放</button><p class="cbneed">あと ${d.cost - st.coin}枚 足りないよ<br>（コンピュータに 勝つ・毎日の ログインボーナスで もらえるよ）</p>`;
    modal(`<h3 class="gold">${esc(d ? d.name : 'いつもの')}<small>${esc(dzWhat(kind))}${d && d.k ? '・' + RAR[d.r] : ''}</small></h3><div class="big"><img src="${big}" alt="${esc(dzWhat(kind))}"></div>`
      + `<div class="col">${btns}<button type="button" class="cbb dk" data-cb="dzback">戻る</button></div>`, 'cbdzm');
  }
  
  function dzAsk(kind, id) {
    const d = dzGet(kind, id); if (!d || d.k || dzOwn(d) || st.coin < d.cost) return;
    dzAt = performance.now();
    modal(`<h3 class="gold">解放する？</h3><div class="big sm"><img src="${d.s}" alt=""></div><p>『${esc(d.name)}』（${esc(dzWhat(kind))}）を 解放するよ</p>`
      + `<p class="cbstkv">${COINI}<b>${st.coin}</b>枚<i>→</i>残り <b>${st.coin - d.cost}</b>枚</p>`
      + `<div class="rowb"><button type="button" class="cbb dk" data-cb="dzback">やめる</button><button type="button" class="cbb" data-cb="dzgo" data-id="${d.id}" data-ck="${kind || ''}">解放する</button></div>`, 'cbdzm');
  }
  function dzGo(kind, id) {
    const d = dzGet(kind, id); if (!d || d.k || dzOwn(d) || st.coin < d.cost) return;
    st.coin -= d.cost; (d.k ? st.faces : st.backs).push(d.id);
    if (d.k) st.face[d.k] = d.id; else st.back = d.id;      
    save(); se('magic', 0.8);
    showDz(); toast(`『${d.name}』を 解放したよ！\n${dzWhat(kind)}が この デザインに なったよ`, 3);
  }
  function dzUse(kind, id) {
    const d = dzGet(kind, id); if (d === undefined || !dzOwn(d)) return;
    if (kind) { if (d) st.face[kind] = d.id; else delete st.face[kind]; } else st.back = d ? d.id : '';
    save(); se('tap', 0.7);
    if (screen === 'pk') { closeMod(); return toast(`${dzWhat(kind)}を『${d ? d.name : 'いつもの'}』に したよ`, 2.4); }      
    showDz(); toast(`${dzWhat(kind)}を『${d ? d.name : 'いつもの'}』に したよ`, 2.4);
  }
  
  const bdGet = id => (id ? BOARDS.find(d => d.id === id) : null);      
  const bdOwn = d => !d || st.boards.indexOf(d.id) >= 0;
  const bdUsed = id => (st.board || '') === (id || '');
  function bdTile(d) {
    const id = d ? d.id : '', used = bdUsed(id), own = bdOwn(d);
    const em = used ? '使って いる' : own ? '持って いる' : `${COINI}${d.cost}枚`;
    return `<button type="button" class="dzt${used ? ' on' : ''}${own ? '' : ' lk'}" data-cb="bdi" data-id="${id}" aria-label="${esc((d ? d.name : 'いつもの') + '・' + em.replace(/<[^>]+>/g, ''))}"><img src="${d ? d.s : 'cb_board.webp'}" alt="" draggable="false"><span>${esc(d ? d.name : 'いつもの')}</span><em>${em}</em></button>`;
  }
  function bdItem(id) {
    const d = bdGet(id); if (d === undefined) return;
    const used = bdUsed(id), own = bdOwn(d);
    let btns;
    if (used) btns = '<button type="button" class="cbb" disabled>使って いるよ</button>';
    else if (own) btns = `<button type="button" class="cbb" data-cb="bduse" data-id="${id || ''}">この ボードを 使う</button>`;
    else if (st.coin >= d.cost) btns = `<button type="button" class="cbb" data-cb="bdopen" data-id="${d.id}">${COINI}バトルコイン ${d.cost}枚で 解放</button>`;
    else btns = `<button type="button" class="cbb" disabled>${COINI}バトルコイン ${d.cost}枚で 解放</button><p class="cbneed">あと ${d.cost - st.coin}枚 足りないよ<br>（コンピュータに 勝つ・毎日の ログインボーナスで もらえるよ）</p>`;
    modal(`<h3 class="gold">${esc(d ? d.name : 'いつもの')}<small>プレイボード</small></h3><div class="big bd"><img src="${d ? d.b : 'cb_board.webp'}" alt="プレイボード"></div>`
      + `<div class="col">${btns}<button type="button" class="cbb dk" data-cb="dzback">戻る</button></div>`, 'cbdzm');
  }
  function bdAsk(id) {
    const d = bdGet(id); if (!d || bdOwn(d) || st.coin < d.cost) return;
    dzAt = performance.now();
    modal(`<h3 class="gold">解放する？</h3><div class="big bd sm"><img src="${d.s}" alt=""></div><p>『${esc(d.name)}』（プレイボード）を 解放するよ</p>`
      + `<p class="cbstkv">${COINI}<b>${st.coin}</b>枚<i>→</i>残り <b>${st.coin - d.cost}</b>枚</p>`
      + `<div class="rowb"><button type="button" class="cbb dk" data-cb="dzback">やめる</button><button type="button" class="cbb" data-cb="bdgo" data-id="${d.id}">解放する</button></div>`, 'cbdzm');
  }
  function bdGo(id) {
    const d = bdGet(id); if (!d || bdOwn(d) || st.coin < d.cost) return;
    st.coin -= d.cost; st.boards.push(d.id); st.board = d.id;      
    save(); se('magic', 0.8); boardImg();
    showDz(); toast(`『${d.name}』を 解放したよ！\nプレイボードが この デザインに なったよ`, 3);
  }
  function bdUse(id) {
    const d = bdGet(id); if (d === undefined || !bdOwn(d)) return;
    st.board = d ? d.id : ''; save(); se('tap', 0.7); boardImg();
    showDz(); toast(`プレイボードを『${d ? d.name : 'いつもの'}』に したよ`, 2.4);
  }
  
  function boardImg() {
    if (!ov) return; const im = $('.cbboard>img'), d = boardNow(), f = d ? d.b : 'cb_board.webp';
    if (im && im.getAttribute('src') !== f) im.setAttribute('src', f);
    const bd = $('.cbboard'); if (bd) { bd.classList.toggle('cust', !!d); bd.classList.toggle('dl', !!(d && d.dl)); }      
  }
  
  
  
  
  
  
  
  
  
  
  let pk = null, pkForce = '', pkReq = null, pkTold = false;
  function randInt(n) {
    if (typeof CBApp._randInt === 'function') return Math.max(0, Math.min(n - 1, Math.floor(CBApp._randInt(n))));
    try { const lim = Math.floor(4294967296 / n) * n, a = new Uint32Array(1); for (let i = 0; i < 64; i++) { crypto.getRandomValues(a); if (a[0] < lim) return a[0] % n; } } catch (e) {   }
    return Math.min(n - 1, Math.floor(Math.random() * n));
  }
  const isTop = f => f.k === 'k' || f.k === 'm';
  
  const pkPool = g => FACES.filter(f => (g === 'n' ? f.r === 'n' : f.r === (g === 'gsr' || g === 'sr' ? 'sr' : 'r') && isTop(f) === (g[0] === 'g')));
  const pkGroupOf = f => (f.r === 'n' ? 'n' : (isTop(f) ? 'g' : '') + f.r);
  const pkGroup = k => { const t = PACK.ranges.find(x => k >= x[1] && k <= x[2]); return t ? t[0] : 'n'; };      
  const pkP = g => { const t = PACK.ranges.find(x => x[0] === g); return t ? (t[2] - t[1] + 1) / PACK.lot : 0; };
  function pkDraw() {
    const N = pkPool('n'), cards = [];
    for (let i = 0; i < PACK.size - 1; i++) cards.push(N[randInt(N.length)].id);
    let k = randInt(PACK.lot);
    if (pkForce) { const t = PACK.ranges.find(x => x[0] === pkForce); if (t) k = t[1] + randInt(t[2] - t[1] + 1); pkForce = ''; }      
    const g = pkGroup(k), pool = pkPool(g);
    cards.push(pool[randInt(pool.length)].id);
    return { cards: cards, g: g, k: k };
  }
  const faceOf = id => FACES.find(f => f.id === id) || null;
  const pkUnseen = () => (st && st.pkh ? st.pkh.filter(h => !h.v) : []);
  
  const packArt = cls => `<div class="pkart${cls ? ' ' + cls : ''}"${cls === 'big' ? ' data-cb="pkrip" role="button" aria-label="パックを 開ける"' : ' aria-hidden="true"'}>${cls === 'big' ? '<img class="bd" src="cb_pack.webp" alt="" draggable="false"><img class="tp" src="cb_pack.webp" alt="" draggable="false">' : '<img src="cb_pack.webp" alt="" draggable="false">'}</div>`;
  const pkNeed = () => `<p class="cbneed">あと ${PACK.cost - st.coin}枚 足りないよ<br>（コンピュータに 勝つ・毎日の ログインボーナスで もらえるよ）</p>`;
  const pct = p => (Math.round(p * 10000) / 100).toFixed(2).replace(/\.?0+$/, '') + '%';
  const when = t => { const d = new Date(t || 0); return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`; };
  
  function pkTab() {
    const ok = st.coin >= PACK.cost, un = pkUnseen(), own = FACES.filter(f => dzOwn(f)).length;
    const grp = g => { const fs = pkPool(g); return `<h4>${esc(GROUP[g])}<small>${g === 'n' ? `${PACK.size - 1}枚は ここから・くじ ${pct(pkP(g))}` : `くじ ${pct(pkP(g))}`}・持って いる ${fs.filter(f => dzOwn(f)).length}／${fs.length}</small></h4><div class="tiles">${fs.map(f => dzTile(f.k, f)).join('')}</div>`; };
    const hist = st.pkh.slice(-10).reverse().map(h => `<button type="button" class="pkhi${h.v ? '' : ' un'}" data-cb="pkhis" data-id="${esc(h.id)}" aria-label="${when(h.t)}・${esc(GROUP[h.g])}"><span class="w">${when(h.t)}</span><span class="cs">${h.cards.map((id, i) => { const f = faceOf(id); return `<img src="${f.s}" alt="" class="${i === PACK.size - 1 && f.r !== 'n' ? 'r-' + f.r : ''}">`; }).join('')}</span><i class="rr k-${faceOf(h.cards[PACK.size - 1]).r}">${RARS[faceOf(h.cards[PACK.size - 1]).r]}</i></button>`).join('');
    return (un.length ? `<div class="pkun"><span>🎴 まだ 見おわって いない パックが ${un.length}つ あるよ</span><button type="button" class="cbb sm" data-cb="pkhis" data-id="${esc(un[0].id)}">見る</button></div>` : '')
      + `<div class="pkbox">${packArt('')}<p class="pkc0">1パック ${COINI}<b>${PACK.cost}</b>枚・<b>${PACK.size}枚</b>入り</p><p class="pkc1">ノーマル ${PACK.size - 1}枚 ＋ くじの 1枚</p>`
      + `<button type="button" class="cbb" data-cb="pkask"${ok ? '' : ' disabled'}>${COINI}${PACK.cost}枚で パックを 開ける</button>${ok ? '' : pkNeed()}`
      + '<button type="button" class="cbb dk sm" data-cb="pkodds">出る 確率</button></div>'
      + `<h3 class="pkh3">この パックで 出る カード<small>${FACES.length}種・持って いる ${own}／${FACES.length}</small></h3>`
      + ['n', 'r', 'gr', 'sr', 'gsr'].map(grp).join('')
      + (hist ? `<h3 class="pkh3">パックの 記録<small>開けた パック ${st.packs}つ・最後の ${Math.min(10, st.pkh.length)}つ</small></h3><div class="pkhl">${hist}</div>` : '')
      + '<p class="dzn">新しい カードは 持って いる カードに 入るよ（同じ カードが 出ても 数は 増えないよ）。出た カードは「表」の タブで 使えるよ。記録を タップすると、その パックを もう 1回 見られるよ</p>';
  }
  
  function pkOdds() {
    const nN = pkPool('n').length;
    const row = g => { const n = pkPool(g).length, t = PACK.ranges.find(x => x[0] === g); return `<tr><th>${esc(GROUP[g])}<small>${n}種・番号 ${t[1]}〜${t[2]}（${t[2] - t[1] + 1}個）</small></th><td>${pct(pkP(g))}<small>1種 ${pct(pkP(g) / n)}</small></td></tr>`; };
    modal(`<h3 class="gold">出る 確率</h3><p>1パック ${PACK.size}枚：<b>ノーマル ${PACK.size - 1}枚</b>（${nN}種から 同じ 確率・1種 ${pct(1 / nN)}。同じ カードが 重なる ことも あるよ）＋ <b>くじの 1枚</b></p>`
      + `<table class="pkod"><caption>くじの 1枚（0〜${PACK.lot - 1} の 番号を 等しく 1つ）</caption>${PACK.ranges.map(t => row(t[0])).join('')}</table>`
      + '<p class="sm">レア 全部 50%（2パックに 1枚）・超レア 全部 20%（5パックに 1枚）。同じ グループの 中では、どの カードも 同じ 確率。どれも 平均なので、23パック 開けても 必ず 出る わけでは ないよ</p>'
      + '<div class="col"><button type="button" class="cbb dk" data-cb="dzback">閉じる</button></div>', 'cbdzm cbodm');
  }
  
  function pkAsk() {
    if (st.coin < PACK.cost) return;
    dzAt = performance.now(); pkReq = 'p' + Date.now().toString(36) + '-' + randInt(1679616).toString(36);
    modal(`<h3 class="gold">パックを 開ける？</h3>${packArt('sm')}<p>カードパック（${PACK.size}枚）を 1つ 開けるよ</p>`
      + `<p class="cbstkv">${COINI}<b>${st.coin}</b>枚<i>→</i>残り <b>${st.coin - PACK.cost}</b>枚</p>`
      + `<div class="rowb"><button type="button" class="cbb dk" data-cb="dzback">やめる</button><button type="button" class="cbb" data-cb="pkgo" data-rq="${pkReq}">開ける</button></div>`, 'cbdzm');
  }
  
  function pkGo(rq) {
    const old = st.pkh.find(h => h.id === rq); if (old) return pkShow(old, !old.v);      
    if (!rq || rq !== pkReq || st.coin < PACK.cost) return;
    pkReq = null;
    const before = JSON.stringify(st), d = pkDraw(), own = st.faces.slice(), nw = [];
    d.cards.forEach(id => { const f = own.indexOf(id) < 0; nw.push(f); if (f) own.push(id); });
    const h = { id: rq, t: Date.now(), g: d.g, k: d.k, cards: d.cards, nw: nw, v: false };
    st.coin -= PACK.cost; st.faces = own; st.packs += 1; st.pkh.push(h); if (st.pkh.length > PKH_MAX) st.pkh = st.pkh.slice(-PKH_MAX);
    if (!saveOk()) { st = JSON.parse(before); closeMod(); return toast('保存が できなかったので、パックは 開けなかったよ\n（コインは 減って いないよ）', 3.4); }
    se('tap'); pkShow(h, true);
  }
  
  function pkShow(h, anim) {
    closeMod();
    const back = pic(null, false), last = PACK.size - 1, cs = h.cards.map((id, i) => ({ f: faceOf(id), isNew: !!h.nw[i] }));
    pk = { h: h, cards: cs, g: h.g, st: anim ? 'pack' : 'done', up: cs.map(() => !anim), anim: !!anim, ready: false, at: performance.now() };      
    const card = (c, i) => `<button type="button" class="pkc g-${i === last ? h.g : 'n'} r-${c.f.r}${anim ? '' : ' got up'}" data-cb="pkflip" data-i="${i}" aria-label="${i + 1}枚目の カード"><span class="gl"></span><span class="bst"></span>`
      + `<span class="in"><img class="bk" src="${back}" alt="" draggable="false"><img class="fr" src="${c.f.s}" alt="" draggable="false"><span class="sh"></span></span>`
      + `<i class="rr k-${c.f.r}">${RARS[c.f.r]}</i>${c.isNew ? '<b class="nw">NEW</b>' : '<b class="hv">持って いる</b>'}</button>`;
    scr.pk.classList.toggle('out', !anim); scr.pk.style.setProperty('--k', String(Math.max(0.01, SPEED)));
    scr.pk.innerHTML = `<div class="pkhd"><b class="gold">カードパック</b>${anim ? '' : `<small>${when(h.t)} に 開けた パック</small>`}</div><p class="pkmsg" aria-live="polite"></p>`
      + `<div class="pkst"><div class="pkgrid"><div class="row">${cs.slice(0, 3).map(card).join('')}</div><div class="row">${cs.slice(3).map((c, j) => card(c, j + 3)).join('')}</div></div>${anim ? packArt('big') : ''}</div>`
      + '<div class="pkft"></div>';
    show('pk'); pkPaint();
  }
  const pkHit = c => (c.f.r === 'n' ? '' : `${c.f.r === 'sr' ? '🌟' : '✨'} ${isTop(c.f) ? nameOf(c.f.k) + 'の ' : ''}${RAR[c.f.r]}！『${c.f.name}』`);
  
  function pkPaint(say) {
    if (!pk || !scr.pk) return;
    const m = $('.pkmsg', scr.pk), f = $('.pkft', scr.pk), ok = st.coin >= PACK.cost, nNew = pk.cards.filter(c => c.isNew).length, lc = pk.cards[PACK.size - 1];
    if (m) m.textContent = say || (pk.st === 'pack' ? 'タップで パックを 開けよう' : pk.st === 'rip' ? '' : pk.st === 'deal' ? 'パックから カードが 出て くるよ…' : pk.st === 'out' ? (pk.ready ? '最後の 1枚（くじ）… タップで めくろう！' : 'ノーマル 4枚…')
      : (pkHit(lc) ? pkHit(lc) + '\n' : '') + (nNew ? `NEW ${nNew}枚！（持って いる カード ${FACES.filter(x => dzOwn(x)).length}／${FACES.length}）` : '全部 持って いる カードだったよ'));
    if (!f) return;
    f.innerHTML = pk.st === 'pack' ? '<button type="button" class="cbb" data-cb="pkrip">パックを 開ける</button>'
      : pk.st === 'rip' || pk.st === 'deal' ? '<button type="button" class="cbb dk" disabled>パックを 開けて いるよ…</button>'
      : pk.st === 'out' ? (pk.ready ? '<button type="button" class="cbb" data-cb="pklast">最後の 1枚を めくる</button>' : '<button type="button" class="cbb dk" disabled>めくって いるよ…</button>')
      : `<div class="rowb"><button type="button" class="cbb dk" data-cb="pkx">閉じる</button><button type="button" class="cbb" data-cb="pkmore"${ok ? '' : ' disabled'}>もう 1パック<small>${COINI}${PACK.cost}枚</small></button></div>${ok ? '' : pkNeed()}`;
  }
  
  async function pkRip() {
    if (!pk || pk.st !== 'pack' || performance.now() - pk.at < (typeof CBApp._guard === 'number' ? CBApp._guard : DZ_GUARD)) return;      
    const me = pk; pk.st = 'rip'; pkPaint(); se('deal', 0.9);
    const art = $('.pkart.big', scr.pk), cs = [...scr.pk.querySelectorAll('.pkc')];
    if (art) art.classList.add('rip');
    await T(reduce() ? 60 : 380); if (pk !== me) return;
    scr.pk.classList.add('out'); pk.st = 'deal'; pkPaint();
    for (let i = 0; i < cs.length; i++) {
      pkOut(cs[i], art, i); se('deal', 0.5);
      await T(reduce() ? 120 : 300); if (pk !== me) return;
    }
    await T(reduce() ? 80 : 640); if (pk !== me) return;
    if (art) art.classList.add('gone');      
    await T(reduce() ? 120 : 520); if (pk !== me) return;
    pk.st = 'out'; pkPaint();
    for (let i = 0; i < PACK.size - 1; i++) { await T(i ? 330 : 200); if (pk !== me) return; pkTurn(i); }
    await T(560); if (pk !== me) return;
    pk.ready = true; pkPaint();
  }
  
  function pkOut(c, art, i) {
    c.classList.add('got');
    if (reduce() || !art || !c.animate) return;      
    const a = art.getBoundingClientRect(), r = c.getBoundingClientRect();
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2, ax = a.left + a.width / 2, cut = a.top + a.height * 0.045;      
    const dx = ax - cx, dy0 = cut + r.height * 0.56 - cy, dy1 = cut - r.height * 0.22 - cy, tilt = [-4, 3, -3, 4, 0][i % 5];
    try {
      c.animate([
        { transform: `translate(${dx}px,${dy0}px) scale(.94)`, easing: 'cubic-bezier(.25,.8,.35,1)' },
        { transform: `translate(${dx}px,${dy1}px) scale(.98) rotate(${tilt}deg)`, offset: 0.42, easing: 'cubic-bezier(.45,0,.25,1)' },
        { transform: 'none' }
      ], { duration: Math.max(1, 640 * SPEED) });
      art.animate([{ transform: 'none' }, { transform: 'translateY(3px) scale(.99,1.01)', offset: 0.35 }, { transform: 'none' }], { duration: Math.max(1, 240 * SPEED) });      
    } catch (e) {   }
  }
  
  function pkTurn(i) {
    const c = pk.cards[i], el = scr.pk.querySelector(`.pkc[data-i="${i}"]`); if (!c || !el || pk.up[i]) return;
    pk.up[i] = true; el.classList.add('up'); se('flip', 0.8);
  }
  async function pkLast() {
    if (!pk || pk.st !== 'out' || !pk.ready) return;
    const me = pk, i = PACK.size - 1, c = pk.cards[i], el = scr.pk.querySelector(`.pkc[data-i="${i}"]`);
    pk.ready = false; pkTurn(i); pkPaint(' ');
    if (c.f.r !== 'n') { await T(reduce() ? 80 : 420); if (pk !== me) return; if (el) el.classList.add('rv'); se(c.f.r === 'sr' ? 'fanfare' : 'magic', 0.85); pkPaint(pkHit(c)); }
    await T(c.f.r !== 'n' ? 900 : 420); if (pk !== me) return;
    pk.st = 'done'; pkSeen(pk.h); pkPaint();
  }
  
  function pkSeen(h) { const x = st.pkh.find(y => y.id === h.id); if (x && !x.v) { x.v = true; save(); } }
  
  function pkTap(i) {
    if (!pk) return;
    if (pk.st === 'out' && i === PACK.size - 1 && pk.ready) return pkLast();
    if (pk.up[i] && pk.st === 'done') return pkBig(i);
  }
  function pkBig(i) {
    const c = pk && pk.cards[i]; if (!c) return;
    const d = c.f, used = dzUsed(d.k, d.id);
    modal(`<h3 class="gold">${esc(d.name)}<small>${esc(dzWhat(d.k))}・${RAR[d.r]}</small></h3><div class="big"><img src="${d.c}" alt="${esc(dzWhat(d.k))}"></div>`
      + `<div class="col">${used ? '<button type="button" class="cbb" disabled>使って いるよ</button>' : `<button type="button" class="cbb" data-cb="dzuse" data-id="${d.id}" data-ck="${d.k}">この デザインを 使う</button>`}<button type="button" class="cbb dk" data-cb="dzback">戻る</button></div>`, 'cbdzm');
  }
  
  const dzApi = {
    add: k => { addCoin(k); save(); showDz(); toast(`🧪 バトルコイン ＋${k}枚（今 ${st.coin}枚）`, 2); },
    set: k => { st.coin = Math.max(0, Math.min(COIN.max, Math.floor(+k || 0))); save(); showDz(); toast(`🧪 バトルコイン ${st.coin}枚に したよ`, 2); },
    reset: () => { st.backs = []; st.faces = []; st.back = ''; st.face = {}; st.boards = []; st.board = ''; st.pkh = []; st.packs = 0; save(); boardImg(); showDz(); toast('🧪 解放と 集めた カード・パックの 記録を 全部 元に 戻したよ', 2.4); },
    
    pk: g => { if (!PACK.ranges.some(t => t[0] === g) || g === 'n') return; pkForce = g; toast(`🧪 次の パックの くじは「${GROUP[g]}」`, 2.4); }
  };

  
  
  let msTab = 'cpu';
  const MS_TABS = ['cpu', 'fr', 'q'];      
  function showMs(tab) {
    if (tab) msTab = MS_TABS.indexOf(tab) >= 0 ? tab : 'cpu';
    closeMod(); msRoll();
    const d = nowD(), mm = /^(\d{4})-(\d{2})$/.exec(st.ms.m), mY = mm ? +mm[1] : d.getFullYear(), mM = mm ? +mm[2] : d.getMonth() + 1;      
    const nx = new Date(mY, mM, 1), left = Math.max(1, Math.ceil((nx - d) / 86400000)), s = st.ms, kd = msTab, cur = kd === 'q' ? 0 : s[kd];
    const nt = kd === 'q' ? null : MS[kd].find(t => s.got[kd].indexOf(t[0]) < 0);      
    const rows = kd === 'q' ? '' : MS[kd].map(t => {
      const done = s.got[kd].indexOf(t[0]) >= 0, nxt = !!nt && nt[0] === t[0];
      return `<div class="msr${done ? ' done' : nxt ? ' next' : ''}" data-n="${t[0]}"><b class="n">${t[0]}連勝</b><span class="c">${COINI}${t[1]}枚</span><em>${done ? '✓ 達成' : nxt ? `あと ${Math.max(1, t[0] - cur)}勝` : ''}</em></div>`;
    }).join('');
    scr.ms.innerHTML = '<div class="hd"><button type="button" class="cbb dk sm" data-cb="msx">← 戻る</button><b>ミッション</b></div>'
      + `<p class="cbcoinl">${COINI}<span>バトルコイン <b>${st.coin}</b>枚</span></p>`
      + `<p class="msm">${mM}月の ミッション<small>${nx.getMonth() + 1}月1日に リセット（あと ${left}日）</small></p>`
      + `<div class="tabs" role="tablist">${MS_TABS.map(k => `<button type="button" role="tab" data-cb="mstab" data-t="${k}" class="${kd === k ? 'on' : ''}" aria-selected="${kd === k}">${MS_WHO[k]}<small>${k === 'q' ? msQ().length : s.got[k].length}／${k === 'q' ? QMS_K.length : MS[k].length} 達成</small></button>`).join('')}</div>`
      + (kd === 'q' ? qmsBody() : `<div class="bd"><h4>${kd === 'cpu' ? 'コンピュータに 連続勝利' : '友達バトルで 連続勝利'}</h4>`
      + `<p class="cur"><span>今</span><b>${cur}</b><span>連勝</span><small>${nt ? `次は ${nt[0]}連勝で ${COINI}${nt[1]}枚（あと ${Math.max(1, nt[0] - cur)}勝）` : '今月の ミッションは 全部 達成！ 🎉'}</small></p>`
      + `<div class="msl">${rows}</div>`
      + '<ul class="note"><li>達成すると、その場で バトルコインが もらえるよ（受け取りは いらない）</li>'
      + '<li>負けると 連勝は 0 に 戻るよ（途中で やめた・対戦の 途中で アプリを 閉じた ときも）。同点は そのまま</li>'
      + (kd === 'fr' ? '<li>友達が 途中で 部屋を 出た・つながりが 切れた ときは 数えないよ</li>' : '')
      + '<li>コンピュータと 友達バトルの 連勝は 別に 数えるよ。決戦調査の 勝ち負けは 数えないよ（「決戦調査」の タブの ミッション）</li><li><b>毎月 1日に リセット</b>（達成も 連勝も 0 に 戻るよ）</li></ul>'
      + `${testOn() && window.CBTest.msHtml ? window.CBTest.msHtml() : ''}</div>`);
    show('ms');
  }
  
  function qmsBody() {
    const got = msQ();
    const grp = QMS.map(t => `<h5 class="qmsg">決戦宝石を <b>${t[0]}個</b> 残して 連続勝利<span aria-hidden="true">${R.GEMS.map((x, i) => `<img class="${i < t[0] ? '' : 'u'}" src="${gemPic(x)}" alt="">`).join('')}</span></h5><div class="msl">`
      + t[1].map(w => { const k = `g${t[0]}w${w[0]}`, done = got.indexOf(k) >= 0; return `<div class="msr${done ? ' done' : ''}" data-k="${k}"><b class="n">${w[0]}連勝</b><span class="c">${COINI}${w[1]}枚</span><em>${done ? '✓ 達成' : ''}</em></div>`; }).join('') + '</div>').join('');
    return '<div class="bd"><h4>決戦調査で 連続勝利</h4><p class="qmsi">1つの 調査（エリアに 挑戦して 連勝が 続く 間）で、<b>決戦宝石を 残して</b> 連続勝利 すると もらえるよ</p>' + grp
      + '<ul class="note"><li>決戦宝石を 多く 残すほど たくさん もらえるよ。5個 残して 3連勝 → 3個・4個・5個 残しの 3連勝が ぜんぶ 達成（30＋50＋90枚）</li>'
      + '<li>達成すると、その場で バトルコインが もらえるよ（受け取りは いらない）</li>'
      + '<li>負けると 1戦目から（決戦宝石も 5つに 戻るよ）。同点は そのまま。途中で やめる・アプリを 閉じると その 調査は ここまで</li>'
      + '<li>討伐した エリアに もう 一度 調査に 行っても 数えるよ（討伐の バトルコインは 毎月 1回目 だけ）</li>'
      + '<li>決戦調査の 勝ち負けは、いつもの ミッション（コンピュータ・友達バトル）には 数えないよ</li><li><b>毎月 1日に リセット</b>（どの ミッションも 1か月に 1回）</li></ul>'
      + `${testOn() && window.CBTest.msHtml ? window.CBTest.msHtml() : ''}</div>`;
  }
  
  const msApi = {
    win: kd => { const g = msWin(kd), c = g.reduce((a, x) => a + x.c, 0); addCoin(c); save(); showMs(kd); toast(g.length ? `🧪 ${MS_WHO[kd]}で 1勝 → ミッション達成！\n${g.map(x => `${x.n}連勝 ＋${x.c}枚`).join('・')}（今 ${st.coin}枚）` : `🧪 ${MS_WHO[kd]}で 1勝（今 ${st.ms[kd]}連勝）`, 2.6); },
    lose: kd => { msRoll(); st.ms[kd] = 0; save(); showMs(kd); toast(`🧪 ${MS_WHO[kd]}で 負け（連勝 0）`, 2); },
    next: () => { st.ms.m = '2000-01'; msRoll(); showMs(); toast('🧪 月が 変わった ことに したよ（ミッションを リセット）', 2.4); }
  };

  
  let room = null;                                     
  function roomNumber() { let n = 0; try { const a = new Uint16Array(1); crypto.getRandomValues(a); n = a[0]; } catch (e) { n = Math.floor(Math.random() * 65536); } return String(1000 + n % 9000); }
  
  
  function showRoom(mode, keep) {
    const old = keep && room && room.stake ? room.stake : null, oldG = keep && room && room.gm ? room.gm : null;      
    closeMod(); roomStop();
    room = { mode: mode, code: mode === 'host' ? (CBApp._room || roomNumber()) : '', nr: null, tm: 0, step: '', stake: old || { e: 0, w: 0 }, gm: oldG };
    if (mode === 'host' && !old) { room.step = 'stake'; paintRoom(); show('room'); return; }      
    paintRoom(); show('room');
    if (mode === 'host') roomGo();
  }
  
  function stakeSet(kind, v) {
    const r = room; if (!r || r.mode !== 'host' || r.step !== 'stake') return;
    const k = r.stake, maxE = Math.min(st.coin, CBNet.STAKE_MAX);
    if (kind === 'e') { const e = Math.max(0, Math.min(maxE, Math.floor(+v || 0))); k.e = e; k.w = e * 2; }
    else k.w = Math.max(k.e, Math.min(k.e * 2, k.w + (v > 0 ? 1 : -1)));
    se('tap', 0.6); paintRoom();
  }
  function paintRoom() {
    const r = room, e = scr.room; if (!r) return;
    const digits = c => [0, 1, 2, 3].map(i => `<span class="${i === c.length ? 'cur' : ''}">${c.charAt(i)}</span>`).join('');
    let h = '<button type="button" class="cbb dk sm cbx" data-cb="roomx">← やめる</button>';
    if (r.mode === 'host' && r.step === 'stake') {      
      const k = r.stake, maxE = Math.min(st.coin, CBNet.STAKE_MAX), chips = STAKE_CHIPS.filter(q => q <= maxE), gm = st.rg, has = st.coin > 0;
      
      const gemBlk = '<div class="blk"><b>決戦宝石</b><small>あり に すると、2人とも 5つの 宝石を 使えるよ（1試合で 1つ 1回ずつ・おたがいに 見える）</small>'
        + `<div class="cbseg" role="group" aria-label="決戦宝石"><button type="button" class="${gm.on ? '' : 'on'}" data-cb="rgon" data-v="0" aria-pressed="${!gm.on}">なし</button><button type="button" class="${gm.on ? 'on' : ''}" data-cb="rgon" data-v="1" aria-pressed="${gm.on}">あり</button></div>`
        + (gm.on ? `<div class="gl5" aria-hidden="true">${R.GEMS.map(g => `<img src="${gemPic(g)}" alt="">`).join('')}</div>` : '') + '</div>';
      h += `<h2 class="gold">部屋を 作る</h2><p>${has ? '参加コインと、勝った 人が もらう コインを 決めてね' : '部屋の 決まりを 決めてね'}</p>`
        + (has ? `<p class="cbcoinl">${COINI}<span>持って いる バトルコイン <b>${st.coin}</b>枚</span></p>` : '')
        + '<div class="cbstk">' + (!has ? '' : '<div class="blk"><b>参加コイン</b><small>2人とも 初めに 出す 数。同じ 数を 持って いる 人 だけ 入れるよ</small>'
        + `<div class="chips" role="group" aria-label="参加コイン">${chips.map(q => `<button type="button" class="${q === k.e ? 'on' : ''}" data-cb="stke" data-n="${q}" aria-pressed="${q === k.e}">${q}</button>`).join('')}</div></div>`
        + '<div class="blk"><b>勝者の 獲得コイン</b><small>勝った 人への プレゼント。参加コインの 2倍 まで</small>'
        + `<div class="cbstp"><button type="button" data-cb="stkw" data-d="-1"${k.w <= k.e ? ' disabled' : ''} aria-label="1枚 減らす">−</button><b aria-live="polite">${k.w}<small>枚</small></b><button type="button" data-cb="stkw" data-d="1"${k.w >= k.e * 2 ? ' disabled' : ''} aria-label="1枚 増やす">＋</button></div></div>`)
        + gemBlk + '</div>'
        + (has ? '<p class="hint">同点の ときは 参加コインが 戻るよ。<br>途中で やめると、参加コインは 戻らないよ</p>' : '')
        + `<button type="button" class="cbb" data-cb="stkgo">${k.e > 0 ? `参加 ${k.e}枚・勝者 ${k.w}枚で 部屋を 作る` : has ? 'コインなしで 部屋を 作る' : '部屋を 作る'}</button>`;
      e.innerHTML = h; return;
    }
    if (r.mode === 'host') {
      h += '<h2 class="gold">部屋を 作ったよ</h2><p>この 番号を 友達に 教えてね</p>' + `<div class="num" aria-label="部屋番号 ${r.code}">${r.code}</div>`
        + (r.stake && r.stake.e > 0 ? `<p class="cbstkl">${COINI}参加コイン <b>${r.stake.e}枚</b>・勝者 <b>${r.stake.w}枚</b></p>` : '')
        + (r.gm && r.gm.on ? '<p class="cbstkl">決戦宝石 あり（2人とも 5つ）</p>' : '')      
        + `<p class="cbtlh">⏱ カードを セットする までは ${Math.round(SET_LIMIT / 1000)}秒（すぎたら 自動で 1枚）</p>`      
        + `<div class="stt">${r.step === 'found' ? '<i class="cbspin"></i>友達が 来たよ！ つないで いるよ…' : r.step === 'fail' ? '部屋を 作れなかったよ' : '<i class="cbspin"></i>友達を 待って いるよ…'}</div>`
        + '<p class="hint">友達は「部屋に 入る」で この 番号を 入れるよ。<br>近くに いる 友達と 直接 つながるよ（2人とも Wi‑Fi か Bluetooth を オンに）</p>';
      if (r.step === 'fail') h += '<button type="button" class="cbb" data-cb="roomre">もう一度 作る</button>';
    } else {
      const busy = r.step === 'wait' || r.step === 'found';
      h += '<h2 class="gold">部屋に 入る</h2><p>友達の 部屋番号（4桁）を 入れてね</p>' + `<div class="num in" aria-label="部屋番号 ${r.code}">${digits(r.code)}</div>`
        + `<p class="cbtlh">⏱ カードを セットする までは ${Math.round(SET_LIMIT / 1000)}秒（すぎたら 自動で 1枚）</p>`      
        + `<div class="stt">${r.step === 'found' ? '<i class="cbspin"></i>部屋を 見つけたよ！ つないで いるよ…' : r.step === 'wait' ? '<i class="cbspin"></i>部屋を 探して いるよ…' : r.step === 'fail' ? '部屋に 入れなかったよ' : ''}</div>`;
      if (busy) h += '<p class="hint">見つからない ときは、番号と、2人とも Wi‑Fi か Bluetooth が オンか 確かめてね</p>';
      else h += '<div class="cbkeys">' + ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'del', '0', 'go'].map(k => (k === 'del' ? '<button type="button" data-key="del" aria-label="1字 消す">⌫</button>' : k === 'go' ? `<button type="button" data-key="go" aria-label="入る"${r.code.length === 4 ? '' : ' disabled'}>入る</button>` : `<button type="button" data-key="${k}">${k}</button>`)).join('') + '</div>';
    }
    if (r.slow) h += '<p class="hint">つながらない とき：iPhone の「設定」→「テンゲル」→「ローカルネットワーク」を オンに してね</p>';
    e.innerHTML = h;
  }
  function roomStop() { if (room) { clearTimeout(room.tm); if (room.nr) { try { room.nr.cancel(); } catch (e) {   } } } room = null; }
  function roomGo() {
    const r = room; if (!r) return;
    r.step = 'wait'; r.slow = false; paintRoom();
    clearTimeout(r.tm); r.tm = setTimeout(() => { if (room === r) { r.slow = true; paintRoom(); } }, 20000);
    const nr = (CBApp._link || CBNet.nativeRoom)(); r.nr = nr;
    nr.open(r.mode, r.code, step => { if (room !== r) return; r.step = step; paintRoom(); }).then(link => {
      if (room !== r) { try { link.close(); } catch (e) {   } return; }
      clearTimeout(r.tm); room = null; se('join');
      const dz = { b: st.back, f: Object.assign({}, st.face) };      
      startMatch(r.mode === 'host' ? CBNet.host(link, CBApp._rng || undefined, CBApp._opt || undefined, r.stake, dz, r.gm || null) : CBNet.guest(link, dz));      
    }).catch(e => {
      if (room !== r) return;
      clearTimeout(r.tm); r.step = 'fail'; r.nr = null; paintRoom();
      if (e && e.message === 'none') toast('この 端末では 部屋を 使えないよ', 3);
    });
  }
  function roomKey(k) {
    const r = room; if (!r || r.mode !== 'join' || r.step === 'wait' || r.step === 'found') return;
    if (k === 'del') r.code = r.code.slice(0, -1);
    else if (k === 'go') { if (r.code.length === 4) roomGo(); return; }
    else if (r.code.length < 4) r.code += k;
    r.step = ''; se('tap', 0.6); paintRoom();
  }

  
  let match = null, V = null, queue = [], pumping = false, mode = { k: 'idle' }, busy = false, lock = false, ended = false, gameNo = 0, dealHold = false;      
  
  let fin = false, ends = [];
  
  let mySets = 0;
  function onEv(u) {
    if (qRun && u && u.view && u.view.my && u.view.my.gem) qRun.gu = u.view.my.gem.used.slice();      
    (u && u.ev || []).forEach(x => {
      if (!x) return;
      if (x.e === 'deal') { fin = false; mySets = 0; }
      else if (x.e === 'end' && !fin) { fin = true; ends.push(settle(x.res)); }
    });
  }
  const WHO = () => (match && match.kind === 'cpu' ? (qRun ? QUEST[qRun.lv - 1].s : 'コンピュータ') : '友達');      
  function startMatch(m) {
    GEN += 1; match = m; V = null; queue = []; pumping = false; mode = { k: 'idle' }; busy = false; lock = false; ended = false; dealHold = false; fin = false; ends = [];
    FL.clear();      
    tlStart();       
    m.onUpdate = u => { if (match === m) onEv(u); queue.push(u); pump(); };
    m.onState = s => onNet(s);
    show('game'); closeMod();
    scr.game.classList.toggle('qm', !!qRun);           
    if (qRun) qHP(QUEST[qRun.lv - 1].w - qRun.won, false);
    $('.cbopp .cbwho b').textContent = WHO();
    paintEmpty(); layout();
    m.start();
    if (m.kind === 'guest') say('相手を 待って いるよ…');
    else if (m.kind === 'host') say(m.stake && m.stake.e > 0 ? `${WHO()}が 参加するか 選んで いるよ…` : '相手を 待って いるよ…');      
  }
  
  function joinAsk() {
    const m = match; if (!m || m.kind !== 'guest' || !m.stake) return;
    const k = m.stake, gm = m.gm && m.gm.on ? m.gm : null;
    if (k.e <= 0 && !gm) { m.join(); return; }
    const need = k.e - st.coin;
    modal(`<h3 class="gold">この 部屋の 決まり</h3>` + (k.e > 0 ? `<div class="cbstkv">${COINI}参加コイン <b>${k.e}枚</b><i>→</i>勝者 <b>${k.w}枚</b></div>`
      + `<p>2人とも 初めに ${k.e}枚 出すよ。勝った 人は ${k.w}枚 もらえる。<br>同点は 戻る・途中で やめると 戻らないよ</p>` : '')
      + (gm ? `<div class="cbjg"><b>決戦宝石 あり</b><small>2人とも 5つの 宝石を 使えるよ（1試合で 1つ 1回ずつ・おたがいに 見える）</small><div class="gl5" aria-hidden="true">${R.GEMS.map(g => `<img src="${gemPic(g)}" alt="">`).join('')}</div></div>` : '')
      + (k.e > 0 ? `<p class="cbhave">${COINI}あなたの バトルコイン <b>${st.coin}</b>枚${need > 0 ? `<br><strong>あと ${need}枚 足りない ので、この 部屋には 入れないよ</strong>` : ''}</p>` : '')
      + (need > 0 ? '<div class="col"><button type="button" class="cbb" data-cb="joinno">メニューへ</button></div>'
        : '<div class="rowb"><button type="button" class="cbb dk" data-cb="joinno">やめる</button><button type="button" class="cbb" data-cb="joinyes">参加する</button></div>'), 'cbjoin');
  }
  function onNet(s) {
    if (!match) return;
    if (s === 'again') { if (ended) { const e = $('.cbend .gift2'); if (e) e.textContent = WHO() + 'が「もう 1回」を 押したよ'; } return; }
    if (s === 'ready') { opPre(); return; }            
    if (s === 'joined') return;
    if (s === 'stake') return joinAsk();
    const playing = !ended && !fin && !!V;      
    const why = s === 'bye' ? WHO() + 'が 部屋を 出たよ' : s === 'ver' ? 'アプリの 版が 違うので 対戦できないよ。\n2人とも 新しい 版に してね' : s === 'bad' ? '相手から 正しくない 知らせが 届いた ので、\n対戦を 終わったよ' : 'つながりが 切れたよ';      
    
    
    
    
    let coinMsg = '';
    if (st.stake) {
      const k = st.stake; st.stake = null;
      if (s === 'bye' && mySets >= CBNet.MIN_SETS) { addCoin(k.w); coinMsg = `${WHO()}が 途中で やめた ので、バトルコイン ${k.w}枚を もらったよ`; }
      else { addCoin(k.e); coinMsg = s === 'bye' ? `${WHO()}が 序盤で やめた ので、参加コイン ${k.e}枚は 戻ったよ` : `参加コイン ${k.e}枚は 戻ったよ`; }
      save();
    }
    if (st.ms.live) { st.ms.live = ''; save(); }      
    match = null; queue = [];
    modal(`<h3 class="gold">${s === 'ver' ? '対戦できないよ' : '対戦は ここまで'}</h3><p>${esc(why).replace(/\n/g, '<br>')}${playing ? '<br>（この 対戦は 勝ち負けに 数えないよ）' : ''}${coinMsg ? `<br>${COINI}${esc(coinMsg)}` : ''}</p><div class="col"><button type="button" class="cbb" data-cb="menu">メニューへ</button></div>`);
  }
  function opPre() { [null, 'k', 'm', '1', '2', '3', '4', '5', '6', '7'].forEach(k => [false, true].forEach(big => { const im = new Image(); im.src = pic(k, big, 'op'); })); }
  async function pump() {
    if (pumping) return; pumping = true;
    const g = GEN;                                     
    try {
      while (queue.length && match && g === GEN) {
        const u = queue.shift();
        await play(u.ev, u.view);
        if (g !== GEN) return;                         
        dealHold = false;
        if (!match) break;
        V = u.view; lock = false; keepMode(); render();
      }
    } finally { if (g === GEN) pumping = false; }
    if (g === GEN && match && !queue.length) match.idle();
  }
  
  
  
  
  
  const EFFQ = { x7: '7', x3: '3', u5: '5', u4: '4' };      
  const EFFTXT = { 6: '6 を 2枚 見せて、相手の 手札を 1枚 見られるよ', 5: '5 と 手札 1枚を 捨てて、山札から 1枚 セットできるよ', 7: '7 を 3枚 山札に 戻して、新しく 3枚 引けるよ',
    3: '3 を 3枚 見せて、その 1枚と 相手の 手札の 1枚（裏の カードから 選ぶ）を 交換できるよ', 4: '4 を 見せて、相手に カードを 交換させるよ' };
  const EFFBAR = { 3: '3 を 3枚 見せて、手札を 1枚 交換できるよ' };
  const effQ = q => `${q} の 効果を 使う？`;      
  const effBtn = q => `${q} の 効果を 使う`;
  const effK = q => q;      
  
  const SIX = { head: 'ターンの 始め！', q: '6 の 効果を 使う？', text: '6 を 2枚 見せて、相手の 手札を 1枚 見られるよ（セットの 前：見てから セットする カードを 選べる）', bar: '6 を 2枚 見せて、相手の 手札を 1枚 見られるよ', btn: '6 の 効果を 使う' };
  
  const X7 = { head: '7 が 4枚！', q: '7 を 4枚 見せて 逆転する？', text: 'セットの 前に 使えるよ（セットは いらない）。4枚 見せて 1枚 捨てると、この 対戦が 終わる まで 数字の 強さが 逆に なるよ', ord: '7＞6＞5＞4＞3＞2＞1', btn: '4枚 見せて 逆転', bar: '7 を 4枚 見せて 逆転' };      
  
  const PRE = [{ c: 'x7r', yes: 'x7yes', no: 'x7no' }, { c: 'x7', yes: 'p7yes', no: 'p7no' }, { c: 'x3', yes: 'p3yes', no: 'p3no' }];
  
  const toName = o => (NAMES[o] ? NAMES[o] + 'に' : o + ' に');
  const REVTXT = (k, o) => `手札の ${k} を 2枚 見せて、1枚 捨てると、${toName(o)} 勝てるよ`;
  const REVBAR = (k, o) => `手札の ${k} を 1枚 捨てて、${toName(o)} 勝てるよ`;
  
  const effSend = use => send({ t: 'eff', use: use });
  const effNow = v => !!(v && v.can.eff && mode.k === 'eff' && mode.n === v.can.eff.n);      
  
  function keepMode() {
    const v = V, has = u => v.my.hand.some(c => c.u === u);
    if (mode.k === 'eff') { if (!effNow(v)) mode = { k: 'idle' }; }      
    else if (mode.k === 'dropm') { if (v.pend && v.pend.mine && v.pend.type === 'm') mode.sel = mode.sel.filter(has); else mode = { k: 'idle' }; }
    else if (mode.k === 'u5') { if (!(v.pend && v.pend.mine && v.pend.type === 'u5')) mode = { k: 'idle' }; }
    else mode = { k: 'idle' };
  }
  const sortHand = h => { const rv = !!(V && V.rv); return h.slice().sort((a, b) => power(a.k, rv) - power(b.k, rv) || a.u - b.u); };      
  const cardBtn = (c, cls, extra, side) => `<button type="button" class="cbc ${cls || ''}${c.tok && c.k ? ' tok' : ''}" data-u="${c.u}" data-ck="${c.k ? esc(c.k) : ''}"${c.tok && c.k ? ` data-tok="${c.tok}"` : ''}${extra || ''} aria-label="${c.k ? esc(nameOf(picK(c))) + (c.tok > 1 ? `（${c.tok}頭分）` : '') + ' の カード' : '伏せた カード'}"><img src="${pic(picK(c), false, side)}" alt="" draggable="false">${c.seen ? '<i class="eye" aria-hidden="true"></i>' : ''}</button>`;      
  function pips(n, turns) { let h = ''; for (let i = 0; i < turns; i++) h += `<i class="${i < n ? 'on' : ''}"></i>`; return h; }
  const turnsOf = () => (V && V.turns) || R.TURNS;      
  function deckImg() { const im = $('.cbdeck img'), f = deckPic(); if (im && im.getAttribute('src') !== f) im.setAttribute('src', f); }      
  function paintEmpty() {
    $('.cbturn').innerHTML = ''; $('.cbohand').innerHTML = ''; $('.cbhand').innerHTML = ''; $('.cbact').innerHTML = ''; say('');
    deckImg(); boardImg(); $('.cbslot.op').innerHTML = ''; $('.cbslot.my').innerHTML = ''; $('.cbdeck .cbn').textContent = ''; $('.cbdis .cbn').textContent = '';
    ov.querySelectorAll('.cbpips').forEach(e => { e.innerHTML = pips(0, turnsOf()); });
    $('.cbglow').classList.remove('on');
    const g = $('.cbgem'), o = $('.cbopp .ogem'); if (g) g.hidden = true; if (o) o.hidden = true;      
  }
  function layout() {
    if (screen !== 'game') return;
    const hd = $('.cbhand'), n = Math.max(1, hd.children.length), r = hd.getBoundingClientRect();
    if (r.width > 0) {
      const W = r.width - 12, H = r.height - 30, LAP = 0.4;       
      let w = Math.max(50, Math.min(100, Math.floor(H * 2 / 3)));
      let lap = n > 1 ? Math.max(0, (n * w - W) / (n - 1)) : 0;
      if (lap > w * LAP) { w = Math.floor(W / (n - (n - 1) * LAP)); lap = w * LAP; }
      hd.style.setProperty('--cw', w + 'px'); hd.style.setProperty('--ov', (lap > 0 ? -lap : Math.min(6, (W - n * w) / Math.max(1, n - 1))).toFixed(1) + 'px');
    }
    const oh = $('.cbohand'), q = oh.getBoundingClientRect();
    if (q.height > 0) oh.style.setProperty('--ow', Math.max(30, Math.min(58, Math.floor((q.height - 4) * 2 / 3))) + 'px');
  }
  
  
  function say(t) {
    const m = $('.cbmsg'); if (!m) return;
    m.style.fontSize = ''; m.textContent = t || '';
    if (!t) return;
    let fs = 13.5;
    while (m.scrollHeight > m.clientHeight + 0.5 && fs > 10.5) { fs -= 0.5; m.style.fontSize = fs + 'px'; }
  }
  function statusText(v) {
    if (v.phase === 'end') return '';
    const w = WHO();
    if (v.pend) {
      const me = v.pend.mine;
      if (v.pend.type === 'swap') return me ? `${w}が 4 の 効果を 使ったよ！\nセットした カードと 交換する 手札を 選んでね` : `${w}が カードを 交換して いるよ…`;
      if (v.pend.type === 'u5' && me) return '交換で 5 を セットしたよ！ 5 の 効果を 使う？\n5 と 手札 1枚を 捨てて、山札から 1枚 セットできるよ';      
      if (v.pend.type === 'k') return me ? `${kmN('k', v.pend.tok)}で 勝った！ 効果を 使う？\n相手の 手札を 1枚 見られるよ` : `${w}が ${kmN('k', v.pend.tok)}の 効果を 使うか 選んで いるよ…`;
      if (v.pend.type === 'm') return me ? `${kmN('m', v.pend.tok)}で 勝った！ 効果を 使う？\n手札を 2枚 捨てて、山札から 2枚 引けるよ` : `${w}が ${kmN('m', v.pend.tok)}の 効果を 使うか 選んで いるよ…`;
      if (v.pend.type === 'rev') return me && v.my.set && v.op.set ? `逆転の チャンス！ ${v.my.set.k} の 効果を 使う？\n${REVBAR(v.my.set.k, v.op.set.k)}` : `${w}が 逆転勝利を 使うか 選んで いるよ…`;
    }
    if (v.phase === 'six') return v.can.six ? `${SIX.head} ${SIX.q}\n${SIX.bar}` : `${w}が 6 の 効果を 使うか 選んで いるよ…`;      
    if (v.phase === 'eff') return `${w}が 効果を 使うか 選んで いるよ…`;      
    if (v.can.set && preList(v).length) { const p = preAsk(v) || preList(v)[0]; return (v.op.set ? `${w}は もう セットしたよ。カードを 選んでね` : 'セットする カードを 選んでね（カードを タップ）') + '\n' + preLine(p.c); }      
    if (v.can.set && v.can.gem && v.can.gem.length) return (v.op.set ? `${w}は もう セットしたよ。カードを 選んでね` : 'セットする カードを 選んでね（カードを タップ）') + '\nセットの 前なら 決戦宝石を 使えるよ（下の ケース）';      
    if (v.can.set) return v.op.set ? `${w}は もう セットしたよ。セットする カードを 選んでね` : 'セットする カードを 選んでね（カードを タップ）';
    return `${w}が 選んで いるよ…`;
  }
  
  function paintDis(list) {
    const top = list.length ? list[list.length - 1] : null;
    $('.cbdis .pl').innerHTML = top ? `<img src="${pic(top.tok ? tokP(top.k) : top.k, false, top.mine === false ? 'op' : 'my')}" alt="" draggable="false">` : '';      
    $('.cbdis .cbn').textContent = String(list.length);
    $('.cbdis').setAttribute('aria-label', `捨て札を 見る（${list.length}枚）`);
  }
  const setTag = (s, mine) => { const t = s.open ? '' : s.up ? '4 の 効果' : !mine ? '' : s.blind ? '山札から' : '伏せて セット'; return t ? `<span class="tag">${t}</span>` : ''; };
  
  const MARK = k => (k === 'k' ? '神' : k === 'm' ? '幻' : String(k));
  const mySet = (s, tap) => {
    if (!s) return '';
    if (s.open || s.up || s.blind || !s.k) return cardBtn({ u: s.u, k: s.open || s.up ? s.k : null, tok: s.open || s.up ? s.tok : 0 }, '', tap ? ' data-cb="mset"' : '') + setTag(s, true);
    return `<button type="button" class="cbc dn${s.tok ? ' tok' : ''}" data-u="${s.u}" data-ck=""${tap ? ' data-cb="mset"' : ''} aria-label="あなたが 伏せて セットした カード（${esc(nameOf(picK(s)))}）"><img src="${pic(null)}" alt="" draggable="false"><i class="mk" aria-hidden="true">${esc(MARK(s.k))}</i></button>` + setTag(s, true);
  };
  function render() {
    const v = V; if (!v || screen !== 'game') return;
    if (v.can.eff && !effNow(v)) mode = { k: 'eff', q: EFFQ[v.can.eff.st], n: v.can.eff.n, step: 'ask' };      
    $('.cbturn').innerHTML = v.phase === 'end' ? '結果' : `ターン ${v.turn}<small>／${v.turns}</small>` + (st.stake ? `<small class="stk">${COINI}勝者 ${st.stake.w}枚</small>` : '') + (v.rv ? '<small class="rv">強さ 逆転中</small>' : '');      
    $('.cbpips[data-p=op]').innerHTML = pips(v.op.wins, v.turns); $('.cbpips[data-p=my]').innerHTML = pips(v.my.wins, v.turns);
    if (qRun) $('.cbopp .qt').textContent = `第${qRun.won + 1}戦・` + (v.phase === 'end' ? '結果' : `ターン ${v.turn}／${v.turns}`);      
    $('.cbohand').innerHTML = v.op.hand.map(c => cardBtn({ u: c.u, k: c.k, tok: c.tok }, c.k ? 'knw' : '', ' data-cb="ocard"', 'op')).join('');
    deckImg(); $('.cbdeck .cbn').textContent = String(v.deckN); paintDis(v.discard);
    const os = v.op.set, ms = v.my.set;
    $('.cbslot.op').innerHTML = os ? cardBtn({ u: os.u, k: os.k, tok: os.tok }, '', ' data-cb="oset"', 'op') + setTag(os, false) : '';
    $('.cbslot.my').innerHTML = mySet(ms, true);      
    $('.cbglow').classList.toggle('on', v.can.set || !!(v.pend && v.pend.mine && v.pend.type === 'swap'));
    if (modOn() && modEl.classList.contains('cbx3')) { if (v.can.x3 && v.can.x3p.length && mode.k === 'idle') pickModal('x3'); else closeMod(); }      
    const asking = dealHold ? false : askSync();       
    paintHand(); paintAct(asking); paintGem(v);
    say(dealHold ? '' : asking ? '効果を 使うか 選んでね' : (modeText() || statusText(v)));
    layout(); applyGlow();      
  }
  
  function paintGem(v) {
    const g = $('.cbgem'), o = $('.cbopp .ogem'), my = v && v.my.gem, op = v && v.op.gem;
    if (!g || !o) return;
    g.hidden = !my; o.hidden = !op;
    if (my) $('.gs', g).innerHTML = R.GEMS.map((k, i) => {
      if (my.list.indexOf(k) < 0) return '';
      const used = my.used.indexOf(k) >= 0, can = my.can.indexOf(k) >= 0, s = GEM_SLOT[i];
      return `<button type="button" class="g ${used ? 'used' : can ? 'can' : 'off'}" data-cb="gem" data-g="${k}" style="left:${s[0]}%;top:${s[1]}%;width:${s[2]}%;height:${s[3]}%" aria-label="${GEMS[k].n}（${used ? 'この 戦では もう 使った' : can ? '使える' : '今は 使えない'}）"><img src="${gemPic(k)}" alt="" draggable="false"></button>`;
    }).join('');
    if (op) { const left = op.list.filter(k => op.used.indexOf(k) < 0); o.setAttribute('aria-label', `${WHO()}の 決戦宝石：のこり ${left.length}つ（${left.map(k => GEMS[k].n).join('・') || 'なし'}）`); o.setAttribute('role', 'img');
      o.innerHTML = op.list.map(k => `<img class="${op.used.indexOf(k) >= 0 ? 'u' : ''}" src="${gemPic(k)}" alt="" data-g="${k}">`).join(''); }      
  }
  
  function gemAsk(g) {
    const v = V, my = v && v.my.gem; if (!my || !GEMS[g] || my.list.indexOf(g) < 0 || ended) return;
    se('tap', 0.6);
    const why = my.used.indexOf(g) >= 0 ? (qRun ? 'この 調査では もう 使ったよ（5つの 宝石は 1つの 調査で 1回ずつ）' : 'この 試合では もう 使ったよ') : my.now ? '決戦宝石は 1ターンに 1つ までだよ' : v.phase !== 'set' || !v.can.set ? 'セットする 前に 使えるよ'
      : v.my.hand.length > R.GEM_HAND ? `手札が ${R.GEM_HAND}枚 以下の ときに 使えるよ` : my.can.indexOf(g) < 0 ? '今は 使えないよ' : '';
    if (why || mode.k !== 'idle' || busy || lock) { toast(`${GEMS[g].n}\n${why || '今は 使えないよ'}`, 2.4); return; }
    modal(`<h3 class="gold">${esc(GEMS[g].n)}</h3><div class="cbgemq"><img class="gm" src="${gemPic(g)}" alt=""><i aria-hidden="true">▶</i><span class="cbc"><img src="${pic(tokP(g), true)}" alt="${esc(GEMS[g].t)}"></span></div>`
      + `<p><b>${esc(GEMS[g].t)}</b>${headOf(R.GEM_W[g])}が 手札に 1枚 来るよ<small>この ターン だけ（使わないと ターンの 終わりに 消えるよ）・この 宝石は ${qRun ? 'この 調査で 1回（連勝が 続く 間）' : 'この 試合で 1回'}</small></p>`
      + `<div class="rowb"><button type="button" class="cbb dk" data-cb="modx">使わない</button><button type="button" class="cbb" data-cb="gemgo" data-g="${g}">使う</button></div>`, 'cbgemm');
  }
  function modeText() {
    if (mode.k === 'eff') return mode.step === 'drop5' ? '5 と 一緒に 捨てる カードを 選んでね（カードを タップ）' : `効果タイム！ ${effQ(mode.q)}\n${effBar(mode.q)}`;
    if (mode.k === 'dropm') return `捨てる カードを 2枚 選んでね（${mode.sel.length}／2）`;
    if (mode.k === 'u5') return '5 と 一緒に 捨てる カードを 選んでね（カードを タップ）';      
    return '';
  }
  
  function paintHand(fresh, list) {
    const hd = $('.cbhand');
    hd.innerHTML = sortHand(list || V.my.hand).map(c => cardBtn(c, (mode.k === 'dropm' && mode.sel.indexOf(c.u) >= 0 ? 'sel ' : '') + (fresh && fresh.indexOf(c.u) >= 0 ? 'new' : ''), ' data-cb="card"')).join('');
    applyGlow();
  }
  
  
  
  
  
  
  
  
  
  
  const FL = new Map(), FL_MS = 1600;
  function glowPlan(v) {
    const P = { myT: new Set(), myS: new Set(), opT: new Set(), opS: new Set(), slot: { my: false, op: false } };
    if (!v || ended || v.phase === 'end' || screen !== 'game') return P;
    const hand = v.my.hand, pt = v.pend ? v.pend.type : '', mine = !!(v.pend && v.pend.mine);
    const all = s => hand.forEach(c => s.add(c.u)), kind = k => hand.forEach(c => { if (c.k === k) P.myS.add(c.u); });      
    const opNew = () => v.op.hand.forEach(c => { if (!c.k) P.opS.add(c.u); });      
    if (mode.k === 'eff') { P.slot.my = true; if (mode.step === 'drop5') all(P.myT); return P; }      
    if (mode.k === 'u5') { P.slot.my = true; all(P.myT); return P; }
    if (mode.k === 'dropm') { hand.forEach(c => { if (mode.sel.indexOf(c.u) < 0) P.myT.add(c.u); }); return P; }
    if (pt === 'swap') { P.slot.my = P.slot.op = true; if (mine) all(P.myT); return P; }      
    if (mine && pt === 'u5') { P.slot.my = true; return P; }
    if (mine && pt === 'rev' && v.my.set) { P.slot.my = true; kind(v.my.set.k); return P; }
    if (mine && pt === 'k') { opNew(); return P; }
    if (mine && pt === 'm') { all(P.myS); return P; }
    if (mode.k !== 'idle') return P;
    if (v.can.six) { kind('6'); opNew(); return P; }
    if (v.can.set) {
      const L = preList(v).map(p => p.c);
      if (L.indexOf('x7') >= 0 || L.indexOf('x7r') >= 0) kind('7');
      if (L.indexOf('x3') >= 0) { kind('3'); (v.can.x3p || []).forEach(u => P.opS.add(u)); }
    }
    return P;
  }
  function applyGlow() {
    if (!ov) return;
    const P = glowPlan(V), now = performance.now();
    const mark = (el, key, tg, src) => {
      el.classList.toggle('tg', !!tg); el.classList.toggle('src', !tg && !!src);
      const t = FL.get(key);
      if (t != null && now - t < FL_MS) {      
        if (el.dataset.flt !== String(t)) { el.classList.remove('fl'); void el.offsetWidth; el.style.setProperty('--fld', Math.round(t - now) + 'ms'); el.classList.add('fl'); el.dataset.flt = String(t); }
      } else { if (t != null) FL.delete(key); if (el.classList.contains('fl')) { el.classList.remove('fl'); el.style.removeProperty('--fld'); delete el.dataset.flt; } }
    };
    const hd = $('.cbhand'), oh = $('.cbohand');
    if (hd) hd.querySelectorAll('.cbc').forEach(el => { const u = +el.dataset.u; mark(el, 'my:' + u, P.myT.has(u), P.myS.has(u)); });
    if (oh) oh.querySelectorAll('.cbc').forEach(el => { const u = +el.dataset.u; mark(el, 'op:' + u, P.opT.has(u), P.opS.has(u)); });
    ['my', 'op'].forEach(sd => { const el = $('.cbslot.' + sd + ' .cbc'); if (el) mark(el, 'slot:' + sd, false, P.slot[sd]); });
  }
  
  function flash(...keys) {
    const t = performance.now();
    keys.forEach(k => { if (k) FL.set(k, t); });
    applyGlow(); later(applyGlow, FL_MS + 60);
  }
  
  
  
  
  
  
  
  
  
  
  
  const SET_LIMIT = 10000, TL_LOW = 3000;
  const TL = { my: null, op: null, t: 0, iv: 0, auto: [] };      
  const tlMax = () => (typeof CBApp._limit === 'number' ? CBApp._limit : SET_LIMIT);
  const tlRoom = () => !!(match && match.kind !== 'cpu' && !qRun && tlMax() > 0);
  function tlStart() { clearInterval(TL.iv); TL.my = TL.op = null; TL.auto = []; TL.t = performance.now(); TL.iv = tlRoom() ? setInterval(tlTick, 100) : 0; tlPaint(); }
  const tlSwap = v => !!(v.pend && v.pend.mine && v.pend.type === 'swap');      
  const tlOpSwap = v => !!(v.pend && !v.pend.mine && v.pend.type === 'swap');
  const tlSetAuto = v => !!(v.my.set && TL.auto.some(a => a.g === gameNo && a.t === v.turn && a.u === v.my.set.u));      
  const tlWasAuto = (t, k) => TL.auto.some(a => a.g === gameNo && a.t === t && k.indexOf(a.k) >= 0);      
  function tlTick() {
    if (!tlRoom()) { clearInterval(TL.iv); TL.iv = 0; TL.my = TL.op = null; tlPaint(); return; }
    const now = performance.now(), dt = Math.max(0, now - TL.t), v = V; TL.t = now;
    if (!v || ended || v.phase === 'end') { TL.my = TL.op = null; tlPaint(); return; }
    const run = !busy && !lock && !pumping && !queue.length && !dealHold, key = gameNo + ':' + v.turn, max = tlMax();
    const mk = v.can.set ? key : tlSwap(v) ? key + ':swap' : '', ok = (v.phase === 'set' && !v.op.set) ? key : tlOpSwap(v) ? key + ':swap' : '';
    if (mk) { if (!TL.my || TL.my.key !== mk) TL.my = { key: mk, left: max }; if (run) TL.my.left -= dt; }
    else TL.my = null;
    if (ok) { if (!TL.op || TL.op.key !== ok) TL.op = { key: ok, left: max }; if (run) TL.op.left -= dt; }
    else TL.op = null;
    tlPaint();
    if (TL.my && TL.my.left <= 0 && run && (TL.my.tries || 0) < 2) tlAuto();      
    else if (run && TL.auto.length) tlAutoNo(v);
  }
  function tlPaint() {
    if (!ov) return;
    const max = Math.max(1, tlMax());
    
    let mm = modEl ? modEl.querySelector('.cbtl[data-p=mym]') : null;
    if (TL.my && modEl && modOn()) { if (!mm) { mm = document.createElement('span'); mm.className = 'cbtl mt'; mm.dataset.p = 'mym'; mm.innerHTML = '<i></i><span class="n"></span>'; modEl.prepend(mm); } }
    else if (mm) { mm.remove(); mm = null; }
    ['my', 'op', 'mym'].forEach(sd => {
      const e = sd === 'mym' ? mm : ov.querySelector('.cbtl[data-p=' + sd + ']'), q = TL[sd === 'mym' ? 'my' : sd]; if (!e) return;
      if (!q) { if (!e.hidden) e.hidden = true; return; }
      const left = Math.max(0, q.left), n = Math.ceil(left / 1000), b = e.querySelector('.n');
      e.hidden = false; e.classList.toggle('lo', left <= TL_LOW);
      e.querySelector('i').style.setProperty('--p', (left / max).toFixed(3));
      if (b.textContent !== String(n)) { b.textContent = String(n); e.setAttribute('aria-label', (sd === 'op' ? WHO() : 'あなた') + 'の のこり ' + n + '秒'); }
    });
  }
  
  function tlAuto() {
    const v = V, sw = !!(v && tlSwap(v)); if (!v || !(v.can.set || sw) || busy || lock || !v.my.hand.length) return;
    let u = null;
    if (modOn()) { const b = modEl.querySelector(sw ? '[data-cb=swap][data-u]' : '[data-cb=set][data-u]'); if (b) u = +b.dataset.u; }      
    if (u == null || !v.my.hand.some(c => c.u === u)) u = v.my.hand[Math.min(v.my.hand.length - 1, Math.floor(Math.random() * v.my.hand.length))].u;
    const c = v.my.hand.find(x => x.u === u);
    if (TL.my) { TL.my.left = 0; TL.my.tries = (TL.my.tries || 0) + 1; } tlPaint();      
    mode = { k: 'idle' }; closeMod();
    se('tap', 0.6);
    TL.auto.push({ g: gameNo, t: v.turn, k: c.k, u: u });
    send(sw ? { t: 'swap', u: u } : { t: 'set', u: u }).then(ok => { if (ok) toast(sw ? `⏱ 時間切れ！\n${nameOf(picK(c))} と 自動で 交換したよ` : `⏱ 時間切れ！\n${nameOf(picK(c))} を 自動で セットしたよ`, 2.6); });
  }
  
  function tlAutoNo(v) {
    if (!v || busy || lock) return;
    if (effNow(v) && mode.step === 'ask' && tlSetAuto(v)) { closeMod(); return effSend({}); }      
    const pd = v.pend && v.pend.mine ? v.pend.type : '';
    if (pd === 'u5' && tlSetAuto(v)) { closeMod(); return send({ t: 'u5', drop: null }); }      
    if (pd === 'rev' && tlSetAuto(v)) { closeMod(); return send({ t: 'rev', use: false }); }      
    if (pd === 'k' && tlWasAuto(v.turn - 1, ['k'])) { closeMod(); return send({ t: 'k', pick: null }); }      
    if (pd === 'm' && tlWasAuto(v.turn - 1, ['m'])) { closeMod(); mode = { k: 'idle' }; return send({ t: 'm', drop: null }); }      
  }
  function paintAct(asking) {
    const v = V, a = $('.cbact'); let h = '';
    const two = (no, yes, yesText) => `<button type="button" class="cbb dk sm" data-cb="${no}">使わない</button><button type="button" class="cbb sm" data-cb="${yes}">${yesText}</button>`;
    if (asking || dealHold) h = '';
    else if (mode.k === 'idle' && v.can.six) h = two('sixno', 'sixyes', SIX.btn);      
    else if (mode.k === 'eff') h = mode.step === 'drop5' ? '<button type="button" class="cbb dk sm" data-cb="effback">戻る</button>' : two('effno', 'effyes', effBtn(mode.q));
    else if (mode.k === 'dropm') h = `<button type="button" class="cbb dk sm" data-cb="modex">戻る</button><button type="button" class="cbb sm" data-cb="mgo"${mode.sel.length === 2 ? '' : ' disabled'}>この 2枚を 捨てて 引く</button>`;
    else if (mode.k === 'idle' && preList(v).length) {      
      const pa = preAsk(v), L = preList(v);
      h = pa ? two(pa.no, pa.yes, preBtn(pa.c)) : L.length === 1 ? `<button type="button" class="cbb sm" data-cb="${L[0].yes}">${preBar(L[0].c)}</button>` : '<button type="button" class="cbb sm" data-cb="prere">セットの 前の 効果</button>';
    }
    else if (v.pend && v.pend.mine && v.pend.type === 'k') h = two('kskip', 'kgo', `${kmN('k', v.pend.tok)}の 効果を 使う`);      
    else if (v.pend && v.pend.mine && v.pend.type === 'm') h = two('mskip', 'mpick', `${kmN('m', v.pend.tok)}の 効果を 使う`);
    else if (v.pend && v.pend.mine && v.pend.type === 'rev' && v.my.set) h = two('revno', 'revyes', `${v.my.set.k} の 効果を 使う`);
    else if (mode.k === 'u5') h = '<button type="button" class="cbb dk sm" data-cb="u5back">戻る</button>';
    else if (v.pend && v.pend.mine && v.pend.type === 'u5') h = two('u5no', 'u5yes', '5 の 効果を 使う');
    a.innerHTML = h;
  }

  
  function modal(html, cls) { modEl.className = 'cbmod on ' + (cls || ''); modEl.innerHTML = html; }
  function closeMod() { if (modEl) { modEl.className = 'cbmod'; modEl.innerHTML = ''; } }
  const modOn = () => modEl.classList.contains('on');
  
  
  
  
  
  let peekId = '';
  
  
  
  
  
  const ASK_GUARD = 350;
  let askAt = 0;
  const tokIn = k => (V && V.my.hand.find(c => c.tok && c.k === k)) || null;      
  const effKey = q => ((q === '7' || q === '3') && tokIn(q) ? tokP(q) : effK(q));
  const effBar = q => (q === '7' && tokIn('7') ? '7トークン（3頭分）を 見せて 捨てると、山札から 3枚 引けるよ' : q === '3' && tokIn('3') ? '3トークン（2頭分）と 3 を 見せて、本物の 3 を 交換できるよ' : EFFBAR[q] || EFFTXT[q]);      
  const effText = q => (q === '7' && tokIn('7') ? '7トークン（3頭分）を 見せて 捨てて、山札から 3枚 引けるよ（トークンは 山札に 戻せないので 捨てる）' : q === '3' && tokIn('3') ? '3トークン（2頭分）と 3 で 3枚 ぶん 見せて、本物の 3 と 相手の 手札の 1枚（裏の カードから 選ぶ）を 交換できるよ' : EFFTXT[q]);
  function askInfo() {
    const v = V; if (!v || ended || !match) return null;
    if (mode.k === 'idle' && v.can.six) return { id: `s${gameNo}.${v.turn}`, k: '6', head: SIX.head, q: SIX.q, text: SIX.text, yes: 'sixyes', no: 'sixno' };      
    if (mode.k === 'eff' && mode.step === 'ask') return { id: `e${gameNo}.${v.turn}.${mode.n}`, k: effKey(mode.q), head: '効果タイム！', q: effQ(mode.q), text: effText(mode.q), yes: 'effyes', no: 'effno' };
    if (mode.k === 'idle' && v.pend && v.pend.mine && v.pend.type === 'k') return { id: `k${gameNo}.${v.turn}`, k: v.pend.tok ? tokP('k') : 'k', head: `${kmN('k', v.pend.tok)}で 勝った！`, q: `${kmN('k', v.pend.tok)}の 効果を 使う？`, text: '相手の 手札を 1枚 見られるよ', yes: 'kgo', no: 'kskip' };      
    if (mode.k === 'idle' && v.pend && v.pend.mine && v.pend.type === 'm') return { id: `m${gameNo}.${v.turn}`, k: v.pend.tok ? tokP('m') : 'm', head: `${kmN('m', v.pend.tok)}で 勝った！`, q: `${kmN('m', v.pend.tok)}の 効果を 使う？`, text: '手札を 2枚 捨てて、山札から 2枚 引けるよ', yes: 'mpick', no: 'mskip' };
    if (mode.k === 'idle' && v.pend && v.pend.mine && v.pend.type === 'u5') return { id: `u${gameNo}.${v.turn}`, k: '5', head: '交換で 5 を セット！', q: '5 の 効果を 使う？', text: EFFTXT[5], yes: 'u5yes', no: 'u5no' };      
    if (mode.k === 'idle' && v.pend && v.pend.mine && v.pend.type === 'rev' && v.my.set && v.op.set) { const k = v.my.set.k, tr = tokIn(k); return { id: `r${gameNo}.${v.turn}`, k: tr ? tokP(k) : k, head: '逆転の チャンス！', q: `${k} の 効果を 使う？`, text: tr ? `場の ${k} と ${nameOf(tokP(k))}（2頭分）で 3枚 ぶん。トークンを 捨てると、${toName(v.op.set.k)} 勝てるよ` : REVTXT(k, v.op.set.k), yes: 'revyes', no: 'revno' }; }      
    const pa = mode.k === 'idle' ? preAsk(v) : null;      
    if (pa && pa.c === 'x7r') return { id: 'x' + preId(v), k: tokIn('7') ? 't7' : '7', head: X7.head, q: X7.q, text: X7.text + (tokIn('7') ? '（7トークンは 3頭分：捨てるのは トークン）' : ''), ord: X7.ord, yes: 'x7yes', no: 'x7no' };
    if (pa) { const q = pa.c === 'x7' ? '7' : '3'; return { id: pa.c + preId(v), k: effKey(q), head: `${q} が 3枚${tokIn(q) ? ' ぶん' : ''}！`, q: effQ(q), text: 'セットの 前に 使えるよ。' + effText(q), yes: pa.yes, no: pa.no }; }      
    return null;
  }
  
  let preOff = {};
  const preId = v => `${gameNo}.${v.turn}`;
  const preList = v => PRE.filter(p => v.can[p.c]);                                   
  const preAsk = v => PRE.find(p => v.can[p.c] && preOff[p.c] !== preId(v)) || null;     
  const preBtn = c => (c === 'x7r' ? X7.btn : c === 'x7' ? effBtn('7') : effBtn('3'));      
  const preBar = c => (c === 'x7r' ? X7.bar : c === 'x7' ? (tokIn('7') ? '7トークンで 3枚 引く' : '7 を 3枚 交換') : '3 を 3枚 見せて 交換');      
  const preLine = c => (c === 'x7r' ? '7 が 4枚！ セットの 前なら 逆転を 使えるよ' : c === 'x7' ? (tokIn('7') ? '7トークン！ セットの 前なら 山札から 3枚 引けるよ' : '7 が 3枚！ セットの 前なら 交換を 使えるよ') : `3 が 3枚${tokIn('3') ? ' ぶん' : ''}！ セットの 前なら 交換を 使えるよ`);
  const askOn = () => !!modEl && modEl.classList.contains('cbask');
  function askSync() {                                 
    const A = askInfo();
    if (!A || peekId === A.id || screen !== 'game') { if (askOn()) closeMod(); return false; }
    if (askOn() && modEl.dataset.ask === A.id) return true;
    if (modOn() && !askOn()) return false;
    modal(`<h3 class="gold">${esc(A.head)}</h3><div class="big"><img src="${pic(A.k, true)}" alt="${esc(nameOf(A.k))}"></div><p class="askq"><b>${esc(A.q)}</b>${esc(A.text)}${A.ord ? `<span class="nw">（${esc(A.ord)}）</span>` : ''}</p>`
      + `<div class="rowb"><button type="button" class="cbb dk lg" data-cb="${A.no}">使わない</button><button type="button" class="cbb lg" data-cb="${A.yes}">使う</button></div>`
      + '<button type="button" class="cbb dk sm" data-cb="askpeek">手札と ボードを 見る</button>', 'cbask');
    modEl.dataset.ask = A.id; askAt = performance.now();
    return true;
  }
  
  function cardModal(u) {
    const v = V, c = v.my.hand.find(x => x.u === u); if (!c) return;
    let btn = '', note = '';
    if (v.pend && v.pend.mine && v.pend.type === 'swap') btn = `<button type="button" class="cbb" data-cb="swap" data-u="${u}">この カードと 交換する</button>`;
    else if (mode.k === 'eff') { if (mode.step === 'drop5') btn = `<button type="button" class="cbb" data-cb="drop5" data-u="${u}">この カードを 捨てる<small>5 と 一緒に 捨てて、山札から 1枚 セット</small></button>`; }      
    else if (mode.k === 'u5') btn = `<button type="button" class="cbb" data-cb="u5drop" data-u="${u}">この カードを 捨てる<small>5 と 一緒に 捨てて、山札から 1枚 セット</small></button>`;      
    else if (v.can.set) btn = `<button type="button" class="cbb" data-cb="set" data-u="${u}">この カードを セットする<small>セットしたら もう 変えられないよ</small></button>`;
    if (c.tok) note += `<p>${esc(nameOf(picK(c)))}${headOf(c.tok)}：この ターン だけ（使わないと ターンの 終わりに 消えるよ）</p>`;      
    modal(`<div class="big"><img src="${pic(picK(c), true)}" alt="${esc(nameOf(picK(c)))}"></div>${c.seen ? '<p>この カードは 相手に 見られて いるよ</p>' : ''}${note}<div class="col">${btn}<button type="button" class="cbb dk" data-cb="modx">戻る</button></div>`);
  }
  
  function showCard(k, text, back, side) { modal(`<div class="big"><img src="${pic(k, true, side)}" alt="${esc(k ? nameOf(k) : '伏せた カード')}"></div>${text ? `<p>${esc(text)}</p>` : ''}<div class="col"><button type="button" class="cbb dk" data-cb="${back === 'discard' ? 'discard' : 'modx'}">戻る</button></div>`); }
  
  function pickModal(kind) {
    const v = V;
    
    
    const seen = v.op.hand.some(c => c.k), x3 = kind === 'x3', ok = c => (x3 ? v.can.x3p.indexOf(c.u) >= 0 : !c.k);
    const head = kind === 'p6' ? '6 の 効果' : x3 ? '3 の 効果' : kmN('k', v.pend && v.pend.tok) + 'の 効果';
    const txt = x3 ? `交換する カードを 1枚 選んでね<br>（相手の 手札の 裏の カード：何が 来るかは わからないよ）<br>${tokIn('3') ? '3トークン（2頭分）と 3 を 見せて、本物の 3 を 1枚 わたすよ' : '手札の 3 を 3枚 相手に 見せて、1枚 わたすよ'}`
      : `見たい カードを 1枚 選んでね${kind === 'p6' ? '<br>（手札の 6 を 2枚 相手に 見せるよ）' : ''}`;
    modal(`<h3 class="gold">${head}</h3><p>${txt}${seen ? '<br>もう 見た カードは 選べないよ' : ''}</p>`
      + `<div class="pick">${v.op.hand.map(c => cardBtn({ u: c.u, k: c.k }, (c.k ? 'knw' : '') + (ok(c) ? ' tg' : ''), ok(c) ? ` data-cb="pick" data-kind="${kind}"` : ' disabled', 'op')).join('')}</div>`      
      + '<div class="col"><button type="button" class="cbb dk" data-cb="modx">戻る</button></div>', x3 ? 'cbx3' : '');
  }
  
  function discardModal() {
    const v = V; if (!v) return;
    const d = v.discard, turns = [], effs = [], w = esc(WHO());
    d.forEach(x => {
      if (x.why === 't') { (turns[x.turn] = turns[x.turn] || []).push(x); return; }
      let g = effs.find(e => e.turn === x.turn && e.why === x.why && e.mine === x.mine);
      if (!g) { g = { turn: x.turn, why: x.why, mine: x.mine, wt: !!x.wt, cards: [] }; effs.push(g); }      
      g.cards.push(x);
    });
    const card = x => `<button type="button" class="cbc" data-cb="dcard" data-k="${esc(picK(x))}" data-sd="${x.mine ? 'my' : 'op'}" aria-label="${esc(nameOf(picK(x)))} の カード"><img src="${pic(picK(x), false, x.mine ? 'my' : 'op')}" alt="" draggable="false"></button>`;      
    const pair = (name, cs) => `<div class="pr"><span>${name}</span><div class="cs">${cs.map(card).join('')}</div></div>`;
    let h = `<h3 class="gold">捨て札（${d.length}枚）</h3><div class="cbdl"><h4>終わった ターンの 捨て札</h4>`;
    if (!turns.some(Boolean)) h += '<p class="none">まだ ないよ（ターンが 終わると、出した カードが ここに 来るよ）</p>';
    turns.forEach((cs, n) => { if (cs) h += `<div class="row" data-dt="${n}"><b>ターン ${n}</b>${pair('あなた', cs.filter(x => x.mine))}${pair(w, cs.filter(x => !x.mine))}</div>`; });
    h += '<h4>効果で 捨てた カード</h4>';
    if (!effs.length) h += '<p class="none">まだ ないよ（1・2・5 の 効果・幻の馬の 効果で 捨てた カードが ここに 来るよ）</p>';
    effs.forEach(g => { h += `<div class="row" data-de="${esc(g.why)}"><b>ターン ${g.turn}${g.why === 'm' ? '<small>始め</small>' : ''}</b>${pair(`${g.mine ? 'あなた' : w}の ${g.why === 'm' ? kmN('m', g.wt) + 'の 効果' : esc(g.why) + ' の 効果'}`, g.cards)}</div>`; });      
    h += `</div><p>山札の 残り ${v.deckN}枚</p><div class="col"><button type="button" class="cbb dk" data-cb="modx">戻る</button></div>`;
    modal(h, 'cbdm');
  }
  
  
  
  
  
  const SETS = [['bgm', 'BGM', '音楽'], ['se', '効果音', 'カードや ボタンの 音']];
  const setOn = k => (k === 'bgm' ? bgmOn() : seOn());
  function gearModal() {
    const rows = SETS.map(([k, name, note]) => { const on = setOn(k); return `<div class="cbsw" data-set="${k}"><span>${name}<small>${note}</small></span><div class="cbseg" role="group" aria-label="${name}">`
      + `<button type="button" class="${on ? 'on' : ''}" data-cb="tg" data-k="${k}" data-v="1" aria-pressed="${on}">オン</button><button type="button" class="${on ? '' : 'on'}" data-cb="tg" data-k="${k}" data-v="0" aria-pressed="${!on}">オフ</button></div></div>`; }).join('');
    const game = screen === 'game' && !!match;
    modal(`<h3 class="gold">設定</h3><div class="cbsws">${rows}</div><div class="col">`
      + (game ? '<button type="button" class="cbb" data-cb="modx">対戦に 戻る</button><button type="button" class="cbb dk" data-cb="help">遊び方</button><button type="button" class="cbb dk" data-cb="quit">対戦を やめる</button>' : '<button type="button" class="cbb" data-cb="modx">戻る</button>')
      + '</div>', 'cbset');
  }
  
  function setSet(k, on) {
    if (['bgm', 'se'].indexOf(k) < 0) return;
    st[k] = !!on; save(); applySets();
    if (k === 'se' && on) se('tap', 0.8);
    if (modEl.classList.contains('cbset')) gearModal();
  }
  function applySets() { bgmSync(); if (!seOn()) qaStop(0.05, true); }      
  function quitModal() {
    const mid = !ended && !!V;
    if (qRun) { modal(`<h3 class="gold">調査を やめる？</h3><p>${mid ? '途中で やめると 調査 失敗に なるよ' : 'マップに 戻るよ（この 調査は ここまで）'}</p><div class="rowb"><button type="button" class="cbb dk" data-cb="modx">続ける</button><button type="button" class="cbb" data-cb="quitgo">やめる</button></div>`); return; }      
    modal(`<h3 class="gold">対戦を やめる？</h3><p>${mid ? '途中で やめると 負けに なるよ（連勝は 0 に 戻るよ）' + (st.stake ? `<br>${COINI}参加コイン ${st.stake.e}枚も 戻らないよ` : '') : 'メニューに 戻るよ'}</p><div class="rowb"><button type="button" class="cbb dk" data-cb="modx">続ける</button><button type="button" class="cbb" data-cb="quitgo">やめる</button></div>`);
  }

  
  
  
  
  function hush() { if (screen !== 'game') return; const a = $('.cbact'); if (a) a.innerHTML = ''; say(''); }
  async function send(a) {
    if (busy || !match) return false;
    busy = true; lock = true; closeMod(); hush();      
    let r = null; const g = GEN;
    try { r = await match.act(a); } catch (e) { r = { ok: false, why: 'err' }; }
    if (g !== GEN) return false;                       
    if (r && r.ok && a && a.t === 'set') mySets += 1;   
    busy = false;
    if (!r || !r.ok) { lock = false; if (match && V) { mode = { k: 'idle' }; render(); toast('その 手は 打てなかったよ', 2); } return false; }
    return true;
  }
  function onClick(e) {
    const key = e.target.closest('[data-key]'); if (key && !key.disabled) return roomKey(key.dataset.key);
    if (qPop && screen === 'qmap' && !e.target.closest('.qpo')) { const nd = e.target.closest('.qnd'); if (!nd || +nd.dataset.lv !== qPop) qPopClose(); }      
    const b = e.target.closest('[data-cb]'); if (!b || b.disabled) return;
    const a = b.dataset.cb, u = +b.dataset.u;
    if (a === 'useok') { if (useSkip) useSkip(); return; }      
    if (/^(effyes|effno|sixyes|sixno|kgo|kskip|mpick|mskip|revyes|revno|u5yes|u5no|x7yes|x7no|p7yes|p7no|p3yes|p3no)$/.test(a) && b.closest('.cbask') && performance.now() - askAt < (typeof CBApp._guard === 'number' ? CBApp._guard : ASK_GUARD)) return;      
    if (a === 'close') return close();
    if (a === 'cpu') { se('tap'); return startMatch(CBNet.cpu(CBApp._rng || undefined, CBApp._think || undefined, CBApp._opt || undefined)); }
    if (a === 'host' || a === 'join') { se('tap'); return showRoom(a); }
    if (a === 'dz') { se('tap'); return showDz('p'); }      
    if (a === 'dzx') return showMenu();
    if (a === 'dztab') { se('tap', 0.6); return showDz(['p', 'b', 'd'].indexOf(b.dataset.t) >= 0 ? b.dataset.t : 'f'); }
    if (a === 'pkask') return pkAsk();      
    if (a === 'pkgo') { if (performance.now() - dzAt < (typeof CBApp._guard === 'number' ? CBApp._guard : DZ_GUARD)) return; b.disabled = true; return pkGo(b.dataset.rq || ''); }
    if (a === 'pkodds') { se('tap', 0.6); return pkOdds(); }
    if (a === 'pkrip') return pkRip();
    if (a === 'pkflip') return pkTap(+b.dataset.i);
    if (a === 'pklast') return pkLast();
    if (a === 'pkmore') return pkAsk();
    if (a === 'pkhis') { const h = st.pkh.find(x => x.id === b.dataset.id); if (h) { se('tap', 0.6); pkShow(h, !h.v); } return; }
    if (a === 'pkx') { if (pk && pk.h) pkSeen(pk.h); pk = null; se('tap', 0.6); return showDz('p'); }
    if (a === 'bdi') { se('tap', 0.6); return bdItem(b.dataset.id || ''); }      
    if (a === 'bdopen') return bdAsk(b.dataset.id || '');
    if (a === 'bdgo') { if (performance.now() - dzAt < (typeof CBApp._guard === 'number' ? CBApp._guard : DZ_GUARD)) return; return bdGo(b.dataset.id || ''); }
    if (a === 'bduse') return bdUse(b.dataset.id || '');
    if (a === 'dzi') { se('tap', 0.6); return dzItem(b.dataset.ck || null, b.dataset.id || ''); }
    if (a === 'dzback') return closeMod();
    if (a === 'dzopen') return dzAsk(b.dataset.ck || null, b.dataset.id || '');
    if (a === 'dzgo') { if (performance.now() - dzAt < (typeof CBApp._guard === 'number' ? CBApp._guard : DZ_GUARD)) return; return dzGo(b.dataset.ck || null, b.dataset.id || ''); }
    if (a === 'dzuse') return dzUse(b.dataset.ck || null, b.dataset.id || '');
    if (a === 'tst') { if (testOn()) window.CBTest.act(b.dataset.t, dzApi); return; }
    if (a === 'ms') { se('tap'); return showMs(); }      
    
    if (a === 'quest') { se('tap'); return showQMap(); }
    if (a === 'qx') { se('tap', 0.6); return showMenu(); }
    if (a === 'qarea') return qArea(+b.dataset.lv);
    if (a === 'qgo') return qGo(+b.dataset.lv);
    if (a === 'qtk') { se('tap', 0.5); return qtModal(false); }      
    if (a === 'qpx') { se('tap', 0.5); return qPopClose(); }
    if (a === 'qtap') return qTap();
    if (a === 'qback') { se('tap', 0.6); return showQMap(); }
    if (a === 'qnext') return qNext();
    if (a === 'qretry') return qRetry();
    if (a === 'qmapgo') { se('tap', 0.6); return qToMap(); }
    if (a === 'qtst') { if (testOn() && window.CBTest.qHtml) modal(`<h3 class="gold">決戦調査の テスト</h3>${window.CBTest.qHtml(qEasy)}<div class="col"><button type="button" class="cbb dk" data-cb="modx">閉じる</button></div>`, 'cbqa'); return; }
    if (a === 'tstq') { if (testOn() && window.CBTest.qAct) window.CBTest.qAct(b.dataset.t, qApi); return; }
    if (a === 'msx') return showMenu();
    if (a === 'mstab') { se('tap', 0.6); return showMs(b.dataset.t); }
    if (a === 'tstm') { if (testOn() && window.CBTest.msAct) window.CBTest.msAct(b.dataset.t, msApi); return; }
    if (a === 'help') return showHelp(screen === 'game' ? 'game' : 'menu');
    if (a === 'helpx') { show(helpBack); if (helpBack === 'game') render(); return; }
    if (a === 'hgo') { const t = scr.help.querySelector(`h4[data-h="${b.dataset.h}"]`); if (t) t.scrollIntoView({ block: 'start', behavior: 'smooth' }); return; }      
    if (a === 'hbig') { const k = b.dataset.k || ''; if (R.KINDS.indexOf(k) >= 0 || (k.length === 2 && k[0] === 't' && GEMS[k[1]])) { se('tap', 0.6); showCard(k); } return; }      
    if (a === 'roomx') { roomStop(); return showMenu(); }
    if (a === 'roomre') return showRoom('host', true);
    if (a === 'stke') return stakeSet('e', +b.dataset.n);
    if (a === 'stkw') return stakeSet('w', +b.dataset.d);
    if (a === 'stkgo') { const r = room; if (!r || r.step !== 'stake') return; se('tap'); r.step = ''; r.gm = { on: st.rg.on }; paintRoom(); return roomGo(); }
    if (a === 'rgon') { const r = room; if (!r || r.mode !== 'host' || r.step !== 'stake') return; st.rg.on = b.dataset.v === '1'; save(); se('tap', 0.6); return paintRoom(); }      
    if (a === 'joinyes') { const m = match; if (!m || m.kind !== 'guest' || !m.stake || st.coin < m.stake.e || V) return; se('tap'); closeMod(); m.join(); say('相手を 待って いるよ…'); return; }
    if (a === 'joinno') { leave(false); return showMenu(); }
    if (a === 'menu') { leave(false); return showMenu(); }
    if (a === 'modx') { closeMod(); if (match && V && screen === 'game' && !busy && !lock && askInfo()) render(); return; }      
    if (a === 'askpeek') { const A = askInfo(); if (A) peekId = A.id; closeMod(); if (V && screen === 'game') render(); return; }      
    if (a === 'gear') { se('tap', 0.6); return gearModal(); }
    if (a === 'tg') return setSet(b.dataset.k, b.dataset.v === '1');
    if (a === 'quit') return quitModal();
    if (a === 'quitgo') { const qq = !!qRun; leave(true); return qq ? showQMap() : showMenu(); }      
    if (a === 'again') return again();
    if (a === 'discard') { if (modEl.classList.contains('cbopen')) return; return discardModal(); }
    if (a === 'dcard') { const k = b.dataset.k; if (R.KINDS.indexOf(k) >= 0 || (k.length === 2 && k[0] === 't' && GEMS[k[1]])) showCard(k, '捨て札の カード', 'discard', b.dataset.sd === 'op' ? 'op' : 'my'); return; }
    if (!match || !V || busy || lock || ended || modEl.classList.contains('cbopen')) return;
    const v = V;
    if (a === 'ocard' || a === 'oset') { const c = a === 'oset' ? v.op.set : v.op.hand.find(x => x.u === u); if (c && c.k) showCard(picK(c), a === 'oset' ? '相手が セットした カード' : c.tok ? '相手の トークン（この ターン だけ）' : '効果で 見た 相手の カード', '', 'op'); return; }
    if (a === 'mset') { const c = v.my.set; if (c) showCard(c.k ? picK(c) : null, c.open ? 'あなたが セットした カード' : c.blind ? '山札から 来た カード（オープンまで 分からない）' : c.up ? '4 の 効果で 見せた カード' : 'あなたが 伏せて セットした カード（相手には 裏・もう 変えられない）'); return; }
    if (a === 'card') {
      if (mode.k === 'dropm') { const j = mode.sel.indexOf(u); if (j >= 0) mode.sel.splice(j, 1); else if (mode.sel.length < 2) mode.sel.push(u); se('tap', 0.6); paintHand(); paintAct(); say(modeText()); layout(); return; }
      se('tap', 0.6); return cardModal(u);
    }
    if (a === 'set') { if (!v.can.set || mode.k !== 'idle') return; return send({ t: 'set', u: u }); }
    if (a === 'gem') return gemAsk(b.dataset.g);      
    if (a === 'gemgo') { const g = b.dataset.g; if (!v.my.gem || v.my.gem.can.indexOf(g) < 0 || mode.k !== 'idle') { closeMod(); return; } se('tap'); return send({ t: 'gem', g: g }); }
    
    if (a === 'x7yes') { if (!v.can.x7r || mode.k !== 'idle') return; se('tap', 0.6); return send({ t: 'x7r' }); }
    if (a === 'x7no') { if (!v.can.x7r) return; se('tap', 0.6); preOff.x7r = preId(v); closeMod(); render(); return; }
    
    if (a === 'p7yes') { if (!v.can.x7 || mode.k !== 'idle') return; se('tap', 0.6); return send({ t: 'x7' }); }
    if (a === 'p3yes') { if (!v.can.x3 || mode.k !== 'idle') return; se('tap', 0.6); return pickModal('x3'); }      
    if (a === 'p7no' || a === 'p3no') { const c = a === 'p7no' ? 'x7' : 'x3'; if (!v.can[c]) return; se('tap', 0.6); preOff[c] = preId(v); closeMod(); render(); return; }
    if (a === 'prere') { if (!preList(v).length || mode.k !== 'idle') return; se('tap', 0.6); preOff = {}; peekId = ''; render(); return; }      
    
    if (a === 'sixyes') { if (!v.can.six || mode.k !== 'idle') return; se('tap', 0.6); return pickModal('p6'); }
    if (a === 'sixno') { if (!v.can.six) return; se('tap', 0.6); return send({ t: 'p6', pick: null }); }
    
    if (a === 'effyes' || a === 'effno' || a === 'effback' || a === 'drop5') {
      if (!effNow(v)) return;
      se('tap', 0.6);
      if (a === 'effback') { mode.step = 'ask'; closeMod(); render(); return; }
      if (a === 'effno') { if (mode.step !== 'ask') return; return effSend({}); }
      if (a === 'drop5') { if (mode.step !== 'drop5' || !v.my.hand.some(c => c.u === u)) return; return effSend({ u5: u }); }
      if (mode.step !== 'ask') return;
      if (mode.q === '5') { mode.step = 'drop5'; render(); return; }
      return effSend(mode.q === '7' ? { x7: true } : mode.q === '3' ? { x3: true } : { u4: true });
    }
    if (a === 'modex') { mode = { k: 'idle' }; render(); return; }
    if (a === 'kgo') return pickModal('k');
    if (a === 'pick') {
      if (!v.op.hand.some(c => c.u === u && !c.k)) return;      
      if (b.dataset.kind === 'p6') { if (!v.can.six) return; return send({ t: 'p6', pick: u }); }      
      if (b.dataset.kind === 'x3') { if (!v.can.x3 || v.can.x3p.indexOf(u) < 0 || mode.k !== 'idle') return; se('tap', 0.6); return send({ t: 'x3', pick: u }); }      
      return send({ t: 'k', pick: u });
    }
    if (a === 'kskip') return send({ t: 'k', pick: null });
    if (a === 'mskip') return send({ t: 'm', drop: null });
    if (a === 'mpick') { mode = { k: 'dropm', sel: [] }; render(); return; }
    if (a === 'mgo') { if (mode.k === 'dropm' && mode.sel.length === 2) return send({ t: 'm', drop: mode.sel.slice() }); return; }
    if (a === 'swap') return send({ t: 'swap', u: u });
    
    if (a === 'u5yes') { if (!(v.pend && v.pend.mine && v.pend.type === 'u5') || mode.k !== 'idle') return; se('tap', 0.6); closeMod(); mode = { k: 'u5' }; render(); return; }
    if (a === 'u5no') { if (!(v.pend && v.pend.mine && v.pend.type === 'u5')) return; se('tap', 0.6); return send({ t: 'u5', drop: null }); }
    if (a === 'u5back') { if (mode.k === 'u5') { mode = { k: 'idle' }; render(); } return; }
    if (a === 'u5drop') { if (mode.k !== 'u5' || !v.my.hand.some(c => c.u === u)) return; closeMod(); return send({ t: 'u5', drop: u }); }
    if (a === 'revyes' || a === 'revno') { if (!(v.pend && v.pend.mine && v.pend.type === 'rev') || mode.k !== 'idle') return; se('tap', 0.6); return send({ t: 'rev', use: a === 'revyes' }); }      
  }

  
  const box = el => { const r = el.getBoundingClientRect(), o = ov.getBoundingClientRect(); return { x: r.left - o.left, y: r.top - o.top, w: r.width, h: r.height }; };
  const mid = (b, w) => ({ x: b.x + b.w / 2 - w / 2, y: b.y + b.h / 2 - w * 0.75, w: w, h: w * 1.5 });      
  function fly(k, from, to, ms, fade, side) {      
    if (reduce() || !from || !to || !from.w || !to.w) return T(40);
    const im = document.createElement('img'); im.src = pic(k, false, side); im.alt = ''; im.className = 'cbfl';
    im.style.cssText = `left:${from.x}px;top:${from.y}px;width:${from.w}px;height:${from.h}px`;
    flyEl.appendChild(im);
    const dx = to.x + to.w / 2 - (from.x + from.w / 2), dy = to.y + to.h / 2 - (from.y + from.h / 2), sc = to.w / from.w, d = Math.max(1, ms * SPEED);
    const g = GEN;
    return new Promise(ok => {
      let done = false; const fin = () => { if (done) return; done = true; im.remove(); if (g === GEN) ok(); };      
      const go = () => { im.style.transition = `transform ${d}ms cubic-bezier(.25,.7,.25,1),opacity ${d}ms`; im.style.transform = `translate(${dx}px,${dy}px) scale(${sc})`; if (fade) im.style.opacity = '0'; };
      if (clk.manual) { void im.offsetWidth; go(); } else requestAnimationFrame(go);
      later(fin, d + 60);
    });
  }
  const slotBox = side => box($('.cbslot.' + side));
  const handBox = side => box(side === 'my' ? $('.cbhand') : $('.cbohand'));
  const deckBox = () => box($('.cbdeck'));
  const disBox = () => box($('.cbdis'));
  const cardBox = (side, u) => { const e = (side === 'my' ? $('.cbhand') : $('.cbohand')).querySelector(`[data-u="${u}"]`); return e ? box(e) : null; };
  
  
  async function openShow(x, rv) {                     
    const hold = x.rev === 'me' || x.rev === 'op', rn = rv && R.NUMS.indexOf(x.my.k) >= 0 && R.NUMS.indexOf(x.op.k) >= 0 ? '（強さ 逆転中）' : '';
    const nm = c => nameOf(picK(c));      
    const txt = x.rev === 'me' ? ['チャンス！', `${nm(x.op)} の ほうが 強い…でも ${x.my.k} の「逆転勝利」を 使えるよ`] : x.rev === 'op' ? ['勝負は まだ！', `${WHO()}は ${x.op.k} の「逆転勝利」を 使えるよ`]
      : x.res === 'win' ? ['勝ち！', `${nm(x.my)} が ${nm(x.op)} に 勝ったよ${rn}`] : x.res === 'lose' ? ['負け…', `${nm(x.op)} の ほうが 強いよ${rn}`] : x.res === 'clash' ? ['かぶり！', `同じ カード（${nameOf(x.my.k)}）＝どちらも 負け`] : x.d4 ? ['ドロー！', 'どちらも 4 の 効果を 使った ので 引き分け'] : ['引き分け', '神様馬 と 幻の馬 は 同じ 強さ'];
    const side = (who, k) => `<div class="sd" data-sd="${who}"><span>${who === 'my' ? 'あなた' : esc(WHO())}</span><div class="cbflip"><div class="in"><img src="${pic(null, true, who)}" alt=""><img class="fc" src="${pic(k, true, who)}" alt="${esc(nameOf(k))}"></div></div></div>`;
    modal(`<h3 class="gold">ターン ${x.turn}　オープン！</h3><div class="cbvs">${side('my', picK(x.my))}<b class="mid gold">VS</b>${side('op', picK(x.op))}</div><div class="cbres gold" aria-live="assertive"><span></span><small></small></div>`, 'cbopen');
    await T(450); se('flip');
    modEl.querySelectorAll('.cbflip').forEach(f => f.classList.add('up'));
    await T(700);
    const res = $('.cbres', modEl); res.firstChild.textContent = txt[0]; res.lastChild.textContent = txt[1]; res.classList.add('on');
    const my = $('[data-sd=my]', modEl), op = $('[data-sd=op]', modEl);
    if (hold) se('magic');
    else if (x.res === 'win') { my.classList.add('wn'); op.classList.add('ls'); se('win'); }
    else if (x.res === 'lose') { op.classList.add('wn'); my.classList.add('ls'); se('lose'); }
    else if (x.res === 'tie') se('even');             
    else { my.classList.add('ls'); op.classList.add('ls'); se('even'); }
    $('.cbpips[data-p=op]').innerHTML = pips(x.wins[1], turnsOf()); $('.cbpips[data-p=my]').innerHTML = pips(x.wins[0], turnsOf());
    $('.cbslot.my').innerHTML = cardBtn({ u: x.my.u, k: x.my.k, tok: x.my.tok }, ''); $('.cbslot.op').innerHTML = cardBtn({ u: x.op.u, k: x.op.k, tok: x.op.tok }, '', '', 'op');
    await T(1900);
    closeMod();
  }
  
  async function peekShow(title, k, note, side) {      
    modal(`<h3 class="gold">${esc(title)}</h3><div class="sd" style="width:min(46vw,190px)"><div class="cbflip"><div class="in"><img src="${pic(null, true, side)}" alt=""><img class="fc" src="${pic(k, true, side)}" alt="${esc(nameOf(k))}"></div></div></div><p>${esc(note)}</p>`, 'cbopen');
    await T(350); se('flip'); const f = $('.cbflip', modEl); if (f) f.classList.add('up');
    await T(1900); closeMod();
  }
  async function play(ev, v) {
    const P = V, g0 = GEN;                             
    
    let hand = P ? P.my.hand.slice() : [], dis = P ? P.discard.slice() : [];
    const rehand = fresh => { paintHand(fresh, hand); layout(); };
    const toDis = cs => { cs.forEach(c => dis.push({ k: c.k, mine: c.mine })); paintDis(dis); };      
    const tokOf = u => (hand.find(q => q.u === u && q.tok) || (P ? P.op.hand.find(q => q.u === u && q.tok) : null)) || null;      
    const kIn = (sd) => { const el = $('.cbslot.' + sd + ' .cbc'); return el && el.dataset.ck ? (el.dataset.tok ? tokP(el.dataset.ck) : el.dataset.ck) : null; };      
    for (const x of ev) {
      if (!match || g0 !== GEN) return;
      if (x.e === 'deal') {
        ended = false; gameNo += 1; closeMod(); V = null; FL.clear(); paintEmpty();
        payStake();                                    
        msLive();                                      
        $('.cbdeck .cbn').textContent = '30'; se('deal');
        if (qRun) { const q = QUEST[qRun.lv - 1], n = qRun.won + 1, rg = qRigText(q.rig[n]); await banner(`第${n}戦 スタート`, (n === 1 ? `${q.n}と 勝負！` : `あと ${q.w - qRun.won}連勝で 討伐！`) + (rg ? `\n⚠ 敵の 手札に 必ず ${rg}！` : ''), rg ? 1500 : 900); }      
        else await banner('対戦 スタート', `${WHO()}と 勝負！`, 900);
        
        const d = deckBox(), hm = handBox('my'), ho = handBox('op'), w = Math.min(60, d.w * 1.2);
        const jobs = [];
        const nDeal = Math.max(v.my.hand.length, v.op.hand.length) || R.HAND;      
        for (let i = 0; i < nDeal; i++) { jobs.push(T(i * 90).then(() => fly(null, mid(d, w), mid(hm, w), 320))); jobs.push(T(i * 90 + 45).then(() => fly(null, mid(d, w), mid(ho, w * 0.7), 320, false, 'op'))); }
        await Promise.all(jobs);
        dealHold = ev.indexOf(x) < ev.length - 1;     
        if (v.my.gem || v.op.gem) R.GEMS.forEach(g => [false, true].forEach(big => { const im = new Image(); im.src = pic(tokP(g), big); }));      
        V = v; mode = { k: 'idle' }; render();
        hand = v.my.hand.slice(); dis = v.discard.slice();
        $('.cbhand').querySelectorAll('.cbc').forEach((c, i) => { c.classList.add('new'); c.style.animationDelay = (i * 50 * SPEED) + 'ms'; });
        await T(380);
      } else if (x.e === 'turn') {
        await banner('ターン ' + x.n, x.n >= ((v && v.turns) || R.TURNS) ? '最後の 勝負！' : '', 800);
      } else if (x.e === 'pre') {                      
        se('magic'); await banner(kmN(x.type, x.tok) + 'の 効果', x.me ? '使うか 選んでね' : `${WHO()}が 使うか 選ぶよ`, 950);      
      } else if (x.e === 'set') {
        se('set');
        if (x.me) {                                    
          const c = hand.find(q => q.u === x.u);
          await fly(null, cardBox('my', x.u) || mid(handBox('my'), 60), slotBox('my'), 300);
          $('.cbslot.my').innerHTML = mySet({ u: x.u, k: c ? c.k : null, tok: c ? c.tok : 0, up: false, blind: false, open: false });
          hand = hand.filter(q => q.u !== x.u); const h = $('.cbhand').querySelector(`[data-u="${x.u}"]`); if (h) h.remove();
        } else {                                       
          const keep = new Set(((v && v.op && v.op.hand) || []).map(c => String(c.u))), hs = Array.from($('.cbohand').children);
          const h = hs.find(e => !keep.has(e.dataset.u)) || hs.filter(e => !e.dataset.ck).pop() || hs[hs.length - 1];
          await fly(null, h ? box(h) : mid(handBox('op'), 40), slotBox('op'), 300, false, 'op'); if (h) h.remove(); $('.cbslot.op').innerHTML = cardBtn({ u: 0, k: null }, '', '', 'op');
        }
      } else if (x.e === 'sixt') {                     
        se('magic'); await banner('6 の 効果', x.mine ? 'セットの 前に 使うか 選んでね' : `${WHO()}が 使うか 選ぶよ`, 950);
      } else if (x.e === 'sixd' || x.e === 'p6skip') {
        if (x.e === 'p6skip' && !x.me) { toast(`${WHO()}は 6 の 効果を 使わなかったよ`, 1.8); await T(500); }      
      } else if (x.e === 'efft') {                     
        $('.cbglow').classList.remove('on');
        if (x.first) await banner('効果タイム', x.mine ? 'カードの 効果を 使うか 選んでね' : `${WHO()}が 効果を 使うか 選ぶよ`, 950);
        else if (x.mine) se('magic', 0.5);
      } else if (x.e === 'effd') {
         
      } else if (x.e === 'fizz') {
        toast(`${x.me ? '' : WHO() + 'の '}${x.k} の 効果は 使えなかったよ`, 2.2); await T(700);
      } else if (x.e === 'p6') {
        await useShow(x);                              
        if (x.me) { await peekShow('6 の 効果', x.k, `${WHO()}の 手札に ${nameOf(x.k)} が あるよ`, 'op'); flash('op:' + x.pick); }      
        else { const c = hand.find(q => q.u === x.pick); flash('my:' + x.pick); toast(c ? `${WHO()}が 6 の 効果で、\nあなたの ${nameOf(c.k)} を 見たよ` : `${WHO()}が 6 を 2枚 見せて、\nあなたの 手札を 1枚 見たよ`, 3.2); await T(1100); }
      } else if (x.e === 'ask5') {                     
        se('magic', 0.7);
      } else if (x.e === 'u5') {                       
        await useShow(x);
        const sd = x.me ? 'my' : 'op';
        toast(x.me ? `5 の 効果！\n5 と ${nameOf(picK(x.drop))} を 捨てて、山札から 1枚 セットしたよ` : `${WHO()}が 5 の 効果を 使ったよ\n5 と ${nameOf(picK(x.drop))} を 捨てて、山札から 1枚`, 3);
        se('flip'); $('.cbslot.' + sd).innerHTML = cardBtn({ u: 0, k: '5' }, '', '', sd); await T(600);      
        $('.cbslot.' + sd).innerHTML = '';
        const oc = x.me ? null : $('.cbohand').querySelector(`[data-u="${x.drop.u}"]`) || $('.cbohand').lastElementChild;
        await Promise.all([fly('5', slotBox(sd), mid(disBox(), 20), 380, true, sd), fly(picK(x.drop), x.me ? (cardBox('my', x.drop.u) || mid(handBox('my'), 60)) : (oc ? box(oc) : mid(handBox('op'), 40)), mid(disBox(), 20), 380, true, sd)]);
        if (x.me) { hand = hand.filter(q => q.u !== x.drop.u); rehand(); } else if (oc) oc.remove();
        toDis([{ k: '5', mine: x.me }, { k: picK(x.drop), mine: x.me }]);
        se('set'); await fly(null, mid(deckBox(), 40), slotBox(sd), 340, false, sd);
        $('.cbslot.' + sd).innerHTML = cardBtn({ u: 0, k: null }, '', '', sd) + (x.me ? '<span class="tag">山札から</span>' : '');
        flash('slot:' + sd);                           
        await T(250);
      } else if (x.e === 'x7') {
        await useShow(x);
        const s7 = x.me ? 'my' : 'op', hb = handBox(s7), d = deckBox(), w = x.me ? 56 : 36;
        if (x.tok) {      
          const t7 = x.drop || tokOf(x.tok) || { u: x.tok, k: '7', tok: 3 };
          modal(`<h3 class="gold">7 の 効果！</h3><div class="three"><span class="cbc"><img src="${pic('t7', false, s7)}" alt="${esc(nameOf('t7'))} の カード" draggable="false"></span></div>`
            + `<p>${x.me ? '7トークン（3頭分）を 見せて 捨てたよ' : `${esc(WHO())}が 7トークン（3頭分）を 見せて 捨てたよ`}<br>山札から 3枚 引くよ</p>`, 'cbopen');
          await T(1500); closeMod();
          const oc = x.me ? null : $('.cbohand').querySelector(`[data-u="${t7.u}"]`) || $('.cbohand').lastElementChild;
          await fly('t7', x.me ? (cardBox('my', t7.u) || mid(hb, w)) : (oc ? box(oc) : mid(hb, w)), mid(disBox(), 20), 380, true, s7);
          if (x.me) { hand = hand.filter(q => q.u !== t7.u); rehand(); } else if (oc) oc.remove();
          toDis([{ k: 't7', mine: x.me }]);
          toast(x.me ? '7 の 効果！\n7トークン（3頭分）を 捨てて、山札から 3枚 引いたよ' : `${WHO()}が 7 の 効果を 使ったよ\n7トークン（3頭分）を 捨てて 3枚 引いた`, 3);
        } else {
          toast(x.me ? '7 の 効果！\n7 を 3枚 戻して、新しく 3枚 引いたよ' : `${WHO()}が 7 の 効果を 使ったよ\n7 を 3枚 戻して 3枚 引いた`, 3);
          await Promise.all([0, 1, 2].map(i => T(i * 70).then(() => fly('7', mid(hb, w), mid(d, 36), 320, true, s7))));
          if (x.me) { let n = 0; hand = hand.filter(q => !(q.k === '7' && n++ < 3)); rehand(); }
        }
        await Promise.all([0, 1, 2].map(i => T(i * 70).then(() => fly(null, mid(d, 36), mid(hb, w), 320, false, s7))));
        if (x.me && x.drew) { hand = hand.concat(x.drew.map(c => ({ u: c.u, k: c.k }))); rehand(x.drew.map(c => c.u)); flash(...x.drew.map(c => 'my:' + c.u)); await T(420); }      
      } else if (x.e === 'x7r') {                      
        await useShow(x);
        const sd = x.me ? 'my' : 'op';
        const tw7 = x.drop.tok || 0, ks7 = tw7 ? ['t7'].concat(Array.from({ length: x.show.length - 1 }, () => '7')) : ['7', '7', '7', '7'];      
        modal(`<h3 class="gold">7 の 効果！ 強さ 逆転</h3><div class="three four">${ks7.map(k => `<span class="cbc"><img src="${pic(k, false, sd)}" alt="${esc(nameOf(k))} の カード" draggable="false"></span>`).join('')}</div>`
          + `<p>${tw7 ? `${x.me ? '' : esc(WHO()) + 'が '}7トークン（3頭分）と 7 で 4枚 ぶん 見せて、7トークンを 捨てたよ` : x.me ? '手札の 7 を 4枚 見せて、1枚 捨てたよ' : `${esc(WHO())}が 手札の 7 を 4枚 見せて、1枚 捨てたよ`}<br><b>この 対戦が 終わる まで、数字の 強さが 逆に なるよ</b></p><p class="rvord">7＞6＞5＞4＞3＞2＞1<small>神様馬・幻の馬は 一番 強い まま</small></p>`, 'cbopen');
        await T(2000); closeMod();
        const oc = x.me ? null : $('.cbohand').querySelector(`[data-u="${x.drop.u}"]`) || $('.cbohand').lastElementChild;
        await fly(picK(x.drop), x.me ? (cardBox('my', x.drop.u) || mid(handBox('my'), 60)) : (oc ? box(oc) : mid(handBox('op'), 40)), mid(disBox(), 20), 380, true, sd);
        if (x.me) { hand = hand.filter(q => q.u !== x.drop.u).map(q => (x.show.indexOf(q.u) >= 0 ? Object.assign({}, q, { seen: true }) : q)); rehand(); } else if (oc) oc.remove();
        toDis([{ k: picK(x.drop), mine: x.me }]);
        await banner('強さ 逆転！', '7＞6＞5＞4＞3＞2＞1（この 対戦が 終わる まで）', 1500);
      } else if (x.e === 'x3') {                       
        const hm = handBox('my'), ho = handBox('op'), tk = x.take.k;
        await useShow(x);
        
        const ks3 = x.three.length < 3 ? x.three.map(u => (u === x.give.u ? '3' : 't3')) : ['3', '3', '3'];      
        modal(`<h3 class="gold">3 の 効果！</h3><div class="three">${ks3.map(k => `<span class="cbc"><img src="${pic(k, false, x.me ? 'my' : 'op')}" alt="${esc(nameOf(k))} の カード" draggable="false"></span>`).join('')}</div><p>${x.three.length < 3 ? (x.me ? '3トークン（2頭分）と 3 で 3枚 ぶん 見せたよ' : `${esc(WHO())}が 3トークン（2頭分）と 3 で 3枚 ぶん 見せたよ`) : x.me ? '手札の 3 を 3枚 見せたよ' : `${esc(WHO())}が 手札の 3 を 3枚 見せたよ`}<br>${x.me ? `その 1枚と、${esc(WHO())}の 手札の 1枚を 交換！` : 'その 1枚と、あなたの 手札の 1枚を 交換！'}</p>`, 'cbopen');
        await T(1700); closeMod();
        if (x.me) {
          await peekShow('3 の 効果：交換！', tk, `${WHO()}の 手札から ${nameOf(tk)} を もらったよ（3 を 1枚 渡した）`, 'op');
          await Promise.all([fly('3', cardBox('my', x.give.u) || mid(hm, 56), mid(ho, 36), 400, false, 'op'), fly(tk, mid(ho, 36), mid(hm, 56), 400)]);
          hand = hand.filter(q => q.u !== x.give.u).map(q => (x.three.indexOf(q.u) >= 0 ? Object.assign({}, q, { seen: true }) : q)).concat([{ u: x.take.u, k: tk, seen: true }]);
          rehand([x.take.u]); flash('my:' + x.take.u);      
        } else {
          toast(`${WHO()}が 3 の 効果を 使ったよ\nあなたの ${nameOf(tk)} と 3 を 交換した`, 3.4);
          await Promise.all([fly(tk, cardBox('my', x.take.u) || mid(hm, 56), mid(ho, 36), 400, false, 'op'), fly('3', mid(ho, 36), mid(hm, 56), 400)]);
          hand = hand.filter(q => q.u !== x.take.u).concat([{ u: x.give.u, k: '3' }]);
          rehand([x.give.u]); flash('my:' + x.give.u);
        }
        await T(500);
      } else if (x.e === 'first') {
        se('flip');
        $('.cbslot.' + (x.me ? 'my' : 'op')).innerHTML = cardBtn({ u: 0, k: '4' }, '', '', x.me ? 'my' : 'op') + '<span class="tag">4 の 効果</span>';
        flash('slot:' + (x.me ? 'my' : 'op'));        
        await useShow(x);                              
      } else if (x.e === 'first2') {
        se('flip');
        $('.cbslot.my').innerHTML = cardBtn({ u: 0, k: '4' }, ''); $('.cbslot.op').innerHTML = cardBtn({ u: 0, k: '4' }, '', '', 'op');
        flash('slot:my', 'slot:op');
        await useShow(x);                              
      } else if (x.e === 'swap') {
        se('set');
        const sd = x.me ? 'my' : 'op', hb = handBox(sd);
        await fly(null, slotBox(sd), mid(hb, x.me ? 56 : 36), 300, false, sd);
        const c = x.me ? hand.find(q => q.u === x.u) : null;
        await fly(null, x.me ? (cardBox('my', x.u) || mid(hb, 56)) : mid(hb, 36), slotBox(sd), 300, false, sd);      
        $('.cbslot.' + sd).innerHTML = x.me ? mySet({ u: x.u, k: c ? c.k : null, tok: c ? c.tok : 0, up: false, blind: false, open: false }) : cardBtn({ u: 0, k: null }, '', '', sd);
        if (x.me) { const bk = v.my.hand.find(q => q.u === x.back) || (P && P.my.set && P.my.set.u === x.back ? { u: x.back, k: P.my.set.k, tok: P.my.set.tok } : null); hand = hand.filter(q => q.u !== x.u); if (bk) hand.push(Object.assign({ u: bk.u, k: bk.k, seen: !!bk.seen }, bk.tok ? { tok: bk.tok } : {})); rehand(bk ? [bk.u] : null); flash('slot:my', bk ? 'my:' + bk.u : null); }      
        else { flash('slot:op'); toast(`${WHO()}が カードを 交換したよ`, 1.8); }
      } else if (x.e === 'open') {
        hush();                                        
        await openShow(x, !!(v && v.rv));
      } else if (x.e === 'k') {
        await useShow(x);
        if (x.me) { await peekShow(`${kmN('k', x.tok)}の 効果`, x.k, `${WHO()}の 手札に ${nameOf(x.k)} が あるよ`, 'op'); flash('op:' + x.pick); }      
        else { const c = hand.find(q => q.u === x.pick); flash('my:' + x.pick); toast(c ? `${WHO()}が ${kmN('k', x.tok)}の 効果で、\nあなたの ${nameOf(c.k)} を 見たよ` : `${WHO()}が ${kmN('k', x.tok)}の 効果で、\nあなたの 手札を 1枚 見たよ`, 3.2); await T(1100); }
      } else if (x.e === 'm') {
        await useShow(x);
        toast(x.me ? `${kmN('m', x.tok)}の 効果！\n${x.drop.map(c => nameOf(c.k)).join(' と ')} を 捨てて、${x.n}枚 引いたよ` : `${WHO()}が ${kmN('m', x.tok)}の 効果を 使ったよ\n${x.drop.map(c => nameOf(c.k)).join(' と ')} を 捨てて、${x.n}枚 引いた`, 3.2);
        const sd = x.me ? 'my' : 'op', hb = handBox(sd), d = deckBox(), w = x.me ? 56 : 36;
        await Promise.all(x.drop.map((c, i) => T(i * 80).then(() => fly(c.k, x.me ? (cardBox('my', c.u) || mid(hb, w)) : mid(hb, w), mid(disBox(), 20), 360, true, sd))));
        if (x.me) { hand = hand.filter(q => !x.drop.some(c => c.u === q.u)); rehand(); }
        toDis(x.drop.map(c => ({ k: c.k, mine: x.me })));
        await Promise.all(Array.from({ length: x.n }, (_, i) => T(i * 80).then(() => fly(null, mid(d, 36), mid(hb, w), 320, false, sd))));
        if (x.me && x.drew) { hand = hand.concat(x.drew.map(c => ({ u: c.u, k: c.k }))); rehand(x.drew.map(c => c.u)); flash(...x.drew.map(c => 'my:' + c.u)); }      
        await T(250);
      } else if (x.e === 'kskip' || x.e === 'mskip') {
        if (!x.me) { toast(`${WHO()}は 効果を 使わなかったよ`, 1.8); await T(500); }
      } else if (x.e === 'rev') {                      
        hush(); await useShow(x);
        const tr = x.drop.tok ? tokP(x.k) : null;      
        modal(`<h3 class="gold">${esc(x.k)} の 効果！</h3><div class="three">${(tr ? [x.k, tr] : [x.k, x.k, x.k]).map(k => `<span class="cbc"><img src="${pic(k, false, x.me ? 'my' : 'op')}" alt="${esc(nameOf(k))} の カード" draggable="false"></span>`).join('')}</div>`
          + (tr ? `<p>${x.me ? '' : esc(WHO()) + 'が '}場の ${esc(x.k)} と ${esc(nameOf(tr))}（2頭分）で 3枚 ぶん 見せたよ<br>${esc(nameOf(tr))}を 捨てて、${esc(toName(x.beat))} 逆転！</p>`
            : `<p>${x.me ? '' : esc(WHO()) + 'が '}${esc(x.k)} を 3枚（場の 1枚 ＋ 手札の 2枚）見せたよ<br>手札の ${esc(x.k)} を 1枚 捨てて、${esc(toName(x.beat))} 逆転！</p>`), 'cbopen');
        await T(1700); closeMod();
        const oc = x.me ? null : $('.cbohand').querySelector(`[data-u="${x.drop.u}"]`) || $('.cbohand').lastElementChild;
        await fly(picK(x.drop), x.me ? (cardBox('my', x.drop.u) || mid(handBox('my'), 60)) : (oc ? box(oc) : mid(handBox('op'), 40)), mid(disBox(), 20), 380, true, x.me ? 'my' : 'op');
        if (x.me) { hand = hand.filter(q => q.u !== x.drop.u).map(q => (x.show.indexOf(q.u) >= 0 ? Object.assign({}, q, { seen: true }) : q)); rehand(); } else if (oc) oc.remove();
        toDis([{ k: picK(x.drop), mine: x.me }]);
        await T(200);
      } else if (x.e === 'revskip') {
        hush();
        if (!x.me) { toast(`${WHO()}は 逆転勝利を 使わなかったよ`, 1.8); await T(500); }
      } else if (x.e === 'fin') {                      
        const mk = kIn('my'), ok = kIn('op'), won = x.res === 'win';
        $('.cbpips[data-p=op]').innerHTML = pips(x.wins[1], turnsOf()); $('.cbpips[data-p=my]').innerHTML = pips(x.wins[0], turnsOf());
        se(won ? 'win' : 'lose');
        await banner(x.rev ? (won ? '逆転勝利！' : '逆転負け…') : (won ? '勝ち！' : '負け…'), mk && ok ? (won ? `${nameOf(mk)} が ${nameOf(ok)} に 勝ったよ` : `${nameOf(ok)} が ${nameOf(mk)} に 勝ったよ`) : '', 1300);
      } else if (x.e === 'clear') {                    
        const ka = kIn('my'), kb = kIn('op'), d = mid(disBox(), 20), jobs = [];
        if ($('.cbslot.my .cbc')) jobs.push(fly(ka, slotBox('my'), d, 380, true));
        if ($('.cbslot.op .cbc')) jobs.push(fly(kb, slotBox('op'), d, 380, true, 'op'));
        $('.cbslot.my').innerHTML = ''; $('.cbslot.op').innerHTML = '';
        await Promise.all(jobs);
        toDis((v.me === 0 ? [{ k: ka, mine: true }, { k: kb, mine: false }] : [{ k: kb, mine: false }, { k: ka, mine: true }]).filter(c => c.k));      
      } else if (x.e === 'gem') {                     
        const gm = GEMS[x.g], c = x.c, w = c.tok || 1, sd = x.me ? 'my' : 'op';
        se('magic');
        if (x.me) {
          const sl = $(`.cbgem .g[data-g="${x.g}"]`); if (sl) { sl.classList.remove('can'); sl.classList.add('pop'); }
          const from = sl ? box(sl) : mid(handBox('my'), 60);
          await fly(picK(c), from, mid(handBox('my'), 60), 460);
          hand = hand.concat([{ u: c.u, k: c.k, tok: c.tok }]); rehand([c.u]); flash('my:' + c.u);      
          await banner(`${gm.n}！`, `${gm.t}${headOf(w)}が 手札に 来たよ\nこの ターン だけ`, 1300);
        } else {
          const og = $('.cbopp .ogem');
          await fly(picK(c), og ? box(og) : mid(handBox('op'), 40), mid(handBox('op'), 40), 420, false, sd);
          await banner(`${WHO()}が ${gm.n}を 使った！`, `${gm.t}${headOf(w)}が ${WHO()}の 手札に`, 1300);
        }
      } else if (x.e === 'tokgone') {                 
        if (x.me) {
          x.u.forEach(u => { const el = $('.cbhand').querySelector(`[data-u="${u}"]`); if (el) el.classList.add('gone'); });
          toast('トークンは この ターン だけ…\n消えたよ', 1.8);
          await T(600);
          hand = hand.filter(q => x.u.indexOf(q.u) < 0); rehand();
        } else { x.u.forEach(u => { const el = $('.cbohand').querySelector(`[data-u="${u}"]`); if (el) el.remove(); }); }
      } else if (x.e === 'end') {
        V = v; render();
        if (x.early) await banner('決着！', `${x.wins[0] > x.wins[1] ? 'あなた' : WHO()}の 勝ちが 決まったよ（のこりの ターンでは 追いつけない）`, 1500);      
        await endShow(x);
      }
    }
  }
  
  async function endShow(x) {
    if (qRun) return qEndShow(x);                      
    ended = true;
    const head = x.res === 'win' ? 'あなたの 勝ち！' : x.res === 'lose' ? 'あなたの 負け…' : '同点！';
    se(x.res === 'win' ? 'fanfare' : x.res === 'lose' ? 'over' : 'even');
    modal(`<h3 class="gold">${head}</h3><div class="sc">${x.wins[0]} － ${x.wins[1]}<small>あなた － ${esc(WHO())}（勝った 数）${x.early ? `<br>${x.early}ターン目で 決着！` : ''}</small></div><div class="gift"></div><div class="gift2" style="min-height:20px;font-size:12.5px;color:#d9c08c"></div>`
      + '<div class="col"><button type="button" class="cbb" data-cb="again">もう 1回</button><button type="button" class="cbb dk" data-cb="menu">メニューへ</button></div>', 'cbend');
    const no = gameNo, r = await (ends.shift() || settle(x.res)), g = $('.cbend .gift');      
    if (!g || no !== gameNo) return;
    
    let h = '';
    if (x.res === 'win') {
      const nx = r.cpu ? Math.min.apply(null, TK_BONUS.map(t => t[0] - r.streak % t[0])) : 0;
      h = `<div><b>${r.streak}連勝中！</b>` + (r.cpu ? `　あと ${nx}勝で 調査隊切符` : '') + '</div>';
    } else if (x.res === 'lose') h = '<div>連勝は 0 に 戻ったよ。もう 1回 やって みよう！</div>';
    else h = `<div>${st.streak > 0 ? `同点なので 連勝（${st.streak}連勝）は そのまま` : '同点！ もう 1回 やって みよう！'}</div>`;
    
    
    const now = `（今 ${r.coins}枚${r.full ? `：${COIN.max}枚 まで` : ''}）`;
    
    
    
    if (r.cb || r.tkGot) h += `<div class="cbsbn" role="status" aria-label="${r.streak}連勝 ボーナス${r.cb ? ` バトルコイン ${r.cb}枚` : ''}${r.tkGot ? ` 調査隊切符 ${r.tkGot}枚` : ''}"><i aria-hidden="true">🔥</i><span>${r.streak}連勝 ボーナス！</span>${r.cb ? `${COINI}<b>＋${r.cb}枚</b>` : ''}${r.tkGot ? `${TKI}<b>＋${r.tkGot}枚</b>` : ''}</div>`;
    if (r.tk) h += `<div class="cbtkl">${TKI}` + (r.tkGot ? `調査隊切符 今 ${r.tks}枚` + (r.tkGot < r.tk ? `（${QT.max}枚 まで なので ${r.tkGot}枚 だけ）` : '') : `調査隊切符は いっぱい（${QT.max}枚）なので、今回は 増えなかったよ`) + '</div>';
    h += r.ms.map(m => `<div class="cbmsn" role="status" aria-label="ミッション達成 ${m.n}連勝 バトルコイン ${m.c}枚"><i aria-hidden="true">🎯</i><span>ミッション達成！</span><b>${m.n}連勝</b>${COINI}<b>＋${m.c}枚</b></div>`).join('');
    if (r.pot) h += `<div class="cbcl">${COINI}${x.res === 'win' ? `<b>バトルコイン ＋${r.pot.w}枚</b>` : x.res === 'draw' ? `同点：参加コイン ${r.pot.e}枚 戻ったよ` : `参加コイン ${r.pot.e}枚は 戻らないよ`}${now}</div>`;
    else if (r.coin) h += `<div class="cbcl">${COINI}<b>バトルコイン ＋${r.coin}枚</b>${now}</div>`;      
    else if (r.ms.length) h += `<div class="cbcl">${COINI}バトルコイン${now}</div>`;      
    g.innerHTML = h;
    if (g.querySelector('.cbmsn') || g.querySelector('.cbsbn')) se('magic', 0.7);
    
    const k = match && match.stake;
    if (k && k.e > 0 && st.coin < k.e) { const ab = $('.cbend [data-cb=again]'), g2 = $('.cbend .gift2'); if (ab) ab.disabled = true; if (g2) g2.textContent = `バトルコインが 足りない ので、もう 1回は できないよ`; }
  }
  function again() {
    if (!match || !ended) return;
    if (match.stake && match.stake.e > 0 && st.coin < match.stake.e) return;      
    const g2 = $('.cbend .gift2'), b = $('.cbend [data-cb=again]');
    if (match.kind !== 'cpu') { if (b) b.disabled = true; if (g2) g2.textContent = `${WHO()}を 待って いるよ…`; }
    match.again();
  }
  
  function leave(count) {
    const m = match; match = null; queue = []; GEN += 1;      
    if (m) { if (count && !ended && !fin && V && !qRun) { st.lose += 1; st.streak = 0; msRoll(); st.ms[msKind(m)] = 0; save(); } try { m.leave(); } catch (e) {   } }      
    fin = false; ends = [];
    if (st && st.stake) { st.stake = null; save(); }      
    if (st && st.ms && st.ms.live) { st.ms.live = ''; save(); }      
    V = null; ended = false; closeMod();
    qRun = null; if (scr.game) scr.game.classList.remove('qm');      
  }

  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  const QG = [[0.50, 0.80, 0.74], [0.52, 0.80, 0.76], [0.50, 0.80, 0.74], [0.50, 0.81, 0.70], [0.52, 0.80, 0.74], [0.50, 0.80, 0.74], [0.50, 0.76, 0.80], [0.50, 0.80, 0.74], [0.50, 0.81, 0.76], [0.50, 0.80, 0.80], [0.50, 0.81, 0.72], [0.50, 0.81, 0.78]];
  const QFOOT = 1 / 1.42;
  
  const QMAP = [[135, 1376], [773, 1342], [779, 1087], [145, 1096], [157, 877], [776, 868], [791, 641], [171, 631], [140, 418], [773, 419], [796, 213], [146, 199]];
  const QUEST = [
    
    
    
    ['若草の原', '若草の鈴駒', '鈴駒', 1, 10, {}, ['「ふぅ、ここでひと休み……」　チリン♪', 'チリンチリンッ！　ダダダッ！　「わっ、子馬がこっちに！」'], 2],
    ['風見峠', '風見峠の疾風', '疾風', 2, 20, {}, ['バタバタバタッ！　「すごい風だ。……坂の上に馬？」', 'ビュンッ！　「早い！こいつも敵か！」'], 2],
    ['茨の森', '茨鎧の森番', '森番', 3, 30, {}, ['ザク、ザク……。　「茨で行き止まりか。」', 'ガサ……ガサッ。　「ん？　茨が動いたぞ。」', 'ブルルッ！　「森番だ！　その茨、鎧だったのか！」'], 3],
    ['鉄門の関所', '鉄門の関守', '関守', 4, 40, {}, ['ジャラララ……。　「よし、門が開くぞ！」', 'ギギギ……ガシャン！　門の奥から、カツン……カツン……ダンッ！', '関守のひと踏みで、門の鎖が揺れる。　「明らかに今までより強そうだ！」'], 3],
    ['霧鏡の湖', '霧鏡の湖霊', '湖霊', 4, 50, { 4: ['1'] }, ['ヒュゥゥ……。霧の奥で、ぴちゃん。……ぴちゃん。　「水面に、馬が映ってる。」', 'そっと振り向く。　「……誰もいない。」', '背後で、ちゃぷ……。すぐ後ろで、ポチャン、、、すぐ後ろに何かいる…ブルルッ！　「……湖霊だ！」'], 3],
    ['刻砂の王墓', '刻砂の時守', '時守', 4, 80, { 4: ['1', '1'] }, ['ヒュオォ……。振り返ると、足跡が砂に消えていく。　「砂の王国……？　さっきもこの門を通ったぞ。」', '王墓の奥で、コン……コン……。大砂時計のガラスが内側から鳴る。　「なんだ、あれ……。砂が上に落ちてる？」', '――ドゴォンッ！　真横で砂が噴き上がり、黄金の馬が飛び出す！　「うわっ！　刻砂の時守だ！」'], 3],
    ['雷鳴峡', '雷鳴峡の迅雷', '迅雷', 5, 100, { 4: ['2', '2'], 5: ['2', '2'] }, ['ハァ……ハァ……。震える足で、吊り橋を踏む。ギシッ。　「やっと六戦……。少し、息を――」', 'ズドォン！ズドォンン！！ズドォン！そこらじゅうに落雷が落ちている…ズドドドォンッ！！　「うわっ！」', 'キィィン……。爆煙が晴れる。パチッ。青い火花が、たてがみを走る。　「……雷鳴峡の迅雷だ！」'], 3],
    ['氷晶砦', '氷晶砦の守将', '守将', 5, 130, { 5: ['2', '2', '2'] }, ['ヒュウゥ……。　「寒っ。息が真っ白だ。」', '門の裏で何かが。ズン、ズン…。ズシィンッ！「自分の足元まで揺れてるぞ……。」', '守将が頭をかがめて門をくぐる。蹄から足元へ、ピキピキピキッ！　「靴の先が凍っている！とてつもない大きさだ！」'], 3],
    ['紅蓮の鍛冶場', '紅蓮の鉄槌', '鉄槌', 6, 160, { 5: ['1', '1'], 6: ['1', '1'] }, ['カーン……カーン……。　「炉の奥で、誰かが鉄を打ってる。」', 'カン、カン、カカカンッ！　音が止まった…？火の向こうで、蹄が鉄をこする。ギリッ……。　「……来る。」', 'ガァンッ！　鉄床を蹴り、火花の幕を突き破って突進してくる！　「紅蓮の鉄槌だ！　来るぞ！」'], 3],
    ['星月の回廊', '星月の天馬', '天馬', 6, 190, { 5: ['1', '1', '1'], 6: ['1', '1', '1'] }, ['ふわり。　「白い羽……どこから？」', '夜空の星が、すうっと動く。　「あの星座、翼だ……！」', 'ファサ……バサッ、バサァッ！　風が頬を打つ。青い石床に、蹄がカツン。　「天馬が目の前に、こんなにデカいのか！」'], 3],
    ['黒曜の天文台', '黒曜の覇王', '覇王', 6, 220, { 5: ['1', 'k'], 6: ['1', 'k'] }, ['ギィ……クルクルクルッ。　「天球儀が、勝手に……！」', 'キリ……キリキリキリッ！　カチッ、カチッ、カチン！　金の輪が一直線に重なる。　「あれは…王冠？」', 'コツ……コツ……。紫水晶が低くうなる。ヴゥゥン……。ダンッ！　王冠の馬が光の中へ踏み出す。　「こいつが、黒曜の覇王か！」'], 3],
    ['日蝕の玉座', '日蝕の薔薇女王', '薔薇女王', 6, 250, { 4: ['1', 'k'], 5: ['1', 'k'], 6: ['1', 'k'] }, ['ギィィ……。　「ここが、最後の玉座か。」', 'ザワ……ザワザワッ。薔薇が一斉に揺れる。玉座の陰から、羽のこすれる音。ファサ……。　「……そこにいるのか。」', '一瞬、静まり返る。――バサァァッ！！　黒い翼が花びらを払い、女王の蹄が最後の一段を降りる。　薔薇女王「十一勝、お見事。あと一勝、取れるかしら？」', 'シャッ！　カードを構える。　「お前が最後だ！行くぞ！」'], 3]
  ].map(([a, n, s, w, c, rig, say, en], i) => ({ lv: i + 1, a: a, n: n, s: s, w: w, c: c, rig: rig, say: say, en: en, g: QG[i], m: QMAP[i] }));
  const QN = QUEST.length;
  const qp2 = n => String(n).padStart(2, '0');
  const qF = lv => `cb_q_f${qp2(lv)}.webp`, qE = lv => `cb_q_e${qp2(lv)}.webp`, qHL = lv => `cb_q_hl${qp2(lv)}.webp`;      
  const qTier = lv => (lv >= 10 ? 3 : lv >= 6 ? 2 : 1);      
  
  
  
  
  
  
  
  
  
  
  
  const QS_SR = 44100;
  const QSND = [
    { b: { ls: 132300, le: 438795 }, s: [{}], t: [null, 0] },                                  
    { b: { ls: 26901, le: 531405 }, s: [{}, {}], t: [0, 1] },                                  
    { b: { len: 352297 }, s: [{}, {}, { d: 0.8 }], t: [0, 1, 2] },                             
    { b: { ls: 372646, le: 712216 }, s: [{}, {}, {}], t: [2, 0, 1] },                          
    { b: { len: 353682 }, s: [{}, {}], t: [null, 0, 1] },                                      
    { b: { len: 352800 }, s: [{}, {}], t: [0, 0, 1] },                                         
    { b: { len: 353259 }, s: [{}], t: [null, 0, 0] },                                          
    { b: { len: 351477 }, s: [{}, {}], t: [null, 0, 1] },                                      
    { b: { ls: 0, le: Infinity }, s: [{}, {}], t: [null, 0, 1] },                              
    { b: { ls: 371971, le: 587387 }, s: [{}, {}], t: [null, 0, 1] },                           
    { b: { len: 1904321 }, s: [{}, {}], t: [0, 0, 1] },                                        
    { b: { len: 1839784, vol: 0.8 }, s: [{}, {}, { k: true }], t: [0, 1, 2, null] }            
  ];
  const QBG = QSND.map((x, i) => Object.assign({ file: `cb_q_bgm${qp2(i + 1)}.mp3`, vol: x.b.vol || 0.45, fin: 0.6, fout: 0.6 },
    x.b.len != null ? { pre: 0.5, len: x.b.len / QS_SR } : { ls: x.b.ls / QS_SR, le: x.b.le / QS_SR, at: 0 }));
  const qaFile = (lv, k) => `cb_q_se${qp2(lv)}${['a', 'b', 'c'][k]}.mp3`;      
  const qa = { lv: 0, buf: {}, cur: null, kept: [] };      
  const qaLog = (...a) => { const L = CBApp._sl; if (Array.isArray(L)) L.push(a); };      
  
  function qaLoad(lv) {
    const A = QSND[lv - 1], c = A && seOn() && typeof fetch === 'function' ? actx() : null;
    if (!c) return Promise.resolve();
    if (qa.lv !== lv) { qa.lv = lv; qa.buf = {}; }
    return Promise.all(A.s.map((x, k) => {
      const f = qaFile(lv, k);
      if (!qa.buf[f]) qa.buf[f] = fetch(f).then(r => (r.ok ? r.arrayBuffer() : null)).then(b => (b ? new Promise(ok => { try { const q = c.decodeAudioData(b, ok, () => ok(null)); if (q && q.catch) q.catch(() => ok(null)); } catch (e) { ok(null); } }) : null)).catch(() => null);
      return qa.buf[f];
    }));
  }
  
  function qaWait(p, ms, fn) { let done = false; const go = () => { if (!done) { done = true; fn(); } }; p.then(go, go); later(go, ms); }
  
  function qaPlay(i) {
    if (!qs) return;
    const lv = qs.lv, A = QSND[lv - 1], k = A ? A.t[i] : null;
    if (k != null && i > 0 && A.t[i - 1] === k) { qaLog('cont', qaFile(lv, k), i); return; }      
    qaStop(0.05);
    if (k == null || !seOn()) return;
    const c = actx(); if (!c) return;
    const x = A.s[k], f = qaFile(lv, k), me = { f: f, keep: !!x.k, s: null, g: null, at: c.currentTime + (x.d || 0), t0: 0, dead: false };
    qa.cur = me;
    (qa.lv === lv && qa.buf[f] ? qa.buf[f] : qaLoad(lv).then(() => qa.buf[f])).then(b => {
      if (me.dead || !b || !seOn() || !qs || qs.lv !== lv || qs.step === 'go' || screen !== 'qf') return;      
      try {
        const s = c.createBufferSource(), g = c.createGain(); s.buffer = b; g.gain.value = 0.9; s.connect(g); g.connect(c.destination);
        s.onended = () => { if (qa.cur === me) qa.cur = null; qa.kept = qa.kept.filter(z => z !== me); try { s.disconnect(); g.disconnect(); } catch (e) {   } };
        me.t0 = Math.max(c.currentTime, me.at); s.start(me.t0); me.s = s; me.g = g; qaLog('play', f, i, x.d || 0, me.keep);
      } catch (e) {   }
    });
  }
  
  
  
  
  
  function qaStop(fade, all) {
    const c = snd.ac, f = fade == null ? 0.05 : fade;
    const cut = o => {
      o.dead = true; if (!o.s || !c) return;
      const n = c.currentTime;
      if (n < o.t0) {      
        qaLog('drop', o.f);
        try { o.g.gain.cancelScheduledValues(n); o.g.gain.setValueAtTime(0, n); o.g.gain.value = 0; } catch (e) {   }
        try { o.s.onended = null; o.s.stop(); } catch (e) {   }
        try { o.s.disconnect(); o.g.disconnect(); } catch (e) {   }
        return;
      }
      qaLog('cut', o.f, f);
      try { o.g.gain.cancelScheduledValues(n); o.g.gain.setValueAtTime(o.g.gain.value, n); o.g.gain.linearRampToValueAtTime(0, n + f); o.s.stop(n + f + 0.02); }
      catch (e) { try { o.s.stop(); } catch (e2) {   } }
    };
    if (qa.cur) { if (qa.cur.keep && !all) qa.kept.push(qa.cur); else cut(qa.cur); qa.cur = null; }
    if (all) { qa.kept.forEach(cut); qa.kept = []; }
  }
  let qRun = null;              
  let lostQ = false;            
  let qs = null;                
  let qNew = 0;                 
  let qPop = 0;                 
  const qRoll = () => { const k = monthKey(); if (k <= st.q.m) return false; st.q = { m: k, clr: 0 }; save(); return true; };      
  const qOpen = () => Math.min(QN, st.q.clr + 1);              
  
  
  
  
  
  
  
  
  const QT = { max: 15, ms: 1800000 };      
  const QTM = () => Math.round(QT.ms / 60000);      
  const TKP = 'cb_q_tk.webp', TKI = `<img class="tki" src="${TKP}" alt="">`;      
  let qtTick = 0;                                      
  
  const QTG = { cut: [0, 24.616, 29.18, 33.768, 38.379, 44.364, 50.419, 55.17, 59.851, 64.718, 70.89, 77.038, 81.858, 86.656, 91.476, 100], right: 20.121, mid: 30.903, ar: 7.4549 };
  const qtT = () => nowD().getTime();
  function qtNow() {                                    
    const t = qtT(); let s = st.qt;
    if (!s) { s = st.qt = { n: QT.max, at: t }; save(); }
    if (s.n >= QT.max) { s.n = QT.max; return s; }
    if (t < s.at) { s.at = t; save(); return s; }      
    const k = Math.floor((t - s.at) / QT.ms);
    if (k > 0) { s.n = Math.min(QT.max, s.n + k); s.at = s.n >= QT.max ? t : s.at + k * QT.ms; save(); }
    return s;
  }
  function qtAdd(k) { const s = qtNow(), n0 = s.n; s.n = Math.min(QT.max, s.n + Math.max(0, Math.floor(+k || 0))); if (s.n !== n0) save(); return s.n - n0; }      
  const qtLeft = () => { const s = qtNow(); return s.n >= QT.max ? 0 : Math.max(0, QT.ms - (qtT() - s.at)); };      
  function qtUse() { const s = qtNow(); if (s.n < 1) return false; if (s.n >= QT.max) s.at = qtT(); s.n -= 1; save(); return true; }      
  const mmss = ms => { const x = Math.ceil(ms / 1000); return `${Math.floor(x / 60)}:${String(x % 60).padStart(2, '0')}`; };
  const qtWait = () => `切符が たまるまで あと ${mmss(qtLeft())}`;
  function qtPaint() {                                  
    if (!st || !ov || !ov.classList.contains('on')) return;
    const s = qtNow(), n = s.n, g = scr.qmap && $('.qtg', scr.qmap);
    if (g && screen === 'qmap') {
      const nb = $('.n', g); if (nb.textContent !== String(n)) nb.textContent = String(n);
      $('.f', g).style.clipPath = `inset(0 ${(100 - QTG.cut[n]).toFixed(3)}% 0 0)`;
      const rc = n < QT.max ? `次の 1枚 まで ${mmss(qtLeft())}` : ''; if ($('.rc', g).textContent !== rc) $('.rc', g).textContent = rc;
      g.setAttribute('aria-label', `調査隊切符 ${n}／${QT.max}枚${rc ? '・' + rc : ''}（タップで くわしく）`);
      const po = $('.qpo.op', scr.qmap);
      if (po) {
        const tk = $('.qpotk b', po); if (tk) tk.textContent = String(n);
        const go = $('[data-cb=qgo]', po); if (go) { go.disabled = n < 1; const w = $('small', go); if (w) w.textContent = n < 1 ? qtWait() : ''; }
      }
    }
    if (modOn()) {
      modEl.querySelectorAll('[data-qt]').forEach(b => { b.disabled = n < 1; const w = $('.qtw', b); if (w) w.textContent = n < 1 ? qtWait() : ''; });
      const ql = $('.qtl b', modEl); if (ql) ql.textContent = String(n);
      if (modEl.classList.contains('cbqtk')) { $('.qtkn b', modEl).textContent = String(n); $('.qtkr', modEl).textContent = n < QT.max ? `次の 1枚 まで あと ${mmss(qtLeft())}` : '満タン！（15枚）'; }
    }
  }
  const qtLine = lose => `<p class="qtl">${TKI}調査隊切符 のこり <b>${qtNow().n}</b>枚<small>${lose ? `（もう 一度 挑戦は 1枚・${QTM()}分で 1枚 たまる）` : `（連勝中は 使わないよ・${QTM()}分で 1枚 たまる）`}</small></p>`;      
  const qtBtn = (cb, label, cls) => `<button type="button" class="cbb${cls || ''}" data-cb="${cb}" data-qt="1"${qtNow().n < 1 ? ' disabled' : ''}>${label}<small class="qtw">${qtNow().n < 1 ? qtWait() : ''}</small></button>`;      
  function qtModal(lack) {                              
    const s = qtNow();
    modal(`<div class="qtkm"><img class="tk" src="cb_q_tk.webp" alt="調査隊切符">${lack ? '<h3 class="gold">切符が 足りないよ…</h3>' : ''}<p class="qtkn">調査隊切符 <b>${s.n}</b>／${QT.max}枚</p>`
      + `<p>エリアに <b>挑戦する とき 1枚</b> 使うよ<br><b>連勝中は 使わない</b>（負けて もう 一度 挑戦する ときは また 1枚）<br><b>${QTM()}分で 1枚</b> たまるよ（${QT.max}枚 まで）</p><p class="qtkr">${s.n < QT.max ? `次の 1枚 まで あと ${mmss(qtLeft())}` : `満タン！（${QT.max}枚）`}</p>`
      + '<div class="col"><button type="button" class="cbb dk" data-cb="modx">閉じる</button></div></div>', 'cbqtk');
  }
  
  function qRigText(cs) {
    if (!cs || !cs.length) return '';
    const n = {}; cs.forEach(k => { n[k] = (n[k] || 0) + 1; });
    const ks = Object.keys(n);
    return ks.length === 1 ? `${nameOf(ks[0])} が ${n[ks[0]]}枚` : ks.map(k => nameOf(k) + (n[k] > 1 ? ` ${n[k]}枚` : '')).join(' と ');
  }
  
  function qOpt(lv, n) {
    const t = typeof CBApp._qopt === 'function' ? CBApp._qopt(lv, n) : qEasy && testOn() ? { turns: 1, hands: [['k', '1', '1', '2', '2', '3', '3'], ['7', '7', '6', '6', '4', '4', '4']] } : null;
    const o = Object.assign({}, t || { rig: [[], (QUEST[lv - 1].rig[n] || []).slice()] });
    o.gems = [R.GEMS.slice(), []]; o.gpub = false;      
    o.gused = [qRun && qRun.gu ? qRun.gu.slice() : [], []];      
    return o;
  }

  
  function showQMap() {
    pk = null; closeMod(); qs = null; qPop = 0; qaStop(0.15, true); show('qmap'); msRoll(); qRoll(); bgmTrack('main');
    $('.qtt', scr.qmap).hidden = !(testOn() && window.CBTest.qHtml);      
    const op = qOpen(), all = st.q.clr >= QN;
    const ym = st.q.m.split('-');
    $('.qmst', scr.qmap).innerHTML = `${+ym[1]}月の 討伐 <b>${st.q.clr}</b>／${QN}` + (all ? '　<b>全部 討伐！</b>' : '');
    $('.qmft', scr.qmap).innerHTML = `${COINI}バトルコイン <b>${st.coin}</b>枚<small>毎月 1日に リセット（討伐した エリアも 最初から）</small>`;
    $('.qmap', scr.qmap).innerHTML = '<img src="cb_q_map.webp" alt="決戦調査の マップ">' + QUEST.map(q => {
      const done = q.lv <= st.q.clr, open = q.lv === op && !done, lock = q.lv > op || (q.lv === op && done);
      const cls = done ? 'dn' : open ? 'op' : 'lk';
      return `<button type="button" class="qnd ${cls}${q.lv === qNew ? ' nw' : ''}" data-cb="qarea" data-lv="${q.lv}" style="--x:${q.m[0]};--y:${q.m[1]}" aria-label="レベル${q.lv} ${esc(q.a)}（${done ? '討伐済み' : open ? '挑戦できる' : 'まだ 行けない'}）">`
        + `<i class="ring"></i>${lock && !done ? '<i class="lock" aria-hidden="true"></i>' : ''}${done ? '<i class="stamp" aria-hidden="true">討伐</i>' : ''}${open ? '<i class="go" aria-hidden="true">挑戦！</i>' : ''}</button>`;
    }).join('');
    qMapLayout(); qtPaint();      
    if (qNew) {
      const q = QUEST[qNew - 1]; qNew = 0;
      if (q && q.lv <= QN) { se('unlock'); toast(`🔓 レベル${q.lv}「${q.a}」が 開いたよ！`, 2.6); }
    }
    if (lostQ) { lostQ = false; toast('前の 決戦調査は 戦の 途中で 終わった ので、\n調査は 失敗に なったよ', 3.2); }
  }
  
  function qMapLayout() {
    if (screen !== 'qmap') return;
    const w0 = $('.qmw', scr.qmap), m = $('.qmap', scr.qmap), g = $('.qtg', scr.qmap), r = w0.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const w = Math.floor(Math.min(r.width - 8, (r.height - 6) / (1536 / 1024 + 1 / QTG.ar)));      
    m.style.width = w + 'px'; m.style.height = Math.round(w * 1536 / 1024) + 'px'; m.style.setProperty('--u', (w / 1024).toFixed(5) + 'px');
    if (g) { g.style.width = w + 'px'; g.style.height = (w / QTG.ar).toFixed(2) + 'px'; }
    qPopPlace();
  }
  
  
  function qArea(lv) {
    const q = QUEST[lv - 1]; if (!q || screen !== 'qmap') return;
    if (qRoll()) showQMap();      
    const m = $('.qmap', scr.qmap);
    if (qPop === lv && $('.qpo', m)) { se('tap', 0.5); return qPopClose(); }      
    const done = lv <= st.q.clr, open = lv === qOpen() && !done, go = done || open;      
    se('tap', go ? 1 : 0.6);
    const ns = Object.keys(q.rig), rig = ns.length ? q.rig[ns[0]] : null;      
    const body = (done ? `<p class="qpoi"><b>討伐済み！</b>　<b>${q.w}連勝</b>で もう 一度 討伐<small>討伐の バトルコインは 毎月 1回目 だけ（決戦調査ミッションは 数えるよ）</small></p>`
      : !open ? `<p class="qpoi">🔒 レベル${lv - 1}「${esc(QUEST[lv - 2].a)}」を<br>討伐すると 行けるよ</p>`
        : `<p class="qpoi"><b>${q.w}連勝</b>で 討伐！　${COINI}<b>${q.c}</b>枚</p>`)
      + (go ? (rig ? `<p class="qpor">⚠ ${ns.join('・')}戦目は 敵の 手札に 必ず ${esc(qRigText(rig))}</p>` : '')
          + `<p class="qpotk">${TKI}挑戦に 調査隊切符 1枚（今 <b>${qtNow().n}</b>枚）<small>連勝中は 使わないよ</small></p>` : '');      
    const bt = '<button type="button" class="cbb dk" data-cb="qpx">もどる</button>' + (go ? `<button type="button" class="cbb" data-cb="qgo" data-lv="${lv}"${qtNow().n < 1 ? ' disabled' : ''}>決戦調査に 行く<small>${qtNow().n < 1 ? qtWait() : ''}</small></button>` : '');
    qPopClose();
    const el = document.createElement('div');
    el.className = 'qpo' + (go ? ' op' : '');
    el.setAttribute('role', 'dialog'); el.setAttribute('aria-label', `レベル${lv} ${q.a}`);
    el.innerHTML = `<p class="qpoh"><small>レベル${lv}</small><b class="gold">${esc(q.a)}</b></p>${body}<div class="qpob">${bt}</div><i class="qpot" aria-hidden="true"></i>`;
    m.appendChild(el); qPop = lv;
    m.querySelectorAll('.qnd').forEach(n => n.classList.toggle('sel', +n.dataset.lv === lv));
    qPopPlace();
    if (go) qaLoad(lv);      
  }
  function qPopClose() {
    const m = scr.qmap && $('.qmap', scr.qmap); qPop = 0; if (!m) return;
    m.querySelectorAll('.qpo').forEach(e => e.remove());
    m.querySelectorAll('.qnd.sel').forEach(n => n.classList.remove('sel'));
  }
  
  function qPopPlace() {
    const m = scr.qmap && $('.qmap', scr.qmap), el = m && $('.qpo', m), q = QUEST[qPop - 1]; if (!el || !q) return;
    const W = m.clientWidth, H = m.clientHeight, u = W / 1024; if (!W || !H) return;
    const bw = Math.min(W - 16, 296); el.style.width = bw + 'px';
    const bh = el.offsetHeight, cx = q.m[0] * u, cy = q.m[1] * u, r = 36 * u, gap = 13;
    const up = cy - r - gap - bh >= 8 || cy + r + gap + bh > H - 8;
    const top = up ? Math.max(8, cy - r - gap - bh) : cy + r + gap, left = Math.max(8, Math.min(W - 8 - bw, cx - bw / 2));
    el.style.left = left + 'px'; el.style.top = top + 'px';
    el.classList.toggle('dn', !up);
    el.style.setProperty('--tx', Math.max(20, Math.min(bw - 20, cx - left)).toFixed(1) + 'px');
  }

  
  function qGo(lv) {
    if (qRoll()) { showQMap(); toast('月が 変わったので、決戦調査を リセットしたよ', 2.6); return; }      
    const q = QUEST[lv - 1]; if (!q || lv > qOpen()) return;      
    if (qtNow().n < 1) { se('tap', 0.5); return qtModal(true); }      
    closeMod(); qPopClose(); se('tap'); qaStop(0.15, true);
    qs = { lv: lv, step: 'say', i: -1, tw: null, g: GEN, rv: 0 };
    const f = scr.qf, pos = `left:${q.g[0] * 100}%;top:${q.g[1] * 100}%;width:${q.g[2] * 100}%`;
    
    
    
    $('.qfld', f).innerHTML = `<img class="bg" src="${qF(lv)}" alt=""><i class="qsh"></i><div class="qe" style="${pos}"><img class="q1" src="${qE(lv)}" alt=""><img class="q2" src="${qE(lv)}" alt=""></div><i class="qdu" style="${pos}"></i>`;
    $('.qfld', f).querySelectorAll('img').forEach(im => { try { if (im.decode) im.decode().catch(() => { }); } catch (e) {   } });
    $('.qfld', f).classList.remove('en');
    $('.qtel', f).classList.remove('on'); $('.qtel', f).innerHTML = `<div class="bd"><b class="gold">レベル${lv}の 敵 出現！</b><small>${lv <= st.q.clr ? `${q.w}連勝して もう 一度 討伐しよう！` : `${q.w}連勝して バトルコインを ${q.c}枚 手に入れよう！`}</small></div>`;
    $('.qnm', f).classList.remove('on'); $('.qnm', f).textContent = q.n;
    $('.qtap', f).classList.remove('on'); $('.qsay', f).classList.remove('on'); $('.qsay p', f).textContent = ''; $('.qsay p', f).style.webkitClipPath = ''; $('.qsay p', f).style.clipPath = '';
    f.classList.remove('in'); show('qf'); qFieldLayout(); bgmTrack('field', lv);      
    void f.offsetWidth; f.classList.add('in');
    { const im = new Image(); im.src = qHL(lv); }      
    try { if (typeof fetch === 'function') fetch(BGMS.quest.file).catch(() => { }); } catch (e) {   }
    const ld = qaLoad(lv);      
    later(() => { if (qs && qs.lv === lv && qs.i < 0 && screen === 'qf') qaWait(ld, 1500 * SPEED, () => { if (qs && qs.lv === lv && qs.i < 0 && screen === 'qf') qLine(0); }); }, 700 * SPEED);
  }
  
  function qFieldLayout() {
    if (screen !== 'qf') return;
    const w0 = $('.qfw', scr.qf), fl = $('.qfld', scr.qf), r = w0.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const w = Math.max(r.width, r.height * 941 / 1672), h = w * 1672 / 941;
    fl.style.width = w + 'px'; fl.style.height = h + 'px'; fl.style.left = ((r.width - w) / 2) + 'px'; fl.style.top = ((r.height - h) / 2) + 'px';
    qsRefit();      
  }
  
  
  
  
  
  
  function qLine(i) {
    const q = QUEST[qs.lv - 1], p = $('.qsay p', scr.qf), t = q.say[i];
    qs.i = i; $('.qsay', scr.qf).classList.add('on');
    if (qs.tw) unlater(qs.tw);
    p.style.fontSize = t.length > 54 ? '15px' : t.length > 36 ? '16px' : '';      
    p.textContent = t;                      
    qs.sy = { t: t, n: 0, m: null };        
    qsMeasure();
    if (!qs.sy.m) qs.sy.n = t.length;       
    qsClip(); qs.tw = null;
    const step = () => { if (!qs || qs.i !== i || !qs.sy || qs.sy.t !== t) return; qs.sy.n += 1; qsClip(); if (qs.sy.n < t.length) qs.tw = later(step, 34 * SPEED); else qs.tw = null; };
    if (qs.sy.n < t.length) step();
    qaPlay(i);                          
    if (i === q.en - 1) qReveal();      
  }
  
  function qsMeasure() {
    const sy = qs && qs.sy; if (!sy) return;
    sy.m = null;
    try {
      const p = $('.qsay p', scr.qf), tn = p.firstChild, pr = p.getBoundingClientRect();
      if (!tn || tn.nodeType !== 3 || tn.length !== sy.t.length || !pr.width || !pr.height || !p.offsetWidth) return;
      const k0 = pr.width / p.offsetWidth, rg = document.createRange(), n = sy.t.length, L = [], X = [], top = [], bot = [];      
      for (let k = 0; k < n; k++) {
        rg.setStart(tn, k); rg.setEnd(tn, k + 1);
        const rs = rg.getClientRects(), r = rs.length ? rs[rs.length - 1] : null;
        if (r && r.height > 0) {
          if (!top.length || r.top > top[top.length - 1] + r.height / 2) { top.push(r.top); bot.push(r.bottom); }      
          L.push(top.length - 1); X.push((r.right - pr.left) / k0);
        } else { L.push(Math.max(0, top.length - 1)); X.push(k > 0 && L[k - 1] === Math.max(0, top.length - 1) ? X[k - 1] : 0); }      
      }
      if (!top.length) return;
      const Y = top.map((v, l) => (l + 1 < top.length ? ((bot[l] + top[l + 1]) / 2 - pr.top) / k0 : p.offsetHeight + 8));
      sy.m = { L: L, X: X, Y: Y, W: p.offsetWidth, H: p.offsetHeight };
    } catch (e) { sy.m = null; }
  }
  
  function qsRefit() {
    if (screen !== 'qf' || !qs || !qs.sy || qs.step !== 'say') return;
    qsMeasure(); if (!qs.sy.m) qs.sy.n = qs.sy.t.length; qsClip();
  }
  
  function qsClip() {
    const sy = qs && qs.sy; if (!sy) return;
    const p = $('.qsay p', scr.qf), n = sy.n, B = 8, f = v => v.toFixed(2) + 'px';
    if (sy.m && n < sy.t.length && (p.offsetWidth !== sy.m.W || p.offsetHeight !== sy.m.H)) { qsMeasure(); if (!sy.m) sy.n = sy.t.length; }      
    const m = sy.m;
    let c = 'none';
    if (m && n < sy.t.length) {
      if (n <= 0) c = 'inset(0 100% 100% 0)';
      else {
        const l = m.L[n - 1], x = f(m.X[n - 1] + 0.5), y1 = f(m.Y[l]);
        c = l === 0 ? `polygon(${f(-B)} ${f(-B)}, ${x} ${f(-B)}, ${x} ${y1}, ${f(-B)} ${y1})`
          : `polygon(${f(-B)} ${f(-B)}, ${f(m.W + B)} ${f(-B)}, ${f(m.W + B)} ${f(m.Y[l - 1])}, ${x} ${f(m.Y[l - 1])}, ${x} ${y1}, ${f(-B)} ${y1})`;
      }
    }
    p.style.webkitClipPath = c; p.style.clipPath = c;
  }
  function qTap() {
    if (!qs || screen !== 'qf') return;
    const q = QUEST[qs.lv - 1];
    if (qs.step === 'say') {
      if (qs.i < 0) return qLine(0);
      if (qs.tw) { unlater(qs.tw); qs.tw = null; if (qs.sy) { qs.sy.n = qs.sy.t.length; qsClip(); } return; }      
      if (qs.i + 1 < q.say.length) return qLine(qs.i + 1);      
      return qEnd();
    }
    if (qs.step === 'en') return qBattle();
  }
  
  
  async function qReveal() {
    const f = scr.qf, lv = qs.lv; if (qs.rv) return;
    qs.rv = 1; $('.qtel', f).classList.add('on');
    await T(900); if (!qs || qs.lv !== lv || qs.rv !== 1) return;
    qShowEnemy();
  }
  function qShowEnemy() {
    const f = scr.qf; if (!qs || qs.rv === 2) return;
    qs.rv = 2; $('.qtel', f).classList.add('on'); $('.qfld', f).classList.add('en');
  }
  
  async function qEnd() {
    const f = scr.qf, lv = qs.lv, fresh = qs.rv !== 2;
    qShowEnemy();
    qs.step = 'en'; $('.qsay', f).classList.remove('on');
    await T(fresh ? 900 : 500); if (!qs || qs.lv !== lv || qs.step !== 'en') return;
    $('.qnm', f).classList.add('on');
    await T(500); if (!qs || qs.lv !== lv || qs.step !== 'en') return;
    $('.qtap', f).classList.add('on');
  }
  
  function qBattle() {
    if (!qs || qs.step !== 'en') return;
    if (qGone()) { qs = null; return; }      
    if (!qtUse()) { qs = null; showQMap(); qtModal(true); return; }      
    const lv = qs.lv; qs.step = 'go'; se('tap'); qaStop(0.05, true);     
    qRun = { lv: lv, won: 0, m: st.q.m, gu: [] };
    startMatch(CBNet.cpu(CBApp._rng || undefined, CBApp._think || undefined, qOpt(lv, 1)));
    bgmTrack('quest');
    toast(`調査隊切符を 1枚 使ったよ\n（のこり ${qtNow().n}枚）`, 1.8, TKP);      
  }
  
  function qHP(left, hit) {
    const q = qRun && QUEST[qRun.lv - 1], g = $('.qhp'); if (!q || !g) return;
    const pc = v => (Math.max(0, v) / q.w * 100).toFixed(3) + '%';
    if (g.dataset.lv !== String(q.lv)) {
      g.dataset.lv = String(q.lv);
      $('.l', g).setAttribute('src', qHL(q.lv)); $('.nm', g).textContent = q.n;
      $('.sg', g).innerHTML = Array.from({ length: q.w - 1 }, (_, i) => `<i style="left:${((i + 1) / q.w * 100).toFixed(3)}%"></i>`).join('');
    }
    const fill = $('.fill', g), dmg = $('.dmg', g);
    g.classList.toggle('ko', left <= 0);
    g.setAttribute('aria-label', `${q.n}の HP：のこり ${Math.max(0, left)}／${q.w}`);
    if (!hit) { g.classList.remove('hit'); fill.style.transition = dmg.style.transition = 'none'; fill.style.width = dmg.style.width = pc(left); void g.offsetWidth; fill.style.transition = dmg.style.transition = ''; return; }
    g.classList.remove('hit'); void g.offsetWidth; g.classList.add('hit');
    fill.style.width = pc(left); dmg.style.width = pc(left);
  }
  
  function qSettle(res) {
    const r = qRun, q = QUEST[r.lv - 1];
    st.ms.live = '';
    let ms = [], coin = 0, cleared = false, first = false, reset = false;
    msRoll();                                                 
    if (qRoll() || r.m !== st.q.m) { reset = true; r.dead = true; }      
    else if (res === 'win') {
      r.won += 1;
      ms = qmsWin(r);                                         
      if (r.won >= q.w) { cleared = true; first = q.lv > st.q.clr; coin = first ? q.c : 0; st.q.clr = Math.max(st.q.clr, q.lv); }      
    }
    const msc = ms.reduce((a, x) => a + x.c, 0), want = coin + msc, c0 = st.coin; addCoin(want);
    save();
    return Promise.resolve({ res: res, q: q, won: r.won, ms: ms, msc: msc, coin: coin, cleared: cleared, first: first, reset: reset, coins: st.coin, full: st.coin - c0 < want });
  }
  
  async function qEndShow(x) {
    ended = true;
    const no = gameNo, r = await (ends.shift() || qSettle(x.res)), q = r.q;
    if (no !== gameNo || !match) return;
    const msh = r.ms.map(m => `<div class="cbmsn" role="status" aria-label="決戦調査ミッション達成 決戦宝石を ${m.g}個 残して ${m.n}連勝 バトルコイン ${m.c}枚"><i aria-hidden="true">🎯</i><span>ミッション達成！</span><b>宝石 ${m.g}個 残して ${m.n}連勝</b>${COINI}<b>＋${m.c}枚</b></div>`).join('');      
    if (r.reset) {
      se('even');
      modal(`<h3 class="gold">月が 変わったよ</h3><p>決戦調査は 毎月 1日に リセット。<br>この 調査は ここまで（最初から 挑戦してね）</p><div class="gift">${msh}</div><div class="col"><button type="button" class="cbb" data-cb="qmapgo">マップへ</button></div>`, 'cbend qend');
      return;
    }
    if (x.res === 'win') {
      se('hit'); qHP(q.w - r.won, true);
      await banner(r.cleared ? '討伐！' : 'ダメージ！', r.cleared ? `${q.n}を 倒した！` : `${q.s}の HP が 減った！`, r.cleared ? 1300 : 1100);
      if (no !== gameNo || !match) return;
      if (r.cleared) return qVictory(r, msh);
      se('magic', 0.6);
      modal(`<h3 class="gold">勝利！</h3><div class="sc">${r.won}連勝<small>あと ${q.w - r.won}連勝で 討伐！</small></div><div class="gift">${qGemLeft()}${qtLine()}${msh}`
        + (r.ms.length ? `<div class="cbcl">${COINI}バトルコイン（今 ${r.coins}枚）</div>` : '') + '</div>'
        + `<div class="col"><button type="button" class="cbb" data-cb="qnext">第${r.won + 1}戦へ</button><button type="button" class="cbb dk" data-cb="qmapgo">マップへ 戻る<small>この 調査は ここまで</small></button></div>`, 'cbend qend');
      return;
    }
    if (x.res === 'lose') {
      se('over');
      modal(`<h3 class="gold">調査 失敗…</h3><div class="sc">${x.wins[0]} － ${x.wins[1]}<small>あなた － ${esc(q.s)}（勝った 数）${x.early ? `<br>${x.early}ターン目で 決着！` : ''}</small></div>`
        + `<div class="gift"><div>${esc(q.s)}に 負けた…。${r.won ? `${r.won}連勝で 止まったよ` : ''}</div><div>もう 一度 1戦目から 挑戦できるよ（決戦宝石も 5つに 戻るよ）</div>${qtLine(true)}${msh}</div>`
        + `<div class="col">${qtBtn('qretry', 'もう 一度 挑戦')}<button type="button" class="cbb dk" data-cb="qmapgo">マップへ</button></div>`, 'cbend qend');
      return;
    }
    se('even');
    modal(`<h3 class="gold">同点！</h3><div class="sc">${x.wins[0]} － ${x.wins[1]}<small>あなた － ${esc(q.s)}（勝った 数）</small></div>`
      + `<div class="gift"><div>同点は 負けじゃ ないよ。<br>第${r.won + 1}戦を やり直そう！（HP は そのまま）</div>${qGemLeft()}${qtLine()}${msh}</div>`
      + `<div class="col"><button type="button" class="cbb" data-cb="qnext">第${r.won + 1}戦を やり直す</button><button type="button" class="cbb dk" data-cb="qmapgo">マップへ 戻る<small>この 調査は ここまで</small></button></div>`, 'cbend qend');
  }
  
  function qGone() {
    if (!qRoll()) return false;
    if (qRun) qRun.dead = true;
    se('even');
    modal('<h3 class="gold">月が 変わったよ</h3><p>決戦調査は 毎月 1日に リセット。<br>この 調査は ここまで（最初から 挑戦してね）<br>調査隊切符は 使って いないよ</p><div class="col"><button type="button" class="cbb" data-cb="qmapgo">マップへ</button></div>', 'cbend qend');
    return true;
  }
  
  function qGemLeft() {
    const gu = qRun && qRun.gu ? qRun.gu : [], left = R.GEMS.filter(g => gu.indexOf(g) < 0);
    return `<div class="qgl">決戦宝石 のこり <b>${left.length}</b>／${R.GEMS.length}<span aria-hidden="true">${R.GEMS.map(g => `<img class="${gu.indexOf(g) >= 0 ? 'u' : ''}" src="${gemPic(g)}" alt="">`).join('')}</span></div>`;
  }
  
  function qNext(paid) {
    if (!qRun || qRun.dead || !match || !ended) return;
    if (!paid && qGone()) return;      
    se('tap'); closeMod();
    if (paid) toast(`調査隊切符を 1枚 使ったよ\n（のこり ${qtNow().n}枚）`, 1.8, TKP);
    match.setOpt(qOpt(qRun.lv, qRun.won + 1));
    match.again();
  }
  
  function qRetry() {
    if (!qRun || qRun.dead || !match || !ended) return;
    if (qGone()) return;      
    if (!qtUse()) { se('tap', 0.5); toast(qtWait(), 1.8, TKP); return qtPaint(); }      
    qRun.won = 0; qRun.m = st.q.m; qRun.gu = []; qHP(QUEST[qRun.lv - 1].w, false);      
    qNext(true);
  }
  
  
  async function qVictory(r, msh) {
    const q = r.q, t = qTier(q.lv), g = GEN;
    qNew = r.first && q.lv < QN ? q.lv + 1 : 0;      
    const rnd = (a, b) => a + Math.random() * (b - a);
    let parts = '';
    if (t >= 2) for (let i = 0; i < 26; i++) parts += `<i class="cf" style="left:${rnd(2, 98).toFixed(1)}%;--d:${rnd(0, 1.4).toFixed(2)}s;--r:${rnd(-540, 540).toFixed(0)}deg;--x:${rnd(-40, 40).toFixed(0)}px;--h:${rnd(0, 360).toFixed(0)}"></i>`;
    if (t >= 3) for (let i = 0; i < 16; i++) parts += `<img class="cn" src="cb_coin.webp" alt="" style="left:${rnd(4, 92).toFixed(1)}%;--d:${rnd(0.3, 2.2).toFixed(2)}s;--s:${rnd(0.7, 1.15).toFixed(2)}">`;
    modal(`<div class="qv t${t}"><i class="rays"></i>${t >= 3 ? '<i class="wave"></i><i class="wave w2"></i>' : ''}<i class="glow"></i>`
      + `<div class="en"><img src="${qE(q.lv)}" alt=""><b class="stamp">討伐</b></div>`
      + `<h3 class="gold">討伐成功！</h3><p class="sub">${esc(q.n)}を 倒した！${t >= 3 ? '<br><small>伝説の 敵に 勝ったよ！</small>' : ''}</p>`
      + (r.first ? `<div class="qget" role="status" aria-label="バトルコイン ${r.coin}枚 GET"><img class="ci" src="cb_coin.webp" alt=""><span><small>バトルコインを GETした！</small><b class="gold">＋<span class="n">0</span>枚</b></span></div>`
        : '<div class="qget re" role="status"><img class="ci" src="cb_coin.webp" alt=""><span><small>討伐の バトルコインは 毎月 1回目 だけ</small><b class="gold">今月は もう もらったよ</b></span></div>')
      + `<div class="gift qg2"><div class="cbcl">${COINI}今 ${r.coins}枚${r.full ? `（${COIN.max}枚 まで）` : ''}</div>${msh}</div>`
      + '<div class="col"><button type="button" class="cbb" data-cb="qmapgo">マップへ</button></div></div>'
      + (parts ? `<div class="qpt">${parts}</div>` : ''), 'qvic');
    se('qwin' + t);
    await T(1100); if (g !== GEN) return;
    const box = $('.qget', modEl); if (!box) return;
    box.classList.add('on'); if (r.first) se('coin');
    const n = $('.qget .n', modEl), steps = 12;
    if (n) for (let i = 1; i <= steps; i++) { await T(55); if (g !== GEN || !n.isConnected) return; n.textContent = String(Math.round(r.coin * i / steps)); }
    await T(250); if (g !== GEN) return;
    const g2 = $('.qg2', modEl); if (g2) g2.classList.add('on');
    if (r.ms.length) se('magic', 0.7);
  }
  function qToMap() { leave(false); showQMap(); }
  
  let qEasy = false;
  const qApi = {
    clr: () => { qRoll(); st.q.clr = Math.min(QN, st.q.clr + 1); save(); closeMod(); showQMap(); toast(`🧪 レベル${st.q.clr}を 討伐済みに したよ`, 2); },
    all: () => { qRoll(); st.q.clr = QN; save(); closeMod(); showQMap(); toast('🧪 全部 討伐済みに したよ', 2); },
    zero: () => { qRoll(); st.q.clr = 0; save(); closeMod(); showQMap(); toast('🧪 討伐を 0 に 戻したよ', 2); },
    next: () => { st.q.m = '2000-01'; qRoll(); closeMod(); showQMap(); toast('🧪 月が 変わった ことに したよ（決戦調査を リセット）', 2.4); },
    easy: () => { qEasy = !qEasy; closeMod(); showQMap(); toast(qEasy ? '🧪 戦を「1ターンで 勝てる 手札」に したよ' : '🧪 戦を いつもの 手札に 戻したよ', 2.4); },
    tk0: () => { st.qt = { n: 0, at: qtT() }; save(); closeMod(); showQMap(); toast(`🧪 調査隊切符を 0枚に したよ（${QTM()}分で 1枚 たまる）`, 2.4); },      
    tkf: () => { st.qt = { n: QT.max, at: qtT() }; save(); closeMod(); showQMap(); toast(`🧪 調査隊切符を ${QT.max}枚に したよ`, 2); }
  };

  
  function open() {
    build(); load();
    ov.classList.add('on');
    try { if (window.TengelWallet && window.TengelWallet.lockZoom) window.TengelWallet.lockZoom(true); } catch (e) {   }
    try { if (window.TengelFx && window.TengelFx.prime) window.TengelFx.prime(); } catch (e) {   }
    ['1', '2', '3', '4', '5', '6', '7', 'k', 'm', null].forEach(k => { const im = new Image(); im.src = pic(k); });
    if (st.back) { const im = new Image(); im.src = deckPic(); }
    boardImg();                                        
    actx(); applySets();                               
    showMenu();
    clearInterval(qtTick); qtTick = setInterval(qtPaint, 1000);      
  }
  function close() {
    clearInterval(qtTick); qtTick = 0;
    roomStop(); leave(true);
    if (ov) ov.classList.remove('on');
    qaStop(0.05, true); qa.lv = 0; qa.buf = {};      
    soundRest();
    try { if (window.TengelWallet && window.TengelWallet.lockZoom) window.TengelWallet.lockZoom(false); } catch (e) {   }
    try { document.dispatchEvent(new CustomEvent('tengel:cb')); } catch (e) {   }
  }
  
  
  document.addEventListener('tengel:cbgift', () => { if (!st || !takeGift()) return; if (ov && ov.classList.contains('on') && screen === 'menu' && !modOn()) showMenu(); });
  return {
    open, close, TK_BONUS, tkBonus, COIN, coinFor, coinBonus, MS, PACK, FACES, _rng: null, _randInt: null, _think: null, _link: null, _opt: null, _room: null, _guard: null, _as: null, _now: null, _sl: null,      
    _t: {      
      get view() { return V; }, get screen() { return screen; }, get match() { return match; }, get mode() { return mode; }, get state() { return st; }, get ended() { return ended; },
      get idle() { return !pumping && !queue.length && !busy && !lock; }, get tl() { return { my: TL.my && Object.assign({}, TL.my), op: TL.op && Object.assign({}, TL.op), on: !!TL.iv, max: tlMax(), SET_LIMIT: SET_LIMIT }; }, get ask() { return askOn(); }, say, get sets() { return { bgm: bgmOn(), se: seOn(), raw: { bgm: st.bgm, se: st.se }, as: AS }; },
      qopt: (lv, n) => qOpt(lv, n), qApi, qtPaint: () => qtPaint(), qGu: a => { if (qRun) qRun.gu = a.slice(); }, qmsWin: r => qmsWin(r), get qt() { return st ? Object.assign({ left: qtLeft() }, qtNow()) : null; }, get quest() { return { run: qRun ? Object.assign({}, qRun) : null, st: st ? Object.assign({}, st.q) : null, scene: qs ? { lv: qs.lv, step: qs.step, i: qs.i, typing: !!qs.tw, rv: qs.rv || 0, shown: qs.sy ? qs.sy.n : 0, len: qs.sy ? qs.sy.t.length : 0, cut: !!(qs.sy && qs.sy.m) } : null, data: QUEST, open: st ? qOpen() : 0, track: bg.trk }; },      
      get bgm() { return { on: !!bg.cur, want: bg.want, have: !!bg.buf, gone: bg.gone, pos: bgmPos(), len: BGM.len, pre: BGM.pre, vol: BGM.vol, file: BGM.file, loop: bg.cur ? [bg.cur.s.loopStart, bg.cur.s.loopEnd] : null, ctx: snd.ac ? snd.ac.state : null, off: bg.cur ? bg.cur.off : null, dur: bg.buf ? bg.buf.duration : null, trk: bg.trk }; },
      get qsnd() { return { lv: qa.lv, cur: qa.cur ? { f: qa.cur.f, keep: qa.cur.keep, on: !!qa.cur.s } : null, kept: qa.kept.map(o => o.f), have: Object.keys(qa.buf), data: QSND, bgs: QBG }; },      
      get mySets() { return mySets; }, setMySets: n => { mySets = Math.max(0, Math.floor(+n || 0)); },      
      setSet, speed: k => { SPEED = k; }, manual: on => { clk.manual = !!on; }, tick, get now() { return clk.now; }, start: m => startMatch(m), menu: () => { leave(false); showMenu(); }, settle, load, save, takeGift, modOn, pkDraw, pkPool, pkGroup, randInt, get pk() { return pk; }, dz: t => showDz(t), dzApi, msKey: () => monthKey(), msRoll, ms: tab => showMs(tab), pic
    }
  };
})();

;window.CBRules = CBRules; window.CBCpu = CBCpu; window.CBNet = CBNet; window.CBApp = CBApp;
