"""Inferencia: preprocesa un registro y devuelve las dos predicciones con su probabilidad."""
from functools import lru_cache

import pandas as pd

from .entrenar import FEATURES_COBERTURA, FEATURES_GENERADOR, entrenar
from .preprocessing import calcular_features, validar_registro

ADVERTENCIA = ('Modelo exploratorio entrenado con 18 partidos del AMBA: con tan pocos datos no supera '
               'claramente al baseline. Usar como demostración, no como base para decisiones.')


@lru_cache(maxsize=1)
def cargar_modelos() -> dict:
    return entrenar()


def predecir(registro: dict) -> dict:
    modelos = cargar_modelos()
    r = validar_registro(registro)
    f = calcular_features(r)

    X1 = pd.DataFrame([[f[c] for c in FEATURES_GENERADOR]], columns=FEATURES_GENERADOR)
    X2 = pd.DataFrame([[f[c] for c in FEATURES_COBERTURA]], columns=FEATURES_COBERTURA)
    p_gen = float(modelos['generador'].predict_proba(X1)[0][1])
    p_cob = float(modelos['cobertura'].predict_proba(X2)[0][1])

    return {
        'nombre_municipio': r['nombre_municipio'],
        'poblacion': int(r['poblacion']),
        'cobertura_agua_pct': r['cobertura_agua_pct'],
        'toneladas_residuos_anuales': r['toneladas_residuos_anuales'],
        'kg_per_capita': round(f['kg_per_capita_2023'], 1),
        'prediccion_alto_generador': int(p_gen >= 0.5),
        'confianza_alto_generador_pct': round(p_gen * 100, 2),
        'prediccion_riesgo_cobertura': int(p_cob >= 0.5),
        'confianza_riesgo_cobertura_pct': round(p_cob * 100, 2),
        'lectura': ('Alto generador de residuos' if p_gen >= 0.5 else 'Generador bajo o medio de residuos')
                   + ' | '
                   + ('Prioritario para inversión en red de agua (cobertura < 75%)' if p_cob >= 0.5
                      else 'Cobertura de agua aceptable (>= 75%)'),
        **modelos['info'],
        'advertencia': ADVERTENCIA,
    }
