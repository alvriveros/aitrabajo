import pytest

from vision import pesos


def test_descarga_con_hash_distinto_no_deja_archivo(tmp_path, monkeypatch):
    falso = tmp_path / "falso.pt"
    falso.write_bytes(b"no son los pesos")
    monkeypatch.setattr(pesos, "URL", falso.as_uri())
    destino = tmp_path / "yolo11n.pt"
    with pytest.raises(SystemExit, match="se esperaba"):
        pesos.preparar(destino)
    assert not destino.exists()
    assert [p.name for p in tmp_path.iterdir()] == ["falso.pt"]


def test_archivo_existente_se_verifica(tmp_path, monkeypatch):
    destino = tmp_path / "yolo11n.pt"
    destino.write_bytes(b"x")
    monkeypatch.setattr(pesos, "SHA256", pesos.sha256(destino))
    pesos.preparar(destino)  # no descarga ni falla
