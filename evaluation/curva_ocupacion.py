"""Cambio acumulado de pasajeros a bordo: referencia frente a estimación, en una grilla de 0,1 s.

Se ejecuta desde la raíz: python -m evaluation.curva_ocupacion

No ejecuta el modelo: lee la referencia humana y las predicciones originales ya guardadas.
Como no se conoce la carga inicial real, compara el cambio acumulado desde el inicio (subidas − bajadas),
no la ocupación absoluta. Los valores negativos predichos se conservan.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

REFERENCIA = Path("data/annotations/prueba-bus-cruces.json")
# Copia versionada de la primera evaluación ciega (CPU de Windows, runs/panel/20261108-200805-374934).
EJECUCION = Path("docs/relevo/2026-11-08-claude-tarea13/primera-evaluacion")
DESTINO_JSON = Path("docs/informe/ocupacion-prueba-bus.json")
DESTINO_PNG = Path("docs/informe/fig-ocupacion.png")
PASO_CS = 10  # 0,1 s en centésimas: enteros para no depender del redondeo de punto flotante


def _cs(segundos: float) -> int:
    return round(segundos * 100)


def cambio_acumulado(eventos: list[dict], fin_s: float) -> list[int]:
    """Valor en cada instante k·0,1 s (0 ≤ t ≤ fin_s), contando cada evento desde su instante."""
    signo = {"subida": 1, "bajada": -1}
    cambios = sorted((_cs(e["tiempo_s"]), signo[e["sentido"]]) for e in eventos)
    curva, i, valor = [], 0, 0
    for t in range(0, _cs(fin_s) + 1, PASO_CS):
        while i < len(cambios) and cambios[i][0] <= t:
            valor += cambios[i][1]
            i += 1
        curva.append(valor)
    return curva


def errores(referencia: list[int], estimada: list[int]) -> tuple[float, float]:
    """MAE y RMSE, en pasajeros, de estimada − referencia sobre la grilla."""
    assert len(referencia) == len(estimada) and referencia
    d = [e - r for r, e in zip(referencia, estimada)]
    return sum(abs(x) for x in d) / len(d), math.sqrt(sum(x * x for x in d) / len(d))


def main() -> None:
    ref = json.loads(REFERENCIA.read_text(encoding="utf-8"))
    pred = json.loads((EJECUCION / "prediccion.json").read_text(encoding="utf-8"))
    config = json.loads((EJECUCION / "prediccion.config.json").read_text(encoding="utf-8"))
    medicion = config["medicion"]
    # Tramo evaluado: el video completo (tramo_s 0 → fin); el último cuadro está en (cuadros − 1)/fps.
    fin_s = (medicion["cuadros"] - 1) / config["propiedades_del_video"]["fps"]
    curva_ref = cambio_acumulado(ref["eventos"], fin_s)
    curva_pred = cambio_acumulado(pred["eventos"], fin_s)
    mae, rmse = errores(curva_ref, curva_pred)
    resultado = {
        "video": "prueba-bus.mp4",
        "video_sha256": ref["video_sha256"],
        "referencia": f"{REFERENCIA.as_posix()} ({ref['anotado_por']})",
        "prediccion": f"{(EJECUCION / 'prediccion.json').as_posix()}, copia de runs/panel/20261108-200805-374934",
        "entorno": {"dispositivo": config["dispositivo"], **config["entorno"]},
        "magnitud": "cambio acumulado de pasajeros desde el inicio (carga inicial real desconocida)",
        "grilla_s": {"inicio": 0.0, "fin": round(fin_s, 2), "paso": PASO_CS / 100, "puntos": len(curva_ref)},
        "mae_pasajeros": round(mae, 4),
        "rmse_pasajeros": round(rmse, 4),
        "final": {"referencia": curva_ref[-1], "estimacion": curva_pred[-1]},
        "curva_referencia": curva_ref,
        "curva_estimacion": curva_pred,
    }
    DESTINO_JSON.write_text(json.dumps(resultado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    graficar(curva_ref, curva_pred)
    print(f"{len(curva_ref)} puntos, 0–{fin_s:.2f} s: MAE {mae:.3f}, RMSE {rmse:.3f} pasajeros")


def graficar(curva_ref: list[int], curva_pred: list[int]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "serif", "font.size": 7})
    t = [k * PASO_CS / 100 for k in range(len(curva_ref))]
    fig, ax = plt.subplots(figsize=(3.45, 1.35), dpi=300)
    ax.step(t, curva_ref, where="post", color="#222222", lw=1.4, label="Referencia (humana)")
    ax.step(t, curva_pred, where="post", color="#2a6fdb", lw=1.4, ls=(0, (4, 1.5)),
            label="Estimación (CPU)")
    ax.axhline(0, color="#999999", lw=0.5)
    ax.set_xlim(0, t[-1])
    ax.set_ylim(-15.5, 1)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Cambio acumulado\n(pasajeros)")
    ax.grid(axis="y", color="#dddddd", lw=0.4)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.legend(loc="lower left", frameon=False, handlelength=2.5, fontsize=6.5, ncol=2, borderaxespad=0.2)
    ax.set_title("Video: prueba-bus (ejecución 20261108-200805-374934)", fontsize=6.5, loc="left")
    fig.tight_layout(pad=0.2)
    fig.savefig(DESTINO_PNG)


if __name__ == "__main__":
    main()
