# Checklist del ensayo final (10 + 2 minutos)

**Estado: SIN REALIZAR.** Lo completa el equipo; no se marca como hecho hasta que el equipo lo confirme.
Guion: [`guion.md`](guion.md). Rama: `cierre-final`.

## Verificado por Claude (9 nov., 01:20)

- [x] **Insumos con el hash esperado:**
  - `yolo11n.pt` (`0ebbc80d…`);
  - `data/raw/prueba-bus.mp4` (`0b4b8c97…`);
  - `data/raw/oficina.mp4` (`02666c2e…`).
- [x] **Entorno:** existe `.venv\Scripts\python.exe`, y `prueba-bus` ya está subido (`runs/videos/0b4b8c97940c5f75`).
- [x] **Prueba de punta a punta por HTTP con el código final** (Linux, CPU, `runs/` separado):
  - 24 eventos, igual que la primera evaluación;
  - la latencia no crece;
  - un segundo pedido recibe 409;
  - la cancelación no publica.
- [x] **Primera evaluación intacta:** `runs/panel/20261108-200805-374934` no se tocó.

## Antes del ensayo (equipo)

- [ ] Docker detenido (`docker compose down`), para que no compita por CPU.
- [ ] API con GPU, en la ventana 1:
  ```powershell
  cd C:\Users\Alvaro\Desktop\Facultad\4to\IA\TpFinal\.worktrees\integracion-video
  $env:VISION_DISPOSITIVO = "cuda:0"
  C:\Users\Alvaro\Desktop\Facultad\4to\IA\venv-gpu\Scripts\python.exe -m uvicorn api.main:app --port 8000
  ```
- [ ] Panel, en la ventana 2: `.\.venv\Scripts\python.exe -m streamlit run ui/app.py` → http://localhost:8501.
- [ ] Abiertos: el informe (`docs/informe/informe.pdf`, Tablas II y III) y el guion.
- [ ] Notebook enchufada y en máximo rendimiento.

## Ensayo cronometrado (equipo)

| Bloque | Tiempo previsto | Tiempo real | ¿Salió bien? | Nota |
|---|---|---|---|---|
| Problema y objetivo + línea de 8 paradas | 0:00–1:30 | | [ ] | |
| Arquitectura (Fig. 1) | 1:30–3:00 | | [ ] | |
| Demo en vivo: subir, geometría, ritmo real, «Reprocesar en vivo» | 3:00–6:30 | | [ ] | Mirar FPS ≈ 25 y descartados ≈ 0 |
| Resultados históricos (Tablas II y III), presentados como históricos | 6:30–9:00 | | [ ] | |
| Conclusiones: prototipo con limitaciones medidas | 9:00–10:00 | | [ ] | |
| Preguntas (2 min), con las respuestas del guion | 10:00–12:00 | | [ ] | |

- [ ] Total ≤ 10:00 sin preguntas. Tiempo medido: ______
- [ ] El respaldo (resultado guardado) se presentó como «resultado guardado, no inferencia en vivo».
- [ ] Se dijo explícitamente que las oclusiones no están resueltas y que no se consiguieron grabaciones de buses de Paraguay.
- [ ] Ninguna captura de `prueba-bus` en las diapositivas: la licencia de iStock no está verificada.

**Confirmación del equipo:** ______________________ (fecha, hora y nombres)
