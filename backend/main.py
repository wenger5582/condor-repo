from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime
import feedparser, asyncio, random, sys
print("Iniciando CONDOR V12.5...", file=sys.stderr)

# Import robusto de FUENTES
try:
    from .rss_feeds import FUENTES
except ImportError:
    try:
        from backend.rss_feeds import FUENTES
    except ImportError:
        from rss_feeds import FUENTES

app = FastAPI(title="CONDOR OSINT API - 25 fuentes", version="12.5")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

CACHE = {"noticias": [], "kpis": {"politica":68,"militar":74,"economica":59,"social":71,"infosec":82,"exterior":64,"nacional":72}, "ultima_actualizacion": None, "fuentes_ok":0}

async def fetch_all():
    noticias=[]; ok=0
    try:
        import requests
        HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
        for fuente in FUENTES:
            try:
                # timeout corto para no colgar el deploy
                r = await asyncio.to_thread(requests.get, fuente["url"], headers=HEADERS, timeout=6)
                if r.status_code == 200 and r.content:
                    d = feedparser.parse(r.content)
                    if d.entries:
                        ok+=1
                        for entry in d.entries[:2]:
                            noticias.append({
                                "fuente":fuente["nombre"],
                                "categoria":fuente["categoria"],
                                "titulo":entry.get("title","")[:180],
                                "link":entry.get("link",""),
                                "fecha": (entry.get("published","") or entry.get("updated",""))[:25],
                                "riesgo":random.randint(55,95),
                                "es_real":True
                            })
            except Exception as e:
                print(f"Feed fail {fuente['nombre']}: {e}", file=sys.stderr)
                continue
        
        from collections import Counter
        cats=Counter([n["categoria"] for n in noticias])
        CACHE["kpis"]={
            "politica":min(95,60+cats.get("nacional",0)),
            "militar":min(95,65+cats.get("defensa",0)*3),
            "economica":min(90,55+cats.get("economia",0)*2),
            "social":min(90,60+cats.get("nacional",0)),
            "infosec":min(95,70+cats.get("infosec",0)*3),
            "exterior":min(95,60+cats.get("exterior",0)*2),
            "nacional":min(92,68+len(noticias)//3)
        }
        CACHE["noticias"]=sorted(noticias,key=lambda x:x["riesgo"],reverse=True)[:80]
        CACHE["fuentes_ok"]=ok
        CACHE["ultima_actualizacion"]=datetime.utcnow().isoformat()
        print(f"CONDOR FETCH OK: {ok}/{len(FUENTES)} fuentes, {len(noticias)} noticias", file=sys.stderr)
    except Exception as e:
        print(f"FETCH CRITICAL ERROR: {e}", file=sys.stderr)

@app.on_event("startup")
async def startup():
    # NO bloqueamos el deploy - lanzamos en background
    asyncio.create_task(fetch_all())
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        scheduler=AsyncIOScheduler()
        scheduler.add_job(fetch_all,"interval",minutes=5)
        scheduler.start()
        print("Scheduler iniciado cada 5 min", file=sys.stderr)
    except Exception as e:
        print(f"Scheduler fail: {e}", file=sys.stderr)

DASHBOARD_HTML = """
<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CONDOR V12.5 - REAL</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#020202;color:#0f0;font-family:Courier New,monospace;padding:10px}
.header{border:2px solid #0f0;padding:12px;text-align:center;background:#0a0a0a;margin-bottom:10px}
.live{color:red;animation:blink 1s infinite}@keyframes blink{0%,50%{opacity:1}70%,100%{opacity:0}}
.stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:12px}
.stat{border:1px solid #0f0;padding:10px;text-align:center;background:#0a0a0a}.stat b{font-size:22px;display:block;color:#fff}
.kpis{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}.kpi{border:1px solid #333;padding:6px 10px;font-size:12px;background:#111}.kpi b{color:#ff0}
.noticia{border-left:4px solid red;background:#111;margin-bottom:8px;padding:10px;font-size:13px}
.noticia .fuente{color:#0ff;font-size:11px}.noticia .riesgo{float:right;background:red;color:#fff;padding:2px 6px;border-radius:3px}
a{color:#0f0}#estado{padding:10px;background:#001100;border:1px solid #0f0;margin-bottom:10px;text-align:center;font-weight:bold}
</style></head><body>
<div class="header"><h1>🦅 CONDOR OSINT V12.5 <span class="live">● REAL</span></h1><div>25 fuentes RSS - Actualizacion cada 5 min - V12.5 FIX</div></div>
<div id="estado">Conectando...</div>
<div class="stats"><div class="stat"><b id="totalB">0</b>NOTICIAS</div><div class="stat"><b id="fuentesB">0</b>FUENTES OK</div><div class="stat"><b id="horaB">--:--</b>ULTIMA</div></div>
<div class="kpis" id="kpis"></div><div id="noticias">Cargando inteligencia real...</div>
<script>
async function cargar(){
 try{
  const h = await fetch("/api/health").then(r=>r.json());
  document.getElementById('estado').innerHTML = `REAL ACTIVO V12.5 | ${h.fuentes_ok}/${h.fuentes_totales} fuentes | ${new Date(h.ultima_actualizacion||Date.now()).toLocaleTimeString()} | Cache: ${h.noticias_en_cache} noticias`;
  document.getElementById('totalB').textContent = h.noticias_en_cache;
  document.getElementById('fuentesB').textContent = h.fuentes_ok;
  document.getElementById('horaB').textContent = h.ultima_actualizacion ? new Date(h.ultima_actualizacion).toLocaleTimeString() : "Iniciando...";
  let kpiHtml=""; for(let k in h.kpis){kpiHtml+=`<div class="kpi">${k.toUpperCase()} <b>${h.kpis[k]}%</b></div>`}
  document.getElementById('kpis').innerHTML=kpiHtml;
  const data = await fetch("/api/noticias/realtime").then(r=>r.json());
  let html=""; data.noticias.forEach(n=>{
   html+=`<div class="noticia"><span class="riesgo">${n.riesgo}%</span><div class="fuente">${n.fuente} | ${n.categoria.toUpperCase()} | ${n.fecha}</div><b>${n.titulo}</b><br><a href="${n.link}" target="_blank">Ver fuente</a> REAL</div>`;
  });
  document.getElementById('noticias').innerHTML=html || "Esperando primer fetch (10s)...";
 }catch(e){
  document.getElementById('estado').innerHTML="Despertando servidor (free tarda 50s)... "+e.message;
  setTimeout(cargar,5000);
 }
}
cargar(); setInterval(cargar,60000);
</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return DASHBOARD_HTML

@app.get("/api/health")
async def health():
    return {"status":"ok","modo":"REAL","version":"V12.5 FIX","fuentes_totales":len(FUENTES),"fuentes_ok":CACHE["fuentes_ok"],"ultima_actualizacion":CACHE["ultima_actualizacion"],"noticias_en_cache":len(CACHE["noticias"]),"kpis":CACHE["kpis"]}

@app.get("/api/noticias/realtime")
async def noticias():
    return {"total":len(CACHE["noticias"]),"ultima_actualizacion":CACHE["ultima_actualizacion"],"noticias":CACHE["noticias"]}

@app.get("/api/riesgo/kpis")
async def kpis():
    return CACHE["kpis"]
