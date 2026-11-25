"""Preprocesamiento de la entrada: validación y cálculo de las variables que usa el modelo."""
import math

CAMPOS_OBLIGATORIOS = ('poblacion', 'cobertura_agua_pct', 'toneladas_residuos_anuales')


def validar_registro(registro: dict) -> dict:
    """Devuelve el registro con los números convertidos o levanta ValueError con el motivo."""
    nombre = str(registro.get('nombre_municipio') or 'Municipio sin nombre')
    try:
        poblacion = float(registro['poblacion'])
        cobertura = float(registro['cobertura_agua_pct'])
        toneladas = float(registro['toneladas_residuos_anuales'])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f'{nombre}: faltan datos o no son numéricos. Se necesitan: {", ".join(CAMPOS_OBLIGATORIOS)}.')

    problemas = []
    if not all(math.isfinite(v) for v in (poblacion, cobertura, toneladas)):
        problemas.append('hay valores no finitos')
    else:
        if poblacion <= 0:
            problemas.append('poblacion debe ser mayor a 0')
        if not 0 <= cobertura <= 100:
            problemas.append('cobertura_agua_pct debe estar entre 0 y 100')
        if toneladas < 0:
            problemas.append('toneladas_residuos_anuales no puede ser negativa')
    if problemas:
        raise ValueError(f'{nombre}: ' + '; '.join(problemas) + '.')

    return {'nombre_municipio': nombre, 'poblacion': poblacion,
            'cobertura_agua_pct': cobertura, 'toneladas_residuos_anuales': toneladas}


def calcular_features(registro: dict) -> dict:
    """Variables derivadas, idénticas a las del entrenamiento (ver scripts/generar_dataset_modelo.py)."""
    return {
        'porcentaje_cobertura': registro['cobertura_agua_pct'],
        'log_poblacion': math.log(registro['poblacion']),
        'kg_per_capita_2023': registro['toneladas_residuos_anuales'] * 1000 / registro['poblacion'],  # toneladas -> kg
    }
