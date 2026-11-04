# aitrabajo · Conteo de pasajeros

TP final de Inteligencia Aplicada. La meta es mostrar una puerta de bus en video, contar subidas y bajadas y reconstruir la ocupación a lo largo de un recorrido del Gran Asunción.

## Organización

Álvaro trabaja en `main` e integra la aplicación. Su compañero trabaja en `vision` y entrega el modelo, el conteo y la evaluación mediante pull requests a `main`. La planificación y el contrato entre ambas partes están en [el plan de entrega](docs/PLAN.md). La [consigna original](contexto.md) define la evaluación.

## Ejecutar el prototipo del miércoles

Desde la raíz, en PowerShell con Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000
```

En otra terminal en la misma carpeta:

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui/app.py
```

Abrí el panel en http://localhost:8501 y mové el selector de tiempo. Con los valores iniciales, en el segundo 0 hay 3 pasajeros, en el 5 hay 5 y en el 10 quedan 4 (20 %). La API documenta el contrato en http://localhost:8000/docs. Para continuar el trabajo con Claude, empezá por [resumen.md](resumen.md).

## Distribución prevista

Ya están implementados la API de ocupación y el panel con eventos simulados. Los módulos de visión, evaluación y despliegue se incorporan en las siguientes etapas.

```text
api/main.py                   API de procesamiento y consulta (Álvaro)
ui/app.py                     Panel de video y ocupación por parada (Álvaro)
vision/pipeline.py            Detección, seguimiento y eventos de cruce (compañero)
vision/train.py               Ajuste reproducible del detector (compañero)
data/README.md                Origen, permisos, particiones y acceso a clips
data/annotations/             Cajas para entrenamiento y cruces manuales para evaluación
evaluation/evaluate.py        Comparación con conteo manual, métricas y tiempos
evaluation/results/           Resultados reproducibles y figura para el informe
docs/PLAN.md                  Calendario, responsables y criterios de cierre
docs/informe/                 Fuente IEEE, referencias y PDF final
docs/demo/                    Guion, configuración del recorrido y respaldo
requirements.txt              Versiones usadas por el equipo
Dockerfile                    Entorno común de API y panel
docker-compose.yml            Arranque de ambos servicios
```
