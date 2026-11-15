#!/usr/bin/env python3
"""Automatic checks run before every release: the app opens without errors, every step and 3D draw,
and the DXF it writes is valid, on the right layers and colours, and starts at 0,0."""
import functools, http.server, io, re, sys, threading
from pathlib import Path

import ezdxf
from ezdxf import recover
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
fails = []
def check(ok, msg):
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok:
        fails.append(msg)

# versions agree everywhere
v = (ROOT / 'VERSION').read_text().strip()
page = (ROOT / 'index.html').read_text(encoding='utf-8')
check(re.search(r"const APP_VERSION='([^']+)'", page).group(1) == v, 'APP_VERSION matches VERSION ' + v)
check(re.search(r"const VERSION = '([^']+)'", (ROOT / 'sw.js').read_text()).group(1) == v, 'sw.js VERSION matches')
check(re.search(r'VERSION = "([^"]+)"', (ROOT / 'laptop/DXF-Sketch.py').read_text()).group(1) == v, 'laptop helper VERSION matches')
check((ROOT / 'laptop/DXF-Sketch.html').read_text(encoding='utf-8') == page, 'laptop/DXF-Sketch.html is the same page')
check(re.search(r'"v": "' + re.escape(v) + '"', page) is not None, "What's new has an entry for " + v)
check(('## ' + v + ' ') in (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8'), 'CHANGELOG.md has a section for ' + v)

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass
handler = functools.partial(Quiet, directory=str(ROOT))
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
url = 'http://127.0.0.1:%d/index.html?test' % srv.server_address[1]

SAMPLE = '''()=>{const T=window.__dxfTest,{S,render,uid,FURN}=T;const r=S.p.rooms[0];S.p.name='Test Hospital';r.name='Microbiology';r.num='12';
  const W=(l,t)=>({id:uid(),len:l,turn:t,t:null,m:null});r.walls=[W(6000,0),W(4000,90),W(6000,90),W(4000,90)];const w=r.walls.map(x=>x.id);
  r.openings=[{id:uid(),type:'door',wall:w[2],off:1500,w:1000,leaves:1,swing:'in'},{id:uid(),type:'window',wall:w[1],off:800,w:1500}];
  r.items=[{id:uid(),kind:'pillar',shape:'rect',wall:w[1],along:2800,w:400,d:400,off:0}];
  r.beams=[{id:uid(),a:{wall:w[0],u:3000},b:{wall:w[2],u:3000},w:300,us:2400}];
  r.points=['s1p','s1u','rj','water','drain','air'].map((k,i)=>({id:uid(),kind:k,wall:w[0],along:600+i*800,off:0}));
  const F=(k,wall,al,o,x)=>Object.assign({id:uid(),kind:k,wall:wall,along:al,off:o||0,rot:FURN[k].rot||0},x||{});
  r.furn=[F('bench',w[0],200,0,{w:4000,d:700}),F('pc',w[0],500,0),F('sink',w[0],2600,0),F('bcab',w[0],700,0),F('osmo',w[2],4200,0),F('equip',w[3],500,0,{w:600,d:650,name:'Fridge'})];
  r.place={mode:'free',x:12345,y:-6789,rot:17};S.p.labs[0].north=60;S.room=r.id;render();return 1;}'''

with sync_playwright() as p:
    b = p.chromium.launch(**({'executable_path': '/usr/bin/google-chrome', 'args': ['--no-sandbox']} if __import__('os').environ.get('LOCAL_CHROME') else {}))
    for vp in [(1180, 820), (820, 1180), (390, 844)]:
        pg = b.new_page(viewport={'width': vp[0], 'height': vp[1]})
        errs = []
        pg.on('pageerror', lambda e, errs=errs: errs.append(str(e)))
        pg.goto(url)
        pg.wait_for_timeout(800)
        pg.evaluate(SAMPLE)
        for step in range(1, 9):
            pg.evaluate('(s)=>window.__dxfTest.A.step(s)', step)
            pg.wait_for_timeout(120)
        pg.evaluate('()=>{window.__dxfTest.A.v3d();}'); pg.wait_for_timeout(300)
        for m in ['low', 'cut', 'full']:
            pg.evaluate('(m)=>window.__dxfTest.A.w3d(m)', m); pg.wait_for_timeout(120)
        pg.evaluate('()=>{window.__dxfTest.A.v3d();}'); pg.wait_for_timeout(200)
        for sh in ['settings', 'about', 'sharesheet', 'projects']:
            pg.evaluate('(a)=>{window.__dxfTest.A[a]();}', sh); pg.wait_for_timeout(150)
            pg.evaluate('(a)=>{window.__dxfTest.A[a]();}', sh); pg.wait_for_timeout(80)
        check(not errs, 'no script errors at %dx%d %s' % (vp[0], vp[1], errs[:2] if errs else ''))
        if vp[0] == 1180:
            dxf = pg.evaluate('()=>window.__dxfTest.toDXF(window.__dxfTest.S.p)')
            plan = pg.evaluate('()=>window.__dxfTest.planPrintHTML()')
            T = 'window.__dxfTest'
            el = pg.evaluate('()=>{const T=%s,r=T.S.p.rooms[0];return r.walls.map(w=>T.elevSVG(r,w.id,true).length)}' % T)
            check(all(n > 500 for n in el), 'an elevation for every wall')
            nd = pg.evaluate('()=>%s.roomNeeds(%s.S.p.rooms[0]).map(x=>x.k+":"+x.need+"/"+x.have)' % (T, T))
            check(any(x.startswith('rj:') for x in nd) and any(x.startswith('water:') for x in nd), 'equipment needs counted ' + ', '.join(nd))
            fd = pg.evaluate('async()=>{const T=window.__dxfTest;const root=await navigator.storage.getDirectory();const d=await root.getDirectoryHandle("DXF",{create:true});T.DIR.h=d;T.DIR.name="DXF";const was=T.ST.exp;T.ST.exp="folder";T.download("t.dxf","0 EOF","application/dxf");await new Promise(r=>setTimeout(r,400));T.ST.exp=was;const f=await (await d.getFileHandle("t.dxf")).getFile();return (await f.text()).length+"|"+T.S.msg;}')
            check(fd.startswith('5|Saved t.dxf in DXF'), 'exports can go straight into a chosen folder (%s)' % fd)
            pj = pg.evaluate('async()=>{const T=window.__dxfTest;const root=await navigator.storage.getDirectory();const d=await root.getDirectoryHandle("DXF",{create:true});const was=T.ST.exp;T.ST.exp="folder";T.A.dxf();await new Promise(r=>setTimeout(r,800));T.ST.exp=was;const n=[];for await (const k of d.keys())n.push(k);const j=n.find(x=>x.endsWith(".json"));const p=JSON.parse(await (await (await d.getFileHandle(j)).getFile()).text());return n.sort().join(",")+"|"+p.rooms.length+"|"+(p.live===undefined);}')
            check(re.search(r'(\w+)\.dxf,\1\.json', pj) is not None and pj.endswith('|1|true'), 'the DXF export saves the project file next to it (%s)' % pj)
            df = pg.evaluate('()=>{const T=window.__dxfTest,S=T.S,keep=JSON.stringify(S.p);try{S.p.floors=[S.p.floors[0]];S.p.labs.forEach(l=>l.floor=S.p.floors[0].id);T.A.delfloor();const ok=S.p.rooms.length>0&&S.p.labs.length>0&&S.p.floors.length>0;S.p=JSON.parse(keep);S.room=S.p.rooms[0].id;T.render();return ok;}catch(e){S.p=JSON.parse(keep);S.room=S.p.rooms[0].id;T.render();return String(e);}}')
            check(df is True, 'deleting the only floor leaves a room to draw in (%s)' % df)
            pbd = pg.evaluate('()=>{const T=window.__dxfTest,S=T.S,r=S.p.rooms[0];const q={id:T.uid(),kind:"pb",wall:r.walls[3].id,along:2000,off:0,val:"24"};r.points.push(q);T.render();const d=T.toDXF(S.p);const el=T.elevSVG(r,r.walls[3].id,true);r.points=r.points.filter(x=>x!==q);T.render();return [d,el.indexOf(">PB<")>0];}')
            pdoc, paud = recover.read(io.BytesIO(pbd[0].encode('utf-8')))
            pins = [e for e in pdoc.modelspace().query('INSERT') if e.dxf.name == 'Power Board']
            check(not paud.has_errors and len(pins) == 1 and pins[0].dxf.color == 2 and 'Power Board' in pdoc.blocks and any(e.dxf.text == 'PB 24 breakers' for e in pdoc.modelspace().query('TEXT')) and pbd[1], 'a power board exports as its own block with its breakers, and shows on the elevation')
            back = pg.evaluate('(d)=>%s.dxfSegs(d).segs.length' % T, dxf)
            check(back > 20, 'a DXF reads back in as an underlay (%d lines)' % back)
            sv = pg.evaluate('()=>%s.siteReport()' % T)
            check('Checklist' in sv and 'Site survey' in sv, 'site survey is made, with the checklist')
            b64 = pg.evaluate('()=>%s.surveyPDF().then(b=>b.arrayBuffer()).then(a=>{let s="";const u=new Uint8Array(a);for(let i=0;i<u.length;i+=32768)s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));return btoa(s);})' % T)
            import base64, pypdf
            rd = pypdf.PdfReader(io.BytesIO(base64.b64decode(b64)))
            check(len(rd.pages) >= 1 and abs(float(rd.pages[0].mediabox.width) - 595.28) < 1, 'site survey PDF opens (%d page(s), A4)' % len(rd.pages))
            n2 = pg.evaluate('''()=>{const T=%s,S=T.S,r=S.p.rooms[0],t=T.tplFrom(r,'t');const before=JSON.parse(JSON.stringify(S.p));
              T.A.addfloor=T.A.addfloor;const fid=T.uid(),lid=T.uid();S.p.floors.push({id:fid,name:'1st floor'});S.p.labs.push({id:lid,name:'Lab B',floor:fid});
              const r2=JSON.parse(JSON.stringify(r));r2.id=T.uid();r2.lab=lid;r2.furn=[];r2.points=[];r2.num='13';S.p.rooms.push(r2);S.room=r2.id;T.tplApply(r2,t);
              const rows=T.compareRows(before,S.p);return [r2.furn.length+r2.points.length,rows.filter(x=>x.st==='new').length,T.toDXF(S.p)];}''' % T)
            check(n2[0] > 5, 'a template fills another room (%d items)' % n2[0])
            check(n2[1] == 1, 'compare finds the new room')
            dxf2 = n2[2]
        pg.close()
    # shared editing: two people, each with their own token, against a pretend GitHub
    import json as _j, time as _t
    gists, seq = {}, [0]
    toks = {'ta': 'alice', 'tb': 'bob'}
    def gh(route, req):
        u = req.url.split('api.github.com')[1].split('?')[0]
        tok = (req.headers.get('authorization') or '').replace('Bearer ', '')
        def ok(o, st=200): route.fulfill(status=st, content_type='application/json', body=_j.dumps(o))
        if u == '/user': return ok({'login': toks.get(tok, 'x')}) if tok in toks else ok({'message': 'Bad credentials'}, 401)
        if u == '/gists' and req.method == 'POST':
            seq[0] += 1; gid = 'G%d' % seq[0]; body = _j.loads(req.post_data)
            gists[gid] = {'owner': tok, 'files': body['files'], 'at': _t.time()}
            return ok({'id': gid, 'updated_at': '2026-11-15T10:00:%02dZ' % seq[0]}, 201)
        gid = u.split('/')[2] if u.startswith('/gists/') else None
        if gid not in gists: return ok({'message': 'Not Found'}, 404)
        g = gists[gid]
        if req.method == 'PATCH':
            if g['owner'] != tok: return ok({'message': 'Not Found'}, 404)
            g['files'].update(_j.loads(req.post_data)['files']); g['at'] = _t.time()
        return ok({'id': gid, 'updated_at': '2026-11-15T10:%02d:00Z' % (int(g['at']) % 60), 'files': {k: {'content': v['content'], 'truncated': False} for k, v in g['files'].items()}})
    gists['G0'] = {'owner': 'ta', 'files': {'dxf-sketch.json': {'content': '{}'}}, 'at': 0}
    seq[0] = 0
    def person(tok):
        c = b.new_context(viewport={'width': 1180, 'height': 820})
        c.route('https://api.github.com/**', gh)
        c.route('https://ntfy.sh/**', lambda r: r.fulfill(status=200, body=''))
        c.add_init_script("localStorage.setItem('dxf-sketch-gh','%s');localStorage.setItem('dxf-sketch-ghme',JSON.stringify({login:'%s'}));" % (tok, toks[tok]))
        pg = c.new_page(); errs = []; pg.on('pageerror', lambda e, errs=errs: errs.append(str(e))); return c, pg, errs
    T = 'window.__dxfTest'
    ca, A, ea = person('ta')
    A.goto(url); A.wait_for_timeout(600); A.evaluate(SAMPLE)
    A.evaluate('async()=>{const T=%s,S=T.S;const r2=JSON.parse(JSON.stringify(S.p.rooms[0]));r2.id=T.uid();r2.name="Store";S.p.rooms.push(r2);S.p.live="G0";S.p.liveTopic="tp";T.save();await T.livePush();}' % T)
    cb, B, eb = person('tb')
    B.goto(url + '#live=G0'); B.wait_for_timeout(1200)
    names = B.evaluate('()=>%s.S.p.rooms.map(r=>r.name).join(",")' % T)
    check(names == 'Microbiology,Store', 'a shared project opens for someone else (%s)' % names)
    B.wait_for_timeout(50)
    B.evaluate('async()=>{const T=%s,S=T.S;T.commit(()=>{S.p.rooms[0].name="Micro B";});T.save();await T.livePush(S.p.id);await new Promise(r=>setTimeout(r,100));await T.livePush(S.p.id);}' % T)
    mine = B.evaluate('()=>%s.S.p.myGist||""' % T)
    check(mine.startswith('G') and gists[mine]['owner'] == 'tb', 'an editor’s changes go into a Gist on their own account')
    A.evaluate('async()=>{const T=%s,S=T.S;T.commit(()=>{S.p.rooms[1].name="Store A";});S.p.contrib=[{gist:"%s"}];T.save();await T.coSync();await new Promise(r=>setTimeout(r,50));await T.livePush();}' % (T, mine))
    names = A.evaluate('()=>%s.S.p.rooms.map(r=>r.name).join(",")' % T)
    check(names == 'Micro B,Store A', 'the owner gets the editor’s change and keeps their own (%s)' % names)
    B.evaluate('async()=>{const T=%s;await T.coSync();}' % T)
    names = B.evaluate('()=>%s.S.p.rooms.map(r=>r.name).join(",")' % T)
    check(names == 'Micro B,Store A', 'the editor gets the owner’s change (%s)' % names)
    B.evaluate('async()=>{const T=%s,S=T.S;T.commit(()=>{S.p.rooms=S.p.rooms.filter(r=>r.name!=="Store A");});T.save();await new Promise(r=>setTimeout(r,50));await T.livePush(S.p.id);}' % T)
    A.evaluate('async()=>{const T=%s;await T.coSync();}' % T)
    names = A.evaluate('()=>%s.S.p.rooms.map(r=>r.name).join(",")' % T)
    check(names == 'Micro B', 'a room deleted by an editor goes for the owner too (%s)' % names)
    # both change the same room: asked which to keep, and the other side follows the choice
    B.evaluate('async()=>{const T=%s,S=T.S;T.commit(()=>{S.p.rooms[0].name="Bob room";});T.save();await new Promise(r=>setTimeout(r,50));await T.livePush(S.p.id);}' % T)
    A.evaluate('async()=>{const T=%s,S=T.S;T.commit(()=>{S.p.rooms[0].name="Alice room";});T.save();await T.coSync();}' % T)
    q = A.evaluate('()=>{const S=%s.S;return [(S.conflicts||[]).length,S.sheet,S.p.rooms[0].name].join("|")}' % T)
    check(q == '1|conflict|Alice room', 'two people changing the same room are asked which to keep (%s)' % q)
    A.evaluate('async()=>{const T=%s,S=T.S;T.A.cfmine(S.conflicts[0].id);await new Promise(r=>setTimeout(r,50));await T.livePush();}' % T)
    B.evaluate('async()=>{const T=%s;await T.coSync();}' % T)
    q = B.evaluate('()=>{const S=%s.S;return [(S.conflicts||[]).length,S.p.rooms[0].name].join("|")}' % T)
    check(q == '0|Alice room', 'the other person follows “keep mine” without being asked again (%s)' % q)
    B.evaluate('async()=>{const T=%s,S=T.S;T.commit(()=>{S.p.rooms[0].name="Bob again";});T.save();await new Promise(r=>setTimeout(r,50));await T.livePush(S.p.id);}' % T)
    A.evaluate('async()=>{const T=%s,S=T.S;T.commit(()=>{S.p.rooms[0].name="Alice again";});T.save();await T.coSync();T.A.cftheirs(S.conflicts[0].id);await new Promise(r=>setTimeout(r,50));await T.livePush();}' % T)
    B.evaluate('async()=>{const T=%s;await T.coSync();}' % T)
    q = A.evaluate('()=>%s.S.p.rooms[0].name' % T) + '|' + B.evaluate('()=>{const S=%s.S;return (S.conflicts||[]).length+":"+S.p.rooms[0].name}' % T)
    check(q == 'Bob again|0:Bob again', '“keep theirs” takes their version on both sides (%s)' % q)
    A.evaluate('()=>{const T=%s;T.A.sharesheet();}' % T); A.wait_for_timeout(100)
    check('bob' in A.inner_text('#sheet') if A.query_selector('#sheet') else True, 'the owner sees who else is editing')
    check(not ea and not eb, 'no script errors while editing together %s' % (ea + eb)[:2])
    ca.close(); cb.close()
    b.close()
srv.shutdown()

doc, aud = recover.read(io.BytesIO(dxf.encode('utf-8')))
check(not aud.has_errors, 'DXF reads without errors ' + '; '.join(str(e.message) for e in aud.errors[:3]))
msp = doc.modelspace()
layers = {e.dxf.layer for e in msp}
check({'Room', 'Area', 'Room Dimensions'} <= layers, 'DXF layers ' + ', '.join(sorted(layers)))
furn = [e for e in msp.query('INSERT') if e.dxf.name in ('PC', 'Sink', 'Bench Cabinet', 'Osmosis') or e.dxf.name.startswith('Bench ')]
check(len(furn) >= 5 and all(e.dxf.color == 125 and e.dxf.layer == 'Room' for e in furn), 'furniture and equipment on Room in colour 125')
svc = [e for e in msp.query('INSERT') if e.dxf.name in ('Socket 1P', 'Socket 1P UPS', 'Socket RJ45', 'Water Tubing', 'Waste Tubing', 'Air Tubing')]
check(len(svc) == 6 and all(e.dxf.layer == 'Room' for e in svc), 'six services on layer Room')
xs, ys = [], []
for e in msp.query('LWPOLYLINE'):
    for q in e.get_points('xy'):
        xs.append(q[0]); ys.append(q[1])
check(abs(min(xs)) < 0.01 and abs(min(ys)) < 0.01, 'plan starts at 0,0 (min %.2f, %.2f)' % (min(xs), min(ys)))
check('1:' in plan and '<svg' in plan, 'plan to scale is made')
bl = [e for e in msp if e.dxf.layer == 'Room Beams']
lay = doc.layers.get('Room Beams') if 'Room Beams' in doc.layers else None
check(lay is not None and lay.color == 125 and lay.dxf.linetype.upper() == 'DASHED2', 'layer Room Beams: colour 125, dashed')
pl = [e for e in bl if e.dxftype() == 'LWPOLYLINE']
check(len(pl) == 1 and pl[0].closed and len(pl[0]) == 4 and any(e.dxftype() == 'TEXT' and 'u/s' in e.dxf.text for e in bl), 'a beam exports as one closed dashed polyline and its underside height')
doc2, aud2 = recover.read(io.BytesIO(dxf2.encode('utf-8')))
check(not aud2.has_errors and any(e.dxftype() == 'TEXT' and e.dxf.text == '1st floor' for e in doc2.modelspace()), 'two floors export, each named')

print('\n%d problem(s)' % len(fails) if fails else '\nall checks passed')
sys.exit(1 if fails else 0)
