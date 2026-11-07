"""Gráfico de confianza.json. Uso, desde la raíz: python docs/casos-deteccion/oficina-bajada-omitida/graficar_confianza.py docs/casos-deteccion/oficina-bajada-omitida"""
import json, sys, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
C = sys.argv[1]
d = json.load(open(f"{C}/confianza.json"))
fig, axs = plt.subplots(2, 1, figsize=(8, 5.2))
for ax, (a, b, tit) in zip(axs, [(1.5, 2.7, "Subida (contada a 2,16 s)"), (3.9, 5.3, "Bajada (omitida; referencia ≈ 4 s)")]):
    f = [x for x in d if a <= x["t"] <= b]
    ax.bar([x["t"] for x in f], [x["conf_max"] for x in f], width=0.03,
           color=["#2a6fdb" if x["centro_y"] is not None and x["centro_y"] < 90 else "#e07b39" for x in f])
    ax.axhline(0.1, color="#444", ls="--", lw=1); ax.text(b + 0.06, 0.1, "0,10: crear o confirmar un track", va="bottom", fontsize=8)
    ax.axhline(0.05, color="#999", ls=":", lw=1); ax.text(b + 0.06, 0.05, "0,05: mínimo para usarla", va="top", fontsize=8)
    ax.set_xlim(a - 0.05, b + 0.05); ax.set_ylim(0, 1); ax.set_title(tit, fontsize=10, loc="left"); ax.set_ylabel("confianza")
    ax.spines[["top", "right"]].set_visible(False)
axs[1].set_xlabel("segundos desde el inicio del tramo")
axs[0].legend(handles=[Patch(color="#2a6fdb", label="caja arriba de la línea (adentro)"),
                       Patch(color="#e07b39", label="caja debajo de la línea (afuera)")], fontsize=8, frameon=False, loc="upper left")
fig.tight_layout(); fig.subplots_adjust(right=0.72); fig.savefig(f"{C}/confianza.png", dpi=130)
