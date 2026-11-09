"""Anotador manual de cruces para la prueba final: mirás el video y marcás cada cruce con una tecla.

Uso, desde la raíz del worktree:  python docs/relevo/2026-11-08-claude-tarea11/anotar_cruces.py
Teclas:  espacio pausa/sigue · S subida · B bajada · Z deshace el último · A / D retrocede / avanza 2 s
         , / . un cuadro atrás / adelante (en pausa) · + / - velocidad · G guarda y sale · Q o Esc sale sin guardar
"""
import json
from datetime import datetime
from pathlib import Path

import cv2

VIDEO = "data/raw/youtube-bus-real-0y08Jtqtkys.mp4"
SALIDA = Path("data/annotations/youtube-bus-real-cruces.json")
LINEA_Y = 20 + 290  # recorte 0,20,586,420 y línea y=290 del recorte (prerregistro-final.md)

captura = cv2.VideoCapture(VIDEO)
fps = captura.get(cv2.CAP_PROP_FPS)
total = int(captura.get(cv2.CAP_PROP_FRAME_COUNT))
eventos, cuadro, pausa, velocidad = [], 0, False, 1.0
if SALIDA.exists():  # continuar una anotación anterior
    eventos = json.loads(SALIDA.read_text(encoding="utf-8"))["eventos"]


def ir(n):
    global cuadro
    cuadro = max(0, min(total - 1, n))
    captura.set(cv2.CAP_PROP_POS_FRAMES, cuadro)


ir(0)
ok, imagen = captura.read()
while True:
    vista = imagen.copy()
    cv2.line(vista, (0, LINEA_Y), (vista.shape[1], LINEA_Y), (0, 0, 255), 1)
    subidas = sum(e["sentido"] == "subida" for e in eventos)
    texto = f"{cuadro / fps:6.1f} s  x{velocidad:g}  subidas {subidas}  bajadas {len(eventos) - subidas}" + ("  [PAUSA]" if pausa else "")
    cv2.putText(vista, texto, (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
    cv2.imshow("anotar cruces (S subida, B bajada, G guarda)", vista)
    tecla = cv2.waitKey(0 if pausa else max(1, int(1000 / fps / velocidad))) & 0xFF
    if tecla in (ord("s"), ord("b")):
        eventos.append({"tiempo_s": round(cuadro / fps, 2), "track_id": len(eventos) + 1,
                        "sentido": "subida" if tecla == ord("s") else "bajada"})
    elif tecla == ord("z") and eventos:
        eventos.pop()
    elif tecla == ord(" "):
        pausa = not pausa
    elif tecla in (ord("a"), ord("d")):
        ir(cuadro + int((2 if tecla == ord("d") else -2) * fps) - 1)
    elif tecla == ord(","):
        ir(cuadro - 2)
    elif tecla == ord("+"):
        velocidad = min(8.0, velocidad * 2)
    elif tecla == ord("-"):
        velocidad = max(0.25, velocidad / 2)
    elif tecla == ord("g"):
        eventos.sort(key=lambda e: e["tiempo_s"])
        SALIDA.write_text(json.dumps({
            "capacidad": 60, "carga_inicial": 0,
            "paradas": [{"nombre": "Puerta de bus real (YouTube 0y08Jtqtkys)", "inicio_s": 0}],
            "anotado_por": "Álvaro, a mano con anotar_cruces.py, antes de ejecutar modelos sobre este video.",
            "fecha": datetime.now().astimezone().isoformat(timespec="minutes"),
            "criterio": "Cruce de la línea y=290 del recorte 0,20,586,420 por el centro del torso (prerregistro-final.md).",
            "notas": [], "eventos": eventos}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Guardado {SALIDA}: {len(eventos)} cruces.")
        break
    elif tecla in (ord("q"), 27):
        break
    if not pausa or tecla in (ord("a"), ord("d"), ord(","), ord(".")):
        ok, imagen = captura.read()
        if not ok:  # fin del video: queda en pausa en el último cuadro
            ir(total - 1); ok, imagen = captura.read(); pausa = True
        cuadro = int(captura.get(cv2.CAP_PROP_POS_FRAMES)) - 1
cv2.destroyAllWindows()
