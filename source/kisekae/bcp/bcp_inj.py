# 結果ボードカスタム（絵の ボード）：見本の 注入 JS（絵の 背景・ボードを 板に 合わせる・紺と 金の ボード・場所は cfg の layout）
#   python3 bcp_inj.py <デザインの フォルダ>   → inj.js
import json, math, os, sys
D = sys.argv[1]
cfg = json.load(open(os.path.join(D, 'cfg.json'), encoding='utf8'))
g = json.load(open(os.path.join(D, 'geom.json')))
m3d = ','.join(f'{v:.8f}' for v in g['m3d'])
HP = g['HP']; L = cfg['layout']; name = cfg['name']
cols = ['#FF5A6E', '#FFD24A', '#49D17A', '#4AA8FF', '#B07CFF', '#FF8AD0']
links, x, i = [], 4.0, 0
while x < 327:
    y = 6.2 + 2.6 * math.sin(math.pi * x / 331); c = cols[i % len(cols)]
    if i % 2 == 0:
        links.append(f'<ellipse cx="{x:.1f}" cy="{y:.2f}" rx="4.3" ry="2.5" fill="none" stroke="{c}" stroke-width="1.7"/>'); x += 7.4
    else:
        links.append(f'<ellipse cx="{x:.1f}" cy="{y:.2f}" rx="2.1" ry="1.5" fill="none" stroke="{c}" stroke-width="1.4"/>'); x += 4.6
    i += 1
gar = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 331 12"><g filter="url(#s)">{"".join(links)}</g><defs><filter id="s" x="-5%" y="-50%" width="110%" height="200%"><feDropShadow dx="0" dy="0.6" stdDeviation="0.5" flood-color="#000" flood-opacity=".55"/></filter></defs></svg>'
def star(cx, cy, r, rot=0):
    pts = []
    for k in range(10):
        a = math.radians(-90 + rot + k * 36); rr = r if k % 2 == 0 else r * 0.45
        pts.append(f'{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}')
    return f'<polygon points="{" ".join(pts)}" fill="url(#gd)" stroke="#9A5A06" stroke-width="0.8" stroke-linejoin="round"/>'
gd = '<defs><linearGradient id="gd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF6C4"/><stop offset=".45" stop-color="#FFD25A"/><stop offset="1" stop-color="#D98A14"/></linearGradient></defs>'
starL = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 46 36">{gd}{star(14, 22, 11, -8)}{star(36, 10, 7.5, 10)}</svg>'
starR = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 46 36">{gd}{star(10, 10, 7.5, -10)}{star(32, 22, 11, 8)}</svg>'
uri = lambda s: 'url("data:image/svg+xml,' + s.replace('"', "'").replace('#', '%23').replace('<', '%3C').replace('>', '%3E') + '")'
import base64
sti = L.get('star_img')
if sti:
    b64 = lambda f: 'data:image/png;base64,' + base64.b64encode(open(os.path.join(D, f), 'rb').read()).decode()
    dy = sti['top'] - L['normal']['title_px'] * 1.08 / 2          # 見出しの 行の まん中 から 星の 上の はし まで
    star_css = (f"#fxOv .rb.bcp.istars .bh::before,#fxOv .rb.bcp.istars .bh::after{{{{content:'';position:absolute;top:calc(50% + {dy:.2f}px);width:{sti['w']}px;height:{sti['h']}px;background-repeat:no-repeat;background-size:100% 100%;"
                f"-webkit-text-stroke:0;pointer-events:none}}}}"
                f"#fxOv .rb.bcp.istars .bh::before{{{{right:100%;margin-right:{sti['gap']}px;background-image:url({b64(sti['left'])})}}}}"
                f"#fxOv .rb.bcp.istars .bh::after{{{{left:100%;margin-left:{sti['gap']}px;background-image:url({b64(sti['right'])})}}}}")
else:
    star_css = ''
css = f"""
#fxOv .ov > :not(.hb):not(.close):not(.bcpbg):not(.sr),#fxOv .fxs > video{{display:none!important}}
#fxOv .bcpbg{{position:absolute;left:0;top:0;width:390px;height:844px;background:url(bcp_{name}.webp) 0 0/390px 844px no-repeat;z-index:0;pointer-events:none}}
#fxOv .ov > .hb{{z-index:2}}
#fxOv .rb.bcp{{position:relative!important;width:350px!important;height:{HP}px!important;padding:0!important;background:transparent!important;box-shadow:none!important;border:0!important;border-radius:0!important;
  transform-origin:0 0!important;transform:matrix3d({m3d})!important;animation:none!important;outline:0!important;box-sizing:border-box}}
#fxOv .rb.bcp::before,#fxOv .rb.bcp::after{{display:none!important}}
#fxOv .rb.bcp .hd{{position:static!important;background:transparent!important;box-shadow:none!important;border:0!important;border-radius:0!important;padding:0!important;margin:0!important;height:0!important;min-height:0!important}}
#fxOv .rb.bcp .bh{{position:absolute!important;white-space:nowrap;line-height:1.08;letter-spacing:1px;margin:0!important;
  background:linear-gradient(180deg,#FFFCEB 0%,#FFE98A 26%,#FFCB3D 50%,#EE9F1E 74%,#C9780F 100%);-webkit-background-clip:text;background-clip:text;color:transparent!important;-webkit-text-fill-color:transparent!important;
  -webkit-text-stroke:.9px #7A3E00;filter:drop-shadow(0 1.6px 0 #5A2E00) drop-shadow(0 0 9px rgba(255,196,70,.62))}}
#fxOv .rb.bcp .bh .bz,#fxOv .rb.bcp .bh .bx3{{color:transparent!important;-webkit-text-fill-color:transparent!important}}
#fxOv .rb.bcp .bh.bcp1x{{letter-spacing:0}}#fxOv .rb.bcp .bh.bcp1x .bzx{{margin-left:-.2em}}
#fxOv .rb.bcp.stars .bh::before,#fxOv .rb.bcp.stars .bh::after{{content:'';position:absolute;top:-3px;width:46px;height:36px;background-repeat:no-repeat;background-size:100% 100%}}
#fxOv .rb.bcp.stars .bh::before{{right:100%;margin-right:14px;background-image:{uri(starL)}}}
#fxOv .rb.bcp.stars .bh::after{{left:100%;margin-left:22px;background-image:{uri(starR)}}}
#fxOv .rb.bcp .bsub{{position:absolute!important;margin:0!important;text-align:center;color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:0 1px 2px rgba(0,0,0,.55);white-space:nowrap}}
#fxOv .rb.bcp .zrib{{position:absolute!important;display:flex!important;width:max-content!important;max-width:none!important;margin:0!important;animation:none!important}}
#fxOv .rb.bcp .bcpgar{{position:absolute;height:12px;background:{uri(gar)} center/100% 100% no-repeat;pointer-events:none}}
#fxOv .rb.bcp .card{{position:absolute!important;background:transparent!important;border:0!important;box-shadow:none!important;border-radius:0!important;padding:0!important;margin:0!important;height:auto!important}}
#fxOv .rb.bcp .card::before,#fxOv .rb.bcp .card::after{{display:none!important}}
#fxOv .rb.bcp .brows li{{min-height:0!important;padding:0 8px!important;background:rgba(40,54,100,.58)!important;border:1px solid rgba(150,172,230,.30)!important;border-radius:11px!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.06)!important;box-sizing:border-box}}
#fxOv .rb.bcp .bt{{background:rgba(12,20,48,.88)!important;border:1px solid rgba(172,192,240,.48)!important;color:#fff!important;-webkit-text-fill-color:#fff!important;height:21px!important}}
#fxOv .rb.bcp .rs.miss,#fxOv .rb.bcp .rs.void{{background:rgba(8,14,36,.92)!important;border:1px solid rgba(160,182,232,.36)!important;color:#fff!important;-webkit-text-fill-color:#fff!important;height:21px!important}}
#fxOv .rb.bcp .rs.hit{{background:linear-gradient(180deg,#FFEDB0,#F7C24C)!important;border:0!important;color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:0 1px 1px rgba(128,72,0,.85),0 0 2px rgba(128,72,0,.5);height:21px!important}}
#fxOv .rb.bcp .ar{{color:#B8C8F0!important;-webkit-text-fill-color:#B8C8F0!important}}
#fxOv .rb.bcp .more{{color:#DDE6FF!important;-webkit-text-fill-color:#DDE6FF!important}}
#fxOv .rb.bcp .brows li.no{{opacity:1!important}}
""" + star_css.replace("{{", "{").replace("}}", "}") + (("#fxOv .ov > .close{border-color:%s!important;background:%s!important;box-shadow:0 0 0 1px rgba(0,0,0,.35),0 0 10px rgba(255,200,90,.35)!important}\n" % (cfg["close_border"], cfg.get("close_bg", "rgba(0,0,0,.35)"))) if cfg.get("close_border") else "")
js = """(() => {
  const L = %s, HP = %s;
  const ov = document.querySelector('#fxOv .ov'); if (!ov) return 'no ov';
  const st = document.createElement('style'); st.id = 'bcpCss'; st.textContent = %s; document.head.appendChild(st);
  const bg = document.createElement('div'); bg.className = 'bcpbg'; ov.insertBefore(bg, ov.firstChild);
  const rb = ov.querySelector('.rb'); rb.classList.add('bcp'); if (L.stars) rb.classList.add('stars'); if (L.star_img) rb.classList.add('istars');
  const bh = rb.querySelector('.bh'), sub = rb.querySelector('.bsub'), rib = rb.querySelector('.zrib'), card = rb.querySelector('.card'), br = rb.querySelector('.brows');
  const n = rb.querySelectorAll('.brows > li').length;
  if (/[^！]！$/.test(bh.textContent)) bh.classList.add('bcp1x');      // 「…的中！」：「！」を 字に よせる（絵の 見出しと 同じ はば）
  const M = Object.assign({}, L.normal, rib ? L.rib : (n > 3 ? L.many : {}));
  const px = v => v + 'px';
  // 見出し：場所の まん中に・はばに おさまらない ときは 字を 小さく
  bh.style.fontSize = px(M.title_px); bh.style.top = px(M.title_top);
  const side = L.star_img ? (L.star_img.w + L.star_img.gap) : (L.stars ? 70 : 0);
  const tx0 = M.text_x[0], tx1 = M.text_x[1], cx = (tx0 + tx1) / 2, room = (tx1 - tx0) - 2 * side;
  if (bh.offsetWidth > room) {
    const fs = M.title_px * room / bh.offsetWidth;
    bh.style.fontSize = fs.toFixed(1) + 'px'; bh.style.top = px(M.title_top + (M.title_px - fs) * 1.08 / 2);
  }
  const w = bh.offsetWidth, half = w / 2 + side, cxp = M.title_cx != null ? M.title_cx : cx;
  const c2 = Math.min(Math.max(cxp, tx0 + half), tx1 - half);          // 絵の 見出しの まん中（title_cx）に。長い ときは 場所の 中に おさまる ように ずらす
  bh.style.left = px(c2 - w / 2);
  const sc = M.sub_cx != null ? M.sub_cx : c2, sw = 2 * Math.min(sc - tx0, tx1 - sc);
  sub.style.fontSize = px(M.sub_px); sub.style.top = px(M.sub_top); sub.style.left = px(sc - sw / 2); sub.style.width = px(sw);
  let rowsTop = M.rows_top;
  if (rib) {
    rib.style.zoom = M.rib_zoom || .8;
    const z = +rib.style.zoom, rw = rib.offsetWidth * z, rh = rib.offsetHeight * z;
    const rcx = M.rib_in === 'rows' ? (M.rows_x[0] + M.rows_x[1]) / 2 : c2;
    rib.style.left = px((rcx - rw / 2) / z); rib.style.top = px(M.rib_top / z);
    if (M.rib_in === 'rows') rowsTop = M.rib_top + rh + 6;
  }
  if (L.garland) { const gq = document.createElement('div'); gq.className = 'bcpgar'; gq.style.left = px(M.gar_x[0]); gq.style.width = px(M.gar_x[1] - M.gar_x[0]); gq.style.top = px(M.gar_top); rb.appendChild(gq); }
  card.style.left = px(M.rows_x[0]); card.style.width = px(M.rows_x[1] - M.rows_x[0]); card.style.top = px(rowsTop);
  br.style.gap = px(M.row_gap); rb.querySelectorAll('.brows > li').forEach(li => { li.style.height = px(M.row_h); });
  // 行：rows_zoom（字を 大きく）・板に おさまらない ときは 小さく（はばは そのまま）
  const avail = M.rows_bottom - rowsTop, z = M.rows_zoom || 1;
  br.style.width = (100 / z).toFixed(3) + '%%';
  let h = br.scrollHeight, k = Math.min(z, avail / h);
  br.style.width = (100 / k).toFixed(3) + '%%'; h = br.scrollHeight; k = Math.min(z, avail / h);
  br.style.width = (100 / k).toFixed(3) + '%%';
  if (Math.abs(k - 1) > 0.002) { br.style.transformOrigin = '0 0'; br.style.transform = 'scale(' + k.toFixed(4) + ')'; }
  return 'ok rows ' + n + ' h ' + h + ' avail ' + avail + ' k ' + k.toFixed(3) + ' title ' + bh.offsetWidth + ' mode ' + (rib ? 'rib' : n > 3 ? 'many' : 'normal');
})()""" % (json.dumps(L, ensure_ascii=False), HP, json.dumps(css))
open(os.path.join(D, 'inj.js'), 'w', encoding='utf8').write(js)
print('inj', name, len(js))
