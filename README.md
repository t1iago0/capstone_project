# Residuos sólidos urbanos (CEAMSE) y cobertura de agua (AySA) en el AMBA

Proyecto final / capstone de análisis de datos. El notebook `capstone_proyect.ipynb` cruza dos fenómenos —**generación de residuos** y **acceso a agua de red**— en los partidos del AMBA que atiende AySA, con el objetivo de identificar territorios prioritarios para invertir en infraestructura sanitaria y ambiental.

Está pensado para correr en **Google Colab**.

## Pregunta y enfoque

- **Fenómeno estudiado:** residuos enviados a disposición final por habitante vs. cobertura de agua de red, por partido.
- **Unidad de análisis:** partido / municipio (18 partidos, los que figuran en ambas fuentes).
- **Métrica de negocio:** `presion_hidrica` = población proyectada 2023 − población con servicio 2023. Hoy son **1.532.263 personas** sin agua de red en los 18 partidos. El objetivo es **reducir** ese número.
- **Decisión asociada al modelo:** el clasificador de `riesgo_cobertura` indica en qué partidos priorizar la inversión en redes de agua.

## Datos de entrada

| Archivo | Contenido | Formato |
|---|---|---|
| `rsu_t_ceamse_2026.csv` | Toneladas anuales de residuos enviadas a CEAMSE por municipio (2022-2024) | `;`, UTF-8 |
| `Cobertura_agua_por_partido_Poblacion_2023.csv` | Población proyectada y población con servicio de AySA por partido (2023) | `;`, latin1, 7 filas de encabezado |
| `dataset_ml-inmuebles-scraper_2026-11-24_10-05-54-959.csv` | Avisos de terrenos de Mercado Libre (144 registros), usados solo en la demo final | `,` |

Los archivos deben estar en la carpeta de trabajo de Colab (algunas celdas los leen desde `/content/`).

## Contenido del notebook

1. **Setup**: librerías (pandas, numpy, matplotlib, seaborn, scipy, scikit-learn).
2. **Carga y limpieza**: cada fuente se limpia por separado (decimales, separadores de miles, `%`, subtotales, partidos combinados, duplicados de Morón) y se normalizan los nombres de municipio con un diccionario `CANON` para poder cruzarlos.
3. **Validación**: sin nulos ni duplicados, cobertura entre 0 y 100 %, y verificación contra la cobertura oficial de AySA (diferencia máxima 0,0045 puntos).
4. **Features derivadas**: `kg_per_capita_2023`, `poblacion_sin_servicio`, `var_residuos_2022_2024_pct`, `log_poblacion`, `nivel_cobertura`.
5. **Análisis exploratorio**: distribuciones, rankings y correlaciones (Pearson, Spearman, Kendall).
6. **Targets y métrica de negocio**: `alto_generador` (kg per cápita sobre la mediana), `riesgo_cobertura` (cobertura < 75 %) y `presion_hidrica`.
7. **Dashboard** resumen de 6 gráficos.
8. **Modelos exploratorios**: regresión logística y árbol de profundidad 2 contra un baseline, con validación cruzada estratificada repetida. Los features no participan en la definición de su propio target, para evitar *data leakage*.
9. **Dataset de inferencia**: se exporta `dataset_inferencia_modelos.csv` con predicciones y probabilidades por partido.
10. **Conclusiones y limitaciones.**
11. **Métrica de negocio**: déficit de personas sin red cubierto por cada estrategia de priorización.
12. **Costo-efectividad (SROI)**: comparación de tres estrategias de priorización.
13. **Métricas del modelo** con Leave-One-Out y propuestas de mejora.
14. **Target encoding regularizado** (con suavizado) de `nivel_cobertura`.
15. **Demo interactiva del modelo**: formulario de Colab para simular un municipio y obtener las dos predicciones.
16. **Demo interactiva de terrenos**: buscador de terrenos de Mercado Libre por presupuesto máximo (USD).

## Resultados principales

- **Cobertura de agua:** 6 partidos quedan por debajo del 75 %: Almirante Brown, Esteban Echeverría, Ezeiza, Hurlingham, Ituzaingó y Tigre. Los más rezagados en porcentaje son Ituzaingó (30,0 %) y Hurlingham (32,6 %).
- **Presión hídrica:** medida en personas, Almirante Brown encabeza (~342 mil) y La Matanza queda segunda (~263 mil) aunque tiene 89,1 % de cobertura. El porcentaje solo no alcanza para priorizar.
- **Residuos vs. agua:** relación débil y no significativa al 5 % (Pearson +0,28, p = 0,26; Spearman +0,41, p = 0,09; n = 18).
- **Modelos:** no superan claramente al baseline. Con Leave-One-Out, `alto_generador` da accuracy 0,56 y `riesgo_cobertura` 0,67 (precisión 0,50, recall 0,17).
- **Estrategias de priorización:**

| Estrategia | Partidos priorizados | Personas sin red cubiertas | % del déficit total |
|---|---|---|---|
| Modelo (regresión logística, promedio) | 2,4 | 209.690 | 13,7 % |
| Regla: cobertura < 75 % | 6 | 1.011.344 | 66,0 % |
| Regla: top 6 por presión hídrica | 6 | 1.171.625 | 76,5 % |

En este análisis, una regla directa sobre el KPI de presión hídrica rinde más que el modelo.

## Limitaciones

- Solo **18 partidos** (los de la concesión de AySA): los modelos son exploratorios y no hay señal predictiva sólida.
- CEAMSE mide **disposición final**, no generación domiciliaria: incluye comercios e industrias del partido.
- La población es **proyectada**, no censal.
- Los datos de Mercado Libre no entran en los modelos; se usan solo en el buscador de terrenos.

## Cómo ampliar

- Bajar a nivel de localidad o radio censal (más de 500 registros).
- Sumar variables como NBI, presupuesto municipal per cápita o densidad de comercios e industrias.
- Incorporar una fuente geoespacial y probar modelos no lineales regularizados (por ejemplo, Random Forest).

## Cómo ejecutarlo

1. Abrir `capstone_proyect.ipynb` en Google Colab.
2. Subir los tres CSV de entrada a la carpeta de trabajo (`/content/`).
3. Ejecutar las celdas **en orden**. Dos advertencias:
   - La celda de carga de Mercado Libre **reasigna la variable `df`**, así que conviene no volver a correr celdas anteriores que dependan de ella sin ejecutar antes la sección de limpieza.
   - La tabla de la sección SROI tiene los valores de la métrica de negocio **escritos a mano**; si cambian los datos o los modelos, hay que actualizarla.
4. El resultado queda en `dataset_inferencia_modelos.csv` (separador `;`, UTF-8).

## Dependencias

`pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `scikit-learn`.
