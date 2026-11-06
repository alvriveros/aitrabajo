import pytest

from vision.cruces import ContadorCruces, Evento, Linea

# Línea horizontal en y = 100 con el interior arriba: en la imagen, abajo → arriba es subida.
LINEA = Linea(0, 100, 200, 100, interior="arriba")
ABAJO = [130, 120, 110]
ARRIBA = [90, 80, 70]


def contador():
    return ContadorCruces(LINEA, margen_px=5, confirmacion=3)


def recorrer(alturas, track_id=1, cuenta=None):
    """Pasa una altura por cuadro, a 10 cuadros por segundo, y devuelve los eventos."""
    cuenta = cuenta or contador()
    for indice, y in enumerate(alturas):
        cuenta.actualizar(track_id, 100, y, indice / 10)
    return cuenta.eventos_ordenados()


def test_abajo_hacia_arriba_es_una_subida():
    assert recorrer(ABAJO + ARRIBA) == [Evento(0.3, 1, "subida")]


def test_arriba_hacia_abajo_es_una_bajada():
    assert recorrer(ARRIBA + ABAJO) == [Evento(0.3, 1, "bajada")]


def test_el_evento_lleva_el_instante_del_paso_por_la_linea():
    # Pasa la línea en el cuadro 4 (98 px), pero el lado recién se confirma en el cuadro 9.
    assert recorrer(ABAJO + [104, 98, 97, 96] + ARRIBA) == [Evento(0.4, 1, "subida")]


def test_temblar_despues_de_cruzar_cuenta_una_sola_vez():
    assert recorrer(ABAJO + ARRIBA + [99, 101, 98, 102, 97, 103] + ARRIBA) == [Evento(0.3, 1, "subida")]


def test_temblar_sobre_la_linea_sin_cruzar_no_cuenta():
    assert recorrer(ABAJO + [102, 98, 101, 97, 103] + ABAJO[::-1]) == []


def test_pico_aislado_al_otro_lado_no_cuenta():
    assert recorrer(ARRIBA + [110, 120] + ARRIBA) == []
    assert recorrer(ABAJO + [90, 80] + ABAJO) == []


def test_regreso_confirmado_genera_un_evento_nuevo():
    assert recorrer(ABAJO + ARRIBA + ABAJO) == [Evento(0.3, 1, "subida"), Evento(0.6, 1, "bajada")]


def test_aparecer_junto_a_la_linea_no_cuenta():
    assert recorrer([101, 99, 102] + ARRIBA) == []
    assert recorrer([98, 101] + ABAJO) == []


def test_aparecer_junto_a_la_linea_no_impide_contar_un_cruce_posterior():
    assert recorrer([101, 99] + ABAJO + ARRIBA) == [Evento(0.5, 1, "subida")]


def test_aparecer_de_un_lado_no_cuenta():
    assert recorrer(ARRIBA) == []


def test_sin_lado_de_origen_confirmado_no_hay_cruce():
    assert recorrer([110, 120] + ARRIBA) == []


def test_personas_simultaneas_cuentan_por_separado():
    cuenta = contador()
    recorrer(ABAJO + ARRIBA, track_id=1, cuenta=cuenta)
    recorrer(ABAJO + ARRIBA, track_id=2, cuenta=cuenta)
    recorrer(ARRIBA + ABAJO, track_id=3, cuenta=cuenta)
    assert cuenta.eventos_ordenados() == [
        Evento(0.3, 1, "subida"),
        Evento(0.3, 2, "subida"),
        Evento(0.3, 3, "bajada"),
    ]


def test_track_perdido_que_reaparece_del_otro_lado_cuenta_al_reaparecer():
    cuenta = contador()
    for tiempo, y in [(0.0, 130), (0.1, 120), (0.2, 110), (1.5, 90), (1.6, 80), (1.7, 70)]:
        cuenta.actualizar(1, 100, y, tiempo)
    assert cuenta.eventos_ordenados() == [Evento(1.5, 1, "subida")]


def test_cambio_de_id_durante_el_cruce_queda_omitido():
    # Limitación conocida de contar por track: cada ID solo conoce su propia trayectoria.
    cuenta = contador()
    recorrer(ABAJO, track_id=1, cuenta=cuenta)
    recorrer(ARRIBA, track_id=2, cuenta=cuenta)
    assert cuenta.eventos_ordenados() == []


def test_eventos_se_ordenan_por_el_instante_del_cruce():
    # El track 2 confirma primero, aunque el track 1 pasó antes la línea.
    cuenta = contador()
    recorrer(ABAJO + [110, 110] + ARRIBA, track_id=2, cuenta=cuenta)
    recorrer(ABAJO + [110, 98, 97, 96, 96, 96] + ARRIBA, track_id=1, cuenta=cuenta)
    assert [evento.track_id for evento in cuenta.eventos] == [2, 1]
    assert cuenta.eventos_ordenados() == [Evento(0.4, 1, "subida"), Evento(0.5, 2, "subida")]


def test_linea_diagonal_mide_la_distancia_perpendicular():
    linea = Linea(0, 0, 100, 100, interior="derecha")
    assert round(linea.distancia(100, 0), 2) == 70.71
    assert round(linea.distancia(0, 100), 2) == -70.71


def test_el_orden_de_los_extremos_no_cambia_el_interior():
    assert LINEA.distancia(50, 40) == 60
    assert Linea(200, 100, 0, 100, interior="arriba").distancia(50, 40) == 60


def test_interior_abajo_invierte_el_sentido():
    cuenta = ContadorCruces(Linea(0, 100, 200, 100, interior="abajo"), margen_px=5, confirmacion=3)
    assert recorrer(ARRIBA + ABAJO, cuenta=cuenta) == [Evento(0.3, 1, "subida")]


def test_linea_invalida():
    for argumentos in [(0, 100, 200, 100, "derecha"), (5, 5, 5, 5, "arriba"), (0, 0, 1, 1, "adentro")]:
        with pytest.raises(ValueError):
            Linea(*argumentos)


def test_parametros_invalidos_del_contador():
    with pytest.raises(ValueError):
        ContadorCruces(LINEA, margen_px=-1)
    with pytest.raises(ValueError):
        ContadorCruces(LINEA, confirmacion=0)
