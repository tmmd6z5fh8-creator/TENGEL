








































































const CBRules = (() => {
  'use strict';
  const NUMS = ['1', '2', '3', '4', '5', '6', '7'], KINDS = NUMS.concat(['k', 'm']);
  const TURNS = 5, HAND = 7, COPIES = 4;      
  const power = k => (k === 'k' || k === 'm' ? 0 : +k);          
  
  function compare(a, b) {
    if (a === b) return 'clash';
    const pa = power(a), pb = power(b);
    return pa === pb ? 'tie' : pa < pb ? 0 : 1;
  }
  function shuffle(a, rng) {
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rng() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  const fullSet = () => { const a = []; NUMS.forEach(k => { for (let i = 0; i < COPIES; i++) a.push(k); }); a.push('k', 'm'); return a; };
  const mkP = () => ({ hand: [], set: null, wins: 0, known: [], eff: null });
  const count = (hand, k) => hand.reduce((n, c) => n + (c.k === k ? 1 : 0), 0);
  const idx = (hand, u) => hand.findIndex(c => c.u === u);

  function newGame(rng, opt) {
    rng = rng || Math.random; opt = opt || {};
    const tn = Math.floor(+opt.turns);
    const S = { v: 3, turn: 1, turns: tn >= 1 && tn <= 9 ? tn : TURNS, phase: 'set', uid: 0, deck: [], discard: [], p: [mkP(), mkP()], pend: null, win: null, last: null, res: null };
    let rest = fullSet();
    const take = k => { const j = rest.indexOf(k); if (j < 0) throw new Error('card ' + k); rest.splice(j, 1); return k; };
    if (opt.hands) {
      const hs = opt.hands.map(h => h.map(take));
      let dk;
      if (opt.deck) { dk = opt.deck.map(take); shuffle(rest, rng); dk = dk.concat(rest); } else dk = shuffle(rest, rng);
      
      for (let i = 0; i < 2; i++) S.p[i].hand = hs[i].map(k => ({ u: ++S.uid, k }));
      S.deck = dk.slice().reverse().map(k => ({ u: ++S.uid, k }));
    } else {
      S.deck = shuffle(rest, rng).map(k => ({ u: ++S.uid, k }));
      for (let n = 0; n < HAND; n++) for (let i = 0; i < 2; i++) S.p[i].hand.push(S.deck.pop());      
    }
    return S;
  }

  const forget = (S, u) => { S.p.forEach(P => { const j = P.known.indexOf(u); if (j >= 0) P.known.splice(j, 1); }); };
  const learn = (P, u) => { if (P.known.indexOf(u) < 0) P.known.push(u); };
  
  const toss = (S, c, by, why) => { forget(S, c.u); S.discard.push({ u: c.u, k: c.k, by: by, why: why, turn: S.turn }); };

  
  const unseen = (P, Q) => Q.hand.filter(c => P.known.indexOf(c.u) < 0);
  
  function canEff(S, i) {
    const P = S.p[i], Q = S.p[1 - i], sk = P.set ? P.set.c.k : null;
    return {
      e6: count(P.hand, '6') >= 2 && unseen(P, Q).length >= 1,                                                  
      e5: sk === '5' && P.hand.length >= 1 && P.hand.length - 1 >= S.turns - S.turn && S.deck.length >= 1,      
      e7: count(P.hand, '7') >= 3 && S.deck.length >= 3,
      e3: count(P.hand, '3') >= 3 && Q.hand.length >= 1,                                                        
      e4: sk === '4' && Q.hand.length >= 1
    };
  }
  const any = c => c.e6 || c.e5 || c.e7 || c.e3 || c.e4;
  
  
  function revWho(S, r) {
    if (r !== 0 && r !== 1) return null;
    const i = 1 - r, P = S.p[i], mk = P.set.c.k, wk = S.p[r].set.c.k;
    const hit = (mk === '1' && (wk === 'k' || wk === 'm')) || (mk === '2' && wk === '1');
    return hit && count(P.hand, mk) >= 2 && P.hand.length - 1 >= S.turns - S.turn ? i : null;
  }
  const NOUSE = () => ({ p6: null, u5: null, x7: false, x3: false, u4: false });

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
      P.set = { c: c, up: false, blind: false, open: false };
      ev.push({ e: 'set', who: i, u: c.u });
      if (S.p[0].set && S.p[1].set) afterSet(S, ev);
      return { ok: true, ev: ev };
    }
    if (a.t === 'eff') {                                 
      if (S.phase !== 'eff' || !P.eff || P.eff.done) return bad('eff');
      const can = P.eff.can, w = a.use && typeof a.use === 'object' ? a.use : {}, use = NOUSE();
      if (w.p6 != null) { if (!can.e6) return bad('e6'); if (idx(Q.hand, w.p6) < 0 || P.known.indexOf(w.p6) >= 0) return bad('pick'); use.p6 = w.p6; }      
      if (w.u5 != null) { if (!can.e5) return bad('e5'); if (idx(P.hand, w.u5) < 0) return bad('drop'); use.u5 = w.u5; }
      if (w.x7) {                                        
        if (!can.e7 || count(P.hand.filter(c => c.u !== use.u5), '7') < 3) return bad('e7');
        use.x7 = true;
      }
      if (w.x3) {                                        
        if (!can.e3 || count(P.hand.filter(c => c.u !== use.u5), '3') < 3) return bad('e3');
        use.x3 = true;
      }
      if (w.u4) { if (!can.e4) return bad('e4'); use.u4 = true; }
      P.eff.use = use; P.eff.done = true;
      ev.push({ e: 'effd', who: i });
      if (S.p[0].eff.done && S.p[1].eff.done) resolve(S, ev, rng);
      return { ok: true, ev: ev };
    }
    if (a.t === 'swap') {                                
      if (S.phase !== 'swap' || !S.pend || S.pend.who !== i) return bad('swap');
      const j = idx(P.hand, a.u); if (j < 0) return bad('card');
      const old = P.set.c, c = P.hand.splice(j, 1)[0];
      P.hand.push(old);
      P.set = { c: c, up: false, blind: false, open: false };
      S.pend = null;
      ev.push({ e: 'swap', who: i, u: c.u, back: old.u });
      open(S, ev);
      return { ok: true, ev: ev };
    }
    if (a.t === 'k') {                                   
      if (S.phase !== 'pre' || !S.pend || S.pend.type !== 'k' || S.pend.who !== i) return bad('k');
      if (a.pick == null) ev.push({ e: 'kskip', who: i });
      else {
        const j = idx(Q.hand, a.pick); if (j < 0 || P.known.indexOf(a.pick) >= 0) return bad('pick');      
        learn(P, Q.hand[j].u);
        ev.push({ e: 'k', who: i, pick: Q.hand[j].u, k: Q.hand[j].k });
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
        out.forEach(c => toss(S, c, i, 'm'));
        const drew = []; while (drew.length < 2 && S.deck.length) drew.push(S.deck.pop());
        drew.forEach(c => P.hand.push(c));
        ev.push({ e: 'm', who: i, drop: out.map(c => ({ u: c.u, k: c.k })), drew: drew.map(c => ({ u: c.u, k: c.k })) });
      }
      S.pend = null; S.phase = 'set';
      return { ok: true, ev: ev };
    }
    if (a.t === 'rev') {                                 
      if (S.phase !== 'rev' || !S.pend || S.pend.type !== 'rev' || S.pend.who !== i) return bad('rev');
      let r = S.pend.res;
      if (a.use) {
        const k = P.set.c.k, kn = c => (Q.known.indexOf(c.u) >= 0 ? 1 : 0);
        const same = P.hand.filter(c => c.k === k).sort((x, y) => kn(y) - kn(x) || x.u - y.u);      
        if (same.length < 2) return bad('rev');
        const drop = same[0], keep = same[1];
        P.hand.splice(P.hand.indexOf(drop), 1); toss(S, drop, i, k);
        learn(Q, keep.u);                                
        r = i;
        ev.push({ e: 'rev', who: i, k: k, show: [drop.u, keep.u], drop: { u: drop.u, k: drop.k }, beat: Q.set.c.k });
      } else ev.push({ e: 'revskip', who: i });
      S.pend = null;
      score(S, r, !!a.use);
      ev.push({ e: 'fin', turn: S.turn, res: r, wins: [S.p[0].wins, S.p[1].wins], rev: !!a.use });
      endTurn(S, ev);
      return { ok: true, ev: ev };
    }
    return bad('type');
  }

  
  function afterSet(S, ev) {
    const c0 = canEff(S, 0), c1 = canEff(S, 1);
    if (!any(c0) && !any(c1)) { open(S, ev); return; }
    S.phase = 'eff';
    S.p[0].eff = { can: c0, done: !any(c0), use: null };
    S.p[1].eff = { can: c1, done: !any(c1), use: null };
    ev.push({ e: 'efft', has: [any(c0), any(c1)] });
  }
  
  function resolve(S, ev, rng) {
    const U = S.p.map(P => (P.eff && P.eff.use) || NOUSE());
    [0, 1].forEach(i => {                                
      const P = S.p[i], Q = S.p[1 - i]; if (U[i].p6 == null) return;
      const j = idx(Q.hand, U[i].p6), six = P.hand.filter(c => c.k === '6').slice(0, 2);
      if (j < 0 || six.length < 2) { ev.push({ e: 'fizz', who: i, k: '6' }); return; }      
      six.forEach(c => learn(Q, c.u));
      learn(P, Q.hand[j].u);
      ev.push({ e: 'p6', who: i, six: six.map(c => c.u), pick: Q.hand[j].u, k: Q.hand[j].k });
    });
    [0, 1].forEach(i => {                                
      const P = S.p[i]; if (U[i].u5 == null) return;
      const d = idx(P.hand, U[i].u5);
      if (d < 0 || !P.set || P.set.c.k !== '5' || S.deck.length < 1) { ev.push({ e: 'fizz', who: i, k: '5' }); return; }
      const five = P.set.c, drop = P.hand.splice(d, 1)[0];
      toss(S, five, i, '5'); toss(S, drop, i, '5');
      P.set = { c: S.deck.pop(), up: false, blind: true, open: false };
      ev.push({ e: 'u5', who: i, five: { u: five.u, k: five.k }, drop: { u: drop.u, k: drop.k } });
    });
    [0, 1].forEach(i => {                                
      const P = S.p[i]; if (!U[i].x7) return;
      const back = P.hand.filter(c => c.k === '7').slice(0, 3);
      if (back.length < 3 || S.deck.length < 3) { ev.push({ e: 'fizz', who: i, k: '7' }); return; }
      P.hand = P.hand.filter(c => back.indexOf(c) < 0);
      const drew = [S.deck.pop(), S.deck.pop(), S.deck.pop()];
      drew.forEach(c => P.hand.push(c));
      back.forEach(c => { forget(S, c.u); S.deck.push({ u: ++S.uid, k: c.k }); });      
      shuffle(S.deck, rng);
      ev.push({ e: 'x7', who: i, n: 3, drew: drew.map(c => ({ u: c.u, k: c.k })) });
    });
    [0, 1].forEach(i => {                                
      const P = S.p[i], Q = S.p[1 - i]; if (!U[i].x3) return;
      const three = P.hand.filter(c => c.k === '3').slice(0, 3);
      if (three.length < 3 || Q.hand.length < 1) { ev.push({ e: 'fizz', who: i, k: '3' }); return; }
      const give = three[0], take = Q.hand[Math.floor(rng() * Q.hand.length)];
      P.hand.splice(P.hand.indexOf(give), 1); Q.hand.splice(Q.hand.indexOf(take), 1);
      P.hand.push(take); Q.hand.push(give);
      forget(S, give.u); forget(S, take.u);              
      three.slice(1).forEach(c => learn(Q, c.u));        
      learn(P, give.u);                                  
      learn(Q, take.u);                                  
      ev.push({ e: 'x3', who: i, three: three.map(c => c.u), give: { u: give.u, k: give.k }, take: { u: take.u, k: take.k } });
    });
    S.p.forEach(P => { P.eff = null; });
    const A = S.p[0], B = S.p[1], f0 = U[0].u4 && A.set.c.k === '4', f1 = U[1].u4 && B.set.c.k === '4';      
    if (f0 && f1) { A.set.up = B.set.up = true; ev.push({ e: 'first2' }); open(S, ev); return; }      
    if (f0 || f1) {
      const w = f0 ? 0 : 1, F = S.p[w], O = S.p[1 - w];
      F.set.up = true;
      ev.push({ e: 'first', who: w });
      if (O.hand.length >= 1) { S.phase = 'swap'; S.pend = { type: 'swap', who: 1 - w }; return; }
    }
    open(S, ev);
  }
  function open(S, ev) {
    const c0 = S.p[0].set.c, c1 = S.p[1].set.c, r = compare(c0.k, c1.k), cs = [{ u: c0.u, k: c0.k }, { u: c1.u, k: c1.k }];
    S.p.forEach(P => { P.set.up = true; P.set.blind = false; P.set.open = true; P.eff = null; });
    const rv = revWho(S, r);
    if (rv != null) {                                    
      S.phase = 'rev'; S.pend = { type: 'rev', who: rv, res: r };
      ev.push({ e: 'open', turn: S.turn, c: cs, res: r, wins: [S.p[0].wins, S.p[1].wins], rev: rv });
      return;
    }
    score(S, r, false);
    ev.push({ e: 'open', turn: S.turn, c: cs, res: r, wins: [S.p[0].wins, S.p[1].wins] });
    endTurn(S, ev);
  }
  
  function score(S, r, rev) {
    const c0 = S.p[0].set.c, c1 = S.p[1].set.c;
    if (r === 0 || r === 1) S.p[r].wins += 1;
    S.last = { turn: S.turn, c: [c0.k, c1.k], res: r, rev: !!rev };
    
    S.win = null;
    if ((r === 0 || r === 1) && S.turn < S.turns) { const wk = r === 0 ? c0.k : c1.k; if (wk === 'k' || wk === 'm') S.win = { type: wk, who: r }; }
  }
  function endTurn(S, ev) {
    S.p.forEach((P, i) => { if (P.set) { toss(S, P.set.c, i, 't'); P.set = null; } P.eff = null; });
    S.pend = null;
    ev.push({ e: 'clear' });
    if (S.turn >= S.turns) {
      const a = S.p[0].wins, b = S.p[1].wins;
      S.phase = 'end'; S.res = a > b ? 0 : b > a ? 1 : 'draw';
      ev.push({ e: 'end', wins: [a, b], res: S.res });
      return;
    }
    S.turn += 1; S.phase = 'set';
    ev.push({ e: 'turn', n: S.turn });
    const w = S.win; S.win = null;
    if (w) {
      const Wn = S.p[w.who], Ls = S.p[1 - w.who];
      if ((w.type === 'k' && unseen(Wn, Ls).length >= 1) || (w.type === 'm' && Wn.hand.length >= 2 && S.deck.length >= 1)) {      
        S.phase = 'pre'; S.pend = { type: w.type, who: w.who };
        ev.push({ e: 'pre', who: w.who, type: w.type });
      }
    }
  }

  
  function view(S, i) {
    const P = S.p[i], Q = S.p[1 - i];
    const setOf = (X, mine) => {
      if (!X.set) return null;
      const c = X.set.c, o = { u: c.u, k: null, up: X.set.up, blind: X.set.blind, open: !!X.set.open };
      if (mine) o.k = X.set.blind ? null : c.k;
      else if (X.set.up || (!X.set.blind && P.known.indexOf(c.u) >= 0)) o.k = c.k;
      return o;
    };
    const ce = S.phase === 'eff' && P.eff && !P.eff.done ? P.eff.can : null;
    return {
      v: 3, me: i, turn: S.turn, turns: S.turns, phase: S.phase, deckN: S.deck.length,
      discard: S.discard.map(d => ({ k: d.k, mine: d.by === i, why: d.why, turn: d.turn })),
      my: { hand: P.hand.map(c => ({ u: c.u, k: c.k, seen: Q.known.indexOf(c.u) >= 0 })), set: setOf(P, true), wins: P.wins },
      op: { hand: Q.hand.map(c => ({ u: c.u, k: P.known.indexOf(c.u) >= 0 ? c.k : null })), set: setOf(Q, false), wins: Q.wins },
      can: { set: S.phase === 'set' && !P.set, eff: ce ? { e6: ce.e6, e5: ce.e5, e7: ce.e7, e3: ce.e3, e4: ce.e4 } : null },
      pend: S.pend ? { type: S.pend.type, mine: S.pend.who === i } : null,
      wait: (S.phase === 'set' && !!P.set && !Q.set) || (S.phase === 'eff' && !!P.eff && P.eff.done && !!Q.eff && !Q.eff.done) || (!!S.pend && S.pend.who !== i),
      last: S.last ? { turn: S.last.turn, c: i === 0 ? S.last.c.slice() : [S.last.c[1], S.last.c[0]], res: S.last.res === 0 || S.last.res === 1 ? (S.last.res === i ? 'win' : 'lose') : S.last.res, rev: !!S.last.rev } : null,
      res: S.phase === 'end' ? (S.res === 'draw' ? 'draw' : S.res === i ? 'win' : 'lose') : null
    };
  }

  
  function evFor(ev, i) {
    return ev.map(x => {
      const o = { e: x.e };
      if (x.who != null) o.me = x.who === i;
      if (x.e === 'x7') { o.n = x.n; if (x.who === i) o.drew = x.drew; }
      else if (x.e === 'set' || x.e === 'swap') { if (x.who === i) { o.u = x.u; if (x.back != null) o.back = x.back; } }
      else if (x.e === 'efft') { o.mine = x.has[i]; o.other = x.has[1 - i]; }
      else if (x.e === 'p6') { o.six = x.six; o.pick = x.pick; if (x.who === i) o.k = x.k; }
      else if (x.e === 'u5') { o.five = x.five; o.drop = x.drop; }
      else if (x.e === 'x3') { o.three = x.three; o.give = x.give; o.take = x.take; }      
      else if (x.e === 'fizz') o.k = x.k;
      else if (x.e === 'open') { o.turn = x.turn; o.my = x.c[i]; o.op = x.c[1 - i]; o.res = x.res === 0 || x.res === 1 ? (x.res === i ? 'win' : 'lose') : x.res; o.wins = [x.wins[i], x.wins[1 - i]]; if (x.rev != null) o.rev = x.rev === i ? 'me' : 'op'; }      
      else if (x.e === 'rev') { o.k = x.k; o.show = x.show; o.drop = x.drop; o.beat = x.beat; }      
      else if (x.e === 'fin') { o.turn = x.turn; o.res = x.res === i ? 'win' : 'lose'; o.wins = [x.wins[i], x.wins[1 - i]]; o.rev = !!x.rev; }
      else if (x.e === 'pre') o.type = x.type;
      else if (x.e === 'k') { o.pick = x.pick; if (x.who === i) o.k = x.k; }
      else if (x.e === 'm') { o.drop = x.drop; o.n = x.drew.length; if (x.who === i) o.drew = x.drew; }
      else if (x.e === 'turn') o.n = x.n;
      else if (x.e === 'end') { o.wins = [x.wins[i], x.wins[1 - i]]; o.res = x.res === 'draw' ? 'draw' : x.res === i ? 'win' : 'lose'; }
      return o;
    });
  }

  
  function legal(S, i) {
    const v = view(S, i), out = [];
    if (v.can.set) out.push('set');
    if (v.can.eff) out.push('eff');
    if (v.pend && v.pend.mine) out.push(v.pend.type);
    return out;
  }

  return { NUMS, KINDS, TURNS, HAND, COPIES, power, compare, shuffle, newGame, act, view, evFor, legal };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = CBRules;

;
















const CBCpu = (() => {
  'use strict';
  const power = k => (k === 'k' || k === 'm' ? 0 : +k);
  const byStrong = hand => hand.slice().sort((a, b) => power(a.k) - power(b.k) || a.u - b.u);      
  const pick = (a, rng) => a[Math.floor(rng() * a.length)];

  function decide(v, rng) {
    rng = rng || Math.random;
    if (!v || v.phase === 'end') return null;
    const hand = v.my.hand, opHand = v.op.hand;
    if (v.pend && v.pend.mine) {
      if (v.pend.type === 'swap') {
        const s = byStrong(hand), win = s.filter(c => power(c.k) < 4);
        if (win.length) return { t: 'swap', u: win[win.length - 1].u };
        const four = s.find(c => c.k === '4'); if (four) return { t: 'swap', u: four.u };
        return { t: 'swap', u: s[s.length - 1].u };
      }
      if (v.pend.type === 'k') {
        const un = opHand.filter(c => c.k == null);
        return { t: 'k', pick: un.length ? pick(un, rng).u : null };
      }
      if (v.pend.type === 'm') {
        const s = byStrong(hand);
        return { t: 'm', drop: [s[s.length - 1].u, s[s.length - 2].u] };
      }
      if (v.pend.type === 'rev') return { t: 'rev', use: true };      
      return null;
    }
    if (v.can.eff) {                                     
      const c = v.can.eff, use = {}, s = byStrong(hand), n7 = hand.filter(x => x.k === '7').length, n3 = hand.filter(x => x.k === '3').length;
      if (c.e6) { const un = opHand.filter(x => x.k == null); if (un.length) use.p6 = pick(un, rng).u; }
      if (c.e7) use.x7 = true;
      if (c.e3 && rng() < (v.turn >= 2 ? 0.55 : 0.35)) use.x3 = true;
      if (c.e5) {
        
        const cand = s.filter(x => !(use.x7 && x.k === '7' && n7 <= 3) && !(use.x3 && x.k === '3' && n3 <= 3)), weak = cand[cand.length - 1];
        if (weak && ((!use.x7 && !use.x3) || (use.x7 && weak.k === '7') || (use.x3 && weak.k === '3') || power(weak.k) >= 5)) use.u5 = weak.u;
      }
      if (c.e4 && (v.turn >= v.turns ? true : v.turn >= 2 ? rng() < 0.5 : false)) use.u4 = true;
      return { t: 'eff', use: use };
    }
    if (v.phase !== 'set' || !v.can.set) return null;
    const s = byStrong(hand), left = v.turns - v.turn + 1;          
    const top = s.slice(0, Math.min(left, s.length));
    if (hand.length - 2 >= v.turns - v.turn && hand.length - 1 >= 1 && v.deckN >= 1) {          
      const third = top[top.length - 1], five = s.find(x => x.k === '5');
      if (five && power(third.k) >= 5) return { t: 'set', u: five.u };
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
  const R = CBRules, PROTO = 4, MAXLEN = 20000;      
  
  const STAKE_MAX = 999;
  function stakeOf(k) {
    const e = Math.max(0, Math.min(STAKE_MAX, Math.floor(+(k && k.e) || 0)));
    const w = Math.max(e, Math.min(e * 2, Math.floor(+(k && k.w) || 0)));
    return { e: e, w: e > 0 ? w : 0 };
  }
  const say = (m, k, v) => { try { if (typeof m[k] === 'function') m[k](v); } catch (e) {   } };

  
  
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
    m.start = () => { if (!alive) return; S = R.newGame(rng, opt); m.wantAgain = [false, false]; n = 0; push([{ e: 'deal' }]); };      
    m.act = a => Promise.resolve(apply(0, a));
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

  
  function host(link, rng, opt, stake) {
    rng = rng || Math.random;
    const stk = stakeOf(stake);
    const mm = parent('host', rng, m => {
      let hello = false, joined = false, closed = false, want = false;
      const send = o => { if (!closed) link.send(JSON.stringify(o)); };
      
      const deal = m.start; m.start = () => { want = true; if (joined) deal(); };
      link.onText = txt => {
        if (closed || typeof txt !== 'string' || txt.length > MAXLEN) return;
        let o; try { o = JSON.parse(txt); } catch (e) { return; }
        if (!o || typeof o !== 'object') return;
        if (o.t === 'hello') { if (o.v !== PROTO) { send({ t: 'hello', v: PROTO }); m._.end('ver'); return; } if (!hello) { hello = true; send({ t: 'hello', v: PROTO, stake: stk }); say(m, 'onState', 'ready'); } return; }
        if (!hello) return;
        if (o.t === 'join') {                           
          const k = stakeOf(o.stake);
          if (!joined && k.e === stk.e && k.w === stk.w) { joined = true; say(m, 'onState', 'joined'); if (want) deal(); }
          return;
        }
        if (o.t === 'bye') { m._.end('bye'); return; }
        if (!joined) return;
        if (o.t === 'act') { const r = m._.apply(1, o.a); send({ t: 'ack', id: o.id, ok: r.ok, why: r.why }); }
        else if (o.t === 'again') m._.seatAgain();
      };
      link.onLost = () => { if (!closed) m._.end('lost'); };
      return {
        up: u => send({ t: 'up', n: u.n, ev: u.ev, view: u.view }),
        again: () => send({ t: 'again' }),
        stop: mine => { if (closed) return; if (mine) send({ t: 'bye' }); closed = true; setTimeout(() => { try { link.close(); } catch (e) {   } }, mine ? 250 : 0); }
      };
    }, opt);
    mm.stake = stk;
    return mm;
  }

  
  function guest(link) {
    let alive = true, id = 0, hello = false;
    const wait = {};
    const m = { kind: 'guest', me: 1, onUpdate: null, onState: null, stake: null };
    const send = o => { if (alive) link.send(JSON.stringify(o)); };
    const end = why => { if (!alive) return; alive = false; Object.keys(wait).forEach(k => wait[k]({ ok: false, why: 'off' })); try { link.close(); } catch (e) {   } say(m, 'onState', why); };
    link.onText = txt => {
      if (!alive || typeof txt !== 'string' || txt.length > MAXLEN) return;
      let o; try { o = JSON.parse(txt); } catch (e) { return; }
      if (!o || typeof o !== 'object') return;
      if (o.t === 'hello') { if (o.v !== PROTO) end('ver'); else if (!hello) { hello = true; m.stake = stakeOf(o.stake); say(m, 'onState', 'ready'); say(m, 'onState', 'stake'); } }      
      else if (o.t === 'up' && o.view && Array.isArray(o.ev)) say(m, 'onUpdate', { n: o.n, ev: o.ev, view: o.view });
      else if (o.t === 'ack') { const f = wait[o.id]; if (f) { delete wait[o.id]; f({ ok: !!o.ok, why: o.why }); } }
      else if (o.t === 'again') say(m, 'onState', 'again');
      else if (o.t === 'bye') end('bye');
    };
    link.onLost = () => end('lost');
    m.start = () => send({ t: 'hello', v: PROTO });
    m.join = () => { if (hello && m.stake) send({ t: 'join', stake: m.stake }); };      
    m.act = a => new Promise(ok => { if (!alive) return ok({ ok: false, why: 'off' }); id += 1; wait[id] = ok; send({ t: 'act', id: id, a: a }); });
    m.idle = () => { };
    m.again = () => send({ t: 'again' });
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

  return { PROTO, STAKE_MAX, stakeOf, cpu, host, guest, nativeRoom };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = CBNet;

;

































const CBApp = (() => {
  'use strict';
  const R = CBRules, SK = 'tengel.cb';
  const REWARD = { win: 1, every: 5, bonus: 3 };
  const COIN = { win: 1, every: 5, bonus: 5, max: 9999 };      
  const coinFor = streak => (streak > 0 && streak % COIN.every === 0 ? COIN.bonus : COIN.win);
  const COINI = '<img class="cbci" src="cb_coin.webp" alt="">';      
  const STAKE_CHIPS = [0, 1, 2, 3, 5, 10, 20, 30, 50, 100];      
  const NAMES = { k: '神様馬', m: '幻の馬' };
  const nameOf = k => NAMES[k] || String(k);
  const pic = (k, big) => 'cb_' + (big ? 'c' : 's') + (k == null ? 'b' : k) + '.webp';
  const power = R.power;
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  let SPEED = 1;                                       
  
  const clk = { manual: false, now: 0, q: [] };
  function later(fn, ms) { if (!clk.manual) return setTimeout(fn, ms); const o = { at: clk.now + Math.max(0, ms), fn: fn }; clk.q.push(o); return o; }
  function unlater(h) { if (h && typeof h === 'object') { const i = clk.q.indexOf(h); if (i >= 0) clk.q.splice(i, 1); } else clearTimeout(h); }
  function tick(ms) {
    clk.now += ms; let n = 0;
    for (;;) { const due = clk.q.filter(o => o.at <= clk.now).sort((a, b) => a.at - b.at)[0]; if (!due) break; clk.q.splice(clk.q.indexOf(due), 1); due.fn(); n++; }
    return n;
  }
  const T = ms => new Promise(ok => later(ok, Math.max(0, ms * SPEED)));
  const reduce = () => !fxOn() || !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);      

  
  let st = null;
  const DEF = () => ({ v: 1, streak: 0, win: 0, lose: 0, draw: 0, owe: 0, bgm: null, se: null, fx: null, coin: 0, stake: null });
  let lostStake = 0;                                   
  function load() {
    try { const s = JSON.parse(localStorage.getItem(SK) || 'null'); st = Object.assign(DEF(), s && s.v === 1 ? s : {}); } catch (e) { st = DEF(); }
    ['streak', 'win', 'lose', 'draw', 'owe'].forEach(k => { st[k] = Math.max(0, Math.floor(+st[k] || 0)); });
    ['bgm', 'se', 'fx'].forEach(k => { st[k] = st[k] === true || st[k] === false ? st[k] : null; });      
    st.coin = Math.max(0, Math.min(COIN.max, Math.floor(+st.coin || 0)));      
    
    const k = st.stake; st.stake = null;
    if (k && typeof k === 'object' && Math.floor(+k.e) > 0) { lostStake = Math.floor(+k.e); save(); }
  }
  const addCoin = n => { st.coin = Math.max(0, Math.min(COIN.max, st.coin + Math.floor(+n || 0))); };
  function save() { try { localStorage.setItem(SK, JSON.stringify(st)); } catch (e) {   } }
  const rewardFor = streak => (streak > 0 && streak % REWARD.every === 0 ? REWARD.bonus : REWARD.win);
  
  async function pay() {
    if (!(st.owe > 0) || typeof window.TCGift !== 'function') return null;
    const want = st.owe; let r = null;
    try { r = await window.TCGift(want); } catch (e) { r = null; }
    if (!r) return null;                               
    st.owe = 0; save();                                
    return { want: want, add: r.add, stock: r.stock, max: r.max };
  }
  
  
  async function settle(res) {
    let got = 0, coin = 0, pot = null; const cpu = !!match && match.kind === 'cpu', k = st.stake;
    if (res === 'win') { st.win += 1; st.streak += 1; got = rewardFor(st.streak); st.owe += got; if (cpu) coin = coinFor(st.streak); }
    else if (res === 'lose') { st.lose += 1; st.streak = 0; }
    else st.draw += 1;
    if (k) { pot = { e: k.e, w: k.w, add: res === 'win' ? k.w : res === 'draw' ? k.e : 0 }; st.stake = null; }
    const want = coin + (pot ? pot.add : 0), c0 = st.coin; addCoin(want);
    save();
    const p = got ? await pay() : null;
    return { res: res, got: got, pay: p, streak: st.streak, coin: coin, pot: pot, coins: st.coin, full: st.coin - c0 < want };
  }
  
  function payStake() {
    const k = match && match.stake; st.stake = null;
    if (k && k.e > 0) { st.coin = Math.max(0, st.coin - k.e); st.stake = { e: k.e, w: k.w }; }
    save();
  }

  
  
  
  
  
  
  const SE = ['deal', 'set', 'flip', 'win', 'lose', 'even', 'magic', 'tap', 'fanfare', 'over', 'join'];
  const snd = { ac: null, buf: {} };
  const AS = (() => { try { return !!(navigator.audioSession && 'type' in navigator.audioSession); } catch (e) { return false; } })();
  const appSound = () => { try { const g = window.TengelFx && window.TengelFx.get ? window.TengelFx.get() : null; return g ? g.sound !== false : true; } catch (e) { return true; } };
  const seOn = () => (st && st.se != null ? st.se : appSound());
  const bgmOn = () => (st && st.bgm != null ? st.bgm : appSound() && (AS || !!CBApp._as));
  const fxOn = () => !(st && st.fx === false);
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
  
  
  
  
  
  
  
  const BGM = { file: 'cb_bgm.m4a', pre: 0.5, len: 34 * 3 * 60 / 76, vol: 0.55, fin: 1.4, fout: 0.45 };      
  const bg = { raw: null, buf: null, dec: null, cur: null, tau: 0, gone: false, want: false };
  function bgmLoad() {
    if (bg.buf || bg.gone) return Promise.resolve(bg.buf);
    if (bg.dec) return bg.dec;
    const c = actx(); if (!c || typeof fetch !== 'function') return Promise.resolve(null);
    if (!bg.raw) bg.raw = fetch(BGM.file).then(r => (r.ok ? r.arrayBuffer() : null)).catch(() => null);
    bg.dec = bg.raw.then(b => (b ? new Promise(ok => { try { const q = c.decodeAudioData(b.slice(0), ok, () => ok(null)); if (q && q.catch) q.catch(() => ok(null)); } catch (e) { ok(null); } }) : null)).then(b => {
      bg.dec = null;
      if (b && b.duration > BGM.len + BGM.pre) bg.buf = b; else if (!b) { bg.gone = true; bg.raw = null; } else bg.gone = true;
      return bg.buf;
    });
    return bg.dec;
  }
  const bgmPos = () => (bg.cur && snd.ac ? (bg.tau + Math.max(0, snd.ac.currentTime - bg.cur.t0)) % BGM.len : bg.tau);      
  function bgmStart() {
    const c = snd.ac; if (!c || bg.cur || !bg.buf) return;
    try {
      const s = c.createBufferSource(), g = c.createGain(), n = c.currentTime;
      s.buffer = bg.buf; s.loop = true; s.loopStart = BGM.pre / 2; s.loopEnd = BGM.pre / 2 + BGM.len;
      let off = BGM.pre + bg.tau; if (off >= BGM.pre / 2 + BGM.len) off -= BGM.len;
      g.gain.setValueAtTime(0, n); g.gain.linearRampToValueAtTime(BGM.vol, n + BGM.fin);
      s.connect(g); g.connect(c.destination); s.start(0, off); bg.cur = { s: s, g: g, t0: n };
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
    const want = !!ov && ov.classList.contains('on') && !document.hidden && bgmOn();
    bg.want = want;
    if (!want) { bgmStop(BGM.fout); return; }
    if (bg.cur) return;
    if (!actx()) return;
    bgmLoad().then(b => { if (b && bg.want && !bg.cur) bgmStart(); });
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
#cbOv.nofx .cbfire{animation:none;opacity:.88}
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

#cbOv .cbroom{align-items:center;justify-content:center;gap:12px;padding-left:22px;padding-right:22px;text-align:center}
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
#cbOv .cbact{flex:none;height:48px;overflow:hidden;display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:nowrap;padding:4px 10px 6px;box-sizing:border-box}
#cbOv .cbact .cbb{flex:0 1 auto;white-space:nowrap}

#cbOv .cbfly{position:absolute;inset:0;pointer-events:none;z-index:5}
#cbOv .cbfl{position:absolute;border-radius:6.5% / 4.3%;will-change:transform;filter:drop-shadow(0 4px 6px rgba(0,0,0,.5))}
#cbOv .cbban{position:absolute;left:0;right:0;top:38%;z-index:6;text-align:center;pointer-events:none;opacity:0;transform:scale(.8);transition:opacity .22s,transform .22s}
#cbOv .cbban.on{opacity:1;transform:none}
#cbOv .cbban .bd{padding:6px 0 8px;background:linear-gradient(90deg,rgba(0,0,0,0),rgba(10,6,3,.86) 16%,rgba(10,6,3,.86) 84%,rgba(0,0,0,0))}
#cbOv .cbban b{display:inline-block;font-size:34px;line-height:1.2;letter-spacing:.06em}
#cbOv .cbban small{display:block;font-size:13px;font-weight:700;color:#fff1cf;margin-top:2px;text-shadow:0 1px 3px #000}

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
#cbOv .cbb.lg{min-height:58px;border-radius:29px;font-size:19px;padding:8px 10px}
#cbOv .cbmod .three{display:flex;justify-content:center;gap:8px}
#cbOv .cbmod .three .cbc{width:min(24vw,104px)}
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
#cbOv .cbend .gift{min-height:186px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;font-size:14px;line-height:1.6;color:#fff1cf}
#cbOv .cbend .gift b{color:#ffe07a;font-size:17px}
#cbOv .cbget{display:inline-flex;align-items:center;gap:14px;box-sizing:border-box;min-width:250px;padding:11px 24px 12px 18px;border-radius:22px;border:2.5px solid #ffd76a;background:linear-gradient(180deg,#5a3a12 0%,#3a240a 55%,#2a1806 100%);box-shadow:0 0 0 1.5px rgba(60,30,0,.7),0 0 22px rgba(255,210,90,.6),inset 0 1px 0 rgba(255,240,190,.35),inset 0 0 14px rgba(255,200,80,.22);animation:cbget .55s cubic-bezier(.3,1.5,.5,1) both}
#cbOv .cbget .tk{flex:none;font-style:normal;font-size:42px;line-height:1;filter:drop-shadow(0 2px 3px rgba(0,0,0,.55))}
#cbOv .cbget .tx{display:block;text-align:left}
#cbOv .cbget small{display:block;font-size:13.5px;font-weight:700;line-height:1.3;color:#ffe9b0}
#cbOv .cbend .gift .cbget .n{display:block;font-size:31px;line-height:1.15;letter-spacing:.03em}
@keyframes cbget{from{transform:scale(.5);opacity:0}to{transform:none;opacity:1}}
#cbOv .cbtoast{position:absolute;left:50%;top:calc(var(--sat,env(safe-area-inset-top)) + 54px);z-index:9;transform:translate(-50%,-8px);width:max-content;max-width:86%;box-sizing:border-box;padding:9px 16px;border-radius:16px;background:rgba(20,12,6,.94);border:1.5px solid #c9a35a;color:#fff1cf;font-size:13.5px;font-weight:700;line-height:1.5;text-align:center;white-space:pre-line;box-shadow:0 6px 16px rgba(0,0,0,.5);opacity:0;pointer-events:none;transition:opacity .2s,transform .2s}
#cbOv .cbtoast.on{opacity:1;transform:translate(-50%,0)}

#cbOv .cbhelp{padding-left:0;padding-right:0}
#cbOv .cbhelp .hd{flex:none;height:48px;display:flex;align-items:center;gap:8px;padding:0 12px}
#cbOv .cbhelp .hd b{flex:1;text-align:center;font-size:17px;color:#ffe9a8;margin-right:64px}
#cbOv .cbhelp .bd{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;padding:4px 18px 26px;font-size:13.5px;line-height:1.75;color:#f0dfb6}
#cbOv .cbhelp h4{margin:16px 0 6px;font-size:15px;color:#ffe2a0;border-left:4px solid #e2a83e;padding-left:8px}
#cbOv .cbhelp ul{margin:0;padding-left:1.2em}#cbOv .cbhelp li{margin:2px 0}
#cbOv .cbhelp .ord{display:flex;align-items:center;justify-content:center;gap:1px;margin:8px -6px}
#cbOv .cbhelp .ord img{flex:0 1 30px;min-width:0;width:30px;height:auto;aspect-ratio:2/3}#cbOv .cbhelp .ord i{flex:none;font-style:normal;color:#c9a35a;font-size:11px}
#cbOv .cbhelp .ef{display:flex;gap:10px;align-items:flex-start;margin:8px 0;padding:8px;border-radius:12px;background:rgba(255,236,190,.06);border:1px solid rgba(255,226,160,.22)}
#cbOv .cbhelp .ef img{flex:none;width:58px;height:87px}
#cbOv .cbhelp .ef b{display:block;color:#ffe9a8;font-size:14px}
#cbOv .cbhelp .ef strong{color:#ffe9a8}
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
#cbOv .cbstk .blk>small{display:block;font-size:11.5px;line-height:1.45;color:#d9c08c;margin-bottom:7px}
#cbOv .cbstk .chips{display:flex;flex-wrap:wrap;gap:6px}
#cbOv .cbstk .chips button{min-width:44px;height:40px;box-sizing:border-box;border-radius:20px;border:1.5px solid #c9a35a;background:#1b1209;color:#ffe9a8;font-size:15px;font-weight:700;padding:0 8px}
#cbOv .cbstk .chips button.on{background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206;border-color:#f7d27c}
#cbOv .cbstp{display:flex;align-items:center;justify-content:center;gap:14px}
#cbOv .cbstp button{width:48px;height:42px;border-radius:14px;border:1.5px solid #c9a35a;background:linear-gradient(180deg,#3a2616,#22150b);color:#ffe9a8;font-size:20px;font-weight:700;padding:0}
#cbOv .cbstp button:disabled{opacity:.35}
#cbOv .cbstp>b{min-width:74px;text-align:center;font-size:26px;line-height:1;color:#ffe07a}
#cbOv .cbstp>b small{font-size:13px;font-weight:400;color:#d9c08c;margin-left:2px}
#cbOv .cbstkl{margin:0;font-size:14px;color:#f0dfb6}#cbOv .cbstkl b{color:#ffe07a;font-size:16px}
#cbOv .cbmod .cbstkv{font-size:16px;line-height:1.5;color:#f0dfb6}
#cbOv .cbmod .cbstkv b{color:#ffe07a;font-size:21px}#cbOv .cbmod .cbstkv i{font-style:normal;color:#c9a35a;margin:0 8px}
#cbOv .cbmod .cbhave b{color:#ffe07a;font-size:16px}#cbOv .cbmod .cbhave strong{color:#ffb38a}
#cbOv .cbmod.cbjoin{background:rgba(8,5,2,.93)}
#cbOv .cbend .gift .cbcl b{color:#ffe07a;font-size:15.5px}
@media (prefers-reduced-motion: reduce){#cbOv .cbglow.on{animation:none}#cbOv .cbhand .cbc.new{animation:none}#cbOv .cbflip .in{transition:none}#cbOv .cbget{animation:none}#cbOv .cbfire{animation:none;opacity:.88}}
#cbOv.nofx .cbglow.on{animation:none}#cbOv.nofx .cbhand .cbc.new{animation:none}#cbOv.nofx .cbflip .in{transition:none}#cbOv.nofx .cbget{animation:none}
#cbOv.nofx .cbban,#cbOv.nofx .cbres,#cbOv.nofx .cbvs .sd,#cbOv.nofx .cbhand .cbc,#cbOv.nofx .cbtoast{transition:none}
`;
  let ov = null, built = false, scr = {}, flyEl = null, modEl = null, toastEl = null, banEl = null;
  const $ = (s, r) => (r || ov).querySelector(s);
  function build() {
    if (built) return; built = true;
    const s = document.createElement('style'); s.id = 'cbCss'; s.textContent = css; document.head.appendChild(s);
    ov = document.createElement('div'); ov.id = 'cbOv'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'TENGERカードバトル');
    ov.innerHTML = '<div class="cbbg"><div class="cbfire"></div></div>'
      + '<section class="cbs cbmenu" data-s="menu"><button type="button" class="cbb dk sm cbx" data-cb="close">← もどる</button>'
      + '<img class="lg" src="cb_logo.webp" alt=""><h1 class="gold"><small>TENGER</small>カードバトル</h1><p class="rec"></p><p class="cbcoinl"></p>'
      + '<div class="btns"><button type="button" class="cbb" data-cb="cpu">コンピュータと 対戦</button>'
      + '<div class="row"><button type="button" class="cbb" data-cb="host">部屋を 作る<small>友だちと 対戦</small></button><button type="button" class="cbb" data-cb="join">部屋に 入る<small>友だちと 対戦</small></button></div>'
      + '<div class="row two"><button type="button" class="cbb dk" data-cb="help">あそび方</button><button type="button" class="cbb dk" data-cb="gear">設定<small>BGM・効果音</small></button></div></div></section>'
      + '<section class="cbs cbroom" data-s="room"></section>'
      + '<section class="cbs cbgame" data-s="game">'
      + '<div class="cbtop"><button type="button" class="cbb dk sm" data-cb="quit">やめる</button><div class="cbturn"></div><button type="button" class="cbb dk sm" data-cb="help" aria-label="あそび方">？</button></div>'
      + '<div class="cbmidw"><div class="cbopp"><div class="cbohand"></div><div class="cbwho"><b></b><span class="cbpips" data-p="op"></span></div></div>'
      + '<div class="cbboard"><img src="cb_board.webp" alt=""><div class="cbfire"></div><div class="cbglow"></div>'
      + '<div class="cbdeck"><img src="cb_deck.webp" alt=""><b class="cbn"></b></div>'
      + '<button type="button" class="cbdis" data-cb="discard" aria-label="捨て札を 見る"><span class="pl"></span><b class="cbn"></b></button>'
      + '<div class="cbslot op"></div><div class="cbslot my"></div>'
      + '<button type="button" class="cbgear" data-cb="gear" aria-label="メニュー"></button></div>'
      + '<div class="cbmsg" aria-live="polite"></div>'
      + '<div class="cbme"><div class="cbwho"><b>あなた</b><span class="cbpips" data-p="my"></span></div></div>'
      + '<div class="cbhand"></div><div class="cbact"></div></div></section>'
      + '<section class="cbs cbhelp" data-s="help"></section>'
      + '<div class="cbfly"></div><div class="cbban"></div><div class="cbmod" role="dialog" aria-modal="true"></div><div class="cbtoast" aria-live="polite"></div>';
    document.body.appendChild(ov);
    ov.querySelectorAll('.cbs').forEach(e => { scr[e.dataset.s] = e; });
    flyEl = $('.cbfly'); modEl = $('.cbmod'); toastEl = $('.cbtoast'); banEl = $('.cbban');
    ov.addEventListener('click', onClick);
    document.addEventListener('visibilitychange', () => { if (ov.classList.contains('on')) bgmSync(); });      
    window.addEventListener('resize', () => { if (ov.classList.contains('on')) layout(); });
    if (window.ResizeObserver) new ResizeObserver(() => { if (ov.classList.contains('on')) layout(); }).observe(scr.game);
  }
  let screen = '';
  function show(name) { screen = name; Object.keys(scr).forEach(k => scr[k].classList.toggle('on', k === name)); }
  let toastT = 0;
  function toast(t, sec) {
    toastEl.textContent = t;
    
    const m = screen === 'game' ? $('.cbmsg') : null;
    if (m && m.getBoundingClientRect().height) { const r = m.getBoundingClientRect(), o = ov.getBoundingClientRect(); toastEl.style.top = Math.max(60, r.top - o.top - 6) + 'px'; } else toastEl.style.top = '';
    toastEl.classList.add('on');
    unlater(toastT); toastT = later(() => toastEl.classList.remove('on'), (sec || 2.4) * 1000 * Math.max(SPEED, 0.2));
  }
  async function banner(big, small, ms) {
    banEl.innerHTML = `<div class="bd"><b class="gold">${esc(big)}</b>${small ? `<small>${esc(small)}</small>` : ''}</div>`; banEl.classList.add('on');
    await T(ms || 900); banEl.classList.remove('on'); await T(180);
  }

  
  function showMenu() {
    closeMod(); show('menu');
    const tot = st.win + st.lose + st.draw;
    $('.rec', scr.menu).innerHTML = (tot ? `<b>${st.win}</b>勝 <b>${st.lose}</b>敗 <b>${st.draw}</b>分` + (st.streak > 0 ? `　いま <b>${st.streak}</b>連勝！` : '') + '<br>' : '')
      + `勝つと お世話トークン <b>${REWARD.win}</b>こ・<b>${REWARD.every}</b>連勝 ごとに <b>${REWARD.bonus}</b>こ`;
    $('.cbcoinl', scr.menu).innerHTML = `${COINI}<span>バトルコイン <b>${st.coin}</b>枚</span><small>コンピュータに 勝つと ${COIN.win}枚・${COIN.every}連勝 ごとに ${COIN.bonus}枚</small>`;
    if (lostStake > 0) { const nn = lostStake; lostStake = 0; toast(`前の 対戦が とちゅうで 終わった ので、\n参加コイン ${nn}枚は もどらなかったよ`, 3.6); }
    const can = !!(window.__NATIVE && window.TengelNative);
    scr.menu.querySelectorAll('[data-cb=host],[data-cb=join]').forEach(b => { b.disabled = !can; });
    pay().then(p => { if (p && p.add > 0 && screen === 'menu') toast(`🎟 前の 対戦の ごほうび\nお世話トークン ${p.add}こを 受け取ったよ`, 3.2); });
  }

  
  let helpBack = 'menu';
  function showHelp(from) {
    helpBack = from || 'menu'; closeMod();
    const ef = (k, t, d) => `<div class="ef"><img src="${pic(k)}" alt=""><div><b>${t}</b>${d}</div></div>`;
    scr.help.innerHTML = '<div class="hd"><button type="button" class="cbb dk sm" data-cb="helpx">← もどる</button><b>あそび方</b></div><div class="bd">'
      + `<h4>勝負の しかた</h4><ul><li>手札は <b>${R.HAND}まい</b>。<b>${R.TURNS}ターン</b>で 勝負するよ</li><li>${R.TURNS}ターン 終わって、<b>勝った 数が 多い 人の 勝ち</b>（同じ なら 同点）。先に 勝ちが 決まっても、さいごの ターンまで やるよ</li><li>出すのは 1ターンに 1まい。${R.HAND - R.TURNS}まいは 使わずに のこるよ</li></ul>`
      + '<h4>1ターンの 流れ</h4><ul><li><b>① セット</b>：手札から 1まい えらんで「この カードを セットする」。ふせて 出すよ。<b>セットしたら もう 変えられない</b></li>'
      + '<li><b>② 効果タイム</b>：2人とも セットしたら、使える 効果が ある 人に「効果を 使う？」と 聞くよ。<b>「使う」「使わない」は 自分で えらべる</b>。2人とも 決めたら、いっしょに 効果が 出る</li>'
      + '<li><b>③ オープン</b>：2まいを いっしょに めくる。<b>強い カードの 勝ち</b>（1・2 の「<b>逆転勝利</b>」は、めくった あとに 使うか えらぶよ）</li></ul>'
      + '<h4>カードの 強さ</h4><div class="ord">' + ['k', 'm'].map(k => `<img src="${pic(k)}" alt="${nameOf(k)}">`).join('<i>＝</i>') + ['1', '2', '3', '4', '5', '6', '7'].map(k => `<i>＞</i><img src="${pic(k)}" alt="${k}">`).join('') + '</div>'
      + '<ul><li><b>神様馬</b>と <b>幻の馬</b>が いちばん 強い（この 2まいが ぶつかったら 引き分け）</li><li>数字は <b>1 が いちばん 強くて、7 が いちばん 弱い</b></li><li><b>同じ 数字</b>が ぶつかったら「かぶり」＝<b>どちらも 負け</b></li><li><b>逆転勝利</b>：1 が 3まい あれば 神様馬・幻の馬に、2 が 3まい あれば 1 に 勝てる（下の「カードの 効果」）</li><li>カードは ぜんぶで 30まい（1〜7 が 4まい ずつ・神様馬 1まい・幻の馬 1まい）</li></ul>'
      + '<h4>カードの 効果</h4><ul><li><b>7・6・5・4・3</b> の 効果は、2人とも セットした あとの「<b>効果タイム</b>」で、使うか えらぶよ</li><li><b>1・2</b> の 効果（逆転勝利）は、<b>オープンした あと</b>、負けた 人が 使うか えらぶよ</li><li><b>神様馬・幻の馬</b>の 効果は、勝った <b>次の ターンの はじめ</b>に、使うか えらぶよ</li><li>どの 効果も、<b>使うか 使わないかは 自分で えらべる</b>よ</li></ul>'
      + ef('7', '7：3まい そろえて 交換', '手札に 7 が 3まい あれば、3まいを 山札に もどして、新しく 3まい 引けるよ。')
      + ef('6', '6：2まい 見せて 手札を 見る', '手札に 6 が 2まい あれば、その 2まいを 相手に 見せて、相手の 手札を 1まい えらんで 見られるよ。<br>相手の 手札が <strong>もう 見た カード だけ</strong>の ときは 使えないよ（見るのは まだ 見て いない カード）。')
      + ef('5', '5：2まい 捨てて 山札から セット', '5 を セットしたら、その 5 と 手札 1まいを 捨てて、山札から 1まいを ふせて セットできるよ。何が 出るかは オープンまで わからない！<br>使えるのは、使った あとの 手札が <strong>のこりの ターンの 数より 少なく ならない とき</strong> だけ（さいごの ターンは、手札が 1まい あれば 使える）。')
      + ef('4', '4：見せて 強制交換', '4 を セットして 効果を 使うと、4 を 先に 見せる かわりに、相手は セットした カードを 手札の 別の カードと 交換しないと いけないよ（2人とも 使ったら 打ち消し）。')
      + ef('3', '3：3まい 見せて 手札を 交換', '手札に 3 が 3まい あれば、その 3まいを 相手に 見せて、その うちの 1まいと、相手の 手札から <strong>ランダムに えらんだ 1まい</strong>を 交換できるよ。')
      + ef('2', '2：3まい 見せて 逆転勝利', '2 を 出して <strong>1 に 負けた</strong> とき、手札に 2 が 2まい あれば（場の 2 と 合わせて 3まい）、その 2まいを 相手に 見せて、1まい 捨てると、<strong>勝ちに できる</strong>よ。')
      + ef('1', '1：3まい 見せて 逆転勝利', '1 を 出して <strong>神様馬・幻の馬に 負けた</strong> とき、手札に 1 が 2まい あれば（場の 1 と 合わせて 3まい）、その 2まいを 相手に 見せて、1まい 捨てると、<strong>勝ちに できる</strong>よ。<br>1・2 とも、使えるのは 捨てた あとの 手札が <strong>のこりの ターンの 数より 少なく ならない とき</strong> だけ。')
      + ef('k', '神様馬：勝ったら 手札を 見る', '神様馬で 勝ったら、次の ターンの はじめに、相手の 手札を 1まい えらんで 見られるよ（まだ 見て いない カードが ある とき）。')
      + ef('m', '幻の馬：勝ったら 手札を 交換', '幻の馬で 勝ったら、次の ターンの はじめに、手札を 2まい 捨てて、山札から 2まい 引けるよ。')
      + '<ul><li>手札の 数は「セットした あと」で 数えるよ（セットした カードは 手札に 入らない）</li><li>効果タイムで 効果が 出る 順番は <b>6 → 5 → 7 → 3 → 4</b></li><li>さいごの ターンに 神様馬・幻の馬で 勝った ときは、次の ターンが ない ので 効果は ないよ</li></ul>'
      + '<h4>見た カード・見られた カード</h4><ul><li>効果で 見た 相手の カードは、相手の 手札に ある あいだ 表で 見えるよ</li><li>相手に 見られた 自分の カードには 目の しるしが つくよ</li></ul>'
      + '<h4>捨て札</h4><ul><li>ボードの「<b>捨て札</b>」を タップすると、捨て札を 見られるよ</li><li><b>終わった ターンの 捨て札</b>（2人が 出した カード）と、<b>効果で 捨てた カード</b>に 分けて 出るよ</li></ul>'
      + `<h4>ごほうび</h4><ul><li>勝つと <b>お世話トークン ${REWARD.win}こ</b></li><li><b>${REWARD.every}連勝</b> ごとに <b>${REWARD.bonus}こ</b>（負けると 連勝は 0 に もどるよ。同点は そのまま）</li><li>お世話トークンは 25こ まで。対戦の とちゅうで やめると 負けに なるよ</li></ul>`
      + `<h4>バトルコイン</h4><ul><li><b>コンピュータに 勝つと ${COIN.win}枚</b>・<b>${COIN.every}連勝 ごとに ${COIN.bonus}枚</b> もらえるよ。<b>買う ことは できない</b>よ</li>`
      + '<li>友だちと 対戦する 部屋を 作る とき、<b>参加コイン</b>と <b>勝者の 獲得コイン</b>（参加コインの 2倍 まで）を 決められるよ</li><li>部屋に 入る 人は、同じ 数の 参加コインを 持って いないと 入れないよ</li>'
      + '<li>2人とも はじめに 参加コインを 出す。<b>勝った 人は、テンゲルから 獲得コインを プレゼントで もらえる</b>。同点は 参加コインが もどる</li><li><b>とちゅうで やめると、参加コインは もどらない</b>（つながりが 切れた ときは もどるよ）</li></ul>'
      + '<h4>音と エフェクト（設定）</h4><ul><li>ボードの 右下の <b>歯車</b>（メニューでは「設定」）を 押すと、<b>BGM</b>・<b>効果音</b>・<b>エフェクト</b>（光や 動きの 演出）を オン／オフ できるよ</li></ul>'
      + '<h4>友だちと 対戦（部屋）</h4><ul><li>1人が「部屋を 作る」→ 出て きた <b>部屋番号（4けた）</b>を 友だちに 教える</li><li>友だちは「部屋に 入る」で その 番号を 入れる</li><li><b>近くに いる 友だち</b>と、iPhone どうしで 直接 つながるよ（インターネットは 使わない）。2人とも Wi‑Fi か Bluetooth を オンに してね</li><li>はじめて 使う とき「ローカルネットワーク」の 確認が 出たら「許可」を 押してね</li></ul>'
      + '</div>';
    show('help');
  }

  
  let room = null;                                     
  function roomNumber() { let n = 0; try { const a = new Uint16Array(1); crypto.getRandomValues(a); n = a[0]; } catch (e) { n = Math.floor(Math.random() * 65536); } return String(1000 + n % 9000); }
  
  
  function showRoom(mode, keep) {
    const old = keep && room && room.stake ? room.stake : null;
    closeMod(); roomStop();
    room = { mode: mode, code: mode === 'host' ? (CBApp._room || roomNumber()) : '', nr: null, tm: 0, step: '', stake: old || { e: 0, w: 0 } };
    if (mode === 'host' && !old && st.coin > 0) { room.step = 'stake'; paintRoom(); show('room'); return; }
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
      const k = r.stake, maxE = Math.min(st.coin, CBNet.STAKE_MAX), chips = STAKE_CHIPS.filter(q => q <= maxE);
      h += '<h2 class="gold">部屋を 作る</h2><p>参加コインと、勝った 人が もらう コインを 決めてね</p>'
        + `<p class="cbcoinl">${COINI}<span>持って いる バトルコイン <b>${st.coin}</b>枚</span></p>`
        + '<div class="cbstk"><div class="blk"><b>参加コイン</b><small>2人とも はじめに 出す 数。同じ 数を 持って いる 人 だけ 入れるよ</small>'
        + `<div class="chips" role="group" aria-label="参加コイン">${chips.map(q => `<button type="button" class="${q === k.e ? 'on' : ''}" data-cb="stke" data-n="${q}" aria-pressed="${q === k.e}">${q}</button>`).join('')}</div></div>`
        + '<div class="blk"><b>勝者の 獲得コイン</b><small>勝った 人への プレゼント。参加コインの 2倍 まで</small>'
        + `<div class="cbstp"><button type="button" data-cb="stkw" data-d="-1"${k.w <= k.e ? ' disabled' : ''} aria-label="1枚 へらす">−</button><b aria-live="polite">${k.w}<small>枚</small></b><button type="button" data-cb="stkw" data-d="1"${k.w >= k.e * 2 ? ' disabled' : ''} aria-label="1枚 ふやす">＋</button></div></div></div>`
        + '<p class="hint">同点の ときは 参加コインが もどるよ。<br>とちゅうで やめると、参加コインは もどらないよ</p>'
        + `<button type="button" class="cbb" data-cb="stkgo">${k.e > 0 ? `参加 ${k.e}枚・勝者 ${k.w}枚で 部屋を 作る` : 'コインなしで 部屋を 作る'}</button>`;
      e.innerHTML = h; return;
    }
    if (r.mode === 'host') {
      h += '<h2 class="gold">部屋を 作ったよ</h2><p>この 番号を 友だちに 教えてね</p>' + `<div class="num" aria-label="部屋番号 ${r.code}">${r.code}</div>`
        + (r.stake && r.stake.e > 0 ? `<p class="cbstkl">${COINI}参加コイン <b>${r.stake.e}枚</b>・勝者 <b>${r.stake.w}枚</b></p>` : '')
        + `<div class="stt">${r.step === 'found' ? '<i class="cbspin"></i>友だちが 来たよ！ つないで いるよ…' : r.step === 'fail' ? '部屋を 作れなかったよ' : '<i class="cbspin"></i>友だちを 待って いるよ…'}</div>`
        + '<p class="hint">友だちは「部屋に 入る」で この 番号を 入れるよ。<br>近くに いる 友だちと 直接 つながるよ（2人とも Wi‑Fi か Bluetooth を オンに）</p>';
      if (r.step === 'fail') h += '<button type="button" class="cbb" data-cb="roomre">もう一度 作る</button>';
    } else {
      const busy = r.step === 'wait' || r.step === 'found';
      h += '<h2 class="gold">部屋に 入る</h2><p>友だちの 部屋番号（4けた）を 入れてね</p>' + `<div class="num in" aria-label="部屋番号 ${r.code}">${digits(r.code)}</div>`
        + `<div class="stt">${r.step === 'found' ? '<i class="cbspin"></i>部屋を 見つけたよ！ つないで いるよ…' : r.step === 'wait' ? '<i class="cbspin"></i>部屋を さがして いるよ…' : r.step === 'fail' ? '部屋に 入れなかったよ' : ''}</div>`;
      if (busy) h += '<p class="hint">見つからない ときは、番号と、2人とも Wi‑Fi か Bluetooth が オンか たしかめてね</p>';
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
      startMatch(r.mode === 'host' ? CBNet.host(link, CBApp._rng || undefined, CBApp._opt || undefined, r.stake) : CBNet.guest(link));
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

  
  let match = null, V = null, queue = [], pumping = false, mode = { k: 'idle' }, busy = false, lock = false, ended = false, gameNo = 0;
  const WHO = () => (match && match.kind === 'cpu' ? 'コンピュータ' : 'ともだち');
  function startMatch(m) {
    match = m; V = null; queue = []; pumping = false; mode = { k: 'idle' }; busy = false; lock = false; ended = false;
    m.onUpdate = u => { queue.push(u); pump(); };
    m.onState = s => onNet(s);
    show('game'); closeMod();
    $('.cbopp .cbwho b').textContent = WHO();
    paintEmpty(); layout();
    m.start();
    if (m.kind === 'guest') say('相手を 待って いるよ…');
    else if (m.kind === 'host') say(m.stake && m.stake.e > 0 ? `${WHO()}が 参加するか えらんで いるよ…` : '相手を 待って いるよ…');      
  }
  
  function joinAsk() {
    const m = match; if (!m || m.kind !== 'guest' || !m.stake) return;
    const k = m.stake;
    if (k.e <= 0) { m.join(); return; }
    const need = k.e - st.coin;
    modal(`<h3 class="gold">この 部屋の 決まり</h3><div class="cbstkv">${COINI}参加コイン <b>${k.e}枚</b><i>→</i>勝者 <b>${k.w}枚</b></div>`
      + `<p>2人とも はじめに ${k.e}枚 出すよ。勝った 人は ${k.w}枚 もらえる。<br>同点は もどる・とちゅうで やめると もどらないよ</p>`
      + `<p class="cbhave">${COINI}あなたの バトルコイン <b>${st.coin}</b>枚${need > 0 ? `<br><strong>あと ${need}枚 足りない ので、この 部屋には 入れないよ</strong>` : ''}</p>`
      + (need > 0 ? '<div class="col"><button type="button" class="cbb" data-cb="joinno">メニューへ</button></div>'
        : '<div class="rowb"><button type="button" class="cbb dk" data-cb="joinno">やめる</button><button type="button" class="cbb" data-cb="joinyes">参加する</button></div>'), 'cbjoin');
  }
  function onNet(s) {
    if (!match) return;
    if (s === 'again') { if (ended) { const e = $('.cbend .gift2'); if (e) e.textContent = WHO() + 'が「もう 1回」を 押したよ'; } return; }
    if (s === 'ready' || s === 'joined') return;
    if (s === 'stake') return joinAsk();
    const playing = !ended && !!V;
    const why = s === 'bye' ? WHO() + 'が 部屋を 出たよ' : s === 'ver' ? 'アプリの 版が ちがうので 対戦できないよ。\n2人とも 新しい 版に してね' : 'つながりが 切れたよ';
    
    let coinMsg = '';
    if (st.stake) {
      const k = st.stake; st.stake = null;
      if (s === 'bye') { addCoin(k.w); coinMsg = `${WHO()}が とちゅうで やめた ので、バトルコイン ${k.w}枚を もらったよ`; } else { addCoin(k.e); coinMsg = `参加コイン ${k.e}枚は もどったよ`; }
      save();
    }
    match = null; queue = [];
    modal(`<h3 class="gold">${s === 'ver' ? '対戦できないよ' : '対戦は ここまで'}</h3><p>${esc(why).replace(/\n/g, '<br>')}${playing ? '<br>（この 対戦は 勝ち負けに 数えないよ）' : ''}${coinMsg ? `<br>${COINI}${esc(coinMsg)}` : ''}</p><div class="col"><button type="button" class="cbb" data-cb="menu">メニューへ</button></div>`);
  }
  async function pump() {
    if (pumping) return; pumping = true;
    try {
      while (queue.length && match) {
        const u = queue.shift();
        await play(u.ev, u.view);
        if (!match) break;
        V = u.view; lock = false; keepMode(); render();
      }
    } finally { pumping = false; }
    if (match && !queue.length) match.idle();
  }
  
  
  const EFFQ = ['6', '5', '7', '3', '4'];
  const EFFTXT = { 6: '6 を 2まい 見せて、相手の 手札を 1まい 見られるよ', 5: '5 と 手札 1まいを 捨てて、山札から 1まい セットできるよ', 7: '7 を 3まい 山札に もどして、新しく 3まい 引けるよ',
    3: '3 を 3まい 見せて、その 1まいと 相手の 手札の 1まい（ランダム）を 交換できるよ', 4: '4 を 見せて、相手に カードを 交換させるよ' };
  const EFFBAR = { 3: '3 を 3まい 見せて、手札を 1まい 交換できるよ' };      
  
  const toName = o => (NAMES[o] ? NAMES[o] + 'に' : o + ' に');
  const REVTXT = (k, o) => `手札の ${k} を 2まい 見せて、1まい 捨てると、${toName(o)} 勝てるよ`;
  const REVBAR = (k, o) => `手札の ${k} を 1まい 捨てて、${toName(o)} 勝てるよ`;
  function effOk(q, v, use) {
    const c = v.can.eff; if (!c) return false;
    const three = k => v.my.hand.filter(x => x.k === k && x.u !== use.u5).length >= 3;
    return q === '6' ? c.e6 : q === '5' ? c.e5 : q === '7' ? c.e7 && three('7') : q === '3' ? !!c.e3 && three('3') : c.e4;
  }
  function effNext(v, use, after) { for (let i = EFFQ.indexOf(after) + 1; i < EFFQ.length; i++) if (effOk(EFFQ[i], v, use)) return EFFQ[i]; return null; }
  
  function effStep() {
    const nx = effNext(V, mode.use, mode.q);
    if (nx) { mode.q = nx; mode.step = 'ask'; render(); return; }
    const use = mode.use; send({ t: 'eff', use: use });
  }
  
  function keepMode() {
    const v = V, has = u => v.my.hand.some(c => c.u === u);
    if (mode.k === 'eff') { if (!v.can.eff) mode = { k: 'idle' }; }
    else if (mode.k === 'dropm') { if (v.pend && v.pend.mine && v.pend.type === 'm') mode.sel = mode.sel.filter(has); else mode = { k: 'idle' }; }
    else mode = { k: 'idle' };
  }
  const sortHand = h => h.slice().sort((a, b) => power(a.k) - power(b.k) || a.u - b.u);
  const cardBtn = (c, cls, extra) => `<button type="button" class="cbc ${cls || ''}" data-u="${c.u}"${extra || ''} aria-label="${c.k ? esc(nameOf(c.k)) + ' の カード' : 'ふせた カード'}"><img src="${pic(c.k)}" alt="" draggable="false">${c.seen ? '<i class="eye" aria-hidden="true"></i>' : ''}</button>`;
  function pips(n, turns) { let h = ''; for (let i = 0; i < turns; i++) h += `<i class="${i < n ? 'on' : ''}"></i>`; return h; }
  const turnsOf = () => (V && V.turns) || R.TURNS;      
  function paintEmpty() {
    $('.cbturn').innerHTML = ''; $('.cbohand').innerHTML = ''; $('.cbhand').innerHTML = ''; $('.cbact').innerHTML = ''; say('');
    $('.cbslot.op').innerHTML = ''; $('.cbslot.my').innerHTML = ''; $('.cbdeck .cbn').textContent = ''; $('.cbdis .cbn').textContent = '';
    ov.querySelectorAll('.cbpips').forEach(e => { e.innerHTML = pips(0, turnsOf()); });
    $('.cbglow').classList.remove('on');
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
      if (v.pend.type === 'swap') return me ? `${w}が 4 の 効果を 使ったよ！\nセットした カードと 交換する 手札を えらんでね` : `${w}が カードを 交換して いるよ…`;
      if (v.pend.type === 'k') return me ? '神様馬で 勝った！ 効果を 使う？\n相手の 手札を 1まい 見られるよ' : `${w}が 神様馬の 効果を 使うか えらんで いるよ…`;
      if (v.pend.type === 'm') return me ? '幻の馬で 勝った！ 効果を 使う？\n手札を 2まい 捨てて、山札から 2まい 引けるよ' : `${w}が 幻の馬の 効果を 使うか えらんで いるよ…`;
      if (v.pend.type === 'rev') return me && v.my.set && v.op.set ? `逆転の チャンス！ ${v.my.set.k} の 効果を 使う？\n${REVBAR(v.my.set.k, v.op.set.k)}` : `${w}が 逆転勝利を 使うか えらんで いるよ…`;
    }
    if (v.phase === 'eff') return `${w}が 効果を 使うか えらんで いるよ…`;
    if (v.can.set) return v.op.set ? `${w}は もう セットしたよ。セットする カードを えらんでね` : 'セットする カードを えらんでね（カードを タップ）';
    return `${w}が えらんで いるよ…`;
  }
  
  function paintDis(list) {
    const top = list.length ? list[list.length - 1] : null;
    $('.cbdis .pl').innerHTML = top ? `<img src="${pic(top.k)}" alt="" draggable="false">` : '';
    $('.cbdis .cbn').textContent = String(list.length);
    $('.cbdis').setAttribute('aria-label', `捨て札を 見る（${list.length}まい）`);
  }
  const setTag = (s, mine) => { const t = s.open ? '' : s.up ? '4 の 効果' : !mine ? '' : s.blind ? '山札から' : 'セット ずみ'; return t ? `<span class="tag">${t}</span>` : ''; };
  function render() {
    const v = V; if (!v || screen !== 'game') return;
    if (v.can.eff && mode.k !== 'eff') { const q = effNext(v, {}, null); mode = q ? { k: 'eff', use: {}, q: q, step: 'ask' } : { k: 'idle' }; }      
    $('.cbturn').innerHTML = v.phase === 'end' ? 'けっか' : `ターン ${v.turn}<small>／${v.turns}</small>` + (st.stake ? `<small class="stk">${COINI}勝者 ${st.stake.w}枚</small>` : '');
    $('.cbpips[data-p=op]').innerHTML = pips(v.op.wins, v.turns); $('.cbpips[data-p=my]').innerHTML = pips(v.my.wins, v.turns);
    $('.cbohand').innerHTML = v.op.hand.map(c => cardBtn({ u: c.u, k: c.k }, c.k ? 'knw' : '', ' data-cb="ocard"')).join('');
    $('.cbdeck .cbn').textContent = String(v.deckN); paintDis(v.discard);
    const os = v.op.set, ms = v.my.set;
    $('.cbslot.op').innerHTML = os ? cardBtn({ u: os.u, k: os.k }, '', ' data-cb="oset"') + setTag(os, false) : '';
    $('.cbslot.my').innerHTML = ms ? cardBtn({ u: ms.u, k: ms.k }, '', ' data-cb="mset"') + setTag(ms, true) : '';
    $('.cbglow').classList.toggle('on', v.can.set || !!(v.pend && v.pend.mine && v.pend.type === 'swap'));
    const asking = askSync();                          
    paintHand(); paintAct(asking);
    say(asking ? '効果を 使うか えらんでね' : (modeText() || statusText(v)));
    layout();
  }
  function modeText() {
    if (mode.k === 'eff') return mode.step === 'drop5' ? '5 と いっしょに 捨てる カードを えらんでね（カードを タップ）' : `効果タイム！ ${mode.q} の 効果を 使う？\n${EFFBAR[mode.q] || EFFTXT[mode.q]}`;
    if (mode.k === 'dropm') return `捨てる カードを 2まい えらんでね（${mode.sel.length}／2）`;
    return '';
  }
  
  function paintHand(fresh, list) {
    const hd = $('.cbhand');
    hd.innerHTML = sortHand(list || V.my.hand).map(c => cardBtn(c, (mode.k === 'dropm' && mode.sel.indexOf(c.u) >= 0 ? 'sel ' : '') + (fresh && fresh.indexOf(c.u) >= 0 ? 'new' : ''), ' data-cb="card"')).join('');
  }
  function paintAct(asking) {
    const v = V, a = $('.cbact'); let h = '';
    const two = (no, yes, yesText) => `<button type="button" class="cbb dk sm" data-cb="${no}">使わない</button><button type="button" class="cbb sm" data-cb="${yes}">${yesText}</button>`;
    if (asking) h = '';
    else if (mode.k === 'eff') h = mode.step === 'drop5' ? '<button type="button" class="cbb dk sm" data-cb="effback">もどる</button>' : two('effno', 'effyes', `${mode.q} の 効果を 使う`);
    else if (mode.k === 'dropm') h = `<button type="button" class="cbb dk sm" data-cb="modex">もどる</button><button type="button" class="cbb sm" data-cb="mgo"${mode.sel.length === 2 ? '' : ' disabled'}>この 2まいを 捨てて 引く</button>`;
    else if (v.pend && v.pend.mine && v.pend.type === 'k') h = two('kskip', 'kgo', '神様馬の 効果を 使う');
    else if (v.pend && v.pend.mine && v.pend.type === 'm') h = two('mskip', 'mpick', '幻の馬の 効果を 使う');
    else if (v.pend && v.pend.mine && v.pend.type === 'rev' && v.my.set) h = two('revno', 'revyes', `${v.my.set.k} の 効果を 使う`);
    a.innerHTML = h;
  }

  
  function modal(html, cls) { modEl.className = 'cbmod on ' + (cls || ''); modEl.innerHTML = html; }
  function closeMod() { if (modEl) { modEl.className = 'cbmod'; modEl.innerHTML = ''; } }
  const modOn = () => modEl.classList.contains('on');
  
  
  
  
  
  let peekId = '';
  
  
  
  
  const ASK_GUARD = 350;
  let askAt = 0;
  function askInfo() {
    const v = V; if (!v || ended || !match) return null;
    if (mode.k === 'eff' && mode.step === 'ask') return { id: `e${gameNo}.${v.turn}.${mode.q}`, k: mode.q, head: '効果タイム！', q: `${mode.q} の 効果を 使う？`, text: EFFTXT[mode.q], yes: 'effyes', no: 'effno' };
    if (mode.k === 'idle' && v.pend && v.pend.mine && v.pend.type === 'k') return { id: `k${gameNo}.${v.turn}`, k: 'k', head: '神様馬で 勝った！', q: '神様馬の 効果を 使う？', text: '相手の 手札を 1まい 見られるよ', yes: 'kgo', no: 'kskip' };
    if (mode.k === 'idle' && v.pend && v.pend.mine && v.pend.type === 'm') return { id: `m${gameNo}.${v.turn}`, k: 'm', head: '幻の馬で 勝った！', q: '幻の馬の 効果を 使う？', text: '手札を 2まい 捨てて、山札から 2まい 引けるよ', yes: 'mpick', no: 'mskip' };
    if (mode.k === 'idle' && v.pend && v.pend.mine && v.pend.type === 'rev' && v.my.set && v.op.set) return { id: `r${gameNo}.${v.turn}`, k: v.my.set.k, head: '逆転の チャンス！', q: `${v.my.set.k} の 効果を 使う？`, text: REVTXT(v.my.set.k, v.op.set.k), yes: 'revyes', no: 'revno' };      
    return null;
  }
  const askOn = () => !!modEl && modEl.classList.contains('cbask');
  function askSync() {                                 
    const A = askInfo();
    if (!A || peekId === A.id || screen !== 'game') { if (askOn()) closeMod(); return false; }
    if (askOn() && modEl.dataset.ask === A.id) return true;
    if (modOn() && !askOn()) return false;
    modal(`<h3 class="gold">${esc(A.head)}</h3><div class="big"><img src="${pic(A.k, true)}" alt="${esc(nameOf(A.k))}"></div><p class="askq"><b>${esc(A.q)}</b>${esc(A.text)}</p>`
      + `<div class="rowb"><button type="button" class="cbb dk lg" data-cb="${A.no}">使わない</button><button type="button" class="cbb lg" data-cb="${A.yes}">使う</button></div>`
      + '<button type="button" class="cbb dk sm" data-cb="askpeek">手札と ボードを 見る</button>', 'cbask');
    modEl.dataset.ask = A.id; askAt = performance.now();
    return true;
  }
  
  function cardModal(u) {
    const v = V, c = v.my.hand.find(x => x.u === u); if (!c) return;
    let btn = '';
    if (v.pend && v.pend.mine && v.pend.type === 'swap') btn = `<button type="button" class="cbb" data-cb="swap" data-u="${u}">この カードと 交換する</button>`;
    else if (mode.k === 'eff') { if (mode.step === 'drop5') btn = `<button type="button" class="cbb" data-cb="drop5" data-u="${u}">この カードを 捨てる<small>5 と いっしょに 捨てて、山札から 1まい セット</small></button>`; }
    else if (v.can.set) btn = `<button type="button" class="cbb" data-cb="set" data-u="${u}">この カードを セットする<small>セットしたら もう 変えられないよ</small></button>`;
    modal(`<div class="big"><img src="${pic(c.k, true)}" alt="${esc(nameOf(c.k))}"></div>${c.seen ? '<p>この カードは 相手に 見られて いるよ</p>' : ''}<div class="col">${btn}<button type="button" class="cbb dk" data-cb="modx">もどる</button></div>`);
  }
  
  function showCard(k, text, back) { modal(`<div class="big"><img src="${pic(k, true)}" alt="${esc(k ? nameOf(k) : 'ふせた カード')}"></div>${text ? `<p>${esc(text)}</p>` : ''}<div class="col"><button type="button" class="cbb dk" data-cb="${back === 'discard' ? 'discard' : 'modx'}">もどる</button></div>`); }
  
  function pickModal(kind) {
    const v = V;
    
    const seen = v.op.hand.some(c => c.k);
    modal(`<h3 class="gold">${kind === 'p6' ? '6 の 効果' : '神様馬の 効果'}</h3><p>見たい カードを 1まい えらんでね${kind === 'p6' ? '<br>（手札の 6 を 2まい 相手に 見せるよ）' : ''}${seen ? '<br>もう 見た カードは えらべないよ' : ''}</p>`
      + `<div class="pick">${v.op.hand.map(c => cardBtn({ u: c.u, k: c.k }, c.k ? 'knw' : '', c.k ? ' disabled' : ` data-cb="pick" data-kind="${kind}"`)).join('')}</div>`
      + '<div class="col"><button type="button" class="cbb dk" data-cb="modx">もどる</button></div>');
  }
  
  function discardModal() {
    const v = V; if (!v) return;
    const d = v.discard, turns = [], effs = [], w = esc(WHO());
    d.forEach(x => {
      if (x.why === 't') { (turns[x.turn] = turns[x.turn] || []).push(x); return; }
      let g = effs.find(e => e.turn === x.turn && e.why === x.why && e.mine === x.mine);
      if (!g) { g = { turn: x.turn, why: x.why, mine: x.mine, cards: [] }; effs.push(g); }
      g.cards.push(x);
    });
    const card = x => `<button type="button" class="cbc" data-cb="dcard" data-k="${esc(x.k)}" aria-label="${esc(nameOf(x.k))} の カード"><img src="${pic(x.k)}" alt="" draggable="false"></button>`;
    const pair = (name, cs) => `<div class="pr"><span>${name}</span><div class="cs">${cs.map(card).join('')}</div></div>`;
    let h = `<h3 class="gold">捨て札（${d.length}まい）</h3><div class="cbdl"><h4>終わった ターンの 捨て札</h4>`;
    if (!turns.some(Boolean)) h += '<p class="none">まだ ないよ（ターンが 終わると、出した カードが ここに 来るよ）</p>';
    turns.forEach((cs, n) => { if (cs) h += `<div class="row" data-dt="${n}"><b>ターン ${n}</b>${pair('あなた', cs.filter(x => x.mine))}${pair(w, cs.filter(x => !x.mine))}</div>`; });
    h += '<h4>効果で 捨てた カード</h4>';
    if (!effs.length) h += '<p class="none">まだ ないよ（1・2・5 の 効果・幻の馬の 効果で 捨てた カードが ここに 来るよ）</p>';
    effs.forEach(g => { h += `<div class="row" data-de="${esc(g.why)}"><b>ターン ${g.turn}${g.why === 'm' ? '<small>はじめ</small>' : ''}</b>${pair(`${g.mine ? 'あなた' : w}の ${g.why === 'm' ? '幻の馬の 効果' : esc(g.why) + ' の 効果'}`, g.cards)}</div>`; });      
    h += `</div><p>山札の のこり ${v.deckN}まい</p><div class="col"><button type="button" class="cbb dk" data-cb="modx">もどる</button></div>`;
    modal(h, 'cbdm');
  }
  
  
  
  
  const SETS = [['bgm', 'BGM', '音楽'], ['se', '効果音', 'カードや ボタンの 音'], ['fx', 'エフェクト', '光や 動きの 演出']];
  const setOn = k => (k === 'bgm' ? bgmOn() : k === 'se' ? seOn() : fxOn());
  function gearModal() {
    const rows = SETS.map(([k, name, note]) => { const on = setOn(k); return `<div class="cbsw" data-set="${k}"><span>${name}<small>${note}</small></span><div class="cbseg" role="group" aria-label="${name}">`
      + `<button type="button" class="${on ? 'on' : ''}" data-cb="tg" data-k="${k}" data-v="1" aria-pressed="${on}">オン</button><button type="button" class="${on ? '' : 'on'}" data-cb="tg" data-k="${k}" data-v="0" aria-pressed="${!on}">オフ</button></div></div>`; }).join('');
    const game = screen === 'game' && !!match;
    modal(`<h3 class="gold">設定</h3><div class="cbsws">${rows}</div><div class="col">`
      + (game ? '<button type="button" class="cbb" data-cb="modx">対戦に もどる</button><button type="button" class="cbb dk" data-cb="help">あそび方</button><button type="button" class="cbb dk" data-cb="quit">対戦を やめる</button>' : '<button type="button" class="cbb" data-cb="modx">もどる</button>')
      + '</div>', 'cbset');
  }
  
  function setSet(k, on) {
    if (['bgm', 'se', 'fx'].indexOf(k) < 0) return;
    st[k] = !!on; save(); applySets();
    if (k === 'se' && on) se('tap', 0.8);
    if (modEl.classList.contains('cbset')) gearModal();
  }
  function applySets() { if (ov) ov.classList.toggle('nofx', !fxOn()); bgmSync(); }
  function quitModal() {
    const mid = !ended && !!V;
    modal(`<h3 class="gold">対戦を やめる？</h3><p>${mid ? 'とちゅうで やめると 負けに なるよ（連勝は 0 に もどるよ）' + (st.stake ? `<br>${COINI}参加コイン ${st.stake.e}枚も もどらないよ` : '') : 'メニューに もどるよ'}</p><div class="rowb"><button type="button" class="cbb dk" data-cb="modx">つづける</button><button type="button" class="cbb" data-cb="quitgo">やめる</button></div>`);
  }

  
  
  
  
  function hush() { if (screen !== 'game') return; const a = $('.cbact'); if (a) a.innerHTML = ''; say(''); }
  async function send(a) {
    if (busy || !match) return false;
    busy = true; lock = true; closeMod(); hush();      
    let r = null;
    try { r = await match.act(a); } catch (e) { r = { ok: false, why: 'err' }; }
    busy = false;
    if (!r || !r.ok) { lock = false; if (match && V) { mode = { k: 'idle' }; render(); toast('その 手は 打てなかったよ', 2); } return false; }
    return true;
  }
  function onClick(e) {
    const key = e.target.closest('[data-key]'); if (key && !key.disabled) return roomKey(key.dataset.key);
    const b = e.target.closest('[data-cb]'); if (!b || b.disabled) return;
    const a = b.dataset.cb, u = +b.dataset.u;
    if (/^(effyes|effno|kgo|kskip|mpick|mskip|revyes|revno)$/.test(a) && b.closest('.cbask') && performance.now() - askAt < (typeof CBApp._guard === 'number' ? CBApp._guard : ASK_GUARD)) return;      
    if (a === 'close') return close();
    if (a === 'cpu') { se('tap'); return startMatch(CBNet.cpu(CBApp._rng || undefined, CBApp._think || undefined, CBApp._opt || undefined)); }
    if (a === 'host' || a === 'join') { se('tap'); return showRoom(a); }
    if (a === 'help') return showHelp(screen === 'game' ? 'game' : 'menu');
    if (a === 'helpx') { show(helpBack); if (helpBack === 'game') render(); return; }
    if (a === 'roomx') { roomStop(); return showMenu(); }
    if (a === 'roomre') return showRoom('host', true);
    if (a === 'stke') return stakeSet('e', +b.dataset.n);
    if (a === 'stkw') return stakeSet('w', +b.dataset.d);
    if (a === 'stkgo') { const r = room; if (!r || r.step !== 'stake') return; se('tap'); r.step = ''; paintRoom(); return roomGo(); }
    if (a === 'joinyes') { const m = match; if (!m || m.kind !== 'guest' || !m.stake || st.coin < m.stake.e || V) return; se('tap'); closeMod(); m.join(); say('相手を 待って いるよ…'); return; }
    if (a === 'joinno') { leave(false); return showMenu(); }
    if (a === 'menu') { leave(false); return showMenu(); }
    if (a === 'modx') { closeMod(); if (match && V && screen === 'game' && !busy && !lock && askInfo()) render(); return; }      
    if (a === 'askpeek') { const A = askInfo(); if (A) peekId = A.id; closeMod(); if (V && screen === 'game') render(); return; }      
    if (a === 'gear') { se('tap', 0.6); return gearModal(); }
    if (a === 'tg') return setSet(b.dataset.k, b.dataset.v === '1');
    if (a === 'quit') return quitModal();
    if (a === 'quitgo') { leave(true); return showMenu(); }
    if (a === 'again') return again();
    if (a === 'discard') { if (modEl.classList.contains('cbopen')) return; return discardModal(); }
    if (a === 'dcard') { const k = b.dataset.k; if (R.KINDS.indexOf(k) >= 0) showCard(k, '捨て札の カード', 'discard'); return; }
    if (!match || !V || busy || lock || ended || modEl.classList.contains('cbopen')) return;
    const v = V;
    if (a === 'ocard' || a === 'oset') { const c = a === 'oset' ? v.op.set : v.op.hand.find(x => x.u === u); if (c && c.k) showCard(c.k, a === 'oset' ? '相手が セットした カード' : '効果で 見た 相手の カード'); return; }
    if (a === 'mset') { const c = v.my.set; if (c) showCard(c.k, c.open ? 'あなたが セットした カード' : c.blind ? '山札から 来た カード（オープンまで わからない）' : c.up ? '4 の 効果で 見せた カード' : 'あなたが セットした カード（相手には 見えない・もう 変えられない）'); return; }
    if (a === 'card') {
      if (mode.k === 'dropm') { const j = mode.sel.indexOf(u); if (j >= 0) mode.sel.splice(j, 1); else if (mode.sel.length < 2) mode.sel.push(u); se('tap', 0.6); paintHand(); paintAct(); say(modeText()); layout(); return; }
      se('tap', 0.6); return cardModal(u);
    }
    if (a === 'set') { if (!v.can.set || mode.k !== 'idle') return; return send({ t: 'set', u: u }); }
    
    if (a === 'effyes' || a === 'effno' || a === 'effback' || a === 'drop5') {
      if (mode.k !== 'eff' || !v.can.eff) return;
      se('tap', 0.6);
      if (a === 'effback') { mode.step = 'ask'; closeMod(); render(); return; }
      if (a === 'effno') { if (mode.step !== 'ask') return; return effStep(); }
      if (a === 'drop5') { if (mode.step !== 'drop5' || !v.my.hand.some(c => c.u === u)) return; mode.use.u5 = u; closeMod(); return effStep(); }
      if (mode.step !== 'ask') return;
      if (mode.q === '6') return pickModal('p6');
      if (mode.q === '5') { mode.step = 'drop5'; render(); return; }
      if (mode.q === '7') mode.use.x7 = true; else if (mode.q === '3') mode.use.x3 = true; else mode.use.u4 = true;
      return effStep();
    }
    if (a === 'modex') { mode = { k: 'idle' }; render(); return; }
    if (a === 'kgo') return pickModal('k');
    if (a === 'pick') {
      if (!v.op.hand.some(c => c.u === u && !c.k)) return;      
      if (b.dataset.kind === 'p6') { if (mode.k !== 'eff' || mode.q !== '6') return; mode.use.p6 = u; closeMod(); return effStep(); }
      return send({ t: 'k', pick: u });
    }
    if (a === 'kskip') return send({ t: 'k', pick: null });
    if (a === 'mskip') return send({ t: 'm', drop: null });
    if (a === 'mpick') { mode = { k: 'dropm', sel: [] }; render(); return; }
    if (a === 'mgo') { if (mode.k === 'dropm' && mode.sel.length === 2) return send({ t: 'm', drop: mode.sel.slice() }); return; }
    if (a === 'swap') return send({ t: 'swap', u: u });
    if (a === 'revyes' || a === 'revno') { if (!(v.pend && v.pend.mine && v.pend.type === 'rev') || mode.k !== 'idle') return; se('tap', 0.6); return send({ t: 'rev', use: a === 'revyes' }); }      
  }

  
  const box = el => { const r = el.getBoundingClientRect(), o = ov.getBoundingClientRect(); return { x: r.left - o.left, y: r.top - o.top, w: r.width, h: r.height }; };
  const mid = (b, w) => ({ x: b.x + b.w / 2 - w / 2, y: b.y + b.h / 2 - w * 0.75, w: w, h: w * 1.5 });      
  function fly(k, from, to, ms, fade) {
    if (reduce() || !from || !to || !from.w || !to.w) return T(40);
    const im = document.createElement('img'); im.src = pic(k); im.alt = ''; im.className = 'cbfl';
    im.style.cssText = `left:${from.x}px;top:${from.y}px;width:${from.w}px;height:${from.h}px`;
    flyEl.appendChild(im);
    const dx = to.x + to.w / 2 - (from.x + from.w / 2), dy = to.y + to.h / 2 - (from.y + from.h / 2), sc = to.w / from.w, d = Math.max(1, ms * SPEED);
    return new Promise(ok => {
      let done = false; const fin = () => { if (done) return; done = true; im.remove(); ok(); };
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
  
  
  async function openShow(x) {
    const hold = x.rev === 'me' || x.rev === 'op';
    const txt = x.rev === 'me' ? ['チャンス！', `${nameOf(x.op.k)} の ほうが 強い…でも ${x.my.k} の「逆転勝利」を 使えるよ`] : x.rev === 'op' ? ['勝負は まだ！', `${WHO()}は ${x.op.k} の「逆転勝利」を 使えるよ`]
      : x.res === 'win' ? ['勝ち！', `${nameOf(x.my.k)} が ${nameOf(x.op.k)} に 勝ったよ`] : x.res === 'lose' ? ['負け…', `${nameOf(x.op.k)} の ほうが 強いよ`] : x.res === 'clash' ? ['かぶり！', `同じ カード（${nameOf(x.my.k)}）＝どちらも 負け`] : ['引き分け', '神様馬 と 幻の馬 は 同じ 強さ'];
    const side = (who, k) => `<div class="sd" data-sd="${who}"><span>${who === 'my' ? 'あなた' : esc(WHO())}</span><div class="cbflip"><div class="in"><img src="${pic(null, true)}" alt=""><img class="fc" src="${pic(k, true)}" alt="${esc(nameOf(k))}"></div></div></div>`;
    modal(`<h3 class="gold">ターン ${x.turn}　オープン！</h3><div class="cbvs">${side('my', x.my.k)}<b class="mid gold">VS</b>${side('op', x.op.k)}</div><div class="cbres gold" aria-live="assertive"><span></span><small></small></div>`, 'cbopen');
    await T(450); se('flip');
    modEl.querySelectorAll('.cbflip').forEach(f => f.classList.add('up'));
    await T(700);
    const res = $('.cbres', modEl); res.firstChild.textContent = txt[0]; res.lastChild.textContent = txt[1]; res.classList.add('on');
    const my = $('[data-sd=my]', modEl), op = $('[data-sd=op]', modEl);
    if (hold) se('magic');
    else if (x.res === 'win') { my.classList.add('wn'); op.classList.add('ls'); se('win'); }
    else if (x.res === 'lose') { op.classList.add('wn'); my.classList.add('ls'); se('lose'); }
    else { my.classList.add('ls'); op.classList.add('ls'); se('even'); }
    $('.cbpips[data-p=op]').innerHTML = pips(x.wins[1], turnsOf()); $('.cbpips[data-p=my]').innerHTML = pips(x.wins[0], turnsOf());
    $('.cbslot.my').innerHTML = cardBtn({ u: x.my.u, k: x.my.k }, ''); $('.cbslot.op').innerHTML = cardBtn({ u: x.op.u, k: x.op.k }, '');
    await T(1900);
    closeMod();
  }
  
  async function peekShow(title, k, note) {
    modal(`<h3 class="gold">${esc(title)}</h3><div class="sd" style="width:min(46vw,190px)"><div class="cbflip"><div class="in"><img src="${pic(null, true)}" alt=""><img class="fc" src="${pic(k, true)}" alt="${esc(nameOf(k))}"></div></div></div><p>${esc(note)}</p>`, 'cbopen');
    await T(350); se('flip'); const f = $('.cbflip', modEl); if (f) f.classList.add('up');
    await T(1900); closeMod();
  }
  async function play(ev, v) {
    const P = V;                                       
    
    let hand = P ? P.my.hand.slice() : [], dis = P ? P.discard.slice() : [];
    const rehand = fresh => { paintHand(fresh, hand); layout(); };
    const toDis = ks => { ks.forEach(k => dis.push({ k: k })); paintDis(dis); };
    const kIn = (sd) => { const el = $('.cbslot.' + sd + ' .cbc img'), m = el ? /cb_s(.)\.webp/.exec(el.getAttribute('src')) : null; return m && m[1] !== 'b' ? m[1] : null; };
    for (const x of ev) {
      if (!match) return;
      if (x.e === 'deal') {
        ended = false; gameNo += 1; closeMod(); V = null; paintEmpty();
        payStake();                                    
        $('.cbdeck .cbn').textContent = '30'; se('deal');
        await banner('対戦 スタート', `${WHO()}と 勝負！`, 900);
        
        const d = deckBox(), hm = handBox('my'), ho = handBox('op'), w = Math.min(60, d.w * 1.2);
        const jobs = [];
        const nDeal = Math.max(v.my.hand.length, v.op.hand.length) || R.HAND;      
        for (let i = 0; i < nDeal; i++) { jobs.push(T(i * 90).then(() => fly(null, mid(d, w), mid(hm, w), 320))); jobs.push(T(i * 90 + 45).then(() => fly(null, mid(d, w), mid(ho, w * 0.7), 320))); }
        await Promise.all(jobs);
        V = v; mode = { k: 'idle' }; render();
        hand = v.my.hand.slice(); dis = v.discard.slice();
        $('.cbhand').querySelectorAll('.cbc').forEach((c, i) => { c.classList.add('new'); c.style.animationDelay = (i * 50 * SPEED) + 'ms'; });
        await T(380);
      } else if (x.e === 'turn') {
        await banner('ターン ' + x.n, x.n >= ((v && v.turns) || R.TURNS) ? 'さいごの 勝負！' : '', 800);
      } else if (x.e === 'pre') {                      
        se('magic'); await banner(nameOf(x.type) + 'の 効果', x.me ? '使うか えらんでね' : `${WHO()}が 使うか えらぶよ`, 950);
      } else if (x.e === 'set') {
        se('set');
        if (x.me) {
          const c = hand.find(q => q.u === x.u);
          await fly(c ? c.k : null, cardBox('my', x.u) || mid(handBox('my'), 60), slotBox('my'), 300);
          $('.cbslot.my').innerHTML = cardBtn({ u: x.u, k: c ? c.k : null }, '') + '<span class="tag">セット ずみ</span>';
          hand = hand.filter(q => q.u !== x.u); const h = $('.cbhand').querySelector(`[data-u="${x.u}"]`); if (h) h.remove();
        } else { const h = $('.cbohand').lastElementChild; await fly(null, h ? box(h) : mid(handBox('op'), 40), slotBox('op'), 300); if (h) h.remove(); $('.cbslot.op').innerHTML = cardBtn({ u: 0, k: null }, ''); }
      } else if (x.e === 'efft') {                     
        $('.cbglow').classList.remove('on');
        await banner('効果タイム', x.mine ? 'カードの 効果を 使うか えらんでね' : `${WHO()}が 効果を 使うか えらぶよ`, 950);
      } else if (x.e === 'effd') {
         
      } else if (x.e === 'fizz') {
        toast(`${x.me ? '' : WHO() + 'の '}${x.k} の 効果は 使えなかったよ`, 2.2); await T(700);
      } else if (x.e === 'p6') {
        if (x.me) await peekShow('6 の 効果', x.k, `${WHO()}の 手札に ${nameOf(x.k)} が あるよ`);
        else { se('magic'); toast(`${WHO()}が 6 を 2まい 見せて、\nあなたの 手札を 1まい 見たよ`, 3.2); await T(1100); }
      } else if (x.e === 'u5') {                       
        const sd = x.me ? 'my' : 'op';
        toast(x.me ? `5 の 効果！\n5 と ${nameOf(x.drop.k)} を 捨てて、山札から 1まい セットしたよ` : `${WHO()}が 5 の 効果を 使ったよ\n5 と ${nameOf(x.drop.k)} を 捨てて、山札から 1まい`, 3);
        se('magic');
        $('.cbslot.' + sd).innerHTML = cardBtn({ u: 0, k: '5' }, ''); await T(600);
        $('.cbslot.' + sd).innerHTML = '';
        const oc = x.me ? null : $('.cbohand').querySelector(`[data-u="${x.drop.u}"]`) || $('.cbohand').lastElementChild;
        await Promise.all([fly('5', slotBox(sd), mid(disBox(), 20), 380, true), fly(x.drop.k, x.me ? (cardBox('my', x.drop.u) || mid(handBox('my'), 60)) : (oc ? box(oc) : mid(handBox('op'), 40)), mid(disBox(), 20), 380, true)]);
        if (x.me) { hand = hand.filter(q => q.u !== x.drop.u); rehand(); } else if (oc) oc.remove();
        toDis(['5', x.drop.k]);
        se('set'); await fly(null, mid(deckBox(), 40), slotBox(sd), 340);
        $('.cbslot.' + sd).innerHTML = cardBtn({ u: 0, k: null }, '') + (x.me ? '<span class="tag">山札から</span>' : '');
        await T(250);
      } else if (x.e === 'x7') {
        se('magic');
        toast(x.me ? '7 の 効果！\n7 を 3まい もどして、新しく 3まい 引いたよ' : `${WHO()}が 7 の 効果を 使ったよ\n7 を 3まい もどして 3まい 引いた`, 3);
        const hb = handBox(x.me ? 'my' : 'op'), d = deckBox(), w = x.me ? 56 : 36;
        await Promise.all([0, 1, 2].map(i => T(i * 70).then(() => fly('7', mid(hb, w), mid(d, 36), 320, true))));
        if (x.me) { let n = 0; hand = hand.filter(q => !(q.k === '7' && n++ < 3)); rehand(); }
        await Promise.all([0, 1, 2].map(i => T(i * 70).then(() => fly(null, mid(d, 36), mid(hb, w), 320))));
        if (x.me && x.drew) { hand = hand.concat(x.drew.map(c => ({ u: c.u, k: c.k }))); rehand(x.drew.map(c => c.u)); await T(420); }
      } else if (x.e === 'x3') {                       
        const hm = handBox('my'), ho = handBox('op'), tk = x.take.k;
        se('magic');
        
        modal(`<h3 class="gold">3 の 効果！</h3><div class="three">${[0, 1, 2].map(() => `<span class="cbc"><img src="${pic('3')}" alt="3 の カード" draggable="false"></span>`).join('')}</div><p>${x.me ? `手札の 3 を 3まい 見せたよ<br>その 1まいと、${esc(WHO())}の 手札の 1まいを 交換！` : `${esc(WHO())}が 手札の 3 を 3まい 見せたよ<br>その 1まいと、あなたの 手札の 1まいを 交換！`}</p>`, 'cbopen');
        await T(1700); closeMod();
        if (x.me) {
          await peekShow('3 の 効果：交換！', tk, `${WHO()}の 手札から ${nameOf(tk)} を もらったよ（3 を 1まい わたした）`);
          await Promise.all([fly('3', cardBox('my', x.give.u) || mid(hm, 56), mid(ho, 36), 400), fly(tk, mid(ho, 36), mid(hm, 56), 400)]);
          hand = hand.filter(q => q.u !== x.give.u).map(q => (x.three.indexOf(q.u) >= 0 ? { u: q.u, k: q.k, seen: true } : q)).concat([{ u: x.take.u, k: tk, seen: true }]);
          rehand([x.take.u]);
        } else {
          toast(`${WHO()}が 3 の 効果を 使ったよ\nあなたの ${nameOf(tk)} と 3 を 交換した`, 3.4);
          await Promise.all([fly(tk, cardBox('my', x.take.u) || mid(hm, 56), mid(ho, 36), 400), fly('3', mid(ho, 36), mid(hm, 56), 400)]);
          hand = hand.filter(q => q.u !== x.take.u).concat([{ u: x.give.u, k: '3' }]);
          rehand([x.give.u]);
        }
        await T(500);
      } else if (x.e === 'first') {
        se('flip');
        $('.cbslot.' + (x.me ? 'my' : 'op')).innerHTML = cardBtn({ u: 0, k: '4' }, '') + '<span class="tag">4 の 効果</span>';
        await banner('4 の 効果！', x.me ? `${WHO()}は カードを 交換するよ` : 'あなたは セットした カードを 交換してね', 1200);
      } else if (x.e === 'first2') {
        se('flip');
        $('.cbslot.my').innerHTML = cardBtn({ u: 0, k: '4' }, ''); $('.cbslot.op').innerHTML = cardBtn({ u: 0, k: '4' }, '');
        await banner('4 の 効果！', 'どちらも 4 の 効果 → 打ち消し', 1300);
      } else if (x.e === 'swap') {
        se('set');
        const sd = x.me ? 'my' : 'op', hb = handBox(sd);
        await fly(null, slotBox(sd), mid(hb, x.me ? 56 : 36), 300);
        const c = x.me ? hand.find(q => q.u === x.u) : null;
        await fly(c ? c.k : null, x.me ? (cardBox('my', x.u) || mid(hb, 56)) : mid(hb, 36), slotBox(sd), 300);
        $('.cbslot.' + sd).innerHTML = cardBtn({ u: 0, k: c ? c.k : null }, '') + (x.me ? '<span class="tag">セット ずみ</span>' : '');
        if (x.me) { const bk = v.my.hand.find(q => q.u === x.back) || (P && P.my.set && P.my.set.u === x.back ? { u: x.back, k: P.my.set.k } : null); hand = hand.filter(q => q.u !== x.u); if (bk) hand.push({ u: bk.u, k: bk.k, seen: !!bk.seen }); rehand(bk ? [bk.u] : null); }
        else toast(`${WHO()}が カードを 交換したよ`, 1.8);
      } else if (x.e === 'open') {
        hush();                                        
        await openShow(x);
      } else if (x.e === 'k') {
        if (x.me) await peekShow('神様馬の 効果', x.k, `${WHO()}の 手札に ${nameOf(x.k)} が あるよ`);
        else { se('magic'); toast(`${WHO()}が 神様馬の 効果で、\nあなたの 手札を 1まい 見たよ`, 3.2); await T(1100); }
      } else if (x.e === 'm') {
        se('magic');
        toast(x.me ? `幻の馬の 効果！\n${x.drop.map(c => nameOf(c.k)).join(' と ')} を 捨てて、${x.n}まい 引いたよ` : `${WHO()}が 幻の馬の 効果を 使ったよ\n${x.drop.map(c => nameOf(c.k)).join(' と ')} を 捨てて、${x.n}まい 引いた`, 3.2);
        const sd = x.me ? 'my' : 'op', hb = handBox(sd), d = deckBox(), w = x.me ? 56 : 36;
        await Promise.all(x.drop.map((c, i) => T(i * 80).then(() => fly(c.k, x.me ? (cardBox('my', c.u) || mid(hb, w)) : mid(hb, w), mid(disBox(), 20), 360, true))));
        if (x.me) { hand = hand.filter(q => !x.drop.some(c => c.u === q.u)); rehand(); }
        toDis(x.drop.map(c => c.k));
        await Promise.all(Array.from({ length: x.n }, (_, i) => T(i * 80).then(() => fly(null, mid(d, 36), mid(hb, w), 320))));
        if (x.me && x.drew) { hand = hand.concat(x.drew.map(c => ({ u: c.u, k: c.k }))); rehand(x.drew.map(c => c.u)); }
        await T(250);
      } else if (x.e === 'kskip' || x.e === 'mskip') {
        if (!x.me) { toast(`${WHO()}は 効果を 使わなかったよ`, 1.8); await T(500); }
      } else if (x.e === 'rev') {                      
        hush(); se('magic');
        modal(`<h3 class="gold">${esc(x.k)} の 効果！</h3><div class="three">${[0, 1, 2].map(() => `<span class="cbc"><img src="${pic(x.k)}" alt="${esc(x.k)} の カード" draggable="false"></span>`).join('')}</div>`
          + `<p>${x.me ? '' : esc(WHO()) + 'が '}${esc(x.k)} を 3まい（場の 1まい ＋ 手札の 2まい）見せたよ<br>手札の ${esc(x.k)} を 1まい 捨てて、${esc(toName(x.beat))} 逆転！</p>`, 'cbopen');
        await T(1700); closeMod();
        const oc = x.me ? null : $('.cbohand').querySelector(`[data-u="${x.drop.u}"]`) || $('.cbohand').lastElementChild;
        await fly(x.k, x.me ? (cardBox('my', x.drop.u) || mid(handBox('my'), 60)) : (oc ? box(oc) : mid(handBox('op'), 40)), mid(disBox(), 20), 380, true);
        if (x.me) { hand = hand.filter(q => q.u !== x.drop.u).map(q => (x.show.indexOf(q.u) >= 0 ? { u: q.u, k: q.k, seen: true } : q)); rehand(); } else if (oc) oc.remove();
        toDis([x.k]);
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
        if ($('.cbslot.op .cbc')) jobs.push(fly(kb, slotBox('op'), d, 380, true));
        $('.cbslot.my').innerHTML = ''; $('.cbslot.op').innerHTML = '';
        await Promise.all(jobs);
        toDis((v.me === 0 ? [ka, kb] : [kb, ka]).filter(Boolean));      
      } else if (x.e === 'end') {
        V = v; render();
        await endShow(x);
      }
    }
  }
  
  async function endShow(x) {
    ended = true;
    const head = x.res === 'win' ? 'あなたの 勝ち！' : x.res === 'lose' ? 'あなたの 負け…' : '同点！';
    se(x.res === 'win' ? 'fanfare' : x.res === 'lose' ? 'over' : 'even');
    modal(`<h3 class="gold">${head}</h3><div class="sc">${x.wins[0]} － ${x.wins[1]}<small>あなた － ${esc(WHO())}（勝った 数）</small></div><div class="gift"></div><div class="gift2" style="min-height:20px;font-size:12.5px;color:#d9c08c"></div>`
      + '<div class="col"><button type="button" class="cbb" data-cb="again">もう 1回</button><button type="button" class="cbb dk" data-cb="menu">メニューへ</button></div>', 'cbend');
    const no = gameNo, r = await settle(x.res), g = $('.cbend .gift');
    if (!g || no !== gameNo) return;
    
    
    const get = (n, bonus) => `<div class="cbget" role="status" aria-label="お世話トークン ${n}こ GET"><i class="tk" aria-hidden="true">🎟</i><span class="tx"><small>${bonus ? `${REWARD.every}連勝 ボーナス！ ` : ''}お世話トークン</small><b class="n gold">＋${n}こ GET！</b></span></div>`;
    let h = '';
    if (x.res === 'win') {
      const p = r.pay, bonus = r.got > REWARD.win;
      if (p && p.add > 0) h = get(p.add, bonus) + `<div>いま ${p.stock}こ／${p.max}こ${p.add < p.want ? `（${p.max}こ まで なので ${p.add}こ だけ）` : ''}</div>`;
      else if (p) h = `<div>お世話トークンが いっぱい（${p.max}こ）なので、今回は もらえなかったよ</div>`;
      else h = get(r.got, bonus) + '<div>つぎに ここを 開いた ときに わたすね</div>';
      h += `<div><b>${r.streak}連勝中！</b>` + (r.streak % REWARD.every ? `　あと ${REWARD.every - r.streak % REWARD.every}勝で ${REWARD.bonus}こ` : '') + '</div>';
    } else if (x.res === 'lose') h = '<div>連勝は 0 に もどったよ。もう 1回 やって みよう！</div>';
    else h = `<div>${st.streak > 0 ? `同点なので 連勝（${st.streak}連勝）は そのまま` : '同点！ もう 1回 やって みよう！'}</div>`;
    
    const now = `（いま ${r.coins}枚${r.full ? `：${COIN.max}枚 まで` : ''}）`;
    if (r.pot) h += `<div class="cbcl">${COINI}${x.res === 'win' ? `<b>バトルコイン ＋${r.pot.w}枚</b>` : x.res === 'draw' ? `同点：参加コイン ${r.pot.e}枚 もどったよ` : `参加コイン ${r.pot.e}枚は もどらないよ`}${now}</div>`;
    else if (r.coin) h += `<div class="cbcl">${COINI}<b>バトルコイン ＋${r.coin}枚</b>${now}</div>`;      
    g.innerHTML = h;
    if (g.querySelector('.cbget')) se('magic', 0.7);
    
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
    const m = match; match = null; queue = [];
    if (m) { if (count && !ended && V) { st.lose += 1; st.streak = 0; save(); } try { m.leave(); } catch (e) {   } }
    if (st && st.stake) { st.stake = null; save(); }      
    V = null; ended = false; closeMod();
  }

  
  function open() {
    build(); load();
    ov.classList.add('on');
    try { if (window.TengelWallet && window.TengelWallet.lockZoom) window.TengelWallet.lockZoom(true); } catch (e) {   }
    try { if (window.TengelFx && window.TengelFx.prime) window.TengelFx.prime(); } catch (e) {   }
    ['1', '2', '3', '4', '5', '6', '7', 'k', 'm', null].forEach(k => { const im = new Image(); im.src = pic(k); });
    actx(); applySets();                               
    showMenu();
  }
  function close() {
    roomStop(); leave(true);
    if (ov) ov.classList.remove('on');
    soundRest();
    try { if (window.TengelWallet && window.TengelWallet.lockZoom) window.TengelWallet.lockZoom(false); } catch (e) {   }
    try { document.dispatchEvent(new CustomEvent('tengel:cb')); } catch (e) {   }
  }
  return {
    open, close, REWARD, rewardFor, COIN, coinFor, _rng: null, _think: null, _link: null, _opt: null, _room: null, _guard: null, _as: null,      
    _t: {      
      get view() { return V; }, get screen() { return screen; }, get match() { return match; }, get mode() { return mode; }, get state() { return st; }, get ended() { return ended; },
      get idle() { return !pumping && !queue.length && !busy && !lock; }, get ask() { return askOn(); }, say, get sets() { return { bgm: bgmOn(), se: seOn(), fx: fxOn(), raw: { bgm: st.bgm, se: st.se, fx: st.fx }, as: AS }; },
      get bgm() { return { on: !!bg.cur, want: bg.want, have: !!bg.buf, gone: bg.gone, pos: bgmPos(), len: BGM.len, pre: BGM.pre, vol: BGM.vol, file: BGM.file, loop: bg.cur ? [bg.cur.s.loopStart, bg.cur.s.loopEnd] : null, ctx: snd.ac ? snd.ac.state : null }; }, setSet, speed: k => { SPEED = k; }, manual: on => { clk.manual = !!on; }, tick, get now() { return clk.now; }, start: m => startMatch(m), menu: () => { leave(false); showMenu(); }, settle, pay, load, save, modOn
    }
  };
})();

;window.CBRules = CBRules; window.CBCpu = CBCpu; window.CBNet = CBNet; window.CBApp = CBApp;
