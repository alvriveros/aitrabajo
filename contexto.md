# Catálogo de Proyectos de Inteligencia Aplicada (4to Año - Ingeniería Informática)

## Directivas Generales de Evaluación y Alcance (2 Meses)

Cada proyecto está concebido para realizarse en parejas durante 8 semanas. Para garantizar el nivel de ingeniería propio del final de la carrera, los estudiantes deben cumplir con el siguiente estándar de entrega:

1. **Investigación e Ingesta:** Obtención o construcción del conjunto de datos (dataset) relevante para el entorno local.
2. **Desarrollo del Modelo:** Algoritmos supervisados, no supervisados o modelos generativos con métricas claras de evaluación (accuracy, f1-score, RMSE, mAP, etc.).
3. **Servicio y API:** Exposición del modelo entrenado a través de una API REST funcional (ej. FastAPI, Flask).
4. **Interfaz Tangible:** Aplicación web o móvil mínima (ej. Streamlit, Gradio, React, Flutter) donde el usuario final pueda interactuar con el sistema.
5. **Contenedorización:** Empaquetado de la solución en contenedores Docker.
6. **Código en git:** Control de versiones con historias y commits descriptivos.

El proyecto práctico se desarrollará en parejas durante un período estricto de 8 semanas. Los estudiantes deben encarar el proyecto con un enfoque de ingeniería de software de extremo a extremo (End-to-End ML/AI System).

---

## Entregables Obligatorios

### 1. Repositorio de Código y Sistema Operativo
* **Dataset:** Conjunto de datos limpio y documentado (preferentemente adaptado al contexto paraguayo).
* **Modelo Entrenado:** Algoritmo supervisado, no supervisado o generativo con métricas formales de desempeño.
* **API REST:** Exposición del modelo mediante FastAPI, Flask o similar.
* **Interfaz de Usuario (UI):** Aplicación interactiva (Streamlit, Gradio, React, Angular, Vuejs, Flutter, o la que manejen) para pruebas en tiempo real.
* **Contenedorización (Puntos extras):** Archivo `Dockerfile` y `docker-compose.yml` listos para desplegar la solución completa con un solo comando.

### 2. Informe Científico (Formato IEEE)
* **Formato:** Plantilla oficial IEEE de dos columnas.
* **Extensión Máxima:** Exactamente 3 páginas.
* **Estructura Requerida:**
  * **Resumen (Abstract):** Descripción sintética del problema, método y principales hallazgos (máx. 150 palabras).
  * **I. Introducción y Contexto:** Justificación de la problemática (enfocada en Paraguay) y estado del arte breve.
  * **II. Metodología y Arquitectura del Sistema:** Descripción del pipeline de datos, preprocesamiento, selección/entrenamiento del modelo y diseño de la API/UI.
  * **III. Resultados y Discusión:** Métricas obtenidas (Accuracy, f1-score, RMSE, mAP, matrices de confusión, tiempos de inferencia, entre otros) presentadas en tablas/gráficos.
  * **IV. Conclusiones y Trabajo Futuro:** Lecciones aprendidas, limitaciones del sistema e ideas de mejora.
  * **Referencias:** Citas en formato IEEE.

### 3. Defensa Oral y Demostración en Vivo
* **Exposición:** 10 minutos por grupo + 2 minutos de preguntas del tribunal/profesor.
* **Obligatoriedad:** Realizar una demostración en vivo (Live Demo) del sistema funcionando.

> **Puntuación Final:**
> [Desarrollo Técnico e Ingeniería: **30 pts**] + [Defensa Oral y Demo: **50 pts**] + [Informe IEEE: **20 pts**] = **100 pts**

---

## Proyecto 10: Estimación de Ocupación y Conteo de Pasajeros en el Transporte Público

* **Contexto local:** La calidad del servicio de buses en el Gran Asunción requiere auditar las frecuencias y el nivel de hacinamiento de las unidades.
* **Objetivo:** Contar el ingreso/egreso de personas en las puertas del bus y calcular el porcentaje de ocupación en tiempo real.
* **Desafío técnico e investigación:** Algoritmos de seguimiento de objetos en movimiento (DeepSORT o ByteTrack) cruzando una "línea virtual" de conteo. Superar oclusiones cuando varias personas suben al mismo tiempo.
* **Entregable:** Módulo de visualización simulado para una empresa de transporte que reporte la carga de pasajeros a lo largo del recorrido.