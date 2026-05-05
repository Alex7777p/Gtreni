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
<meta name="theme-color" content="#0a0f1e">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="GTreni">
<meta name="application-name" content="GTreni">
<title>GTreni</title>
<link rel="manifest" href="/manifest.json">
<style>
:root {
  --bg: #0a0f1e;
  --bg2: #111827;
  --bg3: #1e293b;
  --border: #2d3748;
  --accent: #3b82f6;
  --accent2: #06b6d4;
  --text: #f1f5f9;
  --muted: #64748b;
  --green: #22c55e;
  --red: #ef4444;
  --yellow: #f59e0b;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',sans-serif; background:var(--bg); color:var(--text); min-height:100vh; }

/* HEADER */
header {
  background: linear-gradient(135deg, #0d1f3c 0%, #0a0f1e 100%);
  padding: 18px 32px;
  padding-top: max(18px, env(safe-area-inset-top));
  border-bottom: 1px solid #1a2744;
  display: flex; align-items: center; gap: 16px;
  position: sticky; top: 0; z-index: 100;
}
header .logo { font-size: 2rem; }
header h1 { font-size: 1.4rem; font-weight: 700; letter-spacing: -0.3px; }
header h1 span { color: var(--accent2); }

/* TABS */
.tabs {
  display: flex;
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
  padding: 0 16px;
  gap: 4px;
  position: sticky;
  top: 60px;
  z-index: 99;
  overflow-x: auto;
  scrollbar-width: none;
}
.tabs::-webkit-scrollbar { display: none; }
.tab {
  padding: 14px 20px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--muted);
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  border-radius: 6px 6px 0 0;
}
.tab:hover { color: var(--text); background: rgba(255,255,255,0.04); }
.tab.active { color: var(--accent2); border-bottom-color: var(--accent2); }

/* LAYOUT */
.container { max-width: 920px; margin: 0 auto; padding: 28px 20px; }
.panel { display: none; }
.panel.active { display: block; }

/* CARDS */
.card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 20px;
}
.card-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--muted);
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* FORM */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.form-grid.cols3 { grid-template-columns: 1fr 1fr 1fr; }
.form-grid.cols4 { grid-template-columns: 1fr 1fr 160px 160px; }
@media(max-width:640px) {
  .form-grid, .form-grid.cols3, .form-grid.cols4 { grid-template-columns: 1fr; }
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
.form-group label { font-size: 0.72rem; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; }
.form-group input {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 14px;
  color: var(--text);
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  width: 100%;
  -webkit-appearance: none;
}
.form-group input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(59,130,246,0.12); }
.form-group input::placeholder { color: #374151; }

.btn-row { margin-top: 16px; }
.btn {
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: white;
  border: none;
  border-radius: 10px;
  padding: 13px 28px;
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.1s;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}
.btn:hover { opacity: 0.9; transform: translateY(-1px); }
.btn:active { transform: translateY(0); }

/* AUTOCOMPLETE */
.ac-wrap { position: relative; }
.ac-list {
  position: absolute;
  top: calc(100% + 4px);
  left: 0; right: 0;
  background: var(--bg3);
  border: 1px solid var(--accent);
  border-radius: 10px;
  z-index: 300;
  max-height: 230px;
  overflow-y: auto;
  display: none;
  box-shadow: 0 12px 32px rgba(0,0,0,0.5);
}
.ac-list div {
  padding: 10px 14px;
  cursor: pointer;
  font-size: 0.88rem;
  transition: background 0.12s;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.ac-list div:last-child { border-bottom: none; }
.ac-list div:hover { background: rgba(59,130,246,0.12); color: var(--accent2); }

/* TRAIN CARDS */
.train-list { display: flex; flex-direction: column; gap: 8px; }
.train-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: border-color 0.2s, transform 0.15s;
  cursor: default;
}
.train-card:hover { border-color: var(--accent); transform: translateX(2px); }
.train-badge {
  background: linear-gradient(135deg, #1a2744, #0d1f3c);
  border: 1px solid #2d4a7a;
  color: var(--accent2);
  padding: 8px 10px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.8rem;
  min-width: 76px;
  text-align: center;
  line-height: 1.3;
}
.train-info { flex: 1; min-width: 0; }
.train-dest { font-weight: 600; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.train-sub { font-size: 0.8rem; color: var(--muted); margin-top: 2px; }
.delay-ok { color: var(--green); font-size: 0.82rem; font-weight: 600; white-space: nowrap; }
.delay-late { color: var(--red); font-size: 0.82rem; font-weight: 600; white-space: nowrap; }
.delay-none { color: var(--muted); font-size: 0.82rem; }
.track-box {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 10px;
  text-align: center;
  min-width: 54px;
}
.track-box .track-num { font-weight: 700; font-size: 0.95rem; }
.track-box .track-lbl { font-size: 0.62rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }

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
.sbadge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.s-ok { background: rgba(34,197,94,0.15); color: var(--green); }
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
      <div class="form-grid cols4">
        <div class="form-group">
          <label>Stazione di partenza</label>
          <div class="ac-wrap">
            <input id="v-from" placeholder="Es. Bergamo" autocomplete="off">
            <div class="ac-list" id="ac-vf"></div>
            <input type="hidden" id="v-from-id">
          </div>
        </div>
        <div class="form-group">
          <label>Stazione di arrivo</label>
          <div class="ac-wrap">
            <input id="v-to" placeholder="Es. Milano Centrale" autocomplete="off">
            <div class="ac-list" id="ac-vt"></div>
            <input type="hidden" id="v-to-id">
          </div>
        </div>
        <div class="form-group">
          <label>Data</label>
          <input type="date" id="v-date">
        </div>
        <div class="form-group">
          <label>Ora partenza</label>
          <input type="time" id="v-time">
        </div>
      </div>
      <div class="btn-row">
        <button class="btn" onclick="cercaViaggio()">🔍 Cerca treni diretti</button>
        <button class="btn" style="background:linear-gradient(135deg,#059669,#0d9488);margin-left:10px" onclick="apriTrenitalia()">🌐 Cerca su Trenitalia (con cambi)</button>
      </div>
      <!-- Riquadro dati viaggio per Trenitalia -->
      <div id="trenitalia-box" style="display:none;margin-top:18px;background:#0d2b1f;border:1px solid #059669;border-radius:12px;padding:18px 22px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
          <span style="font-size:1.2rem">🌐</span>
          <span style="font-weight:700;color:#4ade80">Trenitalia si è aperto!</span>
          <button onclick="document.getElementById('trenitalia-box').style.display='none'" style="margin-left:auto;background:none;border:none;color:#64748b;cursor:pointer;font-size:1.1rem">✕</button>
        </div>
        <p id="tr-msg" style="font-size:0.85rem;color:#94a3b8;margin-bottom:14px">Copia questi dati nei campi del sito:</p>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px">
          <div style="background:#0f172a;border-radius:8px;padding:10px 14px;border:1px solid #334155">
            <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;margin-bottom:4px">Partenza</div>
            <div id="tr-from" style="font-weight:700;color:#f1f5f9;font-size:0.95rem"></div>
          </div>
          <div style="background:#0f172a;border-radius:8px;padding:10px 14px;border:1px solid #334155">
            <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;margin-bottom:4px">Arrivo</div>
            <div id="tr-to" style="font-weight:700;color:#f1f5f9;font-size:0.95rem"></div>
          </div>
          <div style="background:#0f172a;border-radius:8px;padding:10px 14px;border:1px solid #334155">
            <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;margin-bottom:4px">Data</div>
            <div id="tr-date" style="font-weight:700;color:#f1f5f9;font-size:0.95rem"></div>
          </div>
          <div style="background:#0f172a;border-radius:8px;padding:10px 14px;border:1px solid #334155">
            <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;margin-bottom:4px">Ora</div>
            <div id="tr-time" style="font-weight:700;color:#f1f5f9;font-size:0.95rem"></div>
          </div>
        </div>
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

// APRI TRENITALIA
function apriTrenitalia(auto) {
  const from = document.getElementById('v-from').value.trim();
  const to = document.getElementById('v-to').value.trim();
  const date = document.getElementById('v-date').value;
  const time = document.getElementById('v-time').value;
  if (!from || !to) return;
  let dateStr = date;
  if (date) {
    const [y,m,d] = date.split('-');
    dateStr = `${d}/${m}/${y}`;
  }
  // Mostra riquadro dati
  const box = document.getElementById('trenitalia-box');
  document.getElementById('tr-from').textContent = from;
  document.getElementById('tr-to').textContent = to;
  document.getElementById('tr-date').textContent = dateStr;
  document.getElementById('tr-time').textContent = time;
  // Messaggio diverso se automatico o manuale
  document.getElementById('tr-msg').textContent = auto
    ? '⚠️ Nessun treno diretto trovato. Apro lefrecce.it con i dati del tuo viaggio — compilali e cerca!'
    : 'Copia questi dati su lefrecce.it per trovare tutte le soluzioni con cambi:';
  box.style.display = 'block';
  window.open('https://www.lefrecce.it', '_blank');
}

// CERCA VIAGGIO
async function cercaViaggio() {
  const fromId = document.getElementById('v-from-id').value;
  const toId = document.getElementById('v-to-id').value;
  const date = document.getElementById('v-date').value;
  const time = document.getElementById('v-time').value;
  const res = document.getElementById('res-v');
  if (!fromId) { res.innerHTML = '<div class="error-box">⚠️ Seleziona la stazione di partenza dalla lista</div>'; return; }
  if (!toId) { res.innerHTML = '<div class="error-box">⚠️ Seleziona la stazione di arrivo dalla lista</div>'; return; }
  res.innerHTML = '<div class="loading">🔍 Ricerca soluzioni...</div>';
  try {
    const toNome = document.getElementById('v-to').value.trim();
    const fromNome = document.getElementById('v-from').value.trim();
    const r = await fetch(`/api/viaggio?from=${encodeURIComponent(fromId)}&to=${encodeURIComponent(toId)}&to-nome=${encodeURIComponent(toNome)}&from-nome=${encodeURIComponent(fromNome)}&date=${encodeURIComponent(date)}&time=${encodeURIComponent(time)}`);
    const data = await r.json();
    if (data.error) { res.innerHTML = `<div class="error-box">❌ ${data.error}</div>`; return; }
    if (!data.length) { res.innerHTML = '<div class="empty-box"><div class="ico">🔍</div>Nessuna soluzione trovata</div>'; return; }
    // Separa diretti da quelli con cambio
    const diretti = data.filter(t => t.soluzioneType === 'diretto');
    const conCambio = data.filter(t => t.soluzioneType === 'cambio');
    const mostraCambio = diretti.length === 0 && conCambio.length > 0;
    const lista = diretti.length > 0 ? diretti : data;

    const htmlTreno = t => {
      const durStr = t.durataMinuti ? fmtDur(t.durataMinuti) : '';
      const cambiStr = t.cambi > 0 ? `<span class="cambio-badge">🔄 ${t.cambi} cambio${t.cambi>1?'i':''}</span>` : '<span class="sbadge s-ok" style="font-size:0.72rem">Diretto</span>';
      return `
        <div class="train-card">
          <div class="train-badge">${t.categoria||''}<br>${t.numeroTreno||'–'}</div>
          <div class="train-info">
            <div class="train-dest">→ ${t.destinazione||'–'}</div>
            <div class="train-sub">
              Partenza: <b>${fmt(t.orarioPartenza)}</b>
              ${t.orarioArrivo ? `· Arrivo: <b>${fmt(t.orarioArrivo)}</b>` : ''}
              ${durStr ? `· ${durStr}` : ''}
            </div>
          </div>
          ${cambiStr}
          ${delayHtml(t.ritardo)}
          <div class="track-box"><div class="track-lbl">Bin.</div><div class="track-num">${t.binarioProgrammatoPartenzaDescrizione||'–'}</div></div>
        </div>`;
    };

    res.innerHTML = `
      ${diretti.length > 0 ? `<div class="section-label" style="margin-bottom:8px">✅ Treni diretti (${diretti.length})</div>` : ''}
      <div class="train-list">${lista.map(htmlTreno).join('')}</div>
      ${mostraCambio ? `<div style="margin-top:6px;padding:10px 14px;background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);border-radius:10px;font-size:0.83rem;color:#fbbf24">⚠️ Nessun treno diretto trovato — mostrate soluzioni con cambio</div>` : ''}
    `;
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
    res.innerHTML = `<div class="train-list">${data.slice(0,25).map(t => `
      <div class="train-card">
        <div class="train-badge">${t.categoria||''}<br>${t.numeroTreno}</div>
        <div class="train-info">
          <div class="train-dest">→ ${t.destinazione||'–'}</div>
          <div class="train-sub">Partenza: <b>${fmt(t.orarioPartenza)}</b></div>
        </div>
        ${delayHtml(t.ritardo)}
        <div class="track-box"><div class="track-lbl">Bin.</div><div class="track-num">${t.binarioProgrammatoPartenzaDescrizione||'–'}</div></div>
      </div>`).join('')}</div>`;
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
    res.innerHTML = `<div class="train-list">${data.slice(0,25).map(t => `
      <div class="train-card">
        <div class="train-badge">${t.categoria||''}<br>${t.numeroTreno}</div>
        <div class="train-info">
          <div class="train-dest">← Da ${t.origine||'–'}</div>
          <div class="train-sub">Arrivo: <b>${fmt(t.orarioArrivo)}</b></div>
        </div>
        ${delayHtml(t.ritardo)}
        <div class="track-box"><div class="track-lbl">Bin.</div><div class="track-num">${t.binarioProgrammatoArrivoDescrizione||'–'}</div></div>
      </div>`).join('')}</div>`;
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
                ${f.ritardo?`<span class="${f.ritardo>0?'delay-late':'delay-ok'}">${f.ritardo>0?'+'+f.ritardo:'✓'}</span>`:''}
              </div>`).join('')}
          </div>`:''}
      </div>`;
  } catch(e) { res.innerHTML = '<div class="error-box">❌ Errore. Riprova.</div>'; }
}
</script>
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(reg => console.log('SW registrato'))
      .catch(err => console.log('SW errore:', err));
  });
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

        # Service Worker
        elif parsed.path == '/sw.js':
            sw_code = "const CACHE='gtreni-v1';self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(['/']))));self.addEventListener('fetch',e=>e.respondWith(fetch(e.request).catch(()=>caches.match(e.request))))); "
            sw = sw_code.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript')
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

            print(f"[DEBUG] from_id={from_id} to_nome={to_nome} from_nome={p('from-nome')} tutti={len(tutti)}", flush=True)

            if not tutti:
                send_json(self, [])
                return

            # Controlla se la dest. è nella destinazione finale (veloce, senza chiamate extra)
            keywords = [w for w in to_nome.split() if len(w) > 3]
            diretti_veloci = []
            da_controllare = []
            for t in tutti[:20]:
                dest = (t.get('destinazione') or '').upper()
                if any(k in dest for k in keywords) or to_nome in dest:
                    diretti_veloci.append(t)
                else:
                    da_controllare.append(t)

            print(f"[DEBUG] keywords={keywords} diretti_veloci={len(diretti_veloci)} da_controllare={len(da_controllare)}", flush=True)

            # Per i treni non diretti, controlla le fermate in parallelo
            def check_fermate(t):
                num = t.get('numeroTreno')
                cod_staz = t.get('codOrigine')  # formato S0XXXX richiesto da /fermate
                ts_ms = t.get('orarioPartenza')
                print(f"[DEBUG] check_fermate num={num} cod_staz={cod_staz} ts_ms={ts_ms}", flush=True)
                if not num or not ts_ms or not cod_staz:
                    print(f"[DEBUG] check_fermate SKIP: dati mancanti", flush=True)
                    return None
                fermate_data = api(f'/andamentoTreno/{cod_staz}/{num}/{ts_ms}')
                print(f"[DEBUG] fermate risposta tipo={type(fermate_data)} val={str(fermate_data)[:200]}", flush=True)
                # L'API può rispondere con stringa JSON o lista
                # andamentoTreno risponde con dict, le fermate sono in ['fermate']
                if isinstance(fermate_data, dict):
                    fermate_list = fermate_data.get('fermate', [])
                elif isinstance(fermate_data, list):
                    fermate_list = fermate_data
                else:
                    print(f"[DEBUG] fermate: risposta inattesa {type(fermate_data)}", flush=True)
                    return None
                if not fermate_list:
                    return None
                stazioni = [(f.get('stazione') or '').upper() for f in fermate_list]
                print(f"[DEBUG] stazioni={stazioni[:5]}", flush=True)
                orig_upper = (t.get('origine') or '').upper()
                orig_kw = [w for w in orig_upper.split() if len(w) > 3]
                # Trova indice stazione di partenza nel percorso
                idx_from = 0
                for i, nome in enumerate(stazioni):
                    if any(k in nome for k in orig_kw):
                        idx_from = i
                        break
                # Cerca destinazione dopo la partenza
                for f in fermate_list[idx_from:]:
                    nome_f = (f.get('stazione') or '').upper()
                    if any(k in nome_f for k in keywords):
                        t['orarioArrivoDestinazione'] = f.get('programmataArrivo') or f.get('effettivaArrivo')
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

            # Strategia 2: arrivi alla stazione di destinazione filtrati per origine
            # Questo cattura il caso in cui la partenza è una stazione intermedia
            to_id = p('to')
            from_nome = p('from-nome').upper().strip()
            from_kw = [w for w in from_nome.split() if len(w) > 3]
            arrivi_trovati = []
            if to_id and from_kw:
                seen_arr = set()
                for delta_h in [0, 2, 4]:
                    dt2 = base_dt + timedelta(hours=delta_h)
                    orario2 = build_orario(dt2.strftime('%H:%M'), dt2.strftime('%Y-%m-%d'))
                    arr = api(f'/arrivi/{to_id}/{urllib.parse.quote(orario2)}')
                    if arr and isinstance(arr, list):
                        for t in arr:
                            key = t.get('numeroTreno')
                            orig = (t.get('origine') or '').upper()
                            if key and key not in seen_arr:
                                if any(k in orig for k in from_kw) or from_nome in orig:
                                    seen_arr.add(key)
                                    arrivi_trovati.append(t)
                arrivi_trovati.sort(key=lambda t: t.get('orarioArrivo') or 0)

            # Unisci le due strategie, preferendo i risultati da partenze
            numeri_gia_trovati = {t.get('numeroTreno') for t in risultati}
            for t in arrivi_trovati:
                if t.get('numeroTreno') not in numeri_gia_trovati:
                    risultati.append(t)

            risultati.sort(key=lambda t: t.get('orarioPartenza') or t.get('orarioArrivo') or 0)

            if risultati:
                send_json(self, risultati[:15])
            else:
                send_json(self, {'error': 'Nessun treno diretto trovato tra queste stazioni. Usa il tasto Cerca su Trenitalia per soluzioni con cambio.'})

        # Stato treno
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
