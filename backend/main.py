from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime
import feedparser, asyncio, random, sys
print("Iniciando CONDOR V12.5...", file=sys.stderr)

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



CONDOR OSINT V12.5 ● REAL
25 fuentes RSS - Actualizacion cada 5 min - V12.5 FIX

Despertando servidor (free tarda 50s)... Unexpected token '<', "

0
NOTICIAS
0
FUENTES OK
--:--
ULTIMA

Cargando inteligencia real...


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
