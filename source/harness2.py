import json, os, sys
from playwright.sync_api import sync_playwright
page_html = open('tengel3.html', encoding='utf8').read()
hist = json.load(open('hist.json', encoding='utf8'))
mock = """<script>
const COLS = { races: %s, bets: [] };
const LIS = { races: [], bets: [] };
function snapOf(name, filters){ return { docs: COLS[name].filter(d=>filters.every(([f,op,v])=> op==='>='? d[f]>=v : op==='<'? d[f]<v : true)).map(d=>({id:d.id, exists:true, data:()=>d})) }; }
function fire(name){ for (const [f,cb] of LIS[name]) setTimeout(()=>cb(snapOf(name,f)),10); }
function mkQuery(name, filters){ return { where(f,op,v){ return mkQuery(name,[...filters,[f,op,v]]); }, limit(){ return this; },
 onSnapshot(cb){ LIS[name].push([filters,cb]); setTimeout(()=>cb(snapOf(name,filters)),30); return ()=>{}; },
 doc(id){ return { set: async(d)=>{ COLS[name]=COLS[name].filter(x=>x.id!==id); COLS[name].push({...d,id}); fire(name); }, update: async(d)=>{ const x=COLS[name].find(x=>x.id===id); if(!x) throw {code:'invalid_argument'}; Object.assign(x,d); fire(name); }, delete: async()=>{ COLS[name]=COLS[name].filter(x=>x.id!==id); fire(name); }, get: async()=>{ const x=COLS[name].find(x=>x.id===id); return {id, exists:!!x, data:()=>x}; } }; } }; }
window.__COLS = COLS;
window.claude = { use: async (n) => n==='db' ? { collection: (name) => mkQuery(name,[]) } : n==='user' ? { canEdit: async()=>true } : null };
</script>""" % json.dumps(hist, ensure_ascii=False)
skeleton = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light}body{margin:0;font:14px system-ui}img{max-width:100%%}[hidden]{display:none!important}</style>%s</head><body>%s</body></html>'
open('harness2.html','w',encoding='utf8').write(skeleton % (mock, page_html))
form = {"venue":"大井","date":"2026-10-10","r":"8","dist":"1400","surface":"ダ","baba":"稍重","n":"14","s1":"41.3","s1combo":"6-2-10","s5":"58.2","s10":"84.0",
 "rows":[{"no":no,"tan":str(t),"fuku":f} for no,t,f in [(1,12.4,'3.0-4.6'),(2,4.1,'1.6-2.2'),(3,31.5,'6.1-9.8'),(4,9.8,'2.6-3.9'),(5,18.2,'4.0-6.2'),(6,2.4,'1.1-1.3'),(7,7.6,'2.1-3.1'),(8,54.0,'9.4-15.0'),(9,25.9,'5.2-8.1'),(10,6.3,'1.9-2.7'),(11,14.7,'3.3-5.1'),(12,88.6,'13.2-21.1'),(13,40.2,'7.7-12.2'),(14,120.5,'18.4-29.6')]]}
with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    for scheme,(w,h,tag) in [('light',(390,1800,'phone')),('dark',(1280,1150,'desk'))]:
        ctx = b.new_context(viewport={'width':w,'height':h}, color_scheme=scheme)
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type=='error' and 'ERR_TUNNEL' not in m.text else None)
        pg.add_init_script("localStorage.setItem('tengel.form', %s)" % json.dumps(json.dumps(form, ensure_ascii=False)))
        pg.goto('file://' + os.path.abspath('harness2.html')); pg.wait_for_timeout(700)
        card = pg.locator('#recCard')
        # B層: 第1 中穴→人気。結果 7-6-2（馬番）= 4人気→1人気→2人気 → 第1的中・3着人気
        card.locator('[data-k=types] button[data-v="3連単"]').click()
        card.locator('[data-k=stake]').fill('1800')
        card.locator('[data-k=res]').fill('7-6-2')
        pg.wait_for_timeout(150)
        print(tag, 'status:', card.locator('[data-k=status]').inner_text().replace('\n',' '), '| hint:', card.locator('[data-k=hint]').inner_text())
        card.locator('[data-k=payout]').fill('5230')
        card.locator('[data-act=save]').click(); pg.wait_for_timeout(400)
        print(tag, 'toast:', pg.locator('#toast').inner_text(), '| bets:', pg.evaluate('JSON.stringify(window.__COLS.bets.map(b=>({id:b.id,p:[b.p1,b.p2,b.p3],n:[b.n1,b.n2,b.n3],types:b.types,stake:b.stake,payout:b.payout,kubun:b.snap.kubun})))'))
        pg.screenshot(path=f'v2_judge_{tag}.png', full_page=False) if tag=='desk' else None
        if tag=='phone':
            card.scroll_into_view_if_needed(); pg.wait_for_timeout(100)
            card.screenshot(path='v2_card_phone.png')
        # second record: 未購入 race (different R) via setting form R
        pg.select_option('#fR', '9'); pg.wait_for_timeout(300)
        card.locator('[data-k=other] button[data-v="未購入"]').click()
        card.locator('[data-k=res]').fill('6-2-10'); pg.wait_for_timeout(100)
        card.locator('[data-act=save]').click(); pg.wait_for_timeout(400)
        # third: 払い戻し
        pg.select_option('#fR', '10'); pg.wait_for_timeout(300)
        card.locator('[data-k=other] button[data-v="払い戻し"]').click()
        card.locator('[data-k=stake]').fill('600'); card.locator('[data-act=save]').click(); pg.wait_for_timeout(400)
        # fourth: 不的中
        pg.select_option('#fR', '11'); pg.wait_for_timeout(300)
        card.locator('[data-k=stake]').fill('1000'); card.locator('[data-k=res]').fill('1-3-5'); card.locator('[data-act=save]').click(); pg.wait_for_timeout(400)
        print(tag, 'n bets', pg.evaluate('window.__COLS.bets.length'), 'races', pg.evaluate('window.__COLS.races.length'))
        sel = '.tabbar' if tag=='phone' else '.tabs-top'
        pg.click(f'{sel} button[data-tab=rec]'); pg.wait_for_timeout(300)
        pg.screenshot(path=f'v2_rec_{tag}.png', full_page=(tag=='phone'))
        pg.click(f'{sel} button[data-tab=stats]'); pg.wait_for_timeout(300)
        pg.screenshot(path=f'v2_stats_{tag}.png', full_page=False)
        print(tag, 'money tiles:', pg.locator('.money-tiles').inner_text().replace('\n',' '))
        sw = pg.evaluate('document.documentElement.scrollWidth')
        if sw > w: errs.append(f'{tag} overflow {sw}')
        ctx.close()
    b.close()
    print('errors:', errs)
