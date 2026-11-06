import json

from evaluation.evaluate import emparejar, evaluar, main


def evento(t, sentido):
    return {"tiempo_s": t, "track_id": 1, "sentido": sentido}


def test_prediccion_exacta_tiene_f1_uno():
    referencia = [evento(2, "subida"), evento(4, "bajada")]
    resultado = evaluar(referencia, referencia)
    assert resultado["total"] == {"aciertos": 2, "omisiones": 0, "falsos_positivos": 0, "f1": 1.0}
    assert resultado["sentidos"]["subida"]["error_conteo_abs"] == 0


def test_tolerancia_incluye_el_limite():
    assert emparejar([2.0], [3.0], tolerancia=1.0) == ([(2.0, 3.0)], [], [])
    assert emparejar([2.0], [3.01], tolerancia=1.0) == ([], [2.0], [3.01])


def test_una_prediccion_empareja_con_un_solo_cruce():
    pares, omitidos, sobrantes = emparejar([2.0, 2.5], [2.2])
    assert pares == [(2.0, 2.2)]
    assert omitidos == [2.5]
    assert sobrantes == []


def test_un_cruce_empareja_con_una_sola_prediccion():
    pares, omitidos, sobrantes = emparejar([2.0], [1.9, 2.1])
    assert pares == [(2.0, 1.9)]
    assert omitidos == []
    assert sobrantes == [2.1]


def test_el_recorrido_en_orden_logra_el_maximo_de_pares():
    # Un emparejamiento por cercanía uniría 2.0 con 2.4 y dejaría a 1.2 y 3.2 sin par.
    pares, omitidos, sobrantes = emparejar([2.0, 3.2], [1.2, 2.4])
    assert pares == [(2.0, 1.2), (3.2, 2.4)]
    assert not omitidos and not sobrantes


def test_el_sentido_contrario_no_empareja():
    resultado = evaluar([evento(2, "subida")], [evento(2, "bajada")])
    assert resultado["sentidos"]["subida"]["omisiones"] == 1
    assert resultado["sentidos"]["bajada"]["falsos_positivos"] == 1
    assert resultado["total"]["f1"] == 0


def test_metricas_con_omisiones_y_falsos_positivos():
    referencia = [evento(t, "subida") for t in (2, 10, 20, 30)]
    prediccion = [evento(t, "subida") for t in (2.2, 10.5, 40)]
    subida = evaluar(referencia, prediccion)["sentidos"]["subida"]
    assert (subida["aciertos"], subida["omisiones"], subida["falsos_positivos"]) == (2, 2, 1)
    assert subida["precision"] == 0.6667
    assert subida["exhaustividad"] == 0.5
    assert subida["f1"] == 0.5714
    assert subida["error_conteo_abs"] == 1
    assert subida["error_tiempo_medio_s"] == 0.35
    assert subida["tiempos_omitidos_s"] == [20, 30]
    assert subida["tiempos_falsos_s"] == [40]


def test_el_tramo_filtra_y_no_incluye_su_final():
    referencia = [evento(2, "subida"), evento(43, "subida"), evento(50, "subida")]
    resultado = evaluar(referencia, referencia, desde=2, hasta=43)
    assert resultado["sentidos"]["subida"]["referencia"] == 1
    assert evaluar(referencia, referencia, desde=43)["sentidos"]["subida"]["referencia"] == 2


def test_sin_cruces_las_razones_quedan_sin_definir():
    resultado = evaluar([], [])
    assert resultado["sentidos"]["bajada"]["f1"] is None
    assert resultado["total"]["f1"] is None


def test_sin_predicciones_todo_queda_omitido():
    resultado = evaluar([evento(2, "subida")], [])
    assert resultado["total"] == {"aciertos": 0, "omisiones": 1, "falsos_positivos": 0, "f1": 0}
    assert resultado["sentidos"]["subida"]["precision"] is None


def test_la_linea_de_comandos_lee_y_guarda_json(tmp_path, capsys):
    referencia = tmp_path / "referencia.json"
    prediccion = tmp_path / "prediccion.json"
    salida = tmp_path / "resultado" / "metricas.json"
    referencia.write_text(json.dumps({"eventos": [evento(2, "subida")]}), encoding="utf-8")
    prediccion.write_text(json.dumps({"eventos": [evento(2.5, "subida")]}), encoding="utf-8")

    main(["--referencia", str(referencia), "--prediccion", str(prediccion), "--salida", str(salida)])

    assert json.loads(salida.read_text(encoding="utf-8"))["total"]["aciertos"] == 1
    assert "subida: 1/1 aciertos" in capsys.readouterr().out
