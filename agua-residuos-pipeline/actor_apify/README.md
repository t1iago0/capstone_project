# Inferencia: riesgo de cobertura de agua y generación de residuos (AMBA)

Actor de Apify que recibe los datos de un municipio, los preprocesa y devuelve dos predicciones:

1. **Alto generador de residuos**: si los kg de residuos por habitante superan la mediana de los 18 partidos de entrenamiento.
2. **Riesgo de cobertura de agua**: si la cobertura de agua de red sería menor al 75%.

## Entrada

| Campo | Tipo | Descripción |
|---|---|---|
| `nombre_municipio` | string | Nombre para identificar el resultado (no entra al modelo) |
| `poblacion` | integer | Habitantes (mayor a 0) |
| `cobertura_agua_pct` | number | Cobertura de agua de red, de 0 a 100 |
| `toneladas_residuos_anuales` | number | Toneladas anuales enviadas a disposición final (0 o más) |
| `municipios` | array | Opcional: lista de objetos con los 4 campos anteriores. Si se completa, se ignoran los campos individuales |

## Salida (dataset)

Una fila por municipio con:
- `kg_per_capita`: residuos por habitante (kg/año), calculado como toneladas × 1000 / población.
- `prediccion_alto_generador` (0 o 1) y `confianza_alto_generador_pct`.
- `prediccion_riesgo_cobertura` (0 o 1) y `confianza_riesgo_cobertura_pct`.
- `lectura`: resumen en texto.
- Información del modelo: `n_partidos_entrenamiento`, `mediana_kg_per_capita_entrenamiento`, `accuracy_loo_alto_generador`, `accuracy_loo_riesgo_cobertura`, `recall_loo_riesgo_cobertura`, `version_scikit_learn`.
- `advertencia`: el modelo es exploratorio (18 partidos).

Si un municipio de una lista es inválido, su fila trae un campo `error` con el motivo. Si la entrada única es inválida, la corrida falla con el motivo en el log.

## Cómo funciona

El modelo se entrena al iniciar la corrida a partir de `data/partidos_modelo.csv` (18 filas, tarda una fracción de segundo). No hay archivos de modelo guardados: así no hay problemas de compatibilidad con la versión de scikit-learn. Los modelos son regresiones logísticas con estandarización.
