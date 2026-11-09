| Variante | Kaggle sub. TP/FP/FN | Kaggle baj. | PAMELA sub. | PAMELA baj. | Errores | Error conteo | FN no sube |
|---|---|---|---|---|---|---|---|
| yolo11n-calibrado@0.0 | 5/4/1 | 0/4/0 | 0/1/0 | 10/0/18 | 28 | 26 | sí |
| yolo11n-calibrado@0.5 | 5/1/1 | 0/3/0 | 0/1/0 | 9/0/19 | 25 | 23 | NO |
| yolo11n-calibrado@1.0 | 5/0/1 | 0/3/0 | 0/1/0 | 9/0/19 | 24 | 24 | NO |
| yolo11n-calibrado@1.5 | 5/0/1 | 0/2/0 | 0/1/0 | 9/0/19 | 23 | 23 | NO |
| yolo11l-calibrado@0.0 | 6/2/0 | 0/2/0 | 0/2/0 | 13/0/15 | 21 | 21 | sí |
| yolo11l-calibrado@0.5 | 6/2/0 | 0/2/0 | 0/2/0 | 13/0/15 | 21 | 21 | sí |
| yolo11l-calibrado@1.0 | 6/1/0 | 0/2/0 | 0/2/0 | 12/0/16 | 21 | 21 | NO |
| yolo11l-calibrado@1.5 | 6/0/0 | 0/2/0 | 0/2/0 | 10/0/18 | 22 | 22 | NO |

Cota (eventos de la referencia que borraría la regla): {'kaggle': {'0.0': 0, '0.5': 0, '1.0': 0, '1.5': 1}, 'pamela-A': {'0.0': 0, '0.5': 3, '1.0': 6, '1.5': 13}}
Elegida: None
Ninguna variante con u > 0 mejora a su detector sin aumentar omisiones: la supresión temporal global no se justifica.
