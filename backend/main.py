rom fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime
import feedparser, asyncio, random, sys, time
print("CONDOR V14 ULTRA iniciando...", file=sys.stderr)

try:
    from .rss_feeds import FUENTES
except ImportError:
    try:
        from backend.rss_feeds import FUENTES
    except ImportError:
        from rss_feeds import FUENTES

app = FastAPI(title="CONDOR V14 ULTRA - FULL SPECTRUM", version="14.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

CACHE = {"noticias": [], "kpis": {"politica":68,"militar":74,"economica":59,"social":71,"infosec":82,"exterior":64,"nacional":72,"frontera":78}, "ultima_actualizacion": None, "fuentes_ok":0, "fuentes_detalle":[],"latencia_avg":0}

async def fetch_one_ultra(fuente):
    start=time.time()
    # Metodo 1: requests con headers reales
    try:
        import requests
        headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36","Accept":"application/rss+xml, application/xml, */*"}
        r=await asyncio.to_thread(requests.get, fuente["url"], headers=headers, timeout=12)
        if r.status_code==200 and len(r.content)>500:
            d=feedparser.parse(r.content)
            if d.entries:
                return d.entries, int((time.time()-start)*1000)
    except: pass
    # Metodo 2: httpx
    try:
        import httpx
        async with httpx.AsyncClient(follow_redirects=True, timeout=12, headers={"User-Agent":"Mozilla/5.0"}) as client:
            r=await client.get(fuente["url"])
            if r.status_code==200 and len(r.content)>500:
                d=feedparser.parse(r.content)
                if d.entries:
                    return d.entries, int((time.time()-start)*1000)
    except: pass
    # Metodo 3: feedparser directo
    try:
        d=await asyncio.to_thread(feedparser.parse, fuente["url"])
        if d.entries:
            return d.entries, int((time.time()-start)*1000)
    except: pass
    return [], 0

async def fetch_all_ultra():
    noticias=[]; ok=0; detalle=[]; latencias=[]
    print(f"V14 ULTRA fetch iniciando {len(FUENTES)} fuentes...", file=sys.stderr)
    for fuente in FUENTES:
        entries, lat = await fetch_one_ultra(fuente)
        if entries:
            ok+=1; latencias.append(lat)
            detalle.append({"nombre":fuente["nombre"],"categoria":fuente["categoria"],"estado":"ON","latencia":lat,"count":len(entries)})
            for entry in entries[:2]:
                cat=fuente["categoria"]
                # riesgo segun categoria
                base={"prensa":60,"defensa":80,"frontera":85,"riesgo":90,"economico":65,"internacional":70}.get(cat,65)
                noticias.append({
                    "fuente":fuente["nombre"],
                    "categoria":cat,
                    "titulo":entry.get("title","")[:220],
                    "link":entry.get("link",""),
                    "fecha": (entry.get("published","") or entry.get("updated",""))[:32],
                    "riesgo": min(99, base + random.randint(-5,15)),
                    "impacto": round(random.uniform(0.55,0.97),2),
                    "es_real":True,
                    "latencia":lat
                })
        else:
            detalle.append({"nombre":fuente["nombre"],"categoria":fuente["categoria"],"estado":"OFF","latencia":0,"count":0})
    from collections import Counter
    cats=Counter([n["categoria"] for n in noticias])
    # KPIs V14 con frontera
    CACHE["kpis"]={
        "politica":min(95,60+cats.get("prensa",0)*2),
        "militar":min(96,65+cats.get("defensa",0)*3),
        "economica":min(92,55+cats.get("economico",0)*2),
        "frontera":min(98,70+cats.get("frontera",0)*3),
        "riesgo":min(96,75+cats.get("riesgo",0)*2),
        "infosec":min(90,65+cats.get("riesgo",0)),
        "exterior":min(94,60+cats.get("internacional",0)*2),
        "nacional":min(93,68+len(noticias)//3)
    }
    CACHE["noticias"]=sorted(noticias,key=lambda x:x["riesgo"],reverse=True)[:120]
    CACHE["fuentes_ok"]=ok
    CACHE["fuentes_detalle"]=detalle
    CACHE["latencia_avg"]= int(sum(latencias)/len(latencias)) if latencias else 0
    CACHE["ultima_actualizacion"]=datetime.utcnow().isoformat()
    print(f"V14 ULTRA OK: {ok}/{len(FUENTES)} fuentes, {len(noticias)} noticias, lat {CACHE['latencia_avg']}ms", file=sys.stderr)

@app.on_event("startup")
async def startup():
    asyncio.create_task(fetch_all_ultra())
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        s=AsyncIOScheduler(); s.add_job(fetch_all_ultra,"interval",minutes=2); s.start()
        print("V14 Scheduler 2min", file=sys.stderr)
    except Exception as e:
        print(f"Scheduler fail {e}", file=sys.stderr)

# Dashboard simple V14 fallback
HTML_V14 = """

🦅 CONDOR V14 ULTRA - FULL SPECTRUM
35 fuentes anti-bloqueo - Triple fetcher - 2min refresh

Despertando V14 (50s)... Unexpected token '<', "

0
NOTICIAS
0
FUENTES
0
LAT MS
--:--
HORA


"""

@app.get("/", response_class=HTMLResponse)
async def dashboard(): return HTML_V14

@app.get("/api/health")
async def health(): return {"status":"ok","modo":"V14 ULTRA","version":"14.0","fuentes_totales":len(FUENTES),"fuentes_ok":CACHE["fuentes_ok"],"ultima_actualizacion":CACHE["ultima_actualizacion"],"noticias_en_cache":len(CACHE["noticias"]),"kpis":CACHE["kpis"],"latencia_avg":CACHE["latencia_avg"]}

@app.get("/api/noticias/realtime")
async def noticias(): return {"total":len(CACHE["noticias"]),"ultima_actualizacion":CACHE["ultima_actualizacion"],"noticias":CACHE["noticias"]}

@app.get("/api/matriz")
async def matriz(): return {"fuentes":CACHE["fuentes_detalle"],"latencia_avg":CACHE["latencia_avg"],"ok":CACHE["fuentes_ok"],"total":len(FUENTES)}

@app.get("/api/radar")
async def radar(): return {"kpis":CACHE["kpis"],"riesgo_nac": round(sum(CACHE["kpis"].values())/len(CACHE["kpis"])/10,1) if CACHE["kpis"] else 6.5}

@app.get("/api/riesgo/kpis")
async def kpis(): return CACHE["kpis"]
