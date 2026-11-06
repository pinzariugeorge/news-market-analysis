"""Build a self-contained HTML dashboard of the agent's decisions.

Usage: python -I src/build_dashboard.py [--run pilot_v0]
Reads  results/<run>/dashboard_data.json (made by src/score_decisions.py) and data/processed/market_days.csv
Writes results/dashboard.html  (no external libraries or network; open it in any browser)
"""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Decisions Dashboard</title>
<style>
:root{--bg:#f7f7f5;--card:#fff;--ink:#1f2328;--mute:#6b7280;--line:#e3e3df;--good:#1a7f4b;--bad:#c0392b;--flat:#8a8f98;--blue:#2563eb;--amber:#b7791f;--grid:#ecece8}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#14161a;--card:#1c1f25;--ink:#e6e7ea;--mute:#9aa1ad;--line:#2b2f37;--good:#3ecf8e;--bad:#ff6b5b;--flat:#7b8190;--blue:#6ea0ff;--amber:#e3b04b;--grid:#262a31}}
:root[data-theme="dark"]{--bg:#14161a;--card:#1c1f25;--ink:#e6e7ea;--mute:#9aa1ad;--line:#2b2f37;--good:#3ecf8e;--bad:#ff6b5b;--flat:#7b8190;--blue:#6ea0ff;--amber:#e3b04b;--grid:#262a31}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:1120px;margin:0 auto;padding:20px 16px 60px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:0 0 8px}
.sub{color:var(--mute);margin:0 0 16px;font-size:13px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:16px}
.kpi,.card{background:var(--card);border:1px solid var(--line);border-radius:10px}
.kpi{padding:10px 12px}.kpi b{display:block;font-size:22px;font-variant-numeric:tabular-nums}.kpi span{color:var(--mute);font-size:12px}
.card{padding:14px;margin-bottom:16px}.card p{margin:0 0 8px;color:var(--mute);font-size:13px}
svg{width:100%;height:auto;display:block}
.legend{display:flex;flex-wrap:wrap;gap:14px;font-size:12px;color:var(--mute);margin-top:6px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;vertical-align:-1px}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:7px 6px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{color:var(--mute);font-weight:600;position:sticky;top:0;background:var(--card)}
tr.row{cursor:pointer}tr.row:hover{background:var(--grid)}
.pill{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;border:1px solid var(--line)}
.up{color:var(--good)}.down{color:var(--bad)}.neg{color:var(--bad)}.pos{color:var(--good)}
.detail td{background:var(--grid);font-size:13px}.detail h4{margin:8px 0 2px;font-size:12px;color:var(--mute);text-transform:uppercase;letter-spacing:.04em}
.tablewrap{overflow-x:auto}.warn{border-left:4px solid var(--amber);padding:8px 12px;background:var(--card);border-radius:6px;margin-bottom:16px;font-size:13px}
text{fill:var(--mute);font-size:11px}
</style></head><body><main>
<h1>Agent decisions &mdash; <span id="runname"></span></h1>
<p class="sub">Each decision is made before the open of day D from past-only information, then scored on D's close-to-close S&amp;P 500 move. Research and simulation only; not financial advice.</p>
<div class="warn" id="warn"></div>
<div class="kpis" id="kpis"></div>
<div class="card"><h2>Where the agent acted</h2><p>S&amp;P 500 close, 2008&ndash;2019, with each decision day marked. Filled = the agent went long; hollow = stayed flat. Green = right call, red = wrong, grey = no directional call.</p><div id="chartA"></div>
<div class="legend"><span><i style="background:var(--good)"></i>correct up/down call</span><span><i style="background:var(--bad)"></i>wrong call</span><span><i style="background:var(--flat)"></i>no edge (flat)</span></div></div>
<div class="card"><h2>Cumulative return on the decision days</h2><p>Sum of daily % returns over the sampled days in date order (days are not consecutive, so this is not an equity curve). Agent vs. simple baselines on the same days, after costs.</p><div id="chartB"></div>
<div class="legend"><span><i style="background:var(--blue)"></i>agent</span><span><i style="background:var(--flat)"></i>buy and hold</span><span><i style="background:var(--amber)"></i>volatility rule</span></div></div>
<div class="card"><h2>Expected range vs. what happened</h2><p>Bar = the agent's expected move range for the day; dot = the actual move. Dot outside the bar = the range missed.</p><div id="chartC"></div></div>
<div class="card"><h2>All decisions</h2><p>Click a row to see the agent's reasoning and the events it identified.</p><div class="tablewrap"><table id="tbl"><thead><tr>
<th>Day</th><th>Type</th><th>Vol regime</th><th>Headlines</th><th>View</th><th>Conf.</th><th>Position</th><th>Expected</th><th>Actual</th><th>Right?</th><th>Agent return</th></tr></thead><tbody></tbody></table></div></div>
</main>
<script>
const DATA = __DATA__;
const PRICES = __PRICES__;
const S = DATA.summary, R = DATA.rows;
const fmt=(x,d=2)=>x===null||x===undefined||x===""?"–":(+x).toFixed(d);
const pct=(x,d=1)=>x===null||x===undefined?"–":(100*x).toFixed(d)+"%";
const cls=x=>x>0?"pos":x<0?"neg":"";
document.getElementById("runname").textContent=S.run;
document.getElementById("warn").textContent="Small sample: "+S.n_scored+" decision days. Results are indicative only and say nothing yet about skill. Days were picked by category (big move, calm, stormy, event) from 2008–2019. Real names and dates are used, so a model may remember later events despite instructions.";
const kp=[
 ["Decision days",S.n_scored],
 ["Directional calls",S.n_committed+" of "+S.n_scored],
 ["Hit rate on calls",S.hit_rate_committed===null?"–":pct(S.hit_rate_committed,0)],
 ["Days long",S.long_days+" of "+S.n_scored],
 ["Avg confidence",fmt(S.avg_confidence,2)],
 ["Range contained outcome",S.in_range_share===null?"–":pct(S.in_range_share,0)],
 ["Agent, sum of returns",fmt(S.sum_ret_pct.strategy_ret_pct)+"%"],
 ["Buy & hold, same days",fmt(S.sum_ret_pct.buy_hold_ret_pct)+"%"],
 ["Vol rule, same days",fmt(S.sum_ret_pct.vol_rule_ret_pct)+"%"]];
document.getElementById("kpis").innerHTML=kp.map(k=>`<div class="kpi"><b>${k[1]}</b><span>${k[0]}</span></div>`).join("");
const colorOf=r=>r.correct===1?"var(--good)":r.correct===0?"var(--bad)":"var(--flat)";
const NS="http://www.w3.org/2000/svg";
function el(n,a,t){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);if(t!==undefined)e.textContent=t;return e}
function tip(node,text){node.appendChild(el("title",{},text));return node}

// Chart A
(function(){
 const W=1060,H=300,m={l:48,r:12,t:10,b:28};const svg=el("svg",{viewBox:`0 0 ${W} ${H}`});
 const xs=PRICES.map(p=>Date.parse(p[0])),ys=PRICES.map(p=>p[1]);
 const x0=Math.min(...xs),x1=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys);
 const X=t=>m.l+(t-x0)/(x1-x0)*(W-m.l-m.r), Y=v=>H-m.b-(v-ymin)/(ymax-ymin)*(H-m.t-m.b);
 for(let i=0;i<=4;i++){const v=ymin+(ymax-ymin)*i/4;svg.appendChild(el("line",{x1:m.l,x2:W-m.r,y1:Y(v),y2:Y(v),stroke:"var(--grid)"}));svg.appendChild(el("text",{x:m.l-6,y:Y(v)+4,"text-anchor":"end"},Math.round(v)))}
 for(let y=2008;y<=2020;y+=2){const t=Date.parse(y+"-01-01");svg.appendChild(el("text",{x:X(t),y:H-8,"text-anchor":"middle"},y))}
 svg.appendChild(el("path",{d:PRICES.map((p,i)=>(i?"L":"M")+X(xs[i]).toFixed(1)+" "+Y(ys[i]).toFixed(1)).join(""),fill:"none",stroke:"var(--mute)","stroke-width":1.3}));
 const px={};PRICES.forEach(p=>px[p[0]]=p[1]);
 R.forEach(r=>{const v=px[r.day];if(v===undefined)return;const c=el("circle",{cx:X(Date.parse(r.day)),cy:Y(v),r:5+r.size_pct/20,fill:r.size_pct>0?colorOf(r):"var(--card)",stroke:colorOf(r),"stroke-width":2});
  svg.appendChild(tip(c,`${r.day}: ${r.direction} (conf ${r.confidence}), size ${r.size_pct}%, actual ${fmt(r.outcome_ret_pct)}%`))});
 document.getElementById("chartA").appendChild(svg);
})();

// Chart B
(function(){
 const W=1060,H=240,m={l:48,r:12,t:10,b:28};const svg=el("svg",{viewBox:`0 0 ${W} ${H}`});
 const series=[["strategy_ret_pct","var(--blue)"],["buy_hold_ret_pct","var(--flat)"],["vol_rule_ret_pct","var(--amber)"]];
 const cum={};series.forEach(([k])=>{let s=0;cum[k]=[0].concat(R.map(r=>s+=r[k]))});
 const all=[].concat(...Object.values(cum));const lo=Math.min(...all,0),hi=Math.max(...all,0.01);
 const n=R.length;const X=i=>m.l+i/(n)*(W-m.l-m.r),Y=v=>H-m.b-(v-lo)/(hi-lo)*(H-m.t-m.b);
 for(let i=0;i<=4;i++){const v=lo+(hi-lo)*i/4;svg.appendChild(el("line",{x1:m.l,x2:W-m.r,y1:Y(v),y2:Y(v),stroke:"var(--grid)"}));svg.appendChild(el("text",{x:m.l-6,y:Y(v)+4,"text-anchor":"end"},v.toFixed(1)+"%"))}
 svg.appendChild(el("line",{x1:m.l,x2:W-m.r,y1:Y(0),y2:Y(0),stroke:"var(--mute)","stroke-dasharray":"3 3"}));
 R.forEach((r,i)=>{svg.appendChild(el("text",{x:X(i+1),y:H-8,"text-anchor":"middle"},r.day.slice(2,7)))});
 series.forEach(([k,c])=>{svg.appendChild(el("path",{d:cum[k].map((v,i)=>(i?"L":"M")+X(i).toFixed(1)+" "+Y(v).toFixed(1)).join(""),fill:"none",stroke:c,"stroke-width":2.2}));
  cum[k].forEach((v,i)=>{if(i)svg.appendChild(tip(el("circle",{cx:X(i),cy:Y(v),r:3,fill:c}),`${R[i-1].day} ${k.replace("_ret_pct","")}: ${v.toFixed(2)}%`))})});
 document.getElementById("chartB").appendChild(svg);
})();

// Chart C
(function(){
 const rows=R.length,rh=26,W=1060,m={l:92,r:12,t:10,b:26},H=m.t+m.b+rows*rh;const svg=el("svg",{viewBox:`0 0 ${W} ${H}`});
 const vals=R.flatMap(r=>[r.outcome_ret_pct,r.exp_low,r.exp_high].filter(v=>v!==null&&v!==""&&v!==undefined)).map(Number);
 const lo=Math.min(...vals,-1)-0.3,hi=Math.max(...vals,1)+0.3;const X=v=>m.l+(v-lo)/(hi-lo)*(W-m.l-m.r);
 for(let v=Math.ceil(lo);v<=hi;v++){svg.appendChild(el("line",{x1:X(v),x2:X(v),y1:m.t,y2:H-m.b,stroke:v===0?"var(--mute)":"var(--grid)"}));svg.appendChild(el("text",{x:X(v),y:H-8,"text-anchor":"middle"},v+"%"))}
 R.forEach((r,i)=>{const y=m.t+i*rh+rh/2;svg.appendChild(el("text",{x:m.l-8,y:y+4,"text-anchor":"end"},r.day));
  if(r.exp_low!==null&&r.exp_low!==""){svg.appendChild(el("rect",{x:X(+r.exp_low),y:y-6,width:Math.max(2,X(+r.exp_high)-X(+r.exp_low)),height:12,rx:3,fill:"var(--blue)",opacity:.28}))}
  const ok=r.in_range===1;svg.appendChild(tip(el("circle",{cx:X(+r.outcome_ret_pct),cy:y,r:5.5,fill:ok?"var(--good)":"var(--bad)"}),`${r.day}: actual ${fmt(r.outcome_ret_pct)}%, expected ${r.exp_low} to ${r.exp_high}`))});
 document.getElementById("chartC").appendChild(svg);
})();

// Table
(function(){
 const tb=document.querySelector("#tbl tbody");
 R.forEach((r,i)=>{
  const tr=document.createElement("tr");tr.className="row";
  const dirTxt=r.direction==="up"?'<span class="up">up</span>':r.direction==="down"?'<span class="down">down</span>':'<span class="pill">no edge</span>';
  const right=r.correct===""?"–":r.correct===1?'<span class="up">yes</span>':'<span class="down">no</span>';
  tr.innerHTML=`<td>${r.day}</td><td>${r.category}</td><td>${r.vol_regime}</td><td>${r.n_headlines}</td><td>${dirTxt}</td><td>${fmt(r.confidence,2)}</td><td>${r.position} ${r.size_pct}%</td><td>${fmt(r.exp_low,1)} to ${fmt(r.exp_high,1)}%</td><td class="${cls(r.outcome_ret_pct)}">${fmt(r.outcome_ret_pct)}%</td><td>${right}</td><td class="${cls(r.strategy_ret_pct)}">${fmt(r.strategy_ret_pct)}%</td>`;
  const d=document.createElement("tr");d.className="detail";d.style.display="none";
  const ev=(r.events||[]).map(e=>`<li>[${e.type||"?"}] ${(e.headline||"").replace(/</g,"&lt;")} <span class="pill">${e.relevant?"kept":"ignored"}</span> ${e.new_or_continuing||""} ${e.scale||""}</li>`).join("")||"<li>none listed</li>";
  d.innerHTML=`<td colspan="11"><h4>Reasoning</h4>${(r.reasoning||"").replace(/</g,"&lt;")}<h4>Handbook used</h4>${r.events_used||"–"}<h4>Events identified</h4><ul>${ev}</ul><h4>Would change my mind</h4>${(r.would_change_my_mind||"–").replace(/</g,"&lt;")}</td>`;
  tr.onclick=()=>{d.style.display=d.style.display==="none"?"table-row":"none"};
  tb.appendChild(tr);tb.appendChild(d)});
})();
</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="pilot_v0")
    a = ap.parse_args()
    data = json.loads((ROOT / "results" / a.run / "dashboard_data.json").read_text(encoding="utf-8"))
    prices = []
    with open(ROOT / "data/processed/market_days.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if "2008-01-01" <= r["date"] <= "2019-12-31":
                prices.append([r["date"], float(r["close"])])
    html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__PRICES__", json.dumps(prices))
    out = ROOT / "results" / "dashboard.html"
    out.write_text(html, encoding="utf-8")
    print("wrote", out, "({:.0f} KB)".format(out.stat().st_size / 1024))


if __name__ == "__main__":
    main()
