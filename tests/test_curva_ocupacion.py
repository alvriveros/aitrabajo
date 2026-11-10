import math

from evaluation.curva_ocupacion import cambio_acumulado, errores


def test_caso_conocido():
    # Grilla 0,0..0,5 s. Referencia: sube en 0,1 s y baja en 0,35 s → 0,1,1,1,0,0.
    referencia = cambio_acumulado([{"tiempo_s": 0.1, "sentido": "subida"},
                                   {"tiempo_s": 0.35, "sentido": "bajada"}], 0.5)
    # Estimación: una bajada en 0,2 s y otra en 0,4 s (negativos que se conservan) → 0,0,-1,-1,-2,-2.
    estimada = cambio_acumulado([{"tiempo_s": 0.4, "sentido": "bajada"},
                                 {"tiempo_s": 0.2, "sentido": "bajada"}], 0.5)
    assert referencia == [0, 1, 1, 1, 0, 0]
    assert estimada == [0, 0, -1, -1, -2, -2]
    # Diferencias 0,-1,-2,-2,-2,-2 → MAE 9/6 = 1,5; RMSE sqrt(17/6).
    mae, rmse = errores(referencia, estimada)
    assert mae == 1.5
    assert math.isclose(rmse, math.sqrt(17 / 6))


def test_evento_cuenta_desde_su_instante():
    assert cambio_acumulado([{"tiempo_s": 0.2, "sentido": "subida"}], 0.3) == [0, 0, 1, 1]
