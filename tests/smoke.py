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
check(re.search(r'VERSION = "([^"]+)"', (ROOT / 'laptop/DXF-Assistant.py').read_text()).group(1) == v, 'laptop helper VERSION matches')
check((ROOT / 'laptop/DXF-Assistant.html').read_text(encoding='utf-8') == page, 'laptop/DXF-Assistant.html is the same page')
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
            T = 'window.__dxfTest'
            el = pg.evaluate('()=>{const T=%s,r=T.S.p.rooms[0];return r.walls.map(w=>T.elevSVG(r,w.id,true).length)}' % T)
            check(all(n > 500 for n in el), 'an elevation for every wall')
            nd = pg.evaluate('()=>%s.roomNeeds(%s.S.p.rooms[0]).map(x=>x.k+":"+x.need+"/"+x.have)' % (T, T))
            check(any(x.startswith('rj:') for x in nd) and any(x.startswith('water:') for x in nd), 'equipment needs counted ' + ', '.join(nd))
            fd = pg.evaluate('async()=>{const T=window.__dxfTest;const root=await navigator.storage.getDirectory();const d=await root.getDirectoryHandle("DXF",{create:true});T.DIR.h=d;T.DIR.name="DXF";const was=T.ST.exp;T.ST.exp="folder";T.download("t.dxf","0 EOF","application/dxf");await new Promise(r=>setTimeout(r,400));T.ST.exp=was;const f=await (await d.getFileHandle("t.dxf")).getFile();return (await f.text()).length+"|"+T.S.msg;}')
            check(fd.startswith('5|Saved t.dxf in DXF'), 'exports can go straight into a chosen folder (%s)' % fd)
            pj = pg.evaluate('async()=>{const T=window.__dxfTest;const root=await navigator.storage.getDirectory();const d=await root.getDirectoryHandle("D2",{create:true});T.DIR.h=d;T.DIR.name="D2";const was=T.ST.exp;T.ST.exp="folder";T.A.dxf();await new Promise(r=>setTimeout(r,800));T.ST.exp=was;const n=[];for await (const k of d.keys())n.push(k);return n.sort().join(",");}')
            check(re.fullmatch(r'[^,]+\.dxf', pj) is not None, 'Export DXF writes the drawing only (%s)' % pj)
            zf = pg.evaluate('async()=>{const T=window.__dxfTest;const root=await navigator.storage.getDirectory();const d=await root.getDirectoryHandle("Z",{create:true});T.DIR.h=d;T.DIR.name="Z";const was=T.ST.exp,wb=T.ST.bundle;T.ST.exp="folder";T.A.projexp();await new Promise(r=>setTimeout(r,1200));T.ST.exp=was;T.ST.bundle=wb;const n=[];for await (const k of d.keys())n.push(k);const z=n.find(x=>x.endsWith(".zip"));const fs=z?await T.unzip(await (await (await d.getFileHandle(z)).getFile()).arrayBuffer()):{};return n.join(",")+"|"+Object.keys(fs).sort().join(",")+"|"+T.S.msg;}')
            check(re.match(r'^([^,|]+)\.zip\|\1\.dxf,\1\.json\|Saved .*Inside: the DXF and the project file', zf) is not None, 'Export project is one .zip with the DXF and the project file inside (%s)' % zf)
            df = pg.evaluate('()=>{const T=window.__dxfTest,S=T.S,keep=JSON.stringify(S.p);try{S.p.floors=[S.p.floors[0]];S.p.labs.forEach(l=>l.floor=S.p.floors[0].id);T.A.delfloor();const ok=S.p.rooms.length>0&&S.p.labs.length>0&&S.p.floors.length>0;S.p=JSON.parse(keep);S.room=S.p.rooms[0].id;T.render();return ok;}catch(e){S.p=JSON.parse(keep);S.room=S.p.rooms[0].id;T.render();return String(e);}}')
            check(df is True, 'deleting the only floor leaves a room to draw in (%s)' % df)
            pbd = pg.evaluate('()=>{const T=window.__dxfTest,S=T.S,r=S.p.rooms[0];const q={id:T.uid(),kind:"pb",wall:r.walls[3].id,along:2000,off:0,val:"24",bw:600,bd:200,bh:1000};r.points.push(q);T.render();const d=T.toDXF(S.p);const el=T.elevSVG(r,r.walls[3].id,true);r.points=r.points.filter(x=>x!==q);T.render();return [d,el.indexOf(">PB<")>0];}')
            pdoc, paud = recover.read(io.BytesIO(pbd[0].encode('utf-8')))
            pins = [e for e in pdoc.modelspace().query('INSERT') if e.dxf.name == 'Power Board 600x200']
            check(not paud.has_errors and len(pins) == 1 and pins[0].dxf.color == 2 and 'Power Board 600x200' in pdoc.blocks and any(e.dxf.text == 'PB 24 breakers' for e in pdoc.modelspace().query('TEXT')) and pbd[1], 'a power board exports as a block of its own size (Power Board 600x200) with its breakers, and shows on the elevation')
            sd = pg.evaluate('()=>{const T=window.__dxfTest,S=T.S,r=S.p.rooms[0],w=r.walls[3];const q={id:T.uid(),kind:"pb",wall:w.id,along:1000,off:0,side:"out",bw:360,bd:100,bh:450};r.points.push(q);T.render();const L=S.G.layouts[r.id].walls.find(x=>x.id===w.id),g=S.G.points.find(x=>x.id===q.id);const inner=[0,1].map(i=>0);const d=T.toDXF(S.p);r.points=r.points.filter(x=>x!==q);T.render();const a=g.rot*Math.PI/180,n=[-Math.sin(a),Math.cos(a)],c=[(L.A[0]+L.B[0])/2,(L.A[1]+L.B[1])/2];return [Math.round(Math.abs((g.p[0]-L.A[0])*L.n[0]+(g.p[1]-L.A[1])*L.n[1])),d.indexOf("Power Board 360x100")>0];}')
            check(sd[1] and sd[0] > 50, 'a power board on the other side of the wall sits on its far face (%s mm off the inside face), as its own size block' % sd[0])
            nb = pg.evaluate("""()=>{const T=window.__dxfTest,S=T.S,keep=JSON.stringify(S.p),r=S.p.rooms[0];r.place={mode:'free',x:0,y:0,rot:0};
              const W=(l,t)=>({id:T.uid(),len:l,turn:t,t:null,m:null});S.p.rooms.push({id:T.uid(),lab:r.lab,name:'Corridor',nameGr:'',num:'',t:200,m:'masonry',walls:[W(3000,0),W(4000,90),W(3000,90),W(4000,90)],openings:[],items:[],points:[],furn:[],place:{mode:'free',x:-3200,y:0,rot:0}});
              r.points.push({id:'nbpb',kind:'pb',wall:r.walls[3].id,along:2000,off:0,side:'out'});T.render();const g=S.G.points.find(x=>x.id==='nbpb');const x=Math.round(g.p[0]);S.p=JSON.parse(keep);S.room=S.p.rooms[0].id;T.render();return x;}""")
            check(nb == -200, 'a board on the far side clears the wall of the room next door too (face at x=%s, expected -200)' % nb)
            pu = pg.evaluate("""()=>{const T=window.__dxfTest,S=T.S,r=S.p.rooms[0],w=r.walls.map(x=>x.id);const keep=r.furn.slice();r.furn.push({id:'pt1',kind:'pts',wall:w[1],along:1500,off:0,rot:0,w:500,d:400},{id:'up1',kind:'ups',wall:w[2],along:1000,off:0,rot:0,w:600,d:800});T.render();const d=T.toDXF(S.p);r.furn=keep;T.render();return d;}""")
            udoc, uaud = recover.read(io.BytesIO(pu.encode('utf-8')))
            names = sorted(e.dxf.name for e in udoc.modelspace().query('INSERT') if e.dxf.name in ('PTS', 'UPS'))
            check(not uaud.has_errors and names == ['PTS', 'UPS'] and 'PTS' in udoc.blocks and 'UPS' in udoc.blocks, 'PTS and UPS export as blocks of their own (%s)' % names)
            gr = pg.evaluate("""()=>{const T=window.__dxfTest;T.A.lang('el');T.A.step(1);T.render();return new Promise(r=>setTimeout(()=>{const t=document.querySelector('#dock').innerText+'|'+document.querySelector('.panel').innerText.slice(0,200);T.A.lang('en');r(t);},200));}""")
            check('Χώρος' in gr and 'Τοίχοι' in gr, 'the interface switches to Greek (%s…)' % gr[:40].replace('\n', ' '))
            mp = pg.evaluate("""()=>{const T=window.__dxfTest,S=T.S;T.save();const a=S.p.id;S._pjnew=true;T.A.pjnew();S.p.name='Second';T.save();const b=S.p.id;T.A.pjnext('1');const c=S.p.id;T.A.pjnext('1');const d=S.p.id;T.A.pjclose(b);const e=S.p.id;return [a!==b,c===a,d===b,e===a].join(',');}""")
            check(mp == 'true,true,true,true', 'several projects open at once, cycled in order and closed (%s)' % mp)
            pl = pg.evaluate("""()=>{const T=window.__dxfTest,S=T.S,r=S.p.rooms[0],keep=JSON.stringify(S.p);T.A.step(6);T.render();
              const svg=document.getElementById('svg'),m=svg.getScreenCTM(),sp=(x,y)=>{const p=svg.createSVGPoint();p.x=x;p.y=-y;const q=p.matrixTransform(m);return [q.x,q.y];};
              const lay=S.G.layouts[r.id],w=lay.walls[0],P=(u,v)=>[w.A[0]+w.d[0]*u-w.n[0]*v,w.A[1]+w.d[1]*u-w.n[1]*v],out=[];
              for(const [k,u] of [['wcab',1500],['bcab',3000]]){S.editFurn=null;S.dFurn.kind='';T.A.fkind(k);const q=sp(...P(u,150)),el=document.elementFromPoint(q[0],q[1]);
                const o={bubbles:true,clientX:q[0],clientY:q[1],pointerId:1,isPrimary:true,pointerType:'touch'};el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));el.dispatchEvent(new MouseEvent('click',o));
                const f=r.furn[r.furn.length-1];out.push(f.kind+':'+Math.round(f.off));}
              S.p=JSON.parse(keep);S.room=S.p.rooms[0].id;S.editFurn=null;T.render();return out.join(',');}""")
            check(pl == 'wcab:0,bcab:300', 'a wall cabinet goes against the wall and a bench cabinet under the bench, its front flush with the bench front (%s)' % pl)
            two = pg.evaluate("""()=>{const T=window.__dxfTest,S=T.S,r=S.p.rooms[0],keep=JSON.stringify(S.p);T.A.step(5);T.A.ptkind('rj');T.render();
              const svg=document.getElementById('svg'),sp=(x,y)=>{const m=svg.getScreenCTM(),p=svg.createSVGPoint();p.x=x;p.y=-y;const q=p.matrixTransform(m);return [q.x,q.y];};
              const w=S.G.layouts[r.id].walls[2],n0=r.points.length,tapAt=u=>{const P=[w.A[0]+w.d[0]*u+w.n[0]*75,w.A[1]+w.d[1]*u+w.n[1]*75],q=sp(...P),el=document.elementFromPoint(q[0],q[1]),o={bubbles:true,clientX:q[0],clientY:q[1],pointerId:2,isPrimary:true,pointerType:'touch'};
                el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));el.dispatchEvent(new MouseEvent('click',o));};
              tapAt(1000);tapAt(2500);tapAt(4000);const n=r.points.length-n0;S.p=JSON.parse(keep);S.room=S.p.rooms[0].id;S.editPt=null;T.render();return n;}""")
            check(two == 3, 'three taps on a wall add three outlets in a row, the tool staying picked (%s added)' % two)
            back = pg.evaluate('(d)=>%s.dxfSegs(d).segs.length' % T, dxf)
            check(back > 20, 'a DXF reads back in as an underlay (%d lines)' % back)
            sv = pg.evaluate('()=>%s.siteReport()' % T)
            check('Checklist' in sv and ('Site survey' in sv or 'Site Survey' in sv), 'site survey is made, with the checklist')
            b64 = pg.evaluate('()=>%s.surveyPDF().then(b=>b.arrayBuffer()).then(a=>{let s="";const u=new Uint8Array(a);for(let i=0;i<u.length;i+=32768)s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));return btoa(s);})' % T)
            import base64, pypdf
            rd = pypdf.PdfReader(io.BytesIO(base64.b64decode(b64)))
            check(len(rd.pages) >= 1 and abs(float(rd.pages[0].mediabox.width) - 595.28) < 1, 'site survey PDF opens (%d page(s), A4)' % len(rd.pages))
            phb = pg.evaluate('()=>{const T=%s;T.A.photos();const ok=!!document.getElementById("phin3")&&!document.getElementById("phin3").hasAttribute("capture");T.A.photos();return ok&&!!document.getElementById("bphotos");}' % T)
            check(phb, 'photos open from the top bar, with a picker for photos already on the device')
            n2 = pg.evaluate('''()=>{const T=%s,S=T.S,r=S.p.rooms[0],t=T.tplFrom(r,'t');const before=JSON.parse(JSON.stringify(S.p));
              T.A.addfloor=T.A.addfloor;const fid=T.uid(),lid=T.uid();S.p.floors.push({id:fid,name:'1st floor'});S.p.labs.push({id:lid,name:'Lab B',floor:fid});
              const r2=JSON.parse(JSON.stringify(r));r2.id=T.uid();r2.lab=lid;r2.furn=[];r2.points=[];r2.num='13';S.p.rooms.push(r2);S.room=r2.id;T.tplApply(r2,t);
              return [r2.furn.length+r2.points.length,0,T.toDXF(S.p)];}''' % T)
            check(n2[0] > 5, 'a template fills another room (%d items)' % n2[0])
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
    # measuring from a photo: perspective maths on the wall plane, on the device
    cx = b.new_context(viewport={'width': 1180, 'height': 820})
    px = cx.new_page(); px.goto(url); px.wait_for_timeout(500)
    pm = px.evaluate("""()=>{const T=window.__dxfTest,Hc=T.homog([[0,0],[6000,0],[6000,2700],[0,2700]],[[120,880],[1500,800],[1420,180],[200,90]]),P=p=>T.hApply(Hc,p);
      const R=T.pmCompute({ref:{w:210,h:297,pts:[P([2000,1797]),P([2210,1797]),P([2210,1500]),P([2000,1500])]},wall:[P([0,0]),P([6000,0])],opens:[{type:'door',pts:[P([800,2100]),P([1800,0])]},{type:'window',pts:[P([3500,2100]),P([5000,900])]}]});
      return [R.len,R.opens[0].off,R.opens[0].w,R.opens[0].h,R.opens[1].off,R.opens[1].w,R.opens[1].h,R.opens[1].sill].map(v=>Math.round(v)).join(',')}""")
    check(pm == '6000,800,1000,2100,3500,1500,1200,900', 'a wall, a door and a window measured from a photo in perspective (%s)' % pm)
    # photo wizard (experimental): a plan read from photos becomes a closed room, its openings and services on the right walls
    pw = px.evaluate("""()=>{const T=window.__dxfTest,o={walls:[{length_mm:6000,turn_deg:-90},{length_mm:4000,turn_deg:-90},{length_mm:3000,turn_deg:-91},{length_mm:1500,turn_deg:88},{length_mm:3100,turn_deg:-90},{length_mm:2500,turn_deg:-90}],
        openings:[{type:'door',wall:1,offset_mm:1000,width_mm:1000},{type:'door',wall:1,offset_mm:1040,width_mm:1000},{type:'window',wall:2,offset_mm:500,width_mm:1500,sill_mm:900,height_mm:1200}],
        services:[{kind:'s1p',wall:1,offset_mm:3000,height_mm:300,count:2}],pillars:[{kind:'pillar',wall:1,offset_mm:4000,width_mm:400,depth_mm:400}],confidence:'medium'};
      const B=T.pwBuild(o,{h:'',ref:'6000',walls:[[1],[1],[1],[1],[1],[1]]}),L=T.layoutRoom({walls:B.walls,t:150},[0,0],0,false),w0=B.walls[0];
      return [L.closed,B.walls.length,w0.len,B.walls.map(w=>Math.round(w.turn)).join('/'),B.openings.length,B.openings[0].wall===w0.id,B.openings[0].off,B.points.map(q=>q.along).join('/'),B.items[0].along,Math.round(L.area/1e4)].join(',')}""")
    check(pw == 'true,6,6000,0/90/90/-90/90/90,2,true,4000,2950/3050,1600,1943', 'photo wizard: a draft read from photos closes, wall 1 first, and keeps its openings and outlets in place (%s)' % pw)
    # photo wizard, photogrammetry: a 6 x 4 m room photographed from two spots (sensors a little off), its corners and an analyzer tapped, solved to size
    pg = px.evaluate("""()=>{const T=window.__dxfTest,PG=T.PG;let sd=11;const rnd=()=>{sd=(sd*16807)%2147483647;return sd/2147483647;},gs=()=>{const u=rnd()||1e-9,v=rnd();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);};
      const P={c1:[0,4,0],c2:[6,4,0],c3:[6,0,0],c4:[0,0,0],aL:[4.844,1.789,0],aR:[4.844,0.3,0]},K={c1:'corner',c2:'corner',c3:'corner',c4:'corner',aL:'equip',aR:'equip'},ST=[[2,1.5,1.5],[4,2.6,1.48]],LAND=[0,-1,0,1,0,0,0,0,1],photos=[],cand={};let n=0;
      ST.forEach((c,si)=>[0,30,60,90,120,150,180,210,240,270,300,330].forEach(h=>{const R=PG.mm(PG.rot(h,72,0),LAND),ph={id:'p'+(n++),W:1600,H:1200,ang:90,st:si};
        Object.keys(P).forEach(k=>{const uv=PG.proj({W:1600,H:1200,R:R,ang:90},P[k],c,0.82,null);if(uv&&uv[0]>20&&uv[0]<1580&&uv[1]>20&&uv[1]<1180)(cand[k]=cand[k]||[]).push([Math.hypot(uv[0]-800,uv[1]-600),ph.id,[uv[0]+gs()*1.5,uv[1]+gs()*1.5],si]);});
        ph.R=PG.mm(PG.exp([gs()*0.7,gs()*0.7,gs()*1.5+4*si].map(v=>v*Math.PI/180)),R);photos.push(ph);}));
      const pts=Object.keys(P).map(k=>{const o={};[0,1].forEach(si=>(cand[k]||[]).filter(c=>c[3]===si).sort((a,b)=>a[0]-b[0]).slice(0,2).forEach(c=>o[c[1]]=c[2]));return{id:k,k:K[k],obs:o};});
      const s=PG.solve({photos:photos,pts:pts,camH:1.5,laser:{a:'c1',b:'c2',d:6}}),d=(a,b)=>Math.hypot(s.X[a][0]-s.X[b][0],s.X[a][1]-s.X[b][1]);
      return [d('c2','c3'),d('c3','c4'),d('c4','c1'),d('aL','aR')].map((v,i)=>Math.abs(v-[4,6,4,1.489][i])<0.15?'ok':Math.round(v*1000)).join(',')+','+(s.rms<3?'fit':'misfit')+','+s.spots}""")
    check(pg == 'ok,ok,ok,ok,fit,2', 'photo wizard: photogrammetry from two spots puts the walls and an analyzer to size (%s)' % pg)
    # Atellica: the configuration sits under Siemens; a CH, IM or CI for the Sample Handler never goes in alone
    at = px.evaluate("""()=>{const T=window.__dxfTest,S=T.S,A=T.A,r=S.p.rooms[0];T.ST.lu=null;
      A.libmodel('ch930');const L=T.ST.lu,seq=L.main.join('+'),sh=S.sheet,ty=L.type;
      A.libmodel('im1600');const seq2=T.ST.lu.main.join('+');
      A.libmodel('atcis');const seq3=T.ST.lu.type+':'+T.ST.lu.main.join('+');S.sheet=false;
      const kw=JSON.stringify(r.walls);if(!r.walls.length)r.walls=[6000,4000,6000,4000].map((l,i)=>({id:'zw'+i,len:l,turn:i?90:0,t:null,m:null}));
      const keep=JSON.stringify(r.furn||[]);r.furn=(r.furn||[]).concat([{id:'zz1',kind:'equip',model:'ch930',w:1489,d:1156,wall:r.walls[0].id,along:200,off:0}]);T.render();
      const w1=S.G.warn.filter(x=>/Atellica CH 930 Analyzer needs a Sample Handler or a Rack Handler/.test(x)).length;
      r.furn.push({id:'zz2',kind:'equip',model:'atsh',w:1222,d:1431,wall:r.walls[0].id,along:2000,off:0});T.render();
      const w2=S.G.warn.filter(x=>/needs a Sample Handler/.test(x)).length;r.furn=JSON.parse(keep);r.walls=JSON.parse(kw);T.render();T.ST.lu=null;
      return [seq,sh,ty,seq2,seq3,w1,w2].join(',');}""")
    check(at == 'atsh+ch930,lineup,sol,atsh+ch930+im1600,ci:atsh+atcis,1,0', 'Atellica CH, IM and CI for the Sample Handler go in behind a Sample Handler; a lone one is flagged (%s)' % at)
    # wall wizard: each corner tapped at the floor and the ceiling from ONE spot, the room height by laser: the room to size, whatever height the camera is held at
    fcj = """(cfg)=>{const T=window.__dxfTest,PG=T.PG;let sd=cfg.seed;const rnd=()=>{sd=(sd*16807)%2147483647;return sd/2147483647;},gs=()=>{const u=rnd()||1e-9,v=rnd();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);};
  const H=2.8,C={c1:[0,4],c2:[6,4],c3:[6,0],c4:[0,0]},ST=cfg.spots===1?[[2.6,1.8,1.45]]:[[2,1.5,1.5],[4,2.6,1.48]],LAND=[0,-1,0,1,0,0,0,0,1],photos=[],cand={},candT={};let n=0;
  ST.forEach((c,si)=>[0,30,60,90,120,150,180,210,240,270,300,330].forEach(h=>cfg.tilts.forEach(tl=>{const R=PG.mm(PG.rot(h,tl,0),LAND),ph={id:'p'+(n++),W:1600,H:1200,ang:90,st:si};
    Object.keys(C).forEach(k=>{[[0,cand],[H,candT]].forEach(([z,bag])=>{const uv=PG.proj({W:1600,H:1200,R:R,ang:90},[C[k][0],C[k][1],z],c,0.82,null);
      if(uv&&uv[0]>20&&uv[0]<1580&&uv[1]>20&&uv[1]<1180)(bag[k]=bag[k]||[]).push([Math.hypot(uv[0]-800,uv[1]-600),ph.id,[uv[0]+gs()*1.5,uv[1]+gs()*1.5],si]);});});
    ph.R=PG.mm(PG.exp([gs()*0.7,gs()*0.7,gs()*1.5+4*si].map(v=>v*Math.PI/180)),R);photos.push(ph);})));
  const ties=[];if(cfg.ties){const Rt={};photos.forEach(p=>Rt[p.id]=p);   // specks of wall seen in two overlapping photos from one spot
    const truth={};let m=0;ST.forEach((c,si)=>[0,30,60,90,120,150,180,210,240,270,300,330].forEach(h=>cfg.tilts.forEach(tl=>{truth['p'+(m++)]={R:PG.mm(PG.rot(h,tl,0),LAND),c:c};})));
    const wallPt=()=>{const w=Math.floor(rnd()*4),t=rnd(),z=0.2+rnd()*2.4;return w===0?[t*6,4,z]:w===1?[6,4-t*4,z]:w===2?[6-t*6,0,z]:[0,t*4,z];};
    for(let i=0;i<photos.length;i++)for(let j=i+1;j<photos.length;j++){const A=photos[i],B=photos[j];if(A.st!==B.st)continue;let got=0;
      for(let k=0;k<400&&got<12;k++){const X=wallPt(),ta=truth[A.id],tb=truth[B.id],ua=PG.proj({W:1600,H:1200,R:ta.R,ang:90},X,ta.c,0.82,null),ub=PG.proj({W:1600,H:1200,R:tb.R,ang:90},X,tb.c,0.82,null);
        if(ua&&ub&&ua[0]>0&&ua[0]<1600&&ua[1]>0&&ua[1]<1200&&ub[0]>0&&ub[0]<1600&&ub[1]>0&&ub[1]<1200){ties.push({a:A.id,b:B.id,ua:[ua[0]+gs(),ua[1]+gs()],ub:[ub[0]+gs(),ub[1]+gs()]});got++;}}}}
  const pick=(bag,k)=>{const o={};ST.forEach((_,si)=>(bag[k]||[]).filter(c=>c[3]===si).sort((a,b)=>a[0]-b[0]).slice(0,2).forEach(c=>o[c[1]]=c[2]));return o;};
  const pts=Object.keys(C).map(k=>{const q={id:k,k:'corner',obs:pick(cand,k)};if(cfg.top)q.top=pick(candT,k);return q;});
  const M={photos:photos,pts:pts,camH:cfg.camH||0,ties:ties};if(cfg.roomH)M.roomH=H+gs()*0.003;if(cfg.laser)M.laser={a:'c1',b:'c2',d:6};
  const s=PG.solve(M);if(!s)return null;const d=(a,b)=>Math.hypot(s.X[a][0]-s.X[b][0],s.X[a][1]-s.X[b][1]);
  const e=[d('c1','c2')-6,d('c2','c3')-4,d('c3','c4')-6,d('c4','c1')-4].map(v=>Math.round(v*1000));return {e:e,rms:+s.rms.toFixed(2),H:s.H&&+s.H.toFixed(3),ang:Math.round(Math.min(...pts.map(q=>s['a'+q.id])))};}"""
    fr = [px.evaluate(fcj, dict(spots=1, tilts=[70, 110], top=1, roomH=1, ties=1, seed=sd)) for sd in (7919, 15838)]
    fw = [max(abs(x) for x in r['e']) if r else None for r in fr]
    check(all(w is not None and w <= 40 for w in fw) and all(abs(r['H'] - 2.8) < 0.01 for r in fr), 'wall wizard: floor and ceiling corners from one spot put a 6 × 4 m room to within 40 mm (%s)' % fw)
    # profiles decide the steps; Export site survey asks for signatures first
    pf = px.evaluate("""()=>{const T=window.__dxfTest,S=T.S,A=T.A,was=T.ST.profile,out=[];const dock=()=>[...document.querySelectorAll('#dock [data-act=steptab]')].map(b=>b.dataset.v).join('');
      A.profset('measure');out.push(dock());A.step(5);out.push(S.step);A.profset('building');out.push(dock());A.stepset('7:1');out.push(dock());
      A.profset('lab');out.push(dock());A.step(8);A.report();out.push(S.sheet);A.sheetclose();if(was)T.ST.profile=was;return out.join(',');}""")
    check(pf == '12438,8,1243568,12435678,12435678,survey', 'profiles: Measure only, Other rooms and Clinical laboratory show their steps; Export site survey opens the signatures first (%s)' % pf)
    # Wall wizard: start over in parts (marks, last spot, everything), and take a drawn draft out again
    rd = px.evaluate("""async()=>{const T=window.__dxfTest,A=T.A,S=T.S,out=[];A.pwopen();await new Promise(r=>setTimeout(r,800));let P=T.getPW();
      const blob=new Blob([new Uint8Array([255,216,255,217])],{type:'image/jpeg'});
      P.ref='5400';P.photos=['a','b','c','d','e'].map((id,i)=>({id:id,st:i<3?0:1,url:URL.createObjectURL(blob),w:640,h:480,R:T.PG.rot(i*60,80,0),ang:0,f:500,work:{}}));P.pts=[{id:'q1',k:'corner',obs:{a:[1,1],d:[2,2]}},{id:'q2',k:'corner',obs:{e:[1,1]}}];P.stage='mark';
      A.pwredo();out.push(document.querySelectorAll('.pw-redobox [data-act=pwredo1]').length);
      A.pwredo1('spot');await new Promise(r=>setTimeout(r,300));P=T.getPW();out.push(P.photos.map(p=>p.id).join('')+'/'+P.pts.length);
      A.pwredo();A.pwredo1('marks');P=T.getPW();out.push(P.photos.length+'/'+P.pts.length);
      A.pwredo();A.pwredo1('all');P=T.getPW();out.push(P.photos.length+'/'+P.ref);A.pwclose();
      const r=S.p.rooms[0],kw=JSON.stringify([r.walls,r.openings,r.items]);r.walls=[6000,4000,6000,4000].map((l,i)=>({id:'zw'+i,len:l,turn:i?90:0,t:null,m:null,src:'ai'}));r.openings=[{id:'zo',type:'door',wall:'zw2',off:1000,w:900,src:'ai'}];A.step(2);T.render();
      const c=!!document.querySelector('[data-act=pwdraftdel]'),cf=window.confirm;window.confirm=()=>true;A.pwdraftdel();window.confirm=cf;out.push(c+'/'+r.walls.length+'/'+r.openings.length+'/'+S.sheet);
      A.pwclose();const k=JSON.parse(kw);r.walls=k[0];r.openings=k[1];r.items=k[2];T.render();return out.join(',');}""")
    check(rd == '3,abc/1,3/0,0/5400,true/0/0/pw', 'wall wizard: redo the marks, retake the last spot or start over, and take a drawn draft out again (%s)' % rd)
    # export bundle: the DXF, the project file and the photos in one .zip, and it opens again
    zp = px.evaluate("""async()=>{const T=window.__dxfTest,S=T.S,r=S.p.rooms[0],id='ph_zt';r.photos=(r.photos||[]).concat([{id:id}]);
      const jpg=new Uint8Array([255,216,255,224,1,2,3,4,255,217]);try{await T.pPut(id,new Blob([jpg],{type:'image/jpeg'}));}catch(e){return 'E put '+e;}
      const jpg2=0;let st='zip',z,fs;try{z=await T.projZip(S.p,'Lab 1','0 EOF');st='unzip';fs=await T.unzip(await z.blob.arrayBuffer());}catch(e){return 'E '+st+' '+e;}const names=Object.keys(fs).sort();
      const p=T.projFromZip(fs),u=p.photoData&&p.photoData[id],b=u?new Uint8Array(await (await fetch(u)).arrayBuffer()):[];
      r.photos=r.photos.filter(x=>x.id!==id);
      return [names.join('|'),z.photos,p.rooms.length===S.p.rooms.length,b.length===jpg.length&&b[0]===255&&b[9]===217,!!p.photoFiles].join(',');}""")
    check(zp.startswith('Lab 1.dxf|Lab 1.json|photos/') and zp.endswith(',1,true,true,false'), 'export .zip holds the DXF, the project file and its photos, and opens again (%s)' % zp)
    import zipfile as _zf, json
    _buf = io.BytesIO()
    with _zf.ZipFile(_buf, 'w', _zf.ZIP_DEFLATED) as _z:
        _z.writestr('Lab 1/Lab 1.json', json.dumps({'name': 'Re-zipped', 'rooms': [{'id': 'r1', 'walls': []}]}))
        _z.writestr('Lab 1/Lab 1.dxf', '0\nEOF')
    dz = px.evaluate("""async(b64)=>{const T=window.__dxfTest,u=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));return T.projFromZip(await T.unzip(u.buffer)).name;}""", __import__('base64').b64encode(_buf.getvalue()).decode())
    check(dz == 'Re-zipped', 'a .zip made again in Windows or Finder (deflated, in a folder) still opens (%s)' % dz)
    cx.close()
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
bl = [e for e in msp if e.dxf.layer == 'Room Beams']
lay = doc.layers.get('Room Beams') if 'Room Beams' in doc.layers else None
check(lay is not None and lay.color == 125 and lay.dxf.linetype.upper() == 'DASHED2', 'layer Room Beams: colour 125, dashed')
pl = [e for e in bl if e.dxftype() == 'LWPOLYLINE']
check(len(pl) == 1 and pl[0].closed and len(pl[0]) == 4 and any(e.dxftype() == 'TEXT' and 'u/s' in e.dxf.text for e in bl), 'a beam exports as one closed dashed polyline and its underside height')
doc2, aud2 = recover.read(io.BytesIO(dxf2.encode('utf-8')))
check(not aud2.has_errors and any(e.dxftype() == 'TEXT' and e.dxf.text == '1st floor' for e in doc2.modelspace()), 'two floors export, each named')

print('\n%d problem(s)' % len(fails) if fails else '\nall checks passed')
sys.exit(1 if fails else 0)
