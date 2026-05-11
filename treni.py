#!/usr/bin/env python3
"""
App Orari Treni - Trenitalia
Server Python fa da proxy per aggirare il blocco CORS.
"""

import http.server
import threading
import webbrowser
import json
import urllib.parse
from datetime import datetime

try:
    import requests
except ImportError:
    print("Installa requests: pip install requests")
    exit(1)

BASE = "http://www.viaggiatreno.it/infomobilita/resteasy/viaggiatreno"
SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'it-IT,it;q=0.9',
    'Referer': 'http://www.viaggiatreno.it/',
})

def api(path):
    try:
        r = SESSION.get(BASE + path, timeout=10)
        if r.status_code == 204 or not r.text.strip():
            return None
        try:
            return r.json()
        except:
            return r.text
    except Exception as e:
        return None

HTML = r"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#c8a87a">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="GTreni">
<meta name="application-name" content="GTreni">
<title>GTreni</title>
<link rel="manifest" href="/manifest.json">
<style>
:root {
  --bg: #f5efe6;
  --bg2: #ede3d4;
  --bg3: #e8dcc8;
  --border: #c8b89a;
  --accent: #7a5c3a;
  --accent2: #9c7248;
  --text: #2c1f0e;
  --muted: #6b5642;
  --green: #4a7c59;
  --red: #8b2e2e;
  --yellow: #a07820;
  --marble-vein: rgba(180,160,130,0.3);
}
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family: 'Georgia', 'Segoe UI', serif;
  background-color: var(--bg);
  background-image:
    radial-gradient(ellipse at 20% 50%, rgba(210,190,160,0.4) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(220,200,170,0.3) 0%, transparent 50%),
    repeating-linear-gradient(125deg, transparent 0px, transparent 40px, rgba(180,155,120,0.08) 40px, rgba(180,155,120,0.08) 41px),
    repeating-linear-gradient(55deg, transparent 0px, transparent 60px, rgba(160,135,100,0.06) 60px, rgba(160,135,100,0.06) 61px),
    repeating-linear-gradient(170deg, transparent 0px, transparent 80px, rgba(190,165,130,0.07) 80px, rgba(190,165,130,0.07) 81px);
  color: var(--text);
  min-height: 100vh;
}

/* HEADER */
header {
  background: linear-gradient(135deg, #c8a87a 0%, #b8956a 40%, #c4a07a 100%);
  padding: 18px 32px;
  padding-top: max(18px, env(safe-area-inset-top));
  border-bottom: 2px solid #9a7550;
  display: flex; align-items: center; gap: 16px;
  position: sticky; top: 0; z-index: 100;
  box-shadow: 0 4px 16px rgba(100,70,30,0.25);
}
header .logo { font-size: 2rem; }
header h1 { font-size: 1.4rem; font-weight: 700; letter-spacing: -0.3px; color: #2c1f0e; text-shadow: 0 1px 2px rgba(255,255,255,0.3); }
header h1 span { color: #5c3a1e; }

/* TABS */
.tabs {
  display: flex;
  background: linear-gradient(180deg, #ddd0ba 0%, #d4c4aa 100%);
  border-bottom: 2px solid #b8a080;
  padding: 0 16px;
  gap: 4px;
  position: sticky;
  top: 60px;
  z-index: 99;
  overflow-x: auto;
  scrollbar-width: none;
  box-shadow: 0 2px 8px rgba(100,70,30,0.1);
}
.tabs::-webkit-scrollbar { display: none; }
.tab {
  padding: 14px 20px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--muted);
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
  border-radius: 6px 6px 0 0;
  letter-spacing: 0.2px;
}
.tab:hover { color: var(--text); background: rgba(100,70,30,0.08); }
.tab.active { color: var(--accent); border-bottom-color: var(--accent); }

/* LAYOUT */
.container { max-width: 920px; margin: 0 auto; padding: 28px 20px; }
.panel { display: none; }
.panel.active { display: block; }

/* CARDS */
.card {
  background: linear-gradient(145deg, #f0e8d8, #e8dcc8, #ede3d2);
  border: 1px solid #c0a880;
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(100,70,30,0.12), 0 1px 3px rgba(255,255,255,0.6) inset;
}
.card-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0.2px;
}

/* FORM */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.form-grid.cols3 { grid-template-columns: 1fr 1fr 1fr; }
.form-grid.cols4 { grid-template-columns: 1fr 1fr 160px 160px; }
.viaggio-form { display: grid; grid-template-columns: 1fr auto 1fr 1fr 1fr; gap: 10px; align-items: end; margin-bottom: 14px; }
@media(max-width:640px) {
  .form-grid, .form-grid.cols3, .form-grid.cols4 { grid-template-columns: 1fr; }
  .viaggio-form { grid-template-columns: 1fr 1fr; }
  .viaggio-form .swap-btn-wrap { display: none; }
  header { padding: 12px 16px; }
  header .logo { font-size: 1.5rem; }
  header h1 { font-size: 1.1rem; }
  .tabs { padding: 0 4px; gap: 0; overflow-x: auto; }
  .tab { padding: 10px 12px; font-size: 0.78rem; white-space: nowrap; }
  .container { padding: 16px 12px; }
  .card { padding: 16px; border-radius: 10px; }
  .btn { width: 100%; padding: 14px; font-size: 1rem; margin-bottom: 8px; }
  .btn-row { display: flex; flex-direction: column; gap: 0; }
  .form-group input { padding: 13px 14px; font-size: 1rem; }
  .ac-list div { padding: 13px 14px; font-size: 0.95rem; }
  .train-card { flex-wrap: wrap; gap: 10px; padding: 12px 14px; }
  .train-badge { min-width: 70px; font-size: 0.78rem; }
  .track-box { min-width: 44px; }
  .detail-grid { grid-template-columns: 1fr 1fr; }
  .stop { font-size: 0.8rem; }
}
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 0.72rem; color: var(--muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; }
.form-group input {
  background: linear-gradient(145deg, #f8f2e8, #ede3d4);
  border: 1px solid #b8a080;
  border-radius: 10px;
  padding: 12px 14px;
  color: var(--text);
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  width: 100%;
  -webkit-appearance: none;
  box-shadow: inset 0 2px 4px rgba(100,70,30,0.1), 0 1px 2px rgba(255,255,255,0.5);
}
.form-group input:focus { border-color: var(--accent); box-shadow: inset 0 2px 4px rgba(100,70,30,0.1), 0 0 0 3px rgba(122,92,58,0.15); }
.form-group input::placeholder { color: #a8906e; }

.btn-row { margin-top: 16px; }
.btn {
  background: linear-gradient(145deg, #c4a070, #a07848, #b08858);
  color: #fff8f0;
  border: 1px solid #8a6030;
  border-radius: 10px;
  padding: 13px 28px;
  font-size: 0.92rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
  box-shadow: 0 4px 8px rgba(100,60,20,0.3), 0 1px 2px rgba(255,255,255,0.2) inset, 0 -2px 4px rgba(80,40,10,0.2) inset;
  text-shadow: 0 1px 2px rgba(80,40,10,0.4);
  letter-spacing: 0.3px;
}
.btn:hover { transform: translateY(-2px); box-shadow: 0 6px 14px rgba(100,60,20,0.35), 0 1px 2px rgba(255,255,255,0.2) inset; }
.btn:active { transform: translateY(1px); box-shadow: 0 2px 4px rgba(100,60,20,0.3), 0 1px 2px rgba(255,255,255,0.1) inset; }

/* AUTOCOMPLETE */
.ac-wrap { position: relative; }
.ac-list {
  position: absolute;
  top: calc(100% + 4px);
  left: 0; right: 0;
  background: linear-gradient(180deg, #f5efe2, #ede3d0);
  border: 1px solid var(--accent);
  border-radius: 10px;
  z-index: 300;
  max-height: 230px;
  overflow-y: auto;
  display: none;
  box-shadow: 0 12px 32px rgba(100,70,30,0.25);
}
.ac-list div {
  padding: 10px 14px;
  cursor: pointer;
  font-size: 0.88rem;
  transition: background 0.12s;
  border-bottom: 1px solid rgba(150,110,60,0.12);
  color: var(--text);
}
.ac-list div:last-child { border-bottom: none; }
.ac-list div:hover { background: rgba(122,92,58,0.12); color: var(--accent); }

/* TRAIN CARDS */
.train-list { display: flex; flex-direction: column; gap: 8px; }
.train-card {
  background: linear-gradient(145deg, #f2e9d8, #ebe0cc, #f0e6d5);
  border: 1px solid #c0a878;
  border-radius: 12px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: border-color 0.2s, transform 0.15s, box-shadow 0.2s;
  cursor: default;
  box-shadow: 0 2px 8px rgba(100,70,30,0.1), 0 1px 2px rgba(255,255,255,0.5) inset;
}
.train-card:hover { border-color: var(--accent); transform: translateX(2px); box-shadow: 0 4px 14px rgba(100,70,30,0.18); }
.train-badge {
  background: linear-gradient(145deg, #b89060, #9a7040, #a88050);
  border: 1px solid #7a5030;
  color: #fff8f0;
  padding: 8px 10px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.8rem;
  min-width: 76px;
  text-align: center;
  line-height: 1.3;
  box-shadow: 0 3px 6px rgba(80,40,10,0.3), 0 1px 2px rgba(255,255,255,0.15) inset;
  text-shadow: 0 1px 2px rgba(60,30,5,0.4);
}
.train-info { flex: 1; min-width: 0; }
.train-dest { font-weight: 600; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.train-sub { font-size: 0.8rem; color: var(--muted); margin-top: 2px; }
.delay-ok { color: var(--green); font-size: 0.82rem; font-weight: 600; white-space: nowrap; }
.delay-late { color: var(--red); font-size: 0.82rem; font-weight: 600; white-space: nowrap; }
.delay-none { color: var(--muted); font-size: 0.82rem; }
.track-box {
  background: linear-gradient(145deg, #c8a870, #a87840);
  border: 1px solid #8a6030;
  border-radius: 8px;
  padding: 6px 10px;
  text-align: center;
  min-width: 54px;
  box-shadow: 0 3px 6px rgba(80,40,10,0.25), 0 1px 2px rgba(255,255,255,0.15) inset;
  color: #fff8f0;
}
.track-box .track-num { font-weight: 700; font-size: 0.95rem; color: #fff8f0; text-shadow: 0 1px 2px rgba(60,30,5,0.4); }
.track-box .track-lbl { font-size: 0.62rem; color: rgba(255,240,210,0.8); text-transform: uppercase; letter-spacing: 0.5px; }

/* VIAGGIO RESULTS */
.viaggio-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 12px;
  transition: border-color 0.2s;
}
.viaggio-card:hover { border-color: var(--accent); }
.viaggio-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.viaggio-times { font-size: 1.2rem; font-weight: 700; color: var(--text); }
.viaggio-times span { color: var(--muted); font-size: 0.9rem; font-weight: 400; margin: 0 6px; }
.viaggio-duration { background: var(--bg3); border-radius: 6px; padding: 4px 10px; font-size: 0.78rem; color: var(--muted); }
.viaggio-price { margin-left: auto; font-size: 1.1rem; font-weight: 700; color: var(--green); }
.viaggio-legs { display: flex; flex-direction: column; gap: 6px; }
.viaggio-leg { display: flex; align-items: center; gap: 10px; font-size: 0.85rem; color: var(--muted); }
.leg-badge { background: #1a2744; color: var(--accent2); padding: 3px 8px; border-radius: 5px; font-weight: 600; font-size: 0.78rem; white-space: nowrap; }
.leg-arrow { color: var(--border); }
.cambio-badge { background: #2d1f0a; color: var(--yellow); border-radius: 5px; padding: 2px 8px; font-size: 0.75rem; }

/* STATO TRENO */
.detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr)); gap: 10px; margin-bottom: 16px; }
.detail-box { background: var(--bg); border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px; }
.detail-box .lbl { font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
.detail-box .val { font-size: 0.98rem; font-weight: 600; }
.stops { display: flex; flex-direction: column; }
.stop { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.84rem; }
.stop:last-child { border-bottom: none; }
.dot { width: 9px; height: 9px; border-radius: 50%; background: var(--border); flex-shrink: 0; }
.dot.passed { background: var(--green); }
.dot.current { background: var(--accent2); box-shadow: 0 0 8px var(--accent2); }
.stop-name { flex: 1; }
.stop-time { color: var(--muted); font-size: 0.78rem; min-width: 40px; }

/* STATUS BADGES */
.sbadge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; border: 1px solid rgba(100,70,30,0.3); }
.btn-fermate { background: linear-gradient(145deg, #d4b888, #b89060); border: 1px solid #8a6030; color: #fff8f0; border-radius: 8px; padding: 5px 12px; font-size: 0.72rem; cursor: pointer; transition: all 0.15s; white-space: nowrap; font-weight: 600; box-shadow: 0 2px 4px rgba(80,40,10,0.2); }
.btn-fermate:hover { transform: translateY(-1px); box-shadow: 0 4px 8px rgba(80,40,10,0.25); }
.fermate-stop { display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 0.82rem; }
.fermate-stop .fs-time { color: var(--muted); min-width: 50px; font-size: 0.78rem; font-weight: 600; }
.fermate-stop .fs-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent2); flex-shrink: 0; }
.fermate-stop.fs-highlight .fs-dot { background: var(--accent); }
.fermate-stop.fs-highlight .fs-name { color: var(--accent); font-weight: 600; }
.s-ok { background: rgba(74,124,89,0.15); color: var(--green); }
.s-late { background: rgba(239,68,68,0.15); color: var(--red); }
.s-grey { background: rgba(100,116,139,0.15); color: var(--muted); }

/* STATES */
.loading { text-align: center; padding: 40px; color: var(--muted); font-size: 0.9rem; }
.error-box { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); color: #fca5a5; padding: 14px 18px; border-radius: 10px; font-size: 0.88rem; }
.empty-box { text-align: center; padding: 40px; color: var(--muted); }
.empty-box .ico { font-size: 2.5rem; margin-bottom: 10px; }

/* DIVIDER */
.section-label { font-size: 0.72rem; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 10px; }
</style>
</head>
<body>

<header>
  <div class="logo">🚄</div>
  <h1>G<span>Treni</span></h1>
</header>

<div class="tabs">
  <div class="tab active" onclick="tab('v')">🗺️ Cerca Viaggio</div>
  <div class="tab" onclick="tab('p')">🚉 Partenze</div>
  <div class="tab" onclick="tab('a')">🏁 Arrivi</div>
  <div class="tab" onclick="tab('t')">🔍 Stato Treno</div>
</div>

<!-- CERCA VIAGGIO -->
<div id="panel-v" class="panel active">
  <div class="container">
    <div class="card">
      <div class="card-title">🗺️ Cerca soluzioni di viaggio</div>
      <div class="viaggio-form">
        <div class="form-group" style="margin:0">
          <label>Stazione di partenza</label>
          <div class="ac-wrap">
            <input id="v-from" placeholder="Es. Bergamo" autocomplete="off">
            <div class="ac-list" id="ac-vf"></div>
            <input type="hidden" id="v-from-id">
          </div>
        </div>
        <div class="swap-btn-wrap" style="display:flex;align-items:flex-end;padding-bottom:2px"><button onclick="reverseViaggio()" title="Inverti stazioni" style="background:var(--card);border:1px solid var(--border);border-radius:50%;width:36px;height:36px;cursor:pointer;font-size:1.1rem;color:var(--muted);flex-shrink:0;transition:all 0.2s" onmouseover="this.style.color='var(--accent)'" onmouseout="this.style.color='var(--muted)'">⇄</button></div>
        <div class="form-group" style="margin:0">
          <label>Stazione di arrivo</label>
          <div class="ac-wrap">
            <input id="v-to" placeholder="Es. Milano Centrale" autocomplete="off">
            <div class="ac-list" id="ac-vt"></div>
            <input type="hidden" id="v-to-id">
          </div>
        </div>
        <div class="form-group" style="margin:0">
          <label>Data</label>
          <input type="date" id="v-date">
        </div>
        <div class="form-group" style="margin:0">
          <label>Ora partenza</label>
          <input type="time" id="v-time">
        </div>
      </div>
      <div class="btn-row">
        <button class="btn" onclick="cercaTutto()">🔍 Cerca</button>
      </div>
    </div>
    <div id="res-v"></div>
  </div>
</div>

<!-- PARTENZE -->
<div id="panel-p" class="panel">
  <div class="container">
    <div class="card">
      <div class="card-title">🚉 Treni in partenza</div>
      <div class="form-grid cols3">
        <div class="form-group" style="grid-column: span 2">
          <label>Stazione</label>
          <div class="ac-wrap">
            <input id="p-staz" placeholder="Es. Milano Centrale" autocomplete="off">
            <div class="ac-list" id="ac-p"></div>
            <input type="hidden" id="p-staz-id">
          </div>
        </div>
        <div class="form-group">
          <label>Orario</label>
          <input type="time" id="p-ora">
        </div>
      </div>
      <div class="btn-row"><button class="btn" onclick="cercaPartenze()">Cerca partenze</button></div>
    </div>
    <div id="res-p"></div>
  </div>
</div>

<!-- ARRIVI -->
<div id="panel-a" class="panel">
  <div class="container">
    <div class="card">
      <div class="card-title">🏁 Treni in arrivo</div>
      <div class="form-grid cols3">
        <div class="form-group" style="grid-column: span 2">
          <label>Stazione</label>
          <div class="ac-wrap">
            <input id="a-staz" placeholder="Es. Roma Termini" autocomplete="off">
            <div class="ac-list" id="ac-a"></div>
            <input type="hidden" id="a-staz-id">
          </div>
        </div>
        <div class="form-group">
          <label>Orario</label>
          <input type="time" id="a-ora">
        </div>
      </div>
      <div class="btn-row"><button class="btn" onclick="cercaArrivi()">Cerca arrivi</button></div>
    </div>
    <div id="res-a"></div>
  </div>
</div>

<!-- STATO TRENO -->
<div id="panel-t" class="panel">
  <div class="container">
    <div class="card">
      <div class="card-title">🔍 Monitora un treno</div>
      <div class="form-grid" style="max-width:380px">
        <div class="form-group">
          <label>Numero treno</label>
          <div class="ac-wrap">
            <input id="t-num" placeholder="Es. 9685" autocomplete="off">
            <div class="ac-list" id="ac-t"></div>
          </div>
        </div>
      </div>
      <div class="btn-row"><button class="btn" onclick="cercaTreno()">Monitora</button></div>
    </div>
    <div id="res-t"></div>
  </div>
</div>

<script>
// Init date/time fields
const now = new Date();
const pad = n => n.toString().padStart(2,'0');
document.getElementById('v-date').value = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}`;
document.getElementById('v-time').value = `${pad(now.getHours())}:${pad(now.getMinutes())}`;
document.getElementById('p-ora').value = `${pad(now.getHours())}:${pad(now.getMinutes())}`;
document.getElementById('a-ora').value = `${pad(now.getHours())}:${pad(now.getMinutes())}`;

// Tab switching
function tab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  const order = ['v','p','a','t'];
  document.querySelectorAll('.tab')[order.indexOf(name)].classList.add('active');
  document.getElementById('panel-' + name).classList.add('active');
}

// Close autocomplete on outside click
document.addEventListener('click', () => {
  document.querySelectorAll('.ac-list').forEach(l => l.style.display = 'none');
});

// Autocomplete stazione
let timers = {};
async function acStaz(inpId, listId, hiddenId) {
  const inp = document.getElementById(inpId);
  const list = document.getElementById(listId);
  if (hiddenId) document.getElementById(hiddenId).value = '';
  clearTimeout(timers[inpId]);
  const q = inp.value.trim();
  if (q.length < 2) { list.style.display = 'none'; return; }
  timers[inpId] = setTimeout(async () => {
    try {
      const r = await fetch(`/api/stazioni?q=${encodeURIComponent(q)}`);
      const data = await r.json();
      if (!data.length) { list.style.display = 'none'; return; }
      list.innerHTML = '';
      data.forEach(s => {
        const div = document.createElement('div');
        div.textContent = s.nome;
        div.onclick = e => {
          e.stopPropagation();
          inp.value = s.nome;
          if (hiddenId) document.getElementById(hiddenId).value = s.id;
          list.style.display = 'none';
        };
        list.appendChild(div);
      });
      list.style.display = 'block';
    } catch(e) { list.style.display = 'none'; }
  }, 280);
}

async function acTreno(inpId, listId) {
  const inp = document.getElementById(inpId);
  const list = document.getElementById(listId);
  clearTimeout(timers[inpId]);
  const q = inp.value.trim();
  if (q.length < 2) { list.style.display = 'none'; return; }
  timers[inpId] = setTimeout(async () => {
    try {
      const r = await fetch(`/api/cerca-treno?n=${encodeURIComponent(q)}`);
      const data = await r.json();
      if (!data.length) { list.style.display = 'none'; return; }
      list.innerHTML = '';
      data.forEach(s => {
        const div = document.createElement('div');
        div.textContent = s.label;
        div.onclick = e => {
          e.stopPropagation();
          inp.value = s.numero;
          list.style.display = 'none';
        };
        list.appendChild(div);
      });
      list.style.display = 'block';
    } catch(e) { list.style.display = 'none'; }
  }, 280);
}

// Bind autocomplete inputs
document.getElementById('v-from').addEventListener('input', () => acStaz('v-from','ac-vf','v-from-id'));
document.getElementById('v-to').addEventListener('input', () => acStaz('v-to','ac-vt','v-to-id'));
document.getElementById('p-staz').addEventListener('input', () => acStaz('p-staz','ac-p','p-staz-id'));
document.getElementById('a-staz').addEventListener('input', () => acStaz('a-staz','ac-a','a-staz-id'));
document.getElementById('t-num').addEventListener('input', () => acTreno('t-num','ac-t'));

// Helpers
function fmt(ts) {
  if (!ts) return '--:--';
  const d = new Date(ts);
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`;
}
function fmtDur(min) {
  if (!min) return '';
  const h = Math.floor(min/60), m = min%60;
  return h ? `${h}h ${m}m` : `${m}m`;
}
function delayHtml(r) {
  if (r === null || r === undefined) return '<span class="delay-none">–</span>';
  if (r <= 0) return '<span class="delay-ok">✓ In orario</span>';
  return `<span class="delay-late">+${r} min</span>`;
}

function apriLefrecce() {
  window.open('https://www.lefrecce.it', '_blank');
}

function apriTrenitalia() {
  window.open('https://www.lefrecce.it', '_blank');
}

function reverseViaggio() {
  const fromInput = document.getElementById('v-from');
  const toInput = document.getElementById('v-to');
  const fromId = document.getElementById('v-from-id');
  const toId = document.getElementById('v-to-id');
  const tmpVal = fromInput.value;
  const tmpId = fromId.value;
  fromInput.value = toInput.value;
  fromId.value = toId.value;
  toInput.value = tmpVal;
  toId.value = tmpId;
  document.getElementById('res-v').innerHTML = '';
}

// CERCA VIAGGIO
// Funzioni globali per rendering card
function htmlTreno(t, idx, toNome) {
  const arrDest = t.orarioArrivoDestinazione ? fmt(t.orarioArrivoDestinazione) : (t.orarioArrivo ? fmt(t.orarioArrivo) : (t.compOrarioArrivo ? t.compOrarioArrivo : null));
  const fromTime = t.orarioPartenza ? new Date(t.orarioPartenza) : null;
  const toTime = t.orarioArrivoDestinazione ? new Date(t.orarioArrivoDestinazione) : (t.orarioArrivo ? new Date(t.orarioArrivo) : null);
  let durStr = '';
  if (fromTime && toTime) {
    const diffMin = Math.round((toTime - fromTime) / 60000);
    if (diffMin > 0) durStr = fmtDur(diffMin);
  }
  const codOrig = (t.codOrigine||'').replace(/'/g,"");
  return `
    <div class="train-card" id="card-v-${idx}">
      <div class="train-badge">${t.categoria||''}<br>${t.numeroTreno||'–'}</div>
      <div class="train-info">
        <div class="train-dest">→ ${t.destinazione||'–'}</div>
        <div class="train-sub">
          🕐 Partenza: <b>${fmt(t.orarioPartenza)}</b>
          ${arrDest ? ('&nbsp;→&nbsp;<b>' + toNome + '</b>: <b>' + arrDest + '</b>') : ''}
          ${durStr ? ('&nbsp;·&nbsp;<span style="color:var(--accent)">' + durStr + '</span>') : ''}
        </div>
      </div>
      <span class="sbadge s-ok" style="font-size:0.72rem">Diretto</span>
      ${delayHtml(t.ritardo)}
      <div class="track-box"><div class="track-lbl">Bin.</div><div class="track-num">${t.binarioProgrammatoPartenzaDescrizione||'–'}</div></div>
      <button class="btn-fermate" onclick="toggleFermate(${idx}, '${codOrig}', ${t.numeroTreno||0}, ${t.orarioPartenza||0})">🛑 Fermate</button>
      <div class="fermate-panel" id="fermate-v-${idx}" style="display:none;width:100%;margin-top:8px;padding-top:8px;border-top:1px solid var(--border)">
        <div class="fermate-loading">Caricamento fermate...</div>
      </div>
    </div>`;
}

function htmlCambio(s, idx, toNome) {
  const t1 = s.treno1;
  const t2 = s.treno2;
  const partStr = fmt(s.orarioPartenza);
  const arrStr = s.orarioArrivo ? fmt(s.orarioArrivo) : '–';
  const arrCambio = fmt(s.oraArrCambio);
  const partCambio = fmt(s.oraPartCambio);
  const attesa = s.attesaMin;
  let durTot = '';
  if (s.orarioPartenza && s.orarioArrivo) {
    const diffMin = Math.round((s.orarioArrivo - s.orarioPartenza) / 60000);
    if (diffMin > 0) durTot = fmtDur(diffMin);
  }
  return `
    <div class="train-card" style="flex-direction:column;align-items:flex-start;gap:10px">
      <div style="display:flex;align-items:center;gap:8px;width:100%;flex-wrap:wrap">
        <span class="sbadge" style="background:#2d1b69;color:#a78bfa;border:1px solid #7c3aed;font-size:0.72rem">🔄 1 cambio</span>
        <span style="font-size:0.82rem;color:var(--muted)">Partenza: <b style="color:var(--text)">${partStr}</b></span>
        ${arrStr !== '–' ? ('<span style="font-size:0.82rem;color:var(--muted)">→ <b style="color:var(--text)">' + toNome + '</b>: <b style="color:var(--text)">' + arrStr + '</b></span>') : ''}
        ${durTot ? ('<span style="color:var(--accent);font-size:0.82rem">· ' + durTot + '</span>') : ''}
      </div>
      <div style="display:flex;align-items:stretch;gap:0;width:100%">
        <div style="flex:1;background:var(--card-2,#1e293b);border-radius:10px 0 0 10px;padding:12px 14px;border:1px solid var(--border)">
          <div style="font-size:0.7rem;color:var(--muted);margin-bottom:6px">${t1.categoriaDescrizione||t1.categoria||'REG'} ${t1.numeroTreno}</div>
          <div style="font-size:1.05rem;font-weight:700;color:#ffffff">${partStr}</div>
          ${arrCambio !== '–' ? '<div style="font-size:1.05rem;font-weight:700;color:#ffffff">→ ' + arrCambio + '</div>' : ''}
          <div style="font-size:0.75rem;color:var(--muted);margin-top:4px">→ ${s.stazioneCAMBIO}</div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 10px;background:var(--bg);border-top:1px solid var(--border);border-bottom:1px solid var(--border);min-width:70px">
          <div style="font-size:0.7rem;color:#a78bfa;font-weight:700">CAMBIO</div>
          <div style="font-size:0.72rem;color:var(--muted);white-space:nowrap;text-align:center;margin:2px 0">${s.stazioneCAMBIO.split(' ').slice(0,2).join(' ')}</div>
          <div style="font-size:0.75rem;color:#a78bfa;font-weight:600">${attesa} min</div>
        </div>
        <div style="flex:1;background:var(--card-2,#1e293b);border-radius:0 10px 10px 0;padding:12px 14px;border:1px solid var(--border)">
          <div style="font-size:0.7rem;color:var(--muted);margin-bottom:6px">${t2.categoriaDescrizione||t2.categoria||'REG'} ${t2.numeroTreno}</div>
          <div style="font-size:1.05rem;font-weight:700;color:#ffffff">${partCambio}</div>
          ${arrStr !== '–' ? '<div style="font-size:1.05rem;font-weight:700;color:#ffffff">→ ' + arrStr + '</div>' : ''}
          <div style="font-size:0.75rem;color:var(--muted);margin-top:4px">→ ${toNome}</div>
        </div>
      </div>
      ${(t1.ritardo > 0 || t2.ritardo > 0) ? '<div style="font-size:0.75rem;color:#f87171">⚠️ Ritardi in corso</div>' : ''}
    </div>`;
}

const _fermateCache = {};

async function cercaTutto() {
  const fromId = document.getElementById('v-from-id').value;
  const toId = document.getElementById('v-to-id').value;
  const date = document.getElementById('v-date').value;
  const time = document.getElementById('v-time').value;
  const res = document.getElementById('res-v');
  if (!fromId) { res.innerHTML = '<div class="error-box">⚠️ Seleziona la stazione di partenza dalla lista</div>'; return; }
  if (!toId) { res.innerHTML = '<div class="error-box">⚠️ Seleziona la stazione di arrivo dalla lista</div>'; return; }
  const toNome = document.getElementById('v-to').value.trim();
  const fromNome = document.getElementById('v-from').value.trim();
  res.innerHTML = '<div class="loading">🔍 Ricerca in corso...</div>';

  const params = `from=${encodeURIComponent(fromId)}&to=${encodeURIComponent(toId)}&to-nome=${encodeURIComponent(toNome)}&from-nome=${encodeURIComponent(fromNome)}&date=${encodeURIComponent(date)}&time=${encodeURIComponent(time)}`;

  try {
    // Lancia diretti e cambi in parallelo
    const [rDiretti, rCambi] = await Promise.all([
      fetch(`/api/viaggio?${params}`),
      fetch(`/api/cambi?${params}`)
    ]);
    const [diretti, cambi] = await Promise.all([rDiretti.json(), rCambi.json()]);

    let html = '';

    // Sezione diretti
    const listaDiretti = Array.isArray(diretti) ? diretti : [];
    if (listaDiretti.length > 0) {
      html += `<div class="section-label" style="margin-bottom:8px;font-size:0.82rem;color:var(--muted)">🚄 Treni diretti (${listaDiretti.length})</div>`;
      html += `<div class="train-list">${listaDiretti.map((t,i) => htmlTreno(t, i, toNome)).join('')}</div>`;
    } else {
      html += '<div style="padding:10px 14px;background:rgba(160,120,72,0.1);border:1px solid rgba(160,120,72,0.3);border-radius:10px;font-size:0.83rem;color:#7a5c3a;margin-bottom:12px">ℹ️ Nessun treno diretto disponibile per questa tratta</div>';
    }

    // Sezione cambi
    const listaCambi = Array.isArray(cambi) ? cambi : [];
    if (listaCambi.length > 0) {
      html += '<div class="section-label" style="margin:16px 0 8px;font-size:0.82rem;color:var(--muted)">🔄 Soluzioni con cambio (' + listaCambi.length + ')</div>';
      html += '<div class="train-list">' + listaCambi.map((s,i) => htmlCambio(s, i, toNome)).join('') + '</div>';
    } else {
      // Mostra riquadro con dati per lefrecce.it
      const dateFormatted = date ? date.split('-').reverse().join('/') : '';
      html += '<div style="margin-top:16px;background:linear-gradient(145deg,#f0e4cc,#e8d8b8);border:1px solid #c0a070;border-radius:12px;padding:16px 18px;box-shadow:0 4px 12px rgba(100,70,30,0.15)">'  +
        '<div style="font-size:0.9rem;font-weight:700;color:#5c3a1e;margin-bottom:12px">🚉 Per questa tratta è necessario un cambio — cerca su lefrecce.it:</div>' +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">' +
          '<div style="background:linear-gradient(145deg,#f8f0e0,#ede0c8);border:1px solid #c0a070;border-radius:8px;padding:8px 12px;box-shadow:inset 0 1px 3px rgba(100,70,30,0.1)">' +
            '<div style="font-size:0.68rem;color:#8a6840;text-transform:uppercase;margin-bottom:3px;font-weight:700;letter-spacing:0.5px">Da</div>' +
            '<div style="font-weight:700;font-size:0.9rem;color:#2c1f0e">' + fromNome + '</div>' +
          '</div>' +
          '<div style="background:linear-gradient(145deg,#f8f0e0,#ede0c8);border:1px solid #c0a070;border-radius:8px;padding:8px 12px;box-shadow:inset 0 1px 3px rgba(100,70,30,0.1)">' +
            '<div style="font-size:0.68rem;color:#8a6840;text-transform:uppercase;margin-bottom:3px;font-weight:700;letter-spacing:0.5px">A</div>' +
            '<div style="font-weight:700;font-size:0.9rem;color:#2c1f0e">' + toNome + '</div>' +
          '</div>' +
          '<div style="background:linear-gradient(145deg,#f8f0e0,#ede0c8);border:1px solid #c0a070;border-radius:8px;padding:8px 12px;box-shadow:inset 0 1px 3px rgba(100,70,30,0.1)">' +
            '<div style="font-size:0.68rem;color:#8a6840;text-transform:uppercase;margin-bottom:3px;font-weight:700;letter-spacing:0.5px">Data</div>' +
            '<div style="font-weight:700;font-size:0.9rem;color:#2c1f0e">' + dateFormatted + '</div>' +
          '</div>' +
          '<div style="background:linear-gradient(145deg,#f8f0e0,#ede0c8);border:1px solid #c0a070;border-radius:8px;padding:8px 12px;box-shadow:inset 0 1px 3px rgba(100,70,30,0.1)">' +
            '<div style="font-size:0.68rem;color:#8a6840;text-transform:uppercase;margin-bottom:3px;font-weight:700;letter-spacing:0.5px">Ora</div>' +
            '<div style="font-weight:700;font-size:0.9rem;color:#2c1f0e">' + time + '</div>' +
          '</div>' +
        '</div>' +
        '<button onclick="apriLefrecce()" style="background:linear-gradient(135deg,#6366f1,#4f46e5);border:none;color:white;padding:10px 20px;border-radius:8px;cursor:pointer;font-size:0.85rem;font-weight:600">🌐 Apri lefrecce.it →</button>' +
      '</div>';
    }

    res.innerHTML = html;
  } catch(e) {
    res.innerHTML = '<div class="error-box">❌ Errore nella ricerca. Riprova.</div>';
  }
}


async function toggleFermate(idx, codOrigine, num, ts) {
  const panel = document.getElementById(`fermate-v-${idx}`);
  if (!panel) return;
  if (panel.style.display === 'block') { panel.style.display = 'none'; return; }
  panel.style.display = 'block';
  const cacheKey = `${codOrigine}-${num}-${ts}`;
  if (_fermateCache[cacheKey]) { renderFermate(panel, _fermateCache[cacheKey]); return; }
  panel.innerHTML = '<div style="font-size:0.8rem;color:var(--muted);padding:4px 0">⏳ Caricamento fermate...</div>';
  try {
    const r = await fetch(`/api/fermate?cod=${encodeURIComponent(codOrigine)}&num=${num}&ts=${ts}`);
    const data = await r.json();
    _fermateCache[cacheKey] = data;
    renderFermate(panel, data);
  } catch(e) {
    panel.innerHTML = '<div style="color:#f87171;font-size:0.8rem">❌ Errore caricamento fermate</div>';
  }
}

function renderFermate(panel, data) {
  if (!data || !data.fermate || !data.fermate.length) {
    panel.innerHTML = '<div style="font-size:0.8rem;color:var(--muted)">Nessuna fermata disponibile</div>';
    return;
  }
  const rows = data.fermate.map(f => {
    const nome = f.stazione || '–';
    const orario = f.programmata ? fmt(f.programmata) : (f.effettiva ? fmt(f.effettiva) : '–');
    const ritardo = f.ritardoArrivo || f.ritardoPartenza || 0;
    const ritardoHtml = ritardo > 0 ? "<span style=\"color:#f87171;font-size:0.72rem\">+" + ritardo + " min</span>" : "";
    return `<div class="fermate-stop">
      <span class="fs-dot"></span>
      <span class="fs-time">${orario}</span>
      <span class="fs-name">${nome}</span>
      ${ritardoHtml}
    </div>`;
  }).join('');
  panel.innerHTML = rows;
}

async function cercaViaggio() {
  // Mantenuto per compatibilita - usa cercaTutto
  cercaTutto();
}

// CAMBI
async function cercaCambi() {
  const fromId = document.getElementById('v-from-id').value;
  const toId = document.getElementById('v-to-id').value;
  const date = document.getElementById('v-date').value;
  const time = document.getElementById('v-time').value;
  const res = document.getElementById('res-v');
  if (!fromId) { res.innerHTML = '<div class="error-box">⚠️ Seleziona la stazione di partenza dalla lista</div>'; return; }
  if (!toId) { res.innerHTML = '<div class="error-box">⚠️ Seleziona la stazione di arrivo dalla lista</div>'; return; }
  res.innerHTML = '<div class="loading">🔄 Ricerca soluzioni con cambio... (può richiedere qualche secondo)</div>';
  try {
    const toNome = document.getElementById('v-to').value.trim();
    const fromNome = document.getElementById('v-from').value.trim();
    const r = await fetch(`/api/cambi?from=${encodeURIComponent(fromId)}&to=${encodeURIComponent(toId)}&to-nome=${encodeURIComponent(toNome)}&from-nome=${encodeURIComponent(fromNome)}&date=${encodeURIComponent(date)}&time=${encodeURIComponent(time)}`);
    const data = await r.json();
    if (!data || !data.length) {
      res.innerHTML = '<div class="error-box">❌ Nessuna soluzione con cambio trovata.</div>';
      return;
    }
    res.innerHTML = `<div class="train-list">${data.map((s,i) => htmlCambio(s,i,toNome)).join("")}</div>`;
  } catch(e) {
    res.innerHTML = '<div class="error-box">❌ Errore nella ricerca. Riprova.</div>';
  }
}

// PARTENZE
async function cercaPartenze() {
  const id = document.getElementById('p-staz-id').value;
  const ora = document.getElementById('p-ora').value;
  const res = document.getElementById('res-p');
  if (!id) { res.innerHTML = '<div class="error-box">⚠️ Seleziona una stazione dalla lista</div>'; return; }
  res.innerHTML = '<div class="loading">⏳ Caricamento...</div>';
  try {
    const r = await fetch(`/api/partenze?id=${encodeURIComponent(id)}&ora=${encodeURIComponent(ora)}`);
    const data = await r.json();
    if (data.error) { res.innerHTML = `<div class="error-box">❌ ${data.error}</div>`; return; }
    if (!data.length) { res.innerHTML = '<div class="empty-box"><div class="ico">🚉</div>Nessun treno trovato</div>'; return; }
    res.innerHTML = '<div class="train-list">' + data.slice(0,25).map(t => {
      return '<div class="train-card">' +
        '<div class="train-badge">' + (t.categoria||'') + '<br>' + t.numeroTreno + '</div>' +
        '<div class="train-info">' +
          '<div class="train-dest">→ ' + (t.destinazione||'–') + '</div>' +
          '<div class="train-sub">Partenza: <b>' + fmt(t.orarioPartenza) + '</b></div>' +
        '</div>' +
        delayHtml(t.ritardo) +
        '<div class="track-box"><div class="track-lbl">Bin.</div><div class="track-num">' + (t.binarioProgrammatoPartenzaDescrizione||'–') + '</div></div>' +
      '</div>';
    }).join('') + '</div>';
  } catch(e) { res.innerHTML = '<div class="error-box">❌ Errore. Riprova.</div>'; }
}

// ARRIVI
async function cercaArrivi() {
  const id = document.getElementById('a-staz-id').value;
  const ora = document.getElementById('a-ora').value;
  const res = document.getElementById('res-a');
  if (!id) { res.innerHTML = '<div class="error-box">⚠️ Seleziona una stazione dalla lista</div>'; return; }
  res.innerHTML = '<div class="loading">⏳ Caricamento...</div>';
  try {
    const r = await fetch(`/api/arrivi?id=${encodeURIComponent(id)}&ora=${encodeURIComponent(ora)}`);
    const data = await r.json();
    if (data.error) { res.innerHTML = `<div class="error-box">❌ ${data.error}</div>`; return; }
    if (!data.length) { res.innerHTML = '<div class="empty-box"><div class="ico">🏁</div>Nessun treno trovato</div>'; return; }
    res.innerHTML = '<div class="train-list">' + data.slice(0,25).map(t => {
      return '<div class="train-card">' +
        '<div class="train-badge">' + (t.categoria||'') + '<br>' + t.numeroTreno + '</div>' +
        '<div class="train-info">' +
          '<div class="train-dest">← Da ' + (t.origine||'–') + '</div>' +
          '<div class="train-sub">Arrivo: <b>' + fmt(t.orarioArrivo) + '</b></div>' +
        '</div>' +
        delayHtml(t.ritardo) +
        '<div class="track-box"><div class="track-lbl">Bin.</div><div class="track-num">' + (t.binarioProgrammatoArrivoDescrizione||'–') + '</div></div>' +
      '</div>';
    }).join('') + '</div>';
  } catch(e) { res.innerHTML = '<div class="error-box">❌ Errore. Riprova.</div>'; }
}

// STATO TRENO
async function cercaTreno() {
  const n = document.getElementById('t-num').value.trim();
  const res = document.getElementById('res-t');
  if (!n) { res.innerHTML = '<div class="error-box">⚠️ Inserisci un numero di treno</div>'; return; }
  res.innerHTML = '<div class="loading">⏳ Caricamento...</div>';
  try {
    const r = await fetch(`/api/treno?n=${encodeURIComponent(n)}`);
    const data = await r.json();
    if (data.error) { res.innerHTML = `<div class="error-box">❌ ${data.error}</div>`; return; }
    const t = data;
    const cancellato = t.provvedimento === 1;
    const inCorso = t.oraUltimoRilevamento && !cancellato;
    res.innerHTML = `
      <div class="card">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:18px;flex-wrap:wrap">
          <div class="train-badge" style="font-size:0.9rem">${t.categoria||''} ${t.numeroTreno}</div>
          <div style="flex:1;font-weight:700;font-size:1.05rem">${t.origine||'–'} → ${t.destinazione||'–'}</div>
          <span class="sbadge ${cancellato?'s-late':inCorso?'s-ok':'s-grey'}">
            ${cancellato?'❌ Cancellato':inCorso?'🟢 In viaggio':'⏸ Non partito'}
          </span>
        </div>
        <div class="detail-grid">
          <div class="detail-box"><div class="lbl">Partenza</div><div class="val">${fmt(t.orarioPartenza)}</div></div>
          <div class="detail-box"><div class="lbl">Arrivo previsto</div><div class="val">${fmt(t.orarioArrivo)}</div></div>
          <div class="detail-box"><div class="lbl">Ritardo</div><div class="val">${t.ritardo!=null?(t.ritardo<=0?'In orario':'+'+t.ritardo+' min'):'–'}</div></div>
          <div class="detail-box"><div class="lbl">Ultimo rilevamento</div><div class="val" style="font-size:0.82rem">${t.stazioneUltimoRilevamento||'–'}</div></div>
        </div>
        ${t.fermate&&t.fermate.length?`
          <div class="section-label">Fermate (${t.fermate.length})</div>
          <div class="stops">
            ${t.fermate.map(f=>`
              <div class="stop">
                <div class="dot ${f.actualFermataType===1?'passed':f.actualFermataType===2?'current':''}"></div>
                <div class="stop-name">${f.stazione}</div>
                <div class="stop-time">${fmt(f.programmata)}</div>
                ${f.ritardo?(f.ritardo>0?('<span class="delay-late">+'+f.ritardo+'</span>'):('<span class="delay-ok">✓</span>')):''}
              </div>`).join('')}
          </div>`:''}
      </div>`;
  } catch(e) { res.innerHTML = '<div class="error-box">❌ Errore. Riprova.</div>'; }
}
</script>
<script>
// Rimuovi tutti i service worker esistenti
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(regs => {
    regs.forEach(r => { r.unregister(); console.log('SW rimosso'); });
  });
  caches.keys().then(keys => keys.forEach(k => caches.delete(k)));
}
</script>
</body>
</html>

"""
def send_json(handler, data, code=200):
    body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    handler.send_response(code)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', len(body))
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.end_headers()
    handler.wfile.write(body)

def build_orario(ora_str, date_str=None):
    try:
        if date_str:
            dt = datetime.strptime(f"{date_str} {ora_str}", "%Y-%m-%d %H:%M")
        else:
            dt = datetime.now().replace(
                hour=int(ora_str.split(':')[0]),
                minute=int(ora_str.split(':')[1]),
                second=0, microsecond=0
            )
        giorni = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        mesi = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        return f"{giorni[dt.weekday()]} {mesi[dt.month-1]} {dt.day:02d} {dt.year} {dt.hour:02d}:{dt.minute:02d}:00 GMT+0200"
    except:
        return datetime.now().strftime("%a %b %d %Y %H:%M:00 GMT+0200")

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def do_HEAD(self):
        # Risponde alle richieste HEAD (usate da UptimeRobot per monitoraggio)
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        def p(k): return params.get(k, [''])[0]

        # Manifest PWA
        if parsed.path == '/manifest.json':
            manifest = {
                "name": "GTreni - Orari Trenitalia",
                "short_name": "GTreni",
                "description": "Orari treni in tempo reale",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#0a0f1e",
                "theme_color": "#0a0f1e",
                "orientation": "portrait",
                "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]
            }
            body = json.dumps(manifest).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/manifest+json')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)

        # Service Worker - versione che non fa cache
        elif parsed.path == '/sw.js':
            sw_code = "self.addEventListener('install',()=>self.skipWaiting());self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.map(k=>caches.delete(k)))).then(()=>self.clients.claim())));self.addEventListener('fetch',e=>e.respondWith(fetch(e.request)));"
            sw = sw_code.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Content-Length', len(sw))
            self.end_headers()
            self.wfile.write(sw)

        # Icone PNG
        elif parsed.path in ('/icon-192.png', '/icon-512.png'):
            fname = parsed.path[1:]
            import os
            fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
            try:
                with open(fpath, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", len(data))
                self.end_headers()
                self.wfile.write(data)
            except:
                self.send_response(404)
                self.end_headers()

        # Serve HTML
        elif parsed.path == '/':

            body = HTML.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)

        # Autocomplete stazioni
        elif parsed.path == '/api/stazioni':
            q = p('q')
            data = api(f'/autocompletaStazione/{urllib.parse.quote(q)}')
            if not data:
                send_json(self, [])
                return
            stazioni = []
            for line in str(data).strip().split('\n'):
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    stazioni.append({'nome': parts[0].strip(), 'id': parts[1].strip()})
            send_json(self, stazioni[:12])

        # Cerca numero treno autocomplete
        elif parsed.path == '/api/cerca-treno':
            n = p('n')
            data = api(f'/cercaNumeroTrenoTrenoAutocomplete/{urllib.parse.quote(n)}')
            if not data:
                send_json(self, [])
                return
            risultati = []
            for line in str(data).strip().split('\n'):
                parts = line.strip().split('|')
                label = parts[0].strip() if parts else line.strip()
                numero = label.split(' - ')[0].strip()
                if numero:
                    risultati.append({'label': label, 'numero': numero})
            send_json(self, risultati[:6])

        # Partenze
        elif parsed.path == '/api/partenze':
            staz_id = p('id')
            ora = p('ora') or datetime.now().strftime('%H:%M')
            orario = build_orario(ora)
            data = api(f'/partenze/{staz_id}/{urllib.parse.quote(orario)}')
            if data is None:
                send_json(self, {'error': 'Nessun dato disponibile'})
                return
            send_json(self, data[:25] if isinstance(data, list) else [])

        # Arrivi
        elif parsed.path == '/api/arrivi':
            staz_id = p('id')
            ora = p('ora') or datetime.now().strftime('%H:%M')
            orario = build_orario(ora)
            data = api(f'/arrivi/{staz_id}/{urllib.parse.quote(orario)}')
            if data is None:
                send_json(self, {'error': 'Nessun dato disponibile'})
                return
            send_json(self, data[:25] if isinstance(data, list) else [])

        # Cerca viaggio: partenze + controllo fermate per trovare treni che passano per la destinazione
        elif parsed.path == '/api/viaggio':
            from_id = p('from')
            to_nome = p('to-nome').upper().strip()
            date = p('date') or datetime.now().strftime('%Y-%m-%d')
            time_str = p('time') or datetime.now().strftime('%H:%M')
            from datetime import timedelta
            import concurrent.futures
            try:
                base_dt = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
            except:
                base_dt = datetime.now()

            # Raccogli partenze su 3 fasce orarie
            tutti = []
            seen = set()
            for delta_h in [0, 2, 4]:
                dt = base_dt + timedelta(hours=delta_h)
                orario = build_orario(dt.strftime('%H:%M'), dt.strftime('%Y-%m-%d'))
                parz = api(f'/partenze/{from_id}/{urllib.parse.quote(orario)}')
                if parz and isinstance(parz, list):
                    for t in parz:
                        key = t.get('numeroTreno')
                        if key and key not in seen:
                            seen.add(key)
                            tutti.append(t)


            if not tutti:
                send_json(self, [])
                return

            # Controlla se la dest. è nella destinazione finale (veloce, senza chiamate extra)
            keywords = [w for w in to_nome.split() if len(w) > 3]
            # Funzione match: richiede che TUTTE le parole siano presenti come parole intere
            def match_stazione(nome_f, kws, nome_completo):
                parole = nome_f.upper().split()
                return nome_completo in nome_f or all(k in parole for k in kws)
            diretti_veloci = []
            da_controllare = []
            for t in tutti[:20]:
                dest = (t.get('destinazione') or '').upper()
                # Match preciso: il nome completo deve essere contenuto nella destinazione
                # oppure tutti i keyword devono essere presenti
                match_esatto = to_nome in dest
                match_kw = keywords and all(k in dest for k in keywords)
                # Evita falsi positivi: se la destinazione contiene parole extra non volute
                # es. "CIAMPINO" non deve matchare "ROMA TUSCOLANA"
                if match_esatto or match_kw:
                    # Verifica che non sia un match parziale indesiderato
                    # Se to_nome è una parola sola, richiedi match esatto nella destinazione
                    parole_dest = dest.split()
                    parole_to = to_nome.split()
                    if all(p in parole_dest for p in parole_to):
                        diretti_veloci.append(t)
                    else:
                        da_controllare.append(t)
                else:
                    da_controllare.append(t)


            # Per i treni non diretti, controlla le fermate in parallelo
            def check_fermate(t):
                num = t.get('numeroTreno')
                cod_staz = t.get('codOrigine')  # formato S0XXXX richiesto da /fermate
                ts_ms = t.get('orarioPartenza')
                if not num or not ts_ms or not cod_staz:
                    return None
                fermate_data = api(f'/andamentoTreno/{cod_staz}/{num}/{ts_ms}')
                # L'API può rispondere con stringa JSON o lista
                # andamentoTreno risponde con dict, le fermate sono in ['fermate']
                if isinstance(fermate_data, dict):
                    fermate_list = fermate_data.get('fermate', [])
                elif isinstance(fermate_data, list):
                    fermate_list = fermate_data
                else:
                    return None
                if not fermate_list:
                    return None
                stazioni = [(f.get('stazione') or '').upper() for f in fermate_list]
                # Usa le keywords della stazione di PARTENZA cercata (from_id -> from_nome)
                from_nome_upper = p('from-nome').upper().strip()
                from_kw_local = [w for w in from_nome_upper.split() if len(w) > 3]
                # Trova indice della stazione di partenza cercata nel percorso
                idx_from = 0
                for i, nome in enumerate(stazioni):
                    if any(k in nome for k in from_kw_local):
                        idx_from = i
                        break
                # Cerca la destinazione DOPO la stazione di partenza
                for f in fermate_list[idx_from + 1:]:
                    nome_f = (f.get('stazione') or '').upper()
                    if match_stazione(nome_f, keywords, to_nome):
                        t['orarioArrivoDestinazione'] = f.get('arrivo_teorico') or f.get('programmata') or f.get('partenza_teorica')
                        return t
                return None

            trovati_fermate = []
            if da_controllare and keywords:
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
                    futures = [ex.submit(check_fermate, t) for t in da_controllare[:12]]
                    for fut in concurrent.futures.as_completed(futures):
                        res = fut.result()
                        if res is not None:
                            trovati_fermate.append(res)

            risultati = diretti_veloci + trovati_fermate
            risultati.sort(key=lambda t: t.get('orarioPartenza') or 0)

            # Strategia 2: arrivi alla stazione di destinazione
            # Filtra per origine oppure controlla nelle fermate (per stazioni intermedie)
            to_id = p('to')
            from_nome = p('from-nome').upper().strip()
            from_kw = [w for w in from_nome.split() if len(w) > 3]
            arrivi_trovati = []
            if to_id and from_kw:
                seen_arr = set()
                candidati_arrivi = []
                for delta_h in [0, 2, 4]:
                    dt2 = base_dt + timedelta(hours=delta_h)
                    orario2 = build_orario(dt2.strftime('%H:%M'), dt2.strftime('%Y-%m-%d'))
                    arr = api(f'/arrivi/{to_id}/{urllib.parse.quote(orario2)}')
                    if arr and isinstance(arr, list):
                        for t in arr:
                            key = t.get('numeroTreno')
                            if key and key not in seen_arr:
                                seen_arr.add(key)
                                orig = (t.get('origine') or '').upper()
                                # Controllo veloce: origine corrisponde
                                if any(k in orig for k in from_kw) or from_nome in orig:
                                    arrivi_trovati.append(t)
                                else:
                                    # Candidato da verificare nelle fermate
                                    candidati_arrivi.append(t)

                # Strategia 3: per i candidati rimasti, verifica nelle fermate
                # Questo cattura il caso in cui ENTRAMBE le stazioni sono intermedie
                numeri_gia = {t.get('numeroTreno') for t in risultati + arrivi_trovati}
                def check_fermate_arrivo(t):
                    num = t.get('numeroTreno')
                    cod = t.get('codOrigine')
                    ts = t.get('orarioArrivo') or t.get('orarioPartenza')
                    if not num or not cod or not ts:
                        return None
                    ferro = api(f'/andamentoTreno/{cod}/{num}/{ts}')
                    if not ferro or not isinstance(ferro, dict):
                        return None
                    fermate = ferro.get('fermate', [])
                    stazioni = [(f.get('stazione') or '').upper() for f in fermate]
                    # Trova indice stazione di partenza
                    idx_f = -1
                    for i, nome in enumerate(stazioni):
                        if any(k in nome for k in from_kw):
                            idx_f = i
                            break
                    if idx_f == -1:
                        return None
                    # Verifica che la destinazione venga dopo
                    for f in fermate[idx_f + 1:]:
                        nome_f = (f.get('stazione') or '').upper()
                        if match_stazione(nome_f, keywords, to_nome):
                            # Recupera orario partenza dalla stazione from
                            t['orarioPartenza'] = fermate[idx_f].get('partenza_teorica') or fermate[idx_f].get('programmata')
                            t['orarioArrivoDestinazione'] = f.get('arrivo_teorico') or f.get('programmata')
                            return t
                    return None

                da_verificare = [t for t in candidati_arrivi[:12] if t.get('numeroTreno') not in numeri_gia]
                if da_verificare:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
                        futs = [ex.submit(check_fermate_arrivo, t) for t in da_verificare]
                        for fut in concurrent.futures.as_completed(futs):
                            res = fut.result()
                            if res is not None:
                                arrivi_trovati.append(res)

                arrivi_trovati.sort(key=lambda t: t.get('orarioPartenza') or t.get('orarioArrivo') or 0)

            # Per i treni trovati via arrivi, recupera destinazione e orario partenza
            def arricchisci_arrivo(t):
                if t.get('destinazione') and t.get('orarioPartenza'):
                    return t
                num = t.get('numeroTreno')
                cod = t.get('codOrigine')
                ts = t.get('orarioArrivo') or t.get('orarioPartenza')
                if not num or not cod or not ts:
                    return t
                ferro = api(f'/andamentoTreno/{cod}/{num}/{ts}')
                if ferro and isinstance(ferro, dict):
                    if not t.get('destinazione'):
                        t['destinazione'] = ferro.get('destinazione') or ''
                    # Trova orario di partenza dalla stazione di partenza cercata
                    from_kw_arr = [w for w in from_nome.split() if len(w) > 3]
                    for f in ferro.get('fermate', []):
                        nome_f = (f.get('stazione') or '').upper()
                        if any(k in nome_f for k in from_kw_arr):
                            t['orarioPartenza'] = f.get('partenza_teorica') or f.get('programmata')
                            t['orarioArrivoDestinazione'] = t.get('orarioArrivo')
                            break
                return t

            # Unisci le due strategie, preferendo i risultati da partenze
            numeri_gia_trovati = {t.get('numeroTreno') for t in risultati}
            for t in arrivi_trovati:
                if t.get('numeroTreno') not in numeri_gia_trovati:
                    risultati.append(arricchisci_arrivo(t))

            risultati.sort(key=lambda t: t.get('orarioPartenza') or t.get('orarioArrivo') or 0)

            if risultati:
                send_json(self, risultati[:15])
            else:
                send_json(self, {'error': 'Nessun treno diretto trovato. Prova il tasto Cerca con cambi 🔄'})

        # Stato treno
        elif parsed.path == '/api/fermate':
            cod = p('cod')
            num = p('num')
            ts = p('ts')
            if not cod or not num or not ts:
                send_json(self, {'error': 'Parametri mancanti'})
                return
            data = api(f'/andamentoTreno/{cod}/{num}/{ts}')
            if not data or not isinstance(data, dict):
                send_json(self, {'fermate': []})
                return
            fermate = data.get('fermate', [])
            send_json(self, {'fermate': fermate})

        elif parsed.path == '/api/cambi':
            from_id   = p('from')
            to_id     = p('to')
            to_nome   = p('to-nome').upper().strip()
            from_nome = p('from-nome').upper().strip()
            date      = p('date') or datetime.now().strftime('%Y-%m-%d')
            time_str  = p('time') or datetime.now().strftime('%H:%M')
            from datetime import timedelta
            MARGINE_MIN = 10
            try:
                base_dt = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
            except:
                base_dt = datetime.now()

            INTERSCAMBI = {
                'ROMA TERMINI': 'S08409', 'MILANO CENTRALE': 'S01700',
                'BOLOGNA CENTRALE': 'S03300', 'FIRENZE S.M.N.': 'S06103',
                'NAPOLI CENTRALE': 'S09218', 'TORINO PORTA NUOVA': 'S00219',
                'VENEZIA SANTA LUCIA': 'S02528', 'GENOVA PIAZZA PRINCIPE': 'S00588',
                'PADOVA': 'S02534', 'VERONA PORTA NUOVA': 'S02112',
                'REGGIO CALABRIA': 'S11781', 'BARI CENTRALE': 'S10030',
                'PALERMO CENTRALE': 'S12101', 'CATANIA CENTRALE': 'S12325',
                'TRIESTE CENTRALE': 'S02827', 'BRESCIA': 'S02002',
                'PISA CENTRALE': 'S06401', 'ANCONA': 'S07101',
                'PESCARA CENTRALE': 'S08101', 'SALERNO': 'S09601',
                'CASSINO': 'S08662', 'FROSINONE': 'S08501',
                'LATINA': 'S08601', 'CASERTA': 'S09101',
                'REGGIO EMILIA': 'S03521', 'MODENA': 'S03501',
                'PARMA': 'S03601', 'PIACENZA': 'S03701',
                'BERGAMO': 'S01940', 'VARESE': 'S01801',
                'COMO SAN GIOVANNI': 'S01901', 'ALESSANDRIA': 'S00501',
            }

            to_kw = [w for w in to_nome.split() if len(w) > 3]

            def _match_strict(dest, nome_completo):
                d = dest.upper().strip()
                n = nome_completo.upper().strip()
                if n == d or n in d or d in n:
                    return True
                parole = [w for w in n.split() if len(w) > 3]
                return bool(parole) and all(w in d for w in parole)

            def _get_int(nome_dest):
                nd = nome_dest.upper()
                for ni, ii in INTERSCAMBI.items():
                    pi = [w for w in ni.split() if len(w) > 3]
                    pd2 = nd.split()
                    if pi and all(p in pd2 for p in pi[:2]):
                        return ii, ni
                    if ni in nd or nd in ni:
                        return ii, ni
                return None, None

            def _get_arr_at_stop(cod, num, ts, stop_nome):
                """Legge le fermate del treno e restituisce l'orario di arrivo alla fermata indicata."""
                fd = api(f'/andamentoTreno/{cod}/{num}/{ts}')
                if not fd or not isinstance(fd, dict):
                    return None, None
                fermate = fd.get('fermate', [])
                stop_kw = [w for w in stop_nome.split() if len(w) > 3]
                for fm in fermate:
                    nf = (fm.get('stazione') or '').upper()
                    if _match_strict(nf, stop_nome) or (stop_kw and all(k in nf for k in stop_kw)):
                        arr = fm.get('arrivo_teorico') or fm.get('programmata') or fm.get('partenza_teorica')
                        return arr, fermate
                return None, fermate

            def _cerca_int(sid, snome, arr_ms, t1):
                sols = []
                try:
                    arr_dt = datetime.fromtimestamp(arr_ms / 1000)
                except:
                    return sols
                min_dt = arr_dt + timedelta(minutes=MARGINE_MIN)

                tb_all = []
                seen_t = set()
                for dh in [0, 1, 2, 3, 4]:
                    dt_try = min_dt + timedelta(hours=dh)
                    orario2 = build_orario(dt_try.strftime('%H:%M'), dt_try.strftime('%Y-%m-%d'))
                    tb = api(f'/partenze/{sid}/{urllib.parse.quote(orario2)}')
                    if tb and isinstance(tb, list):
                        for tx in tb:
                            k = tx.get('numeroTreno')
                            if k and k not in seen_t:
                                seen_t.add(k)
                                tb_all.append(tx)

                print(f"[INT] {snome} trovati {len(tb_all)} treni, min_dt={min_dt}", flush=True)

                for t2 in tb_all:
                    dest2 = (t2.get('destinazione') or '').upper()
                    op2 = (t2.get('orarioPartenza') or
                           t2.get('millisDataPartenza') or
                           t2.get('dataPartenzaTreno'))
                    if not op2:
                        continue
                    try:
                        p2_dt = datetime.fromtimestamp(op2 / 1000)
                    except:
                        continue
                    if p2_dt < min_dt:
                        continue

                    ok = _match_strict(dest2, to_nome)
                    arr_d = None  # lo calcoliamo sempre dalle fermate
                    if not ok:
                        c2 = t2.get('codOrigine')
                        n2 = t2.get('numeroTreno')
                        if c2 and n2:
                            f2d = api(f'/andamentoTreno/{c2}/{n2}/{op2}')
                            if f2d and isinstance(f2d, dict):
                                fermate2 = f2d.get('fermate', [])
                                # Trova indice stazione di cambio
                                idx_cambio = -1
                                for i, fm in enumerate(fermate2):
                                    nf = (fm.get('stazione') or '').upper()
                                    if _match_strict(nf, snome):
                                        idx_cambio = i
                                        break
                                # Cerca destinazione SOLO nelle fermate DOPO il cambio
                                for fm in fermate2[idx_cambio + 1:]:
                                    nf = (fm.get('stazione') or '').upper()
                                    if _match_strict(nf, to_nome):
                                        arr_d = fm.get('arrivo_teorico') or fm.get('programmata')
                                        ok = True
                                        break
                    if ok:
                        # Cerca sempre orario arrivo a destinazione nelle fermate dopo cambio
                        if not arr_d:
                            c2x = t2.get('codOrigine')
                            n2x = t2.get('numeroTreno')
                            if c2x and n2x:
                                f2x = api(f'/andamentoTreno/{c2x}/{n2x}/{op2}')
                                if f2x and isinstance(f2x, dict):
                                    fermate2x = f2x.get('fermate', [])
                                    idx_cx = -1
                                    for i, fm in enumerate(fermate2x):
                                        if _match_strict((fm.get('stazione') or '').upper(), snome):
                                            idx_cx = i
                                            break
                                    for fm in fermate2x[idx_cx + 1:]:
                                        if _match_strict((fm.get('stazione') or '').upper(), to_nome):
                                            arr_d = fm.get('arrivo_teorico') or fm.get('programmata')
                                            break
                        print(f"[TROVATO] cambio a {snome} con {t2.get('numeroTreno')} dest={dest2} arr={arr_d}", flush=True)
                        sols.append({
                            'tipo': 'cambio', 'treno1': t1, 'treno2': t2,
                            'stazioneCAMBIO': snome, 'oraArrCambio': arr_ms,
                            'oraPartCambio': op2,
                            'attesaMin': int((p2_dt - arr_dt).total_seconds() / 60),
                            'orarioPartenza': t1.get('orarioPartenza'),
                            'orarioArrivo': arr_d or t2.get('orarioArrivo'),
                        })
                        break
                return sols

            # Raccogli treni da A
            treni_a = []
            seen = set()
            for dh in [0, 2]:
                dt = base_dt + timedelta(hours=dh)
                or1 = build_orario(dt.strftime('%H:%M'), dt.strftime('%Y-%m-%d'))
                parz = api(f'/partenze/{from_id}/{urllib.parse.quote(or1)}')
                if parz and isinstance(parz, list):
                    for t in parz:
                        k = t.get('numeroTreno')
                        if k and k not in seen:
                            seen.add(k)
                            treni_a.append(t)

            print(f"[CAMBI] from={from_id} to={to_id} to_nome={to_nome} trovati {len(treni_a)} treni", flush=True)
            if not treni_a:
                send_json(self, [])
                return

            tutte = []
            for t in treni_a[:8]:
                num  = t.get('numeroTreno')
                ts   = t.get('orarioPartenza')
                dest = (t.get('destinazione') or '').upper()
                cod  = t.get('codOrigine')
                if not num or not ts or not cod:
                    continue
                print(f"[TRENO] {num} dest={dest}", flush=True)

                # Leggi SEMPRE le fermate per avere l'orario reale di arrivo all'interscambio
                sid, snome = _get_int(dest)
                if sid and sid != from_id and sid != to_id:
                    # Prendi orario reale di arrivo alla stazione di cambio
                    arr_reale, fermate = _get_arr_at_stop(cod, num, ts, snome)
                    arr_ms = arr_reale or t.get('orarioArrivo') or ts
                    print(f"[TRENO] {num} arrivo a {snome}: {arr_ms}", flush=True)
                    tutte.extend(_cerca_int(sid, snome, arr_ms, t))
                else:
                    # Cerca nelle fermate altri interscambi
                    fd = api(f'/andamentoTreno/{cod}/{num}/{ts}')
                    fermate = fd.get('fermate', []) if fd and isinstance(fd, dict) else []
                    fkw = [w for w in from_nome.split() if len(w) > 3]
                    idx = 0
                    for i, fm in enumerate(fermate):
                        if any(k in (fm.get('stazione') or '').upper() for k in fkw):
                            idx = i
                            break
                    seen_int = set()
                    for fm in fermate[idx + 1:]:
                        nf = (fm.get('stazione') or '').upper()
                        si2, sn2 = _get_int(nf)
                        if not si2 or si2 == from_id or si2 == to_id:
                            continue
                        if sn2 in seen_int:
                            continue
                        seen_int.add(sn2)
                        am = fm.get('arrivo_teorico') or fm.get('programmata') or fm.get('partenza_teorica')
                        if not am:
                            continue
                        tutte.extend(_cerca_int(si2, sn2, am, t))
                        if len(tutte) >= 3:
                            break

                if len(tutte) >= 3:
                    break

            seen_s = set()
            uniche = []
            for s in tutte:
                k = (s['treno1'].get('numeroTreno'), s['stazioneCAMBIO'], s['treno2'].get('numeroTreno'))
                if k not in seen_s:
                    seen_s.add(k)
                    uniche.append(s)
            uniche.sort(key=lambda s: s.get('orarioPartenza') or 0)
            print(f"[CAMBI] Soluzioni trovate: {len(uniche)}", flush=True)
            send_json(self, uniche[:8])

        elif parsed.path == '/api/treno':
            n = p('n')
            cerca = api(f'/cercaNumeroTrenoTrenoAutocomplete/{urllib.parse.quote(n)}')
            if not cerca:
                send_json(self, {'error': f'Treno {n} non trovato'})
                return
            try:
                prima = str(cerca).strip().split('\n')[0]
                meta = prima.split('|')[1] if '|' in prima else ''
                parts = meta.split('-')
                cod_staz = parts[1]
                ts = parts[2]
                data = api(f'/andamentoTreno/{cod_staz}/{n}/{ts}')
                if data is None:
                    send_json(self, {'error': 'Dati non disponibili (treno cancellato o non in servizio)'})
                    return
                send_json(self, data)
            except Exception:
                send_json(self, {'error': 'Impossibile recuperare i dati del treno'})

        else:
            self.send_response(404)
            self.end_headers()

def main():
    PORT = 7890
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"\n🚄 App Treni Trenitalia avviata!")
    print(f"   → http://localhost:{PORT}")
    print(f"   Premi Ctrl+C per chiudere\n")
    threading.Timer(0.8, lambda: webbrowser.open(f'http://localhost:{PORT}')).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nApp chiusa.")

if __name__ == '__main__':
    main()
