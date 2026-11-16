// 馬カードバトルの「対戦の 進め役」（第4.176版）：ルール（cb_rules.js）と 画面（cb_app.js）の あいだ
//   まさちゃん 2026/11/15 21:54「・コンピュータと対戦 ・部屋を作成して、友達と対戦 これをやりたい！」
//
//   対戦の 中身（山札の 並び・2人の 手札）は「親」だけが 持つ：
//     ・コンピュータと 対戦：この 端末が 親。相手の 席に コンピュータ（cb_cpu.js）が すわる
//     ・部屋を 作った 人（ホスト）：この 端末が 親。友だち（ゲスト）には「友だちに 見せて いい こと」だけを 送る（CBRules.view・evFor）
//     ・部屋に 入った 人（ゲスト）：自分の 手を 親に 送って、見せて もらった ものを 画面に 出す だけ
//   どの 形でも 画面からは 同じ 使い方（match）：
//     match.kind（'cpu'・'host'・'guest'）・match.onUpdate＝{ ev, view } を 受ける 関数・match.onState＝つながりの できごと（'again'：相手が もう 1回・'lost'：切れた・'bye'：相手が やめた・'ver'：版が ちがう）
//     match.start()・match.act(a) → Promise<{ ok, why }>・match.again()（もう 1回）・match.idle()（画面の 動きが 終わった：コンピュータは ここから 考える）・match.leave()
//
//   つなぎ方（link）は 部品を さしかえる：{ send(文字), onText＝受けた 文字を もらう 関数, onLost＝切れた, close() }
//     ・近くの 友だち（アプリ）：CBNet.nativeRoom()（Swift の Room.swift：iPhone どうしが 直接 つながる・サーバーなし）
//     ・テスト：2つの 画面を じかに つなぐ（test_cb.py）
//   やりとり する もの（JSON の 文字・1つ 20KB まで）：
//     { t:'hello', v }（はじめに おたがいに。版が ちがえば 対戦しない）・{ t:'up', n, ev, view }（親 → ゲスト）・{ t:'act', id, a }（ゲスト → 親）・{ t:'ack', id, ok, why }（親 → ゲスト）
//     { t:'again' }（もう 1回）・{ t:'bye' }（やめる）
const CBNet = (() => {
  'use strict';
  const R = CBRules, PROTO = 3, MAXLEN = 20000;      // PROTO 3（第4.178版）：5ターン・手札 7まい・6 の 条件が かわった ＝ 前の 版の アプリとは 対戦しない（「アプリの 版が ちがう」と 出る）。PROTO 2＝第4.177版（5 の 条件・3 の 効果）
  const say = (m, k, v) => { try { if (typeof m[k] === 'function') m[k](v); } catch (e) { /* 画面の 中の まちがいで 対戦を 止めない */ } };

  // ---------- 親（コンピュータと 対戦・部屋の ホスト）----------
  //   seat1＝相手の 席：{ up(u)（相手に 見せる ものが できた）, idle()（画面が 落ちついた）, stop() }
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
    m.start = () => { if (!alive) return; S = R.newGame(rng, opt); m.wantAgain = [false, false]; n = 0; push([{ e: 'deal' }]); };      // opt＝手札を 決めて はじめる（テスト・見本 用）
    m.act = a => Promise.resolve(apply(0, a));
    m.idle = () => { if (seat && seat.idle) seat.idle(); };
    m.again = () => {                                   // もう 1回：2人とも 押したら 配り直す（コンピュータは いつでも OK）
      if (!alive || !S || S.phase !== 'end') return;
      m.wantAgain[0] = true; if (seat && seat.again) seat.again();
      if (m.wantAgain[1]) m.start();
    };
    m.leave = () => { if (!alive) return; alive = false; if (seat) seat.stop(true); };
    m._ = { state: () => S, apply: apply, seatAgain: () => { m.wantAgain[1] = true; if (m.wantAgain[0]) m.start(); else say(m, 'onState', 'again'); }, end: why => { if (!alive) return; alive = false; if (seat) seat.stop(false); say(m, 'onState', why); } };
    seat = mkSeat(m);
    return m;
  }

  // コンピュータと 対戦
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
        // 画面の 動きが 終わって から 考えはじめる（めくる 動きの 間に 次の カードを 出して いた ように 見えない ため）
        idle: () => { if (stopped || timer || !last || !CBCpu.decide(last, () => 0.5)) return; timer = setTimeout(go, think ? think(last) : 700 + Math.floor(rng() * 900)); },
        again: () => { m.wantAgain[1] = true; },
        stop: () => { stopped = true; clearTimeout(timer); }
      };
    }, opt);
  }

  // 部屋の ホスト（親）：link の むこうに 友だち
  function host(link, rng, opt) {
    rng = rng || Math.random;
    return parent('host', rng, m => {
      let hello = false, closed = false, want = false;
      const send = o => { if (!closed) link.send(JSON.stringify(o)); };
      // 配るのは 友だちの あいさつ（hello：版が 同じ）が 届いて から
      const deal = m.start; m.start = () => { want = true; if (hello) deal(); };
      link.onText = txt => {
        if (closed || typeof txt !== 'string' || txt.length > MAXLEN) return;
        let o; try { o = JSON.parse(txt); } catch (e) { return; }
        if (!o || typeof o !== 'object') return;
        if (o.t === 'hello') { if (o.v !== PROTO) { send({ t: 'hello', v: PROTO }); m._.end('ver'); return; } if (!hello) { hello = true; send({ t: 'hello', v: PROTO }); say(m, 'onState', 'ready'); if (want) deal(); } return; }
        if (!hello) return;
        if (o.t === 'act') { const r = m._.apply(1, o.a); send({ t: 'ack', id: o.id, ok: r.ok, why: r.why }); }
        else if (o.t === 'again') m._.seatAgain();
        else if (o.t === 'bye') m._.end('bye');
      };
      link.onLost = () => { if (!closed) m._.end('lost'); };
      return {
        up: u => send({ t: 'up', n: u.n, ev: u.ev, view: u.view }),
        again: () => send({ t: 'again' }),
        stop: mine => { if (closed) return; if (mine) send({ t: 'bye' }); closed = true; setTimeout(() => { try { link.close(); } catch (e) { /* なし */ } }, mine ? 250 : 0); }
      };
    }, opt);
  }

  // 部屋の ゲスト：親（ホスト）に 手を 送って、見せて もらった ものを 受ける
  function guest(link) {
    let alive = true, id = 0, hello = false;
    const wait = {};
    const m = { kind: 'guest', me: 1, onUpdate: null, onState: null };
    const send = o => { if (alive) link.send(JSON.stringify(o)); };
    const end = why => { if (!alive) return; alive = false; Object.keys(wait).forEach(k => wait[k]({ ok: false, why: 'off' })); try { link.close(); } catch (e) { /* なし */ } say(m, 'onState', why); };
    link.onText = txt => {
      if (!alive || typeof txt !== 'string' || txt.length > MAXLEN) return;
      let o; try { o = JSON.parse(txt); } catch (e) { return; }
      if (!o || typeof o !== 'object') return;
      if (o.t === 'hello') { if (o.v !== PROTO) end('ver'); else if (!hello) { hello = true; say(m, 'onState', 'ready'); } }
      else if (o.t === 'up' && o.view && Array.isArray(o.ev)) say(m, 'onUpdate', { n: o.n, ev: o.ev, view: o.view });
      else if (o.t === 'ack') { const f = wait[o.id]; if (f) { delete wait[o.id]; f({ ok: !!o.ok, why: o.why }); } }
      else if (o.t === 'again') say(m, 'onState', 'again');
      else if (o.t === 'bye') end('bye');
    };
    link.onLost = () => end('lost');
    m.start = () => send({ t: 'hello', v: PROTO });
    m.act = a => new Promise(ok => { if (!alive) return ok({ ok: false, why: 'off' }); id += 1; wait[id] = ok; send({ t: 'act', id: id, a: a }); });
    m.idle = () => { };
    m.again = () => send({ t: 'again' });
    m.leave = () => { if (!alive) return; send({ t: 'bye' }); alive = false; setTimeout(() => { try { link.close(); } catch (e) { /* なし */ } }, 250); };
    return m;
  }

  // ---------- 近くの 友だちと つなぐ（アプリ：Swift の Room.swift）----------
  //   nativeRoom().open('host'|'join', 部屋番号) → Promise<link>（つながったら）。onStep(名前)＝とちゅうの 様子（'wait'：さがして いる・待って いる／'found'：見つけた）
  //   やめる とき：cancel()
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

  return { PROTO, cpu, host, guest, nativeRoom };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = CBNet;
