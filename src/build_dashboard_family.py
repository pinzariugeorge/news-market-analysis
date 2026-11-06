"""Build the family-run dashboard: every price, every commodity and driver, and what the agent decided.

Usage: python -I src/build_dashboard_family.py [--run fam_v0]
Reads results/<run>/dashboard_data.json (from src/score_family_run.py), the commodity and driver CSVs and the stock cache.
Writes results/dashboard_family.html (self-contained, no network). Prices shown from 2022-07-01 to the latest data; the agent run
covers the validation decision days only (2023-2024); the final test period is reserved and has no decisions.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import familydata as fd  # noqa: E402

START = "2022-07-01"

TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Family Run Dashboard</title>
<style>
:root{--bg:#f7f7f5;--card:#fff;--ink:#1f2328;--mute:#6b7280;--line:#e3e3df;--good:#1a7f4b;--bad:#c0392b;--flat:#8a8f98;--blue:#2563eb;--amber:#b7791f;--grid:#ecece8;--win:#eef3ff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#14161a;--card:#1c1f25;--ink:#e6e7ea;--mute:#9aa1ad;--line:#2b2f37;--good:#3ecf8e;--bad:#ff6b5b;--flat:#7b8190;--blue:#6ea0ff;--amber:#e3b04b;--grid:#262a31;--win:#202838}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:1200px;margin:0 auto;padding:20px 16px 60px}h1{font-size:22px;margin:0 0 4px}h2{font-size:18px;margin:26px 0 6px}h3{font-size:14px;margin:0 0 2px}
.sub{color:var(--mute);margin:0 0 14px;font-size:13px}.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:14px}
.kpi,.card{background:var(--card);border:1px solid var(--line);border-radius:10px}.kpi{padding:10px 12px}.kpi b{display:block;font-size:21px;font-variant-numeric:tabular-nums}.kpi span{color:var(--mute);font-size:12px}
.card{padding:10px 12px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:10px}.warn{border-left:4px solid var(--amber);padding:8px 12px;background:var(--card);border-radius:6px;margin-bottom:14px;font-size:13px}
svg{width:100%;height:auto;display:block}text{fill:var(--mute);font-size:10px}.legend{display:flex;flex-wrap:wrap;gap:12px;font-size:12px;color:var(--mute);margin:4px 0 8px}.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;vertical-align:-1px}
.strip{display:flex;gap:3px;flex-wrap:wrap;margin:6px 0 10px}.cell{width:46px;border:1px solid var(--line);border-radius:6px;padding:2px 3px;font-size:10px;text-align:center;background:var(--card)}.cell b{display:block;font-size:11px}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:6px 6px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--mute);position:sticky;top:0;background:var(--card)}
tr.row{cursor:pointer}tr.row:hover{background:var(--grid)}.detail td{background:var(--grid)}.pos{color:var(--good)}.neg{color:var(--bad)}.pill{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;border:1px solid var(--line)}
.tablewrap{max-height:520px;overflow:auto}select{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:3px 6px}
</style></head><body><main>
<h1>Family run &mdash; <span id="run"></span></h1>
<p class="sub">Five families (oil and gas, gold miners, chips, pharma, copper and uranium), five stocks' worth of prices each, every commodity and driver, and the agent's call on each decision day. Research and simulation only; not financial advice.</p>
<div class="warn" id="warn"></div>
<div class="kpis" id="kpis"></div>
<h2>Portfolio (1,000 USD, whole shares, real order costs)</h2><div class="card" id="equity"></div>
<div id="families"></div>
<h2>Market regime</h2><div class="grid" id="macro"></div>
<h2>Every decision</h2>
<p class="sub">Filter: <select id="ff"><option value="">all families</option></select> <select id="fc"><option value="">all calls</option><option>long</option><option>flat</option></select>. Click a row for the agent's reasoning. "If long" is what holding the leader for the chosen period would have returned after costs.</p>
<div class="card tablewrap"><table id="tbl"><thead><tr><th>Day</th><th>Family</th><th>Leader</th><th>Call</th><th>Hold</th><th>Conf.</th><th>If long: entry to exit</th><th>If long (net)</th><th>Family basket</th><th>Driver</th></tr></thead><tbody></tbody></table></div>
</main>
<script>
const D = __DATA__;
const AX = __AXIS__;
const PX = __PRICES__;
const FAMS = __FAMS__;
const S = D.summary, R = D.rows;
const NS = "http://www.w3.org/2000/svg";
const el=(n,a,t)=>{const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);if(t!==undefined)e.textContent=t;return e};
const fmt=(x,d=2)=>x===null||x===undefined?"–":(+x).toFixed(d);
const cls=x=>x>0?"pos":x<0?"neg":"";
const idx=d=>{let lo=0,hi=AX.length-1;while(lo<hi){const m=(lo+hi)>>1;if(AX[m]<d)lo=m+1;else hi=m}return lo};
document.getElementById("run").textContent=S.run;
const nLong=S.long_calls;
document.getElementById("warn").textContent=(nLong===0?"All "+S.calls+" calls were flat: the agent never reached the 0.55 confidence needed for a long, so the portfolio stayed in cash. Dots on the stock charts show what holding the leader would have returned (green = a gain was missed, red = a loss was avoided). ":"")+"Validation run on decision days in 2023-2024 only (shaded); the final test period (2025 onward) is reserved and has no decisions. Real names and dates are used, so a model may remember later events despite instructions.";
const pos=R.filter(r=>r.positive_after_cost).length;
const kp=[["Decision days",S.decision_days],["Family calls",S.calls],["Long calls",S.long_calls],["Flat calls",S.flat_calls],["Avg confidence",fmt(S.avg_confidence_flat,2)],["Long would have gained",(100*pos/R.length).toFixed(0)+"%"],
 ["Mean if always long",fmt(S.mean_net_always_long_all_calls)+"%"],["Agent portfolio","$"+S.portfolio.final.toFixed(0)],["Leaders basket","$"+S.benchmarks.leaders_basket_final.toFixed(0)],["Fees paid","$"+S.portfolio.fees.toFixed(2)]];
document.getElementById("kpis").innerHTML=kp.map(k=>`<div class="kpi"><b>${k[1]}</b><span>${k[0]}</span></div>`).join("");

function chart(host,title,sub,series,o){
  o=o||{};const W=560,H=190,m={l:44,r:8,t:8,b:20};const svg=el("svg",{viewBox:`0 0 ${W} ${H}`});
  const i0=o.i0||0,i1=o.i1||AX.length-1;let lo=1e18,hi=-1e18;
  series.forEach(s=>{for(let i=i0;i<=i1;i++){const v=s.vals[i];if(v!==null&&v!==undefined){lo=Math.min(lo,v);hi=Math.max(hi,v)}}});
  if(lo===hi){lo-=1;hi+=1}const pad=(hi-lo)*.06;lo-=pad;hi+=pad;
  const X=i=>m.l+(i-i0)/(i1-i0)*(W-m.l-m.r),Y=v=>H-m.b-(v-lo)/(hi-lo)*(H-m.t-m.b);
  if(o.win){const a=X(idx(o.win[0])),b=X(Math.min(i1,idx(o.win[1])));svg.appendChild(el("rect",{x:a,y:m.t,width:b-a,height:H-m.t-m.b,fill:"var(--win)"}))}
  for(let k=0;k<=3;k++){const v=lo+(hi-lo)*k/3;svg.appendChild(el("line",{x1:m.l,x2:W-m.r,y1:Y(v),y2:Y(v),stroke:"var(--grid)"}));svg.appendChild(el("text",{x:m.l-4,y:Y(v)+3,"text-anchor":"end"},Math.abs(v)>=100?Math.round(v):v.toFixed(2)))}
  for(let y=+AX[i0].slice(0,4)+1;y<=+AX[i1].slice(0,4);y++){const i=idx(y+"-01-01");svg.appendChild(el("text",{x:X(i),y:H-5,"text-anchor":"middle"},y))}
  series.forEach(s=>{let d="",pen=false;for(let i=i0;i<=i1;i++){const v=s.vals[i];if(v===null||v===undefined){pen=false;continue}d+=(pen?"L":"M")+X(i).toFixed(1)+" "+Y(v).toFixed(1);pen=true}
    svg.appendChild(el("path",{d,fill:"none",stroke:s.color,"stroke-width":s.w||1.4}))});
  (o.spans||[]).forEach(sp=>{const a=X(sp.i0),b=X(sp.i1);svg.appendChild(el("rect",{x:a,y:m.t,width:Math.max(1,b-a),height:H-m.t-m.b,fill:sp.color,opacity:.18}))});
  (o.marks||[]).forEach(mk=>{const s=series[mk.s||0];const v=s.vals[mk.i];if(v===null||v===undefined)return;const c=el("circle",{cx:X(mk.i),cy:Y(v),r:mk.r||3.4,fill:mk.color,stroke:"var(--card)","stroke-width":.8});c.appendChild(el("title",{},mk.tip));svg.appendChild(c)});
  const box=document.createElement("div");box.className="card";box.innerHTML=`<h3>${title}</h3><div class="sub" style="margin:0 0 2px">${sub||""}</div>`;box.appendChild(svg);
  if(series.length>1){const lg=document.createElement("div");lg.className="legend";lg.innerHTML=series.map(s=>`<span><i style="background:${s.color}"></i>${s.label}</span>`).join("");box.appendChild(lg)}
  host.appendChild(box);return box}

const COL=["#2563eb","#b7791f","#1a7f4b","#8b5cf6","#c0392b","#0e7490"];
const WIN=["2023-01-03","2024-12-31"];
const FL={oil_gas:"Oil and gas producers",gold_miners:"Gold miners",chips:"Chips",pharma:"Pharma",copper_uranium:"Copper and uranium"};
// equity
(function(){const host=document.getElementById("equity");
  const ed=D.equity,bd=D.bench;const eAx=idx(ed[0][0]),eEnd=idx(ed[ed.length-1][0]);
  const mk=(arr)=>{const v=new Array(AX.length).fill(null);arr.forEach(([d,x])=>{v[idx(d)]=x});let last=null;for(let i=eAx;i<=eEnd;i++){if(v[i]!==null)last=v[i];else v[i]=last}return v};
  const grid=document.createElement("div");grid.className="grid";host.appendChild(grid);
  chart(grid,"Agent portfolio vs. leaders basket","Start 1,000 USD at the first decision. Basket = the five leaders equal weight, 21-day holds, 0.3% cost.",[{label:"agent portfolio",color:"var(--blue)",vals:mk(ed),w:2.2},{label:"leaders basket (always long)",color:"var(--amber)",vals:mk(bd),w:1.8},{label:"cash",color:"var(--flat)",vals:AX.map((d,i)=>i>=eAx&&i<=eEnd?1000:null),w:1.2}],{i0:eAx,i1:eEnd});
  const b=document.createElement("div");b.className="card";b.innerHTML=`<h3>What the numbers say</h3><p class="sub">Agent: ${S.portfolio.orders} orders, fees ${S.portfolio.fees.toFixed(2)} USD, final ${S.portfolio.final.toFixed(0)} USD, max drawdown ${S.portfolio.max_drawdown_pct}%.<br>Leaders basket (always long): ${S.benchmarks.leaders_basket_final.toFixed(0)} USD. Random calls with the agent's number of longs: median ${S.benchmarks.random_calls_final_median}, 5th to 95th percentile ${S.benchmarks.random_calls_final_5th} to ${S.benchmarks.random_calls_final_95th} USD.<br>Mean net return if long on every call: ${fmt(S.mean_net_always_long_all_calls)}% per holding period; the agent averaged ${fmt(S.avg_confidence_flat,2)} confidence, below the 0.55 threshold for a long.</p>`;grid.appendChild(b)})();
// families
const FH=document.getElementById("families");
FAMS.forEach((F,fi)=>{
  const sec=document.createElement("section");const rows=R.filter(r=>r.family===F.key);
  sec.innerHTML=`<h2>${F.label}</h2><p class="sub">Drivers: ${F.drivers.map(d=>d.label).join(", ")}. Stocks: ${F.names.join(", ")} (the rule picks the leader at each date).</p>`;
  const strip=document.createElement("div");strip.className="strip";
  rows.forEach(r=>{const c=document.createElement("div");c.className="cell";c.title=r.day+" "+r.leader+": "+r.reasoning;c.innerHTML=`${r.day.slice(2,7)}<b>${r.call}</b>${(+r.confidence).toFixed(2)}<br><span class="${cls(r.net_pct)}">${(+r.net_pct>0?"+":"")}${(+r.net_pct).toFixed(1)}%</span>`;strip.appendChild(c)});
  sec.appendChild(strip);const hint=document.createElement("div");hint.className="legend";hint.innerHTML='<span>Each cell: month, call, confidence, and what holding the leader would have returned after costs.</span>';sec.appendChild(hint);
  const grid=document.createElement("div");grid.className="grid";sec.appendChild(grid);
  F.drivers.forEach((d,k)=>{const marks=rows.map(r=>({i:idx(r.day),color:r.call==="long"?"var(--good)":"var(--flat)",tip:r.day+": "+r.call+" ("+(+r.confidence).toFixed(2)+")"}));
    chart(grid,d.label,d.sym+" (driver, not traded)",[{label:d.label,color:COL[k%6],vals:PX[d.sym]}],{win:WIN,marks:k===0?marks:[]})});
  F.names.forEach((t,k)=>{const mine=rows.filter(r=>r.leader===t);
    const marks=mine.map(r=>({i:idx(r.day),color:r.net_pct>0?"var(--good)":"var(--bad)",tip:r.day+" "+t+": "+r.call+", if long "+(r.net_pct>0?"+":"")+r.net_pct+"% after cost ("+r.entry_date+" to "+r.exit_date+")"}));
    const spans=mine.filter(r=>r.call==="long").map(r=>({i0:idx(r.entry_date),i1:idx(r.exit_date),color:"var(--good)"}));
    chart(grid,t+(mine.length?" (leader on "+mine.length+" decision days)":""),"stock price, USD",[{label:t,color:COL[(k+2)%6],vals:PX[t]}],{win:WIN,marks,spans})});
  FH.appendChild(sec)});
// macro
(function(){const g=document.getElementById("macro");[["^VIX","VIX volatility index"]].forEach(([s,l])=>chart(g,l,s,[{label:l,color:"var(--bad)",vals:PX[s]}],{win:WIN}))})();
// table
const tb=document.querySelector("#tbl tbody"),ff=document.getElementById("ff"),fc=document.getElementById("fc");
FAMS.forEach(F=>{const o=document.createElement("option");o.value=F.key;o.textContent=F.label;ff.appendChild(o)});
function draw(){tb.innerHTML="";R.filter(r=>(!ff.value||r.family===ff.value)&&(!fc.value||r.call===fc.value)).forEach(r=>{
  const tr=document.createElement("tr");tr.className="row";
  tr.innerHTML=`<td>${r.day}</td><td>${FL[r.family]}</td><td>${r.leader}</td><td>${r.call==="long"?'<span class="pill pos">long</span>':'<span class="pill">flat</span>'}</td><td>${r.horizon}d</td><td>${(+r.confidence).toFixed(2)}</td><td>${r.entry_date} to ${r.exit_date}</td><td class="${cls(r.net_pct)}">${fmt(r.net_pct)}%</td><td class="${cls(r.basket_ret_pct)}">${fmt(r.basket_ret_pct)}%</td><td class="${cls(r.driver_ret_pct)}">${fmt(r.driver_ret_pct)}%</td>`;
  const d=document.createElement("tr");d.className="detail";d.style.display="none";
  d.innerHTML=`<td colspan="10"><b>Reasoning:</b> ${(r.reasoning||"").replace(/</g,"&lt;")}<br><b>Market view that day:</b> ${(r.market_view||"").replace(/</g,"&lt;")}<br><b>Would change my mind:</b> ${(r.would_change_my_mind||"").replace(/</g,"&lt;")}</td>`;
  tr.onclick=()=>{d.style.display=d.style.display==="none"?"table-row":"none"};tb.appendChild(tr);tb.appendChild(d)})}
ff.onchange=draw;fc.onchange=draw;draw();
</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="fam_v0")
    a = ap.parse_args()
    data = json.loads((ROOT / "results" / a.run / "dashboard_data.json").read_text(encoding="utf-8"))
    series, stocks, sel = fd.load_series(), fd.load_stocks(), fd.selections()
    axis = sorted(d for d in stocks["XOM"] if d >= START)
    prices = {}
    def put(key, closes):
        prices[key] = [round(closes[d], 2) if d in closes else None for d in axis]
    fams = []
    for fam in fd.FAMILIES:
        names = []
        for snap in sel.values():
            for t in snap[fam]:
                if t not in names:
                    names.append(t)
        names = [t for t in names if t in stocks]
        for t in names:
            put(t, stocks[t])
        drivers = []
        for sym, label in fd.DRIVERS[fam]:
            put(sym, series[sym])
            drivers.append({"sym": sym, "label": label})
        fams.append({"key": fam, "label": fd.FAMILY_LABEL[fam], "names": names, "drivers": drivers})
    put("^VIX", series["^VIX"])
    html = (TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__AXIS__", json.dumps(axis))
            .replace("__PRICES__", json.dumps(prices)).replace("__FAMS__", json.dumps(fams)))
    out = ROOT / "results" / "dashboard_family.html"
    out.write_text(html, encoding="utf-8")
    print("wrote", out, "({:.0f} KB), {} price series, {} days".format(out.stat().st_size / 1024, len(prices), len(axis)))


if __name__ == "__main__":
    main()
