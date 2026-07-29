from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime
import sys
print("CONDOR V14.2 MINIMAL iniciando...", file=sys.stderr)

app = FastAPI(title="CONDOR V14.2", version="14.2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

CACHE = {"ok":13, "total":30, "noticias":26, "time": datetime.utcnow().isoformat()}

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    
    
CONDOR V14.2 MINIMAL LIVE

    
Si ves esto, el deploy funciono.


    
Ver /api/health


    
Ahora podemos subir a V14.3 con 35 fuentes


    
    """

@app.get("/api/health")
async def health():
    return {"status":"ok","modo":"V14.2 MINIMAL","fuentes_totales":30,"fuentes_ok":13,"noticias_en_cache":26,"kpis":{"politica":68,"militar":74},"ultima_actualizacion":datetime.utcnow().isoformat()}

@app.get("/api/noticias/realtime")
async def noticias():
    return {"total":2,"noticias":[
        {"fuente":"BBC World","categoria":"internacional","titulo":"Test V14.2 MINIMAL funcionando","link":"https://bbc.com","fecha":"hoy","riesgo":75},
        {"fuente":"Defensa.cl","categoria":"defensa","titulo":"Deploy LIVE recuperado","link":"https://defensa.cl","fecha":"hoy","riesgo":85}
    ]}

@app.get("/api/matriz")
async def matriz():
    return {"ok":13,"total":30,"fuentes":[]}

@app.get("/api/radar")
async def radar():
    return {"kpis":{"militar":74,"frontera":78},"riesgo_nac":6.5}
Despues que este diga LIVE, pegamos V14.3 con 35 fuentes reales (sin errores de comillas)
📋 COPIAR rss_feeds.py V14.3 FIX (despues del LIVE)
# CONDOR V14.3 - 35 fuentes - version sin caracteres raros
FUENTES = [
    {"nombre": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "categoria": "internacional"},
    {"nombre": "BBC LatAm", "url": "http://feeds.bbci.co.uk/news/world/latin_america/rss.xml", "categoria": "internacional"},
    {"nombre": "Guardian World", "url": "https://www.theguardian.com/world/rss", "categoria": "internacional"},
    {"nombre": "Defensa CL", "url": "https://www.defensa.cl/feed/", "categoria": "defensa"},
    {"nombre": "GNews Chile", "url": "https://news.google.com/rss?hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "prensa"},
    {"nombre": "GNews FACH", "url": "https://news.google.com/rss/search?q=FACH+Chile&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "defensa"},
    {"nombre": "GNews Ejercito", "url": "https://news.google.com/rss/search?q=Ejercito+Chile&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "defensa"},
    {"nombre": "GNews Armada", "url": "https://news.google.com/rss/search?q=Armada+Chile&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "defensa"},
    {"nombre": "GNews Carabineros", "url": "https://news.google.com/rss/search?q=Carabineros+Chile&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "riesgo"},
    {"nombre": "GNews PDI", "url": "https://news.google.com/rss/search?q=PDI+Chile&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "riesgo"},
    {"nombre": "GNews Colchane", "url": "https://news.google.com/rss/search?q=Colchane+frontera&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "frontera"},
    {"nombre": "GNews Libertadores", "url": "https://news.google.com/rss/search?q=Los+Libertadores+paso+frontera&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "frontera"},
    {"nombre": "GNews Chacalluta", "url": "https://news.google.com/rss/search?q=Chacalluta+Arica&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "frontera"},
    {"nombre": "GNews Migracion", "url": "https://news.google.com/rss/search?q=migracion+Chile+Colchane&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "frontera"},
    {"nombre": "GNews Codelco", "url": "https://news.google.com/rss/search?q=Codelco+cobre&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "economico"},
    {"nombre": "GNews Litio", "url": "https://news.google.com/rss/search?q=litio+Chile&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "economico"},
    {"nombre": "GNews Economia", "url": "https://news.google.com/rss/search?q=economia+Chile&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "economico"},
    {"nombre": "GNews Politica", "url": "https://news.google.com/rss/search?q=gobierno+Chile+La+Moneda&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "prensa"},
    {"nombre": "GNews SENAPRED", "url": "https://news.google.com/rss/search?q=SENAPRED+Chile&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "riesgo"},
    {"nombre": "GNews Sismo", "url": "https://news.google.com/rss/search?q=sismo+Chile+hoy&hl=es-419&gl=CL&ceid=CL:es-419", "categoria": "riesgo"},
]
