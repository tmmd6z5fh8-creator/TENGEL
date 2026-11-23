# テスト用：おもちゃ（お世話チャレンジ・TENGERカードバトル：第4.212版から 1つ 3,000P で 解放）を、0P で 解放した ことに する。
#   カードバトル・トレーニングセンターの 中身の テストは、解放の あとの 動きを 見る もの → はじめに これを 呼ぶ（ポイントの 残りは かわらない）。
#   解放の 窓（🔒・「3,000Pを使って解放する」・足りない とき）は test_native.py・test_cb.py・test_tc_drop.py が 本物の 流れで 見る。
#   やり方：台帳（TengelWallet.snapshot）に 0P の 解放の しるし（unlock-toy:<id>）を 足して 入れ直す（TengelWallet.restore：アプリの 自動バックアップから 戻す 口と 同じ）。
#   アプリの 中に テスト用の 入口は 作らない（アプリの コードは かえない）
OPEN_TOYS_JS = """async ids => {
  if (!window.TengelWallet || !TengelWallet.toy) return null;
  await TengelWallet.ready;
  const s = TengelWallet.snapshot(); if (!s) return null;
  let n = 0, add = 0; s.events.forEach(e => { if (e && +e.n > n) n = +e.n; });
  for (const id of ids) if (!s.events.some(e => e && e.id === 'unlock-toy:' + id)) {
    s.events.push({ id: 'unlock-toy:' + id, kind: 'unlock', bucket: '', amount: 0, at: new Date().toISOString(), what: 'toy:' + id, device: 'test', use: { paid_sub: 0, paid_pack: 0, free: 0 }, n: ++n }); add++;
  }
  if (add) { await TengelWallet.restore(s); document.dispatchEvent(new CustomEvent('tengel:wallet')); }
  return ids.map(id => TengelWallet.toy.has(id));
}"""


def open_toys(pg, ids=('cb', 'drop')):
    """おもちゃを 0P で 解放した ことに する。返り値：[解放して あるか, …]（財布が まだ ない ページでは None）"""
    return pg.evaluate(OPEN_TOYS_JS, list(ids))
