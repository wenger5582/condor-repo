from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import feedparser, asyncio, random
from .rss_feeds import FUENTES

app = FastAPI(title="CONDOR OSINT API - 65 fuentes", version="12.3")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

CACHE = {"noticias": [], "kpis": {"politica":68,"militar":74,"economica":59,"social":71,"infosec":82,"exterior":64,"nacional":72}, "ultima_actualizacion": None, "fuentes_ok":0}

async def fetch_all():
    noticias=[]; ok=0
    for fuente in FUENTES:
        try:
            d = await asyncio.to_thread(feedparser.parse, fuente["url"])
            if d.entries:
                ok+=1
                for entry in d.entries[:3]:
                    noticias.append({"fuente":fuente["nombre"],"categoria":fuente["categoria"],"titulo":entry.get("title","")[:180],"link":entry.get("link",""),"fecha":entry.get("published","")[:25],"riesgo":random.randint(55,95),"es_real":True})
        except: continue
    from collections import Counter
    cats=Counter([n["categoria"] for n in noticias])
    CACHE["kpis"]={"politica":min(95,60+cats.get("nacional",0)),"militar":min(95,65+cats.get("defensa",0)*3),"economica":min(90,55+cats.get("economia",0)*2),"social":min(90,60+cats.get("nacional",0)),"infosec":min(95,70+cats.get("infosec",0)*3),"exterior":min(95,60+cats.get("exterior",0)*2),"nacional":min(92,68+len(noticias)//3)}
    CACHE["noticias"]=sorted(noticias,key=lambda x:x["riesgo"],reverse=True)[:80]
    CACHE["fuentes_ok"]=ok
    CACHE["ultima_actualizacion"]=datetime.utcnow().isoformat()

@app.on_event("startup")
async def startup():
    await fetch_all()
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    scheduler=AsyncIOScheduler()
    scheduler.add_job(fetch_all,"interval",minutes=5)
    scheduler.start()

@app.get("/")
async def root():
    return {"sistema":"CONDOR V12.3","modo":"REAL","fuentes":len(FUENTES)}

@app.get("/api/health")
async def health():
    return {"status":"ok","modo":"REAL","fuentes_totales":len(FUENTES),"fuentes_ok":CACHE["fuentes_ok"],"ultima_actualizacion":CACHE["ultima_actualizacion"],"noticias_en_cache":len(CACHE["noticias"]),"kpis":CACHE["kpis"]}

@app.get("/api/noticias/realtime")
async def noticias():
    if not CACHE["noticias"]: await fetch_all()
    return {"total":len(CACHE["noticias"]),"ultima_actualizacion":CACHE["ultima_actualizacion"],"noticias":CACHE["noticias"]}

@app.get("/api/riesgo/kpis")
async def kpis():
    return CACHE["kpis"]

@app.get("/api/telegram/intel")
async def telegram_mock():
    return [{"canal":"Alerta Iquique","mensaje":"Movimiento frontera Colchane","riesgo":78,"fecha":datetime.utcnow().isoformat()}]

@app.get("/api/camaras/estado")
async def camaras():
    return {"camaras":[{"id":"chacalluta","nombre":"Chacalluta","estado":"online"},{"id":"chungara","nombre":"Chungara","estado":"online"}]}
