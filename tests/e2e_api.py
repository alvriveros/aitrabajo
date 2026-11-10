import json, time, urllib.request as u
A = "http://127.0.0.1:8000"
def req(ruta, metodo="GET", datos=None, js=None):
    h = {}
    if js is not None: datos, h = json.dumps(js).encode(), {"Content-Type": "application/json"}
    try:
        with u.urlopen(u.Request(A + ruta, data=datos, headers=h, method=metodo), timeout=60) as r: return r.status, json.loads(r.read())
    except u.HTTPError as e: return e.code, json.loads(e.read())
s, info = req("/videos?nombre=prueba-bus.mp4", "POST", open("data/raw/prueba-bus.mp4", "rb").read())
print("subida", s, info["id"], info["ancho"], info["alto"], info["fps"], info["duracion_s"])
geo = {"recorte": [0, 0, 768, 432], "linea": [274, 431, 467, 242], "interior": "arriba", "parada": "Puerta", "capacidad": 30, "carga_inicial": 20}
t0 = time.time(); s, r = req(f"/videos/{info['id']}/procesamientos", "POST", js=geo); print("inicio", s, r, f"{time.time()-t0:.2f}s")
id_ = r["id"]
print("doble clic", req(f"/videos/{info['id']}/procesamientos", "POST", js=geo)[0], "actual", req("/procesamientos/actual")[1])
vistos = []
while True:
    e = req(f"/procesamientos/{id_}/estado")[1]
    p = e["progreso"] or {}
    if p:
        ev = sorted(p["eventos"], key=lambda x: x["tiempo_s"])
        oc = req("/ocupacion", "POST", js={"capacidad": 30, "carga_inicial": 20, "paradas": [{"nombre": "Puerta", "inicio_s": 0}], "eventos": ev})[1]["paradas"][-1]
        vistos.append((round(time.time()-t0, 1), p["tiempo_video_s"], len(ev), oc["pasajeros"], oc["ocupacion_pct"]))
    if e["estado"] != "en_curso": break
    time.sleep(2)
print("estado final", e["estado"], e["detalle"])
for v in vistos[::3]: print("  t=%5.1fs video=%5.2fs eventos=%2d pasajeros=%d ocupacion=%s%%" % v)
print("listado", req(f"/procesamientos?video={info['id']}")[1])
c = req(f"/procesamientos/{id_}")[1]
print("eventos finales", len(c["recorrido"]["eventos"]), "medicion", c["configuracion"]["medicion"]["fps_procesados"], c["configuracion"]["medicion"]["latencia_ms"])
print("repetir sin pedirlo", req(f"/videos/{info['id']}/procesamientos", "POST", js=geo))
# cancelación
s, r = req(f"/videos/{info['id']}/procesamientos", "POST", js={**geo, "repetir_para_demostracion": True}); id2 = r["id"]
time.sleep(8); print("cancelar", req(f"/procesamientos/{id2}/cancelar", "POST"))
while req(f"/procesamientos/{id2}/estado")[1]["estado"] == "en_curso": time.sleep(1)
print("tras cancelar", req(f"/procesamientos/{id2}/estado")[1]["estado"], "publicado:", id2 in req(f"/procesamientos?video={info['id']}")[1])
