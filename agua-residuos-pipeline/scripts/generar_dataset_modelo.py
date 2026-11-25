"""Etapa de limpieza y preprocesamiento (ETL): de los CSV crudos a la tabla con la que se entrena el modelo.

Uso (desde la raíz del repositorio):
    python scripts/generar_dataset_modelo.py

Lee  data/raw/rsu_t_ceamse_2026.csv y data/raw/Cobertura_agua_por_partido_Poblacion_2023.csv
Genera data/processed/partidos_modelo.csv (y una copia en actor_apify/data/, que es la que usa el Actor).
"""
import re
import shutil
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
CEAMSE = RAIZ / 'data' / 'raw' / 'rsu_t_ceamse_2026.csv'
AYSA = RAIZ / 'data' / 'raw' / 'Cobertura_agua_por_partido_Poblacion_2023.csv'
SALIDA = RAIZ / 'data' / 'processed' / 'partidos_modelo.csv'
SALIDA_ACTOR = RAIZ / 'actor_apify' / 'data' / 'partidos_modelo.csv'

UMBRAL_COBERTURA = 75.0

CANON = {
    'C DE BS AIRES': 'CABA', 'CAPITAL FEDERAL': 'CABA',
    'CIUDAD AUTONOMA DE BUENOS AIRES': 'CABA', 'CIUDAD DE BUENOS AIRES': 'CABA',
    'ALTE BROWN': 'ALMIRANTE BROWN', 'ALMTE BROWN': 'ALMIRANTE BROWN',
    'EST ECHEVERRIA': 'ESTEBAN ECHEVERRIA',
    'G SAN MARTIN': 'SAN MARTIN', 'GENERAL SAN MARTIN': 'SAN MARTIN', 'GRAL SAN MARTIN': 'SAN MARTIN',
    'L DE ZAMORA': 'LOMAS DE ZAMORA',
    'VTE LOPEZ': 'VICENTE LOPEZ',
    '3 DE FEBRERO': 'TRES DE FEBRERO',
}


def num_ceamse(serie):
    return pd.to_numeric(serie.astype(str).str.replace(',', '.', regex=False), errors='coerce')


def num_aysa(serie):
    s = (serie.astype(str).str.replace('%', '', regex=False)
         .str.replace('.', '', regex=False)      # puntos de miles
         .str.replace(',', '.', regex=False)     # coma decimal
         .str.strip())
    return pd.to_numeric(s, errors='coerce')


def normalizar(texto):
    s = unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode().upper()
    s = re.sub(r'[^A-Z0-9 ]', ' ', s)
    return ' '.join(s.split())


def extraer():
    ceamse = pd.read_csv(CEAMSE, sep=';', encoding='utf-8')
    ceamse.columns = ['municipio', 't_2022', 't_2023', 't_2024']
    for c in ['t_2022', 't_2023', 't_2024']:
        ceamse[c] = num_ceamse(ceamse[c])
    ceamse['clave'] = ceamse['municipio'].map(normalizar).replace(CANON)
    ceamse = ceamse[~ceamse['clave'].str.startswith(('SUBTOTAL', 'GENERADORES', 'OTROS'))].copy()

    aysa_raw = pd.read_csv(AYSA, sep=';', encoding='latin1', skiprows=7, header=None)
    # columna 10 = población proyectada 2023, 11 = población con servicio 2023, 12 = cobertura oficial.
    # (La columna 9 es el coeficiente de proyección: no es población.)
    aysa = aysa_raw.iloc[:, [0, 10, 11, 12]].copy()
    aysa.columns = ['partido', 'poblacion_2023', 'poblacion_con_servicio_2023', 'cobertura_oficial']
    for c in ['poblacion_2023', 'poblacion_con_servicio_2023', 'cobertura_oficial']:
        aysa[c] = num_aysa(aysa[c])
    aysa['clave'] = aysa['partido'].map(normalizar).replace(CANON)
    aysa = aysa.dropna(subset=['partido', 'poblacion_2023', 'poblacion_con_servicio_2023'])
    aysa = aysa[~aysa['clave'].str.startswith(('REGION', 'TOTAL'))]       # subtotales
    aysa = aysa[~aysa['partido'].str.contains('-')]                       # partidos combinados
    aysa = aysa.drop_duplicates(subset='clave', keep='first')             # Morón: se conserva el partido, no el subtotal
    return ceamse, aysa


def transformar(ceamse, aysa):
    df = ceamse.merge(aysa, on='clave', how='inner').rename(columns={'clave': 'municipio_clave'})
    df = df.drop(columns=['municipio', 'partido'])
    df['porcentaje_cobertura'] = df['poblacion_con_servicio_2023'] / df['poblacion_2023'] * 100
    dif = (df['porcentaje_cobertura'] - df['cobertura_oficial']).abs()
    assert dif.max() < 0.05, 'La cobertura calculada no coincide con la oficial: revisar las columnas de AySA'

    df['kg_per_capita_2023'] = df['t_2023'] * 1000 / df['poblacion_2023']       # toneladas -> kg
    df['log_poblacion'] = np.log(df['poblacion_2023'])
    df['riesgo_cobertura'] = (df['porcentaje_cobertura'] < UMBRAL_COBERTURA).astype(int)
    df['alto_generador'] = (df['kg_per_capita_2023'] > df['kg_per_capita_2023'].median()).astype(int)
    return df


def main():
    ceamse, aysa = extraer()
    df = transformar(ceamse, aysa)
    columnas = ['municipio_clave', 'poblacion_2023', 'porcentaje_cobertura', 'kg_per_capita_2023',
                'log_poblacion', 'alto_generador', 'riesgo_cobertura']
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df[columnas].to_csv(SALIDA, index=False)
    SALIDA_ACTOR.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SALIDA, SALIDA_ACTOR)
    print(f'{len(df)} partidos guardados en {SALIDA}')


if __name__ == '__main__':
    main()
