#!/usr/bin/env python3
"""Build the interactive portfolio-audit HTML (tabbed: Synthesis & Plan | Audit).
Usage: gen_audit.py <workflow-output.json|result.json> <out.html> [<synthesis.json>]
synthesis: {"themes":[...],"topPriorities":[...],"plan":[{title,items:[...]}],
  "projects":[{project,verdict,readiness,revenue,differentiation,effort,fit,note}]}
Dimension scores 1-5, higher = more favorable (effort: higher = easier/closer).
Tab 1 = synthesis + plan; Tab 2 = all granular to-dos (sort/filter/check/export). Both always ship."""
import json, html, sys

IN=sys.argv[1]; OUT=sys.argv[2]; SYN=sys.argv[3] if len(sys.argv)>3 else None
raw=json.load(open(IN))
data=raw['result'] if isinstance(raw,dict) and 'result' in raw else raw
syn=json.load(open(SYN)) if SYN else None
LENS_ORDER=['developer','product','marketing','business']
LENS_NAME={'developer':'Developer','product':'Product Designer','marketing':'Marketing / GTM','business':'Business / Ops'}
DIMS=[('revenue','Rev'),('differentiation','Diff'),('effort','Effort'),('fit','Fit')]
def esc(s): return html.escape(str(s or ''))
def sc(v):
    try: n=int(round(float(v)))
    except: return ('<span class="sco sco-0">–</span>',0)
    n=max(0,min(5,n)); return (f'<span class="sco sco-{n}">{n}</span>',n)

ALLP=[e.get('project') for e in data if e]
by={e.get('project'):{l.get('lens'):l for l in e.get('lenses',[])} for e in data if e}
verdict={p.get('project'):p for p in (syn.get('projects',[]) if syn else [])}

tot=0; byprio={'high':0,'med':0,'low':0}; bytype={}
for p in ALLP:
    for l in by.get(p,{}).values():
        for t in l.get('todos',[]):
            tot+=1; byprio[t.get('priority','med')]=byprio.get(t.get('priority','med'),0)+1
            bytype[t.get('type','?')]=bytype.get(t.get('type','?'),0)+1

# ---- Tab 1: synthesis + plan ----
syn_html=''
if syn:
    themes=''.join(f'<li>{esc(t)}</li>' for t in syn.get('themes',[]))
    tops=''.join(f'<li>{esc(t)}</li>' for t in syn.get('topPriorities',[]))
    vrows=''
    for p in ALLP:
        v=verdict.get(p,{}); vd=v.get('verdict','')
        dcells=''.join(f'<td>{sc(v.get(k))[0]}</td>' for k,_ in DIMS)
        vrows+=(f'<tr data-project="{esc(p)}"><td><a href="#p-{esc(p)}" class="jump" data-p="{esc(p)}">{esc(p)}</a></td>'
                f'<td><span class="badge vd-{esc(vd)}">{esc(vd) or "—"}</span></td>'
                f'<td>{esc(v.get("readiness",""))}</td>{dcells}<td class="vnote">{esc(v.get("note",""))}</td></tr>')
    dhead=''.join(f'<th>{lbl}</th>' for _,lbl in DIMS)
    plan=syn.get('plan',[])
    waves=''.join(f'<div class="wave"><h4>{esc(w.get("title"))}</h4><ul>'+''.join(f'<li>{esc(it)}</li>' for it in w.get('items',[]))+'</ul></div>' for w in plan)
    plan_html=f'<section class="plan"><h2>Plan of action</h2><div class="waves">{waves}</div></section>' if plan else ''
    syn_html=f'''<section class="synthesis">
  <h2>Portfolio synthesis</h2>
  <div class="syncols">
    <div class="syncol"><h3>Cross-cutting themes</h3><ul>{themes or "<li>—</li>"}</ul></div>
    <div class="syncol"><h3>Top priorities</h3><ul>{tops or "<li>—</li>"}</ul></div>
  </div>
  <h3>Direction per project <span class="scohint">(scores 1–5, higher = more favorable; effort: higher = easier/closer)</span></h3>
  <div class="tablewrap"><table class="vtable" id="vtable"><thead><tr><th>Project</th><th>Verdict</th><th>Readiness</th>{dhead}<th>Direction</th></tr></thead><tbody>{vrows}</tbody></table></div>
</section>{plan_html}
<p class="synnote">This frames the audit — every one of the {tot} individual to-dos lives in the <b>Audit</b> tab, fully granular and checkable.</p>'''

# ---- Tab 2: granular audit ----
rows=[]
for p in ALLP:
    lenses=by.get(p,{}); pcount=sum(len(l.get('todos',[])) for l in lenses.values())
    missing=[lk for lk in LENS_ORDER if lk not in lenses]
    miss_html='<span class="miss">⚠ pending: '+', '.join(LENS_NAME[m] for m in missing)+'</span>' if missing else ''
    v=verdict.get(p,{}); vd=v.get('verdict','')
    vbadge=f'<span class="badge vd-{esc(vd)}">{esc(vd)}</span>' if vd else ''
    dattrs=' '.join(f'data-{k}="{sc(v.get(k))[1]}"' for k,_ in DIMS)
    hscores=''.join(f'<span class="hsco" title="{k}">{lbl}:{sc(v.get(k))[0]}</span>' for k,lbl in DIMS) if v else ''
    lens_html=[]
    for lk in LENS_ORDER:
        if lk not in lenses: continue
        l=lenses[lk]; todo_html=[]
        for i,t in enumerate(l.get('todos',[])):
            tid=f"{p}::{lk}::{i}"; deps=t.get('deps','')
            deps_html=f'<div class="deps">↳ depends on: {esc(deps)}</div>' if deps else ''
            todo_html.append(f'''<li class="todo" data-project="{esc(p)}" data-lens="{lk}" data-type="{esc(t.get('type','?'))}" data-priority="{esc(t.get('priority','med'))}">
  <input type="checkbox" class="chk" id="{esc(tid)}" data-id="{esc(tid)}">
  <div class="tbody"><div class="tline"><label for="{esc(tid)}" class="ttitle">{esc(t.get('title'))}</label>
    <span class="badge type-{esc(t.get('type','?'))}">{esc(t.get('type','?'))}</span><span class="badge prio-{esc(t.get('priority','med'))}">{esc(t.get('priority','med'))}</span></div>
    <div class="tdesc">{esc(t.get('desc',''))}</div>{deps_html}</div></li>''')
        lens_html.append(f'''<div class="lens lens-{lk}"><div class="lenshead"><span class="lensname">{LENS_NAME[lk]}</span> <span class="lenscount">{len(l.get("todos",[]))}</span></div>
  <div class="assessment">{esc(l.get('assessment',''))}</div><ul class="todos">{''.join(todo_html)}</ul></div>''')
    rows.append(f'''<section class="project" id="p-{esc(p)}" data-project="{esc(p)}" data-verdict="{esc(vd)}" {dattrs}>
  <h2 class="phead"><span class="pname">{esc(p)}</span> {vbadge} <span class="hscores">{hscores}</span> <span class="pcount">{pcount} to-dos</span> {miss_html} <span class="psel" data-project="{esc(p)}"></span></h2>
  <div class="lenses">{''.join(lens_html)}</div></section>''')

type_opts=''.join(f'<option value="{esc(k)}">{esc(k)} ({v})</option>' for k,v in sorted(bytype.items(), key=lambda x:-x[1]))
proj_opts=''.join(f'<option value="{esc(p)}">{esc(p)}</option>' for p in ALLP)
sort_opts=''.join(f'<option value="{k}">Sort: {lbl}</option>' for k,lbl in DIMS)

HTML=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Portfolio Audit</title><style>
:root{{--bg:#faf9f7;--card:#fff;--ink:#1c1b1a;--mut:#6b6864;--line:#e7e4df;--acc:#b45309}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}}
header{{position:sticky;top:0;z-index:10;background:rgba(250,249,247,.97);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:12px 22px 0}}
h1{{margin:0 0 8px;font-size:19px}}
.tabs{{display:flex;gap:4px}}
.tab{{font:inherit;font-size:14px;font-weight:600;padding:8px 16px;border:none;border-bottom:2px solid transparent;background:none;color:var(--mut);cursor:pointer}}
.tab.active{{color:var(--acc);border-bottom-color:var(--acc)}}
.panel{{max-width:1080px;margin:18px auto;padding:0 22px}}
.controls{{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:14px;position:sticky;top:78px;z-index:5;background:var(--bg);padding:8px 0}}
select,input[type=search],button.btn{{font:inherit;font-size:13px;padding:6px 9px;border:1px solid var(--line);border-radius:7px;background:#fff;color:var(--ink)}}button.btn{{cursor:pointer}}button.primary{{background:var(--acc);color:#fff;border-color:var(--acc)}}
.stats{{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--mut);margin-left:auto}}.stats b{{color:var(--ink)}}
.synthesis{{background:#fffdf7;border:1px solid #f0e6cf;border-radius:12px;padding:16px 18px;margin-bottom:18px}}
.synthesis h2,.plan h2{{margin:0 0 10px;font-size:17px}}.synthesis h3{{font-size:13px;text-transform:uppercase;letter-spacing:.03em;color:var(--mut);margin:12px 0 6px}}
.scohint{{text-transform:none;letter-spacing:0;font-weight:400;font-size:11px}}
.syncols{{display:flex;gap:24px;flex-wrap:wrap}}.syncol{{flex:1;min-width:240px}}.syncol ul{{margin:0;padding-left:18px;font-size:13.5px}}.syncol li{{margin-bottom:5px}}
.tablewrap{{overflow-x:auto}}.vtable{{width:100%;border-collapse:collapse;font-size:13px;margin-top:4px;min-width:640px}}.vtable th{{text-align:left;color:var(--mut);font-weight:600;padding:4px 8px;border-bottom:1px solid var(--line)}}
.vtable td{{padding:5px 8px;border-bottom:1px solid #f0eee9;vertical-align:top}}.vtable a{{color:var(--acc);text-decoration:none;font-weight:600;cursor:pointer}}.vnote{{color:#54514d;min-width:280px}}
.plan{{background:#f7faf7;border:1px solid #dcebdc;border-radius:12px;padding:16px 18px;margin-bottom:18px}}
.waves{{display:flex;flex-direction:column;gap:10px}}.wave h4{{margin:0 0 4px;font-size:14px}}.wave ul{{margin:0;padding-left:18px;font-size:13.5px}}.wave li{{margin-bottom:3px}}
.synnote{{font-size:12px;color:var(--mut);margin:2px 0 0;font-style:italic}}
.sco{{display:inline-block;min-width:18px;text-align:center;font-weight:700;font-size:11px;border-radius:5px;padding:1px 5px}}
.sco-5,.sco-4{{background:#d1fae5;color:#047857}}.sco-3{{background:#fef3c7;color:#b45309}}.sco-2,.sco-1{{background:#fee2e2;color:#b91c1c}}.sco-0{{background:#f3f4f6;color:#9ca3af}}
.hscores{{display:inline-flex;gap:5px}}.hsco{{font-size:10px;color:var(--mut)}}
.project{{background:var(--card);border:1px solid var(--line);border-radius:12px;margin-bottom:16px;overflow:hidden;scroll-margin-top:150px}}
.phead{{display:flex;align-items:center;gap:10px;margin:0;padding:13px 16px;font-size:16px;border-bottom:1px solid var(--line);cursor:pointer;flex-wrap:wrap}}
.pname{{font-weight:700}}.pcount{{font-size:12px;color:var(--mut);font-weight:400}}
.miss{{font-size:11px;color:#b45309;background:#fef3c7;padding:2px 7px;border-radius:20px}}.psel{{margin-left:auto;font-size:12px;color:var(--acc);font-weight:600}}
.lenses{{padding:6px 16px 14px}}.lens{{padding:10px 0;border-top:1px solid var(--line)}}.lens:first-child{{border-top:none}}
.lenshead{{display:flex;align-items:center;gap:8px;margin-bottom:6px}}.lensname{{font-weight:600;font-size:13px;letter-spacing:.02em;text-transform:uppercase}}
.lens-developer .lensname{{color:#2563eb}}.lens-product .lensname{{color:#7c3aed}}.lens-marketing .lensname{{color:#ea580c}}.lens-business .lensname{{color:#059669}}
.lenscount{{font-size:11px;color:var(--mut);background:#f3f1ee;padding:1px 7px;border-radius:20px}}
.assessment{{font-size:13.5px;color:#44413d;background:#f7f5f2;border-radius:8px;padding:9px 12px;margin-bottom:9px}}
.todos{{list-style:none;margin:0;padding:0}}.todo{{display:flex;gap:9px;padding:7px 4px;border-top:1px dashed var(--line)}}
.chk{{margin-top:3px;width:16px;height:16px;flex:none;cursor:pointer}}.tbody{{flex:1;min-width:0}}
.tline{{display:flex;align-items:center;gap:7px;flex-wrap:wrap}}.ttitle{{font-weight:600;cursor:pointer}}
.badge{{font-size:10.5px;padding:1px 7px;border-radius:20px;text-transform:uppercase;letter-spacing:.03em;font-weight:600}}
.type-bug{{background:#fee2e2;color:#b91c1c}}.type-core{{background:#e0e7ff;color:#3730a3}}.type-feature{{background:#dbeafe;color:#1d4ed8}}.type-chore{{background:#f3f4f6;color:#4b5563}}.type-polish{{background:#fae8ff;color:#a21caf}}.type-docs{{background:#ecfccb;color:#4d7c0f}}.type-infra{{background:#e0f2fe;color:#0369a1}}.type-design{{background:#f5d0fe;color:#86198f}}.type-marketing{{background:#ffedd5;color:#c2410c}}.type-business{{background:#d1fae5;color:#047857}}.type-ops{{background:#d1fae5;color:#065f46}}
.prio-high{{background:#fee2e2;color:#b91c1c}}.prio-med{{background:#fef3c7;color:#b45309}}.prio-low{{background:#f3f4f6;color:#6b7280}}
.vd-keep{{background:#d1fae5;color:#047857}}.vd-prioritize{{background:#dbeafe;color:#1d4ed8}}.vd-park{{background:#f3f4f6;color:#6b7280}}.vd-kill{{background:#fee2e2;color:#b91c1c}}
.tdesc{{font-size:13px;color:#54514d;margin-top:2px}}.deps{{font-size:12px;color:#8a8681;margin-top:3px;font-style:italic}}
.hidden{{display:none!important}}.collapsed .lenses{{display:none}}
dialog{{border:1px solid var(--line);border-radius:12px;padding:0;max-width:720px;width:92%}}dialog .dh{{padding:12px 16px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center}}dialog textarea{{width:100%;height:300px;border:none;padding:14px 16px;font:12.5px/1.5 ui-monospace,Menlo,monospace;resize:vertical}}
</style></head><body>
<header><h1>Portfolio Audit</h1>
  <div class="tabs"><button class="tab active" data-tab="plan">Synthesis &amp; Plan</button><button class="tab" data-tab="audit">Audit · {tot} to-dos</button></div>
</header>
<div id="tab-plan" class="panel">{syn_html}</div>
<div id="tab-audit" class="panel hidden">
  <div class="controls">
    <select id="fsort"><option value="">Sort: default</option>{sort_opts}<option value="verdict">Sort: verdict</option></select>
    <select id="fproj"><option value="">All projects</option>{proj_opts}</select>
    <select id="flens"><option value="">All lenses</option><option value="developer">Developer</option><option value="product">Product</option><option value="marketing">Marketing</option><option value="business">Business</option></select>
    <select id="fprio"><option value="">Any priority</option><option value="high">High</option><option value="med">Med</option><option value="low">Low</option></select>
    <select id="ftype"><option value="">Any type</option>{type_opts}</select>
    <input type="search" id="fsearch" placeholder="search…"><button class="btn" id="onlysel">Show selected only</button><button class="btn primary" id="expbtn">Export selected ▸</button>
    <span class="stats"><span id="selstat"><b>0</b> selected</span> · 🔴<b>{byprio['high']}</b> 🟡<b>{byprio['med']}</b> ⚪<b>{byprio['low']}</b></span>
  </div>
  <div id="projects">{''.join(rows)}</div>
</div>
<dialog id="dlg"><div class="dh"><b>Selected to-dos</b><button class="btn" onclick="document.getElementById('dlg').close()">Close</button></div><textarea id="dlgtext" readonly></textarea></dialog>
<script>
// tabs
document.querySelectorAll('.tab').forEach(function(b){{ b.onclick=function(){{
  document.querySelectorAll('.tab').forEach(function(x){{x.classList.remove('active')}}); b.classList.add('active');
  document.getElementById('tab-plan').classList.toggle('hidden', b.dataset.tab!=='plan');
  document.getElementById('tab-audit').classList.toggle('hidden', b.dataset.tab!=='audit');
}}; }});
// jump from synthesis table to a project in the audit tab
document.querySelectorAll('.jump').forEach(function(a){{ a.onclick=function(e){{ e.preventDefault();
  document.querySelector('.tab[data-tab="audit"]').click();
  var el=document.getElementById('p-'+a.dataset.p); if(el) el.scrollIntoView({{behavior:'smooth'}}); }}; }});
// checkboxes + persistence
var LS='portfolioAuditChecked'; var checked=new Set(JSON.parse(localStorage.getItem(LS)||'[]'));
document.querySelectorAll('.chk').forEach(function(c){{ if(checked.has(c.dataset.id))c.checked=true;
  c.addEventListener('change',function(){{ c.checked?checked.add(c.dataset.id):checked.delete(c.dataset.id); localStorage.setItem(LS,JSON.stringify([...checked])); updateSel(); }}); }});
function updateSel(){{ document.querySelector('#selstat b').textContent=checked.size;
  document.querySelectorAll('.psel').forEach(function(s){{ var p=s.dataset.project; var n=[...checked].filter(function(id){{return id.indexOf(p+'::')===0}}).length; s.textContent=n?('✓ '+n+' picked'):''; }}); }}
updateSel();
// filters
var F={{proj:'',lens:'',prio:'',type:'',q:'',sel:false}};
function applyF(){{ document.querySelectorAll('.todo').forEach(function(t){{ var ok=true;
  if(F.proj&&t.dataset.project!==F.proj)ok=false; if(F.lens&&t.dataset.lens!==F.lens)ok=false; if(F.prio&&t.dataset.priority!==F.prio)ok=false; if(F.type&&t.dataset.type!==F.type)ok=false; if(F.sel&&!t.querySelector('.chk').checked)ok=false; if(F.q&&t.textContent.toLowerCase().indexOf(F.q)<0)ok=false;
  t.classList.toggle('hidden',!ok); }});
  document.querySelectorAll('.lens').forEach(function(l){{ l.classList.toggle('hidden',![...l.querySelectorAll('.todo')].some(function(t){{return !t.classList.contains('hidden')}})); }});
  document.querySelectorAll('.project').forEach(function(p){{ p.classList.toggle('hidden',![...p.querySelectorAll('.todo')].some(function(t){{return !t.classList.contains('hidden')}})); }}); }}
// sort
var VORD={{prioritize:0,keep:1,park:2,kill:3,'':9}};
function sortBy(k){{ var cont=document.getElementById('projects'); var secs=[...cont.querySelectorAll('.project')];
  secs.sort(function(a,b){{ if(k==='verdict') return (VORD[a.dataset.verdict]==null?9:VORD[a.dataset.verdict])-(VORD[b.dataset.verdict]==null?9:VORD[b.dataset.verdict]);
    if(k) return (parseInt(b.dataset[k])||0)-(parseInt(a.dataset[k])||0); return 0; }});
  if(k) secs.forEach(function(s){{cont.appendChild(s)}}); }}
document.getElementById('fsort').onchange=function(e){{sortBy(e.target.value)}};
document.getElementById('fproj').onchange=function(e){{F.proj=e.target.value;applyF()}};
document.getElementById('flens').onchange=function(e){{F.lens=e.target.value;applyF()}};
document.getElementById('fprio').onchange=function(e){{F.prio=e.target.value;applyF()}};
document.getElementById('ftype').onchange=function(e){{F.type=e.target.value;applyF()}};
document.getElementById('fsearch').oninput=function(e){{F.q=e.target.value.toLowerCase();applyF()}};
document.getElementById('onlysel').onclick=function(){{F.sel=!F.sel;this.textContent=F.sel?'Show all':'Show selected only';applyF()}};
document.querySelectorAll('.phead').forEach(function(h){{ h.onclick=function(e){{ if(e.target.closest('a,input,label'))return; h.parentElement.classList.toggle('collapsed'); }}; }});
document.getElementById('expbtn').onclick=function(){{ var out='# Selected to-dos\\n\\n'; var byp={{}};
  document.querySelectorAll('.todo').forEach(function(t){{ var c=t.querySelector('.chk'); if(!c.checked)return; var p=t.dataset.project; (byp[p]=byp[p]||[]).push('- ['+t.dataset.type+'/'+t.dataset.priority+'] '+t.querySelector('.ttitle').textContent+'  ('+t.dataset.lens+')'); }});
  Object.keys(byp).forEach(function(p){{ out+='## '+p+'\\n'+byp[p].join('\\n')+'\\n\\n'; }});
  if(!Object.keys(byp).length)out+='(nothing selected yet)';
  document.getElementById('dlgtext').value=out; document.getElementById('dlg').showModal(); }};
</script></body></html>'''
open(OUT,'w').write(HTML)
print('wrote',OUT,'|',tot,'todos |',len(ALLP),'projects |','synthesis:'+('yes' if syn else 'no'),'| plan:'+('yes' if (syn and syn.get('plan')) else 'no'))
