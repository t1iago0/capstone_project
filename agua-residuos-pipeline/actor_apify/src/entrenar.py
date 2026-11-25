"""Entrenamiento de los dos modelos a partir de data/partidos_modelo.csv (18 partidos del AMBA)."""
from pathlib import Path

import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

RUTA_DATOS = Path(__file__).resolve().parent.parent / 'data' / 'partidos_modelo.csv'

FEATURES_GENERADOR = ['porcentaje_cobertura', 'log_poblacion']      # predice alto_generador
FEATURES_COBERTURA = ['log_poblacion', 'kg_per_capita_2023']        # predice riesgo_cobertura (sin usar la cobertura)


def _modelo():
    return make_pipeline(StandardScaler(), LogisticRegression())


def entrenar() -> dict:
    df = pd.read_csv(RUTA_DATOS)
    X1, y1 = df[FEATURES_GENERADOR], df['alto_generador']
    X2, y2 = df[FEATURES_COBERTURA], df['riesgo_cobertura']

    # Métricas fuera de muestra (leave-one-out): cada partido lo predice un modelo que no lo vio
    loo = LeaveOneOut()
    pred1 = cross_val_predict(_modelo(), X1, y1, cv=loo)
    pred2 = cross_val_predict(_modelo(), X2, y2, cv=loo)

    return {
        'generador': _modelo().fit(X1, y1),
        'cobertura': _modelo().fit(X2, y2),
        'info': {
            'n_partidos_entrenamiento': int(len(df)),
            'mediana_kg_per_capita_entrenamiento': round(float(df['kg_per_capita_2023'].median()), 1),
            'accuracy_loo_alto_generador': round(float(accuracy_score(y1, pred1)), 2),
            'accuracy_loo_riesgo_cobertura': round(float(accuracy_score(y2, pred2)), 2),
            'recall_loo_riesgo_cobertura': round(float(recall_score(y2, pred2, zero_division=0)), 2),
            'version_scikit_learn': sklearn.__version__,
        },
    }
