# aitrabajo · Conteo de pasajeros

TP final de Inteligencia Aplicada. La meta es mostrar una puerta de bus en video, contar subidas y bajadas y reconstruir la ocupación a lo largo de un recorrido del Gran Asunción.

## Organización

Álvaro trabaja en `main` e integra la aplicación. Su compañero trabaja en `vision` y entrega el modelo, el conteo y la evaluación mediante pull requests a `main`. La planificación y el contrato entre ambas partes están en [el plan de entrega](docs/PLAN.md). La [consigna original](contexto.md) define la evaluación.

## Distribución prevista

Los módulos se incorporan al implementarlos. Este primer commit contiene la consigna y el plan.

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
