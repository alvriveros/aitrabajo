"""Prepara los pesos oficiales de YOLO11n y verifica su SHA-256.

Uso, desde la raíz: python vision/pesos.py [destino]   (por defecto, yolo11n.pt)

- Si el archivo ya existe, solo lo verifica: no lo reemplaza.
- Si falta, lo descarga del release oficial de Ultralytics y lo verifica antes de dejarlo en su lugar.
Sale con código 1 y un mensaje claro si la descarga falla o el hash no coincide.
"""
from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

URL = "https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo11n.pt"
SHA256 = "0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1"  # 5.613.764 bytes; igual en v8.3.0


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def preparar(destino: Path) -> None:
    if destino.exists():
        if sha256(destino) != SHA256:
            raise SystemExit(f"ERROR: {destino} existe pero su SHA-256 no es el oficial ({SHA256}). "
                             "Borralo para descargarlo de nuevo o revisá de dónde salió.")
        print(f"{destino}: ya estaba, SHA-256 verificado.")
        return
    print(f"Descargando {URL} …")
    fd, temporal = tempfile.mkstemp(dir=destino.parent or ".", suffix=".descarga")
    os.close(fd)
    temporal = Path(temporal)
    try:
        try:
            urllib.request.urlretrieve(URL, temporal)
        except OSError as e:
            raise SystemExit(f"ERROR: no se pudo descargar {URL}: {e}. "
                             f"Sin red, copiá a mano un yolo11n.pt con SHA-256 {SHA256}.")
        obtenido = sha256(temporal)
        if obtenido != SHA256:
            raise SystemExit(f"ERROR: el archivo descargado tiene SHA-256 {obtenido}; se esperaba {SHA256}. No se usa.")
        temporal.replace(destino)
    finally:
        temporal.unlink(missing_ok=True)
    print(f"{destino}: descargado y SHA-256 verificado.")


if __name__ == "__main__":
    preparar(Path(sys.argv[1] if len(sys.argv) > 1 else "yolo11n.pt"))
