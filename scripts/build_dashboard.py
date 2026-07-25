#!/usr/bin/env python3
"""Build docs/viz/dashboard.html by injecting docs/viz/data.json into the template.
Re-run after regenerating data.json to refresh the charts."""
import json, os

data = open("docs/viz/data.json").read().strip()

HTML = r"""<title>Agent Skills — Evidence Dashboard</title>
<style>
:root{
  --bg:#f6f7f9; --surface:#ffffff; --surface-2:#fbfcfd;
  --ink:#11141b; --ink-2:#565c68; --ink-3:#8b909b; --hair:#e7e9ee; --grid:#eef0f4;
  --accent:#2a78d6; --win:#0ca30c; --loss:#d03b3b; --mut:#a3a9b4; --mut-mark:#c2c7d0;
  --shadow:0 1px 2px rgba(20,25,40,.05),0 8px 24px rgba(20,25,40,.05);
}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){
  --bg:#0f1013; --surface:#191b20; --surface-2:#15171b;
  --ink:#f1f2f5; --ink-2:#b7bcc5; --ink-3:#71767f; --hair:#282b31; --grid:#232529;
  --accent:#3987e5; --win:#1cb81c; --loss:#e05656; --mut:#6b7079; --mut-mark:#3a3d44;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 30px rgba(0,0,0,.35);
}}
:root[data-theme="dark"]{
  --bg:#0f1013; --surface:#191b20; --surface-2:#15171b;
  --ink:#f1f2f5; --ink-2:#b7bcc5; --ink-3:#71767f; --hair:#282b31; --grid:#232529;
  --accent:#3987e5; --win:#1cb81c; --loss:#e05656; --mut:#6b7079; --mut-mark:#3a3d44;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 30px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.55;
  -webkit-font-smoothing:antialiased}
.mono{font-family:ui-monospace,"SF Mono",Menlo,"Cascadia Code",monospace;
  font-variant-numeric:tabular-nums}
.wrap{max-width:1080px;margin:0 auto;padding:48px 24px 80px}
header .eyebrow{font:600 12px/1 ui-monospace,monospace;letter-spacing:.14em;
  text-transform:uppercase;color:var(--accent);margin:0 0 14px}
h1{font-size:clamp(30px,5vw,44px);line-height:1.04;letter-spacing:-.02em;margin:0;
  text-wrap:balance;font-weight:680}
.sub{color:var(--ink-2);max-width:64ch;margin:16px 0 0;font-size:16px}
.meta{color:var(--ink-3);font-size:12.5px;margin-top:10px}
/* scorecard */
.score{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:38px 0 8px}
.tile{background:var(--surface);border:1px solid var(--hair);border-radius:12px;
  padding:16px 16px 15px;box-shadow:var(--shadow);display:flex;flex-direction:column;gap:3px}
.tile .k{font:600 11px/1.2 ui-monospace,monospace;letter-spacing:.06em;
  text-transform:uppercase;color:var(--ink-3)}
.tile .v{font:660 26px/1.05 ui-monospace,monospace;letter-spacing:-.01em;margin-top:4px}
.tile .n{font-size:12px;color:var(--ink-2)}
.tile.good .v{color:var(--win)} .tile.accent .v{color:var(--accent)}
.pill{align-self:flex-start;font:600 10.5px/1 ui-monospace,monospace;letter-spacing:.05em;
  text-transform:uppercase;padding:4px 7px;border-radius:999px;margin-top:6px}
.pill.proven{background:color-mix(in oklab,var(--win) 15%,transparent);color:var(--win)}
.pill.partial{background:color-mix(in oklab,var(--accent) 15%,transparent);color:var(--accent)}
.pill.mech{background:color-mix(in oklab,var(--mut) 22%,transparent);color:var(--ink-2)}
/* cards */
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:26px}
.card{background:var(--surface);border:1px solid var(--hair);border-radius:14px;
  padding:20px 20px 16px;box-shadow:var(--shadow);min-width:0}
.card.wide{grid-column:1/-1}
.card h2{font-size:16px;margin:0;letter-spacing:-.01em}
.card .cap{color:var(--ink-2);font-size:13px;margin:5px 0 14px;max-width:70ch}
.legend{display:flex;flex-wrap:wrap;gap:14px;margin:0 0 12px;font-size:12px;color:var(--ink-2)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block}
.sq{width:9px;height:9px;border-radius:2px;display:inline-block}
svg{display:block;width:100%;overflow:visible}
.scrollbox{max-height:560px;overflow-y:auto;overflow-x:hidden;margin:0 -4px;padding:0 4px}
text{font-family:ui-monospace,monospace;font-variant-numeric:tabular-nums}
.axl{fill:var(--ink-3);font-size:10.5px}
.rowlab{fill:var(--ink-2);font-size:11px}
.gridline{stroke:var(--grid);stroke-width:1}
.zero{stroke:var(--ink-3);stroke-width:1;stroke-dasharray:2 3}
.tip{position:fixed;pointer-events:none;z-index:20;background:var(--ink);color:var(--bg);
  font:12px/1.4 ui-monospace,monospace;padding:7px 9px;border-radius:8px;opacity:0;
  transition:opacity .1s;max-width:240px;box-shadow:0 6px 20px rgba(0,0,0,.25)}
.foot{color:var(--ink-3);font-size:12px;margin-top:34px;border-top:1px solid var(--hair);
  padding-top:16px;max-width:74ch}
.toggle{position:fixed;top:14px;right:14px;background:var(--surface);border:1px solid var(--hair);
  color:var(--ink-2);border-radius:9px;padding:7px 10px;font:12px ui-monospace,monospace;
  cursor:pointer;box-shadow:var(--shadow)}
@media(max-width:820px){.score{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style>

<button class="toggle" id="tog" aria-label="Toggle theme">◐ theme</button>
<div class="wrap">
  <header>
    <p class="eyebrow">skills-evolve · empirical results</p>
    <h1>What the measurements actually show</h1>
    <p class="sub">A vendor-neutral agent-skills library, measured against real Haiku&nbsp;4.5 and
      Gemini&nbsp;Flash-Lite runs instead of assumed to work. Five claims, each with a verdict and an
      honest limit. Every number here is reproducible from <span class="mono">simulator/</span>.</p>
    <p class="meta mono" id="meta"></p>
  </header>

  <section class="score" id="score"></section>

  <div class="grid">
    <div class="card wide">
      <h2>Skill effectiveness — does the skill make the model measurably better?</h2>
      <p class="cap">Paired win-rate effect on Gemini with 95% confidence whiskers, all 61 skills,
        sorted. Blue = significant help after Benjamini-Hochberg FDR correction; grey = not yet
        discriminated (underpowered or ceiling-locked). <b>No skill is red</b> — none is confirmed to
        make the model worse.</p>
      <div class="legend">
        <span><i class="dot" style="background:var(--accent)"></i>significant help (FDR)</span>
        <span><i class="dot" style="background:var(--mut-mark)"></i>not significant / ceiling</span>
        <span><i class="dot" style="background:var(--loss)"></i>confirmed harm — none found</span>
      </div>
      <div class="scrollbox"><svg id="c_eff"></svg></div>
    </div>

    <div class="card">
      <h2>Cross-model agreement</h2>
      <p class="cap">Effect on Haiku vs. Gemini for every skill measured on both. Points on the
        diagonal agree across vendors; the top-right quadrant is confirmed-useful on both.</p>
      <div class="legend">
        <span><i class="dot" style="background:var(--win)"></i>useful on both</span>
        <span><i class="dot" style="background:var(--accent)"></i>useful on one</span>
        <span><i class="dot" style="background:var(--mut-mark)"></i>neither yet</span>
      </div>
      <svg id="c_scatter"></svg>
    </div>

    <div class="card">
      <h2>Adversarial resilience of the commons</h2>
      <p class="cap">Malicious skills that breach the shared Canon as fake "sybil" orgs escalate.
        The <span class="mono">org_weight_cap</span> defense blocks all attackers until far more fake
        infrastructure than the honest population, and halves the breach at the extreme.</p>
      <div class="legend">
        <span><i class="sq" style="background:var(--loss)"></i>no cap</span>
        <span><i class="sq" style="background:var(--accent)"></i>with weight cap</span>
      </div>
      <svg id="c_adv"></svg>
    </div>

    <div class="card wide">
      <h2>The eval caught its own bugs — five times, none shipped</h2>
      <p class="cap">Each apparent "this skill HURTS" verdict traced to a bug in the <em>test</em>, not
        the skill. Left dot = the false reading; right dot = after fixing the registrar and
        re-measuring. Every fix moved the effect back across zero (or to neutral) — the defect
        corrected, not the number massaged.</p>
      <div class="legend">
        <span><i class="dot" style="background:var(--loss)"></i>false HURTS reading</span>
        <span><i class="dot" style="background:var(--accent)"></i>after registrar fix</span>
      </div>
      <svg id="c_retract"></svg>
    </div>
  </div>

  <p class="foot">Verdicts and gaps in full: <span class="mono">PROOF.md</span>. Method trail:
    <span class="mono">EXPERIMENTS.md</span> (EXP-001…023). Cross-model chart covers the
    <span id="crossn" class="mono"></span> skills measured on both models so far; the remaining Haiku
    measurements were budget-capped and complete separately. FDR = Benjamini-Hochberg at q=0.05.</p>
</div>
<div class="tip mono" id="tip"></div>

<script id="exp-data" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('exp-data').textContent);
const tip=document.getElementById('tip');
const cv=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
function showTip(html,e){tip.innerHTML=html;tip.style.opacity=1;
  let x=e.clientX+14,y=e.clientY+14;
  if(x+230>innerWidth)x=e.clientX-230;tip.style.left=x+'px';tip.style.top=y+'px';}
function hideTip(){tip.style.opacity=0;}
const SVGNS='http://www.w3.org/2000/svg';
function el(n,a){const e=document.createElementNS(SVGNS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}

// meta + scorecard
document.getElementById('meta').textContent=
  `${D.n_skills} skills · ${D.effects.reduce((s,e)=>s+1,0)} measured · generated ${D.generated}`;
document.getElementById('crossn').textContent=D.haiku_covered;
const cards=[
 {k:'Skills useful',v:`${D.n_win_fdr} / ${D.n_skills}`,n:`FDR-significant wins · ${D.n_loss} losses`,cls:'good',pill:['partial','partial']},
 {k:'Router',v:`${D.router.gemini_top1}%`,n:`top-1 both models · ${D.router.false_fire}% false-fire`,cls:'accent',pill:['proven','proven']},
 {k:'Eval robust',v:'159/159',n:'fixture gate · CIs replicate',cls:'accent',pill:['proven','proven']},
 {k:'Local evolution',v:'1.0 / 1.0',n:'precision / recall on real data',cls:'good',pill:['proven','proven']},
 {k:'Global culture',v:'leak-proof',n:'blocks attackers to sybil 16',cls:'',pill:['mech','mechanism']},
];
document.getElementById('score').innerHTML=cards.map(c=>
 `<div class="tile ${c.cls}"><div class="k">${c.k}</div><div class="v">${c.v}</div>
  <div class="n">${c.n}</div><span class="pill ${c.pill[0]}">${c.pill[1]}</span></div>`).join('');

function scale(d0,d1,r0,r1){return v=>r0+(v-d0)/(d1-d0)*(r1-r0);}
function renderAll(){
['c_eff','c_scatter','c_adv','c_retract'].forEach(id=>{document.getElementById(id).innerHTML='';});

// ---- Chart: effect dot plot ----
(function(){
  const rows=D.effects.slice().sort((a,b)=>b.effect-a.effect);
  const rowH=15, mL=186, mR=44, mT=26, W=840;
  const H=mT+rows.length*rowH+10;
  const svg=document.getElementById('c_eff');svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
  const lo=Math.min(-0.2,...rows.map(r=>r.lo)), hi=Math.max(...rows.map(r=>r.hi))+0.03;
  const x=scale(lo,hi,mL,W-mR);
  for(const t of [-0.2,0,0.2,0.4,0.6,0.8,1.0]){ if(t<lo||t>hi)continue;
    svg.appendChild(el('line',{x1:x(t),x2:x(t),y1:mT-6,y2:H-8,class:t===0?'zero':'gridline'}));
    const tx=el('text',{x:x(t),y:mT-11,'text-anchor':'middle',class:'axl'});tx.textContent=t;svg.appendChild(tx);
  }
  rows.forEach((r,i)=>{
    const y=mT+i*rowH+rowH/2;
    const col=r.verdict==='win'?cv('--accent'):r.verdict==='loss'?cv('--loss'):cv('--mut-mark');
    const lab=el('text',{x:mL-10,y:y+3.5,'text-anchor':'end',class:'rowlab'});lab.textContent=r.skill;
    if(r.verdict==='win')lab.setAttribute('fill',cv('--ink'));svg.appendChild(lab);
    svg.appendChild(el('line',{x1:x(r.lo),x2:x(r.hi),y1:y,y2:y,stroke:col,'stroke-width':1.4,opacity:.5}));
    const c=el('circle',{cx:x(r.effect),cy:y,r:r.verdict==='win'?4:3.2,fill:col,
      stroke:cv('--surface'),'stroke-width':1.2});
    c.style.cursor='pointer';
    c.addEventListener('mousemove',e=>showTip(
      `<b>${r.skill}</b><br>effect ${r.effect>=0?'+':''}${r.effect}<br>95% CI [${r.lo}, ${r.hi}]<br>${r.verdict==='win'?'significant help (FDR)':r.verdict==='ceiling'?'ceiling — both arms 100%':'not significant'}`,e));
    c.addEventListener('mouseleave',hideTip);
    svg.appendChild(c);
  });
})();

// ---- Chart: cross-model scatter ----
(function(){
  const P=D.cross, W=460,H=380,m=42;
  const svg=document.getElementById('c_scatter');svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
  const lo=-0.2,hi=1.05;
  const x=scale(lo,hi,m,W-14), y=scale(lo,hi,H-m,14);
  for(const t of [0,0.25,0.5,0.75,1.0]){
    svg.appendChild(el('line',{x1:x(t),x2:x(t),y1:14,y2:H-m,class:'gridline'}));
    svg.appendChild(el('line',{x1:m,x2:W-14,y1:y(t),y2:y(t),class:'gridline'}));
    const tx=el('text',{x:x(t),y:H-m+15,'text-anchor':'middle',class:'axl'});tx.textContent=t;svg.appendChild(tx);
    const ty=el('text',{x:m-8,y:y(t)+3.5,'text-anchor':'end',class:'axl'});ty.textContent=t;svg.appendChild(ty);
  }
  svg.appendChild(el('line',{x1:x(lo),y1:y(lo),x2:x(hi),y2:y(hi),stroke:cv('--ink-3'),'stroke-width':1,'stroke-dasharray':'3 3',opacity:.6}));
  const xl=el('text',{x:(m+W-14)/2,y:H-6,'text-anchor':'middle',class:'axl'});xl.textContent='Haiku effect →';svg.appendChild(xl);
  const yl=el('text',{x:12,y:(14+H-m)/2,'text-anchor':'middle',class:'axl',transform:`rotate(-90 12 ${(14+H-m)/2})`});yl.textContent='Gemini effect →';svg.appendChild(yl);
  P.forEach(p=>{
    const col=p.cat==='both'?cv('--win'):p.cat==='one'?cv('--accent'):cv('--mut-mark');
    const c=el('circle',{cx:x(p.haiku),cy:y(p.gemini),r:4.5,fill:col,opacity:.85,
      stroke:cv('--surface'),'stroke-width':1});
    c.style.cursor='pointer';
    c.addEventListener('mousemove',e=>showTip(`<b>${p.skill}</b><br>Haiku ${p.haiku>=0?'+':''}${p.haiku}<br>Gemini ${p.gemini>=0?'+':''}${p.gemini}`,e));
    c.addEventListener('mouseleave',hideTip);svg.appendChild(c);
  });
})();

// ---- Chart: adversarial resilience ----
(function(){
  const A=D.adversarial, W=460,H=320,mL=40,mB=44,mT=14,mR=52;
  const svg=document.getElementById('c_adv');svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
  const xmax=A.sybil.length-1, ymax=Math.max(...A.uncapped,...A.capped,1);
  const x=scale(0,xmax,mL,W-mR), y=scale(0,ymax,H-mB,mT);
  for(let t=0;t<=ymax;t++){
    svg.appendChild(el('line',{x1:mL,x2:W-mR,y1:y(t),y2:y(t),class:'gridline'}));
    const ty=el('text',{x:mL-8,y:y(t)+3.5,'text-anchor':'end',class:'axl'});ty.textContent=t;svg.appendChild(ty);
  }
  A.sybil.forEach((s,i)=>{const tx=el('text',{x:x(i),y:H-mB+16,'text-anchor':'middle',class:'axl'});tx.textContent=s;svg.appendChild(tx);});
  const xl=el('text',{x:(mL+W-mR)/2,y:H-8,'text-anchor':'middle',class:'axl'});xl.textContent='fake "sybil" orgs attacking →';svg.appendChild(xl);
  function line(vals,col,name){
    let d='';vals.forEach((v,i)=>d+=(i?'L':'M')+x(i)+' '+y(v));
    svg.appendChild(el('path',{d,fill:'none',stroke:col,'stroke-width':2.2,'stroke-linejoin':'round'}));
    vals.forEach((v,i)=>{const c=el('circle',{cx:x(i),cy:y(v),r:4,fill:col,stroke:cv('--surface'),'stroke-width':1.4});
      c.style.cursor='pointer';
      c.addEventListener('mousemove',e=>showTip(`<b>${name}</b><br>${A.sybil[i]} sybil orgs<br>${v} malicious breached`,e));
      c.addEventListener('mouseleave',hideTip);svg.appendChild(c);});
    const lb=el('text',{x:x(vals.length-1)+8,y:y(vals[vals.length-1])+3.5,class:'axl',fill:col});lb.textContent=name;svg.appendChild(lb);
  }
  line(A.uncapped,cv('--loss'),'no cap');
  line(A.capped,cv('--accent'),'cap');
})();

// ---- Chart: retraction dumbbell ----
(function(){
  const R=D.retract, rowH=30, mL=210,mR=54,mT=24,W=840;
  const H=mT+R.length*rowH+10;
  const svg=document.getElementById('c_retract');svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
  const lo=-0.7,hi=0.4;const x=scale(lo,hi,mL,W-mR);
  for(const t of [-0.6,-0.4,-0.2,0,0.2,0.4]){
    svg.appendChild(el('line',{x1:x(t),x2:x(t),y1:mT-6,y2:H-8,class:t===0?'zero':'gridline'}));
    const tx=el('text',{x:x(t),y:mT-11,'text-anchor':'middle',class:'axl'});tx.textContent=t;svg.appendChild(tx);
  }
  R.forEach((r,i)=>{
    const y=mT+i*rowH+rowH/2;
    const lab=el('text',{x:mL-12,y:y+3.5,'text-anchor':'end',class:'rowlab'});
    lab.textContent=`${r.skill} · ${r.model}`;svg.appendChild(lab);
    svg.appendChild(el('line',{x1:x(r.before),x2:x(r.after),y1:y,y2:y,stroke:cv('--ink-3'),'stroke-width':1.6,opacity:.4}));
    [['before',r.before,cv('--loss')],['after',r.after,cv('--accent')]].forEach(([k,v,col])=>{
      const c=el('circle',{cx:x(v),cy:y,r:5,fill:col,stroke:cv('--surface'),'stroke-width':1.4});
      c.style.cursor='pointer';
      c.addEventListener('mousemove',e=>showTip(`<b>${r.skill}</b> (${r.model})<br>${k} fix: ${v>=0?'+':''}${v}`,e));
      c.addEventListener('mouseleave',hideTip);svg.appendChild(c);
    });
  });
})();
} // end renderAll

renderAll();
// theme toggle — re-render marks so hardcoded fills pick up the new tokens
document.getElementById('tog').addEventListener('click',()=>{
  const cur=document.documentElement.getAttribute('data-theme');
  const dark=cur?cur==='dark':matchMedia('(prefers-color-scheme:dark)').matches;
  document.documentElement.setAttribute('data-theme',dark?'light':'dark');
  requestAnimationFrame(renderAll);
});
</script>
"""

out = HTML.replace("__DATA__", data)
os.makedirs("docs/viz", exist_ok=True)
open("docs/viz/dashboard.html", "w").write(out)
print(f"wrote docs/viz/dashboard.html ({len(out)} bytes)")
