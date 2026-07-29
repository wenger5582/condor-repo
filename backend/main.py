from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime
import feedparser, asyncio, random, sys
print("CONDOR V12.6 TURBO iniciando...", file=sys.stderr)

try:
    from .rss_feeds import FUENTES
except ImportError:
    try:
        from backend.rss_feeds import FUENTES
    except ImportError:
        from rss_feeds import FUENTES

app = FastAPI(title="CONDOR V12.6 TURBO", version="12.6")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

CACHE = {"noticias": [], "kpis": {"politica":68,"militar":74,"economica":59,"social":71,"infosec":82,"exterior":64,"nacional":72}, "ultima_actualizacion": None, "fuentes_ok":0, "debug":[]}

async def fetch_one(fuente):
    for metodo in ["requests","httpx","direct"]:
        try:
            if metodo == "requests":
                import requests
                HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"}
                r = await asyncio.to_thread(requests.get, fuente["url"], headers=HEADERS, timeout=8)
                if r.status_code == 200:
                    d = feedparser.parse(r.content)
                    if d.entries: return d.entries
            elif metodo == "httpx":
                import httpx
                async with httpx.AsyncClient(follow_redirects=True, timeout=8) as client:
                    r = await client.get(fuente["url"], headers={"User-Agent": "Mozilla/5.0"})
                    if r.status_code == 200:
                        d = feedparser.parse(r.content)
                        if d.entries: return d.entries
            else:
                d = await asyncio.to_thread(feedparser.parse, fuente["url"])
                if d.entries: return d.entries
        except Exception as e:
            continue
    return []

async def fetch_all():
    noticias=[]; ok=0; debug=[]
    for fuente in FUENTES:
        try:
            entries = await fetch_one(fuente)
            if entries:
                ok+=1
                for entry in entries[:3]:
                    noticias.append({
                        "fuente":fuente["nombre"],
                        "categoria":fuente["categoria"],
                        "titulo":entry.get("title","")[:200],
                        "link":entry.get("link",""),
                        "fecha": (entry.get("published","") or entry.get("updated",""))[:30],
                        "riesgo":random.randint(55,98),
                        "es_real":True
                    })
                debug.append(f"OK {fuente['nombre']}: {len(entries)}")
            else:
                debug.append(f"FAIL {fuente['nombre']}")
        except Exception as e:
            debug.append(f"ERR {fuente['nombre']}: {str(e)[:50]}")
    from collections import Counter
    cats=Counter([n["categoria"] for n in noticias])
    CACHE["kpis"]={
        "politica":min(95,60+cats.get("nacional",0)*2),
        "militar":min(95,65+cats.get("defensa",0)*4),
        "economica":min(90,55+cats.get("economia",0)*3),
        "social":min(90,60+cats.get("nacional",0)),
        "infosec":min(95,70+cats.get("infosec",0)*4),
        "exterior":min(95,60+cats.get("exterior",0)*2),
        "nacional":min(92,68+len(noticias)//2)
    }
    CACHE["noticias"]=sorted(noticias,key=lambda x:x["riesgo"],reverse=True)[:100]
    CACHE["fuentes_ok"]=ok
    CACHE["ultima_actualizacion"]=datetime.utcnow().isoformat()
    CACHE["debug"]=debug[-20:]
    print(f"V12.6 TURBO: {ok}/{len(FUENTES)} fuentes, {len(noticias)} noticias", file=sys.stderr)

@app.on_event("startup")
async def startup():
    asyncio.create_task(fetch_all())
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        s=AsyncIOScheduler(); s.add_job(fetch_all,"interval",minutes=3); s.start()
    except Exception as e:
        print(f"Scheduler fail {e}", file=sys.stderr)

HTML = """
Cargando inteligencia TURBO...

"""
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return HTML

@app.get("/api/health")
async def health():
    return {"status":"ok","modo":"REAL TURBO","version":"V12.6","fuentes_totales":len(FUENTES),"fuentes_ok":CACHE["fuentes_ok"],"ultima_actualizacion":CACHE["ultima_actualizacion"],"noticias_en_cache":len(CACHE["noticias"]),"kpis":CACHE["kpis"],"debug":CACHE["debug"]}

@app.get("/api/noticias/realtime")
async def noticias():
    return {"total":len(CACHE["noticias"]),"ultima_actualizacion":CACHE["ultima_actualizacion"],"noticias":CACHE["noticias"]}

@app.get("/api/riesgo/kpis")
async def kpis():
    return CACHE["kpis"]

@app.get("/api/debug")
async def debug():
    return {"debug":CACHE["debug"],"fuentes":len(FUENTES)}
