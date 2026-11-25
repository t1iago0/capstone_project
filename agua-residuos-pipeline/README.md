# Pipeline de agua y residuos en el AMBA

Extracción, limpieza, modelado e inferencia de la relación entre cobertura de agua (AySA) y residuos enviados a disposición final (CEAMSE) en los 18 partidos del AMBA que atiende AySA. El modelo de inferencia se publica como un Actor de Apify.

## 1. Arquitectura y flujo

```
Trigger (manual, n8n)
   -> Extracción (n8n + Apify: link del CSV de AySA; HTTP: CSV de CEAMSE)
   -> Carga (carpeta de Google Drive: data/raw)
   -> ETL (limpieza, normalización de nombres, cruce por partido)      scripts/generar_dataset_modelo.py
   -> Preprocesamiento (validación y variables del modelo)            actor_apify/src/preprocessing.py
   -> Inferencia (2 regresiones logísticas)                           actor_apify/src/inference.py
   -> Destino (dataset del Actor en Apify)
```

## 2. Estructura del repositorio

```
agua-residuos-pipeline/
├── actor_apify/                 # Actor de inferencia (se sube a Apify)
│   ├── .actor/actor.json
│   ├── .actor/input_schema.json
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── README.md
│   ├── data/partidos_modelo.csv # datos de entrenamiento (18 partidos)
│   └── src/
│       ├── __main__.py          # punto de entrada
│       ├── main.py              # lee la entrada y guarda los resultados
│       ├── preprocessing.py     # validación y variables derivadas
│       ├── entrenar.py          # entrenamiento de los modelos
│       └── inference.py         # predicción
├── colabs/                      # notebook de análisis (agregar acá el .ipynb)
├── data/
│   ├── raw/                     # CSV originales de AySA y CEAMSE
│   └── processed/               # partidos_modelo.csv
├── scripts/generar_dataset_modelo.py
└── README.md
```

## 3. Funciones de ETL, preprocesamiento y modelo

| Función | Entrada | Salida | Descripción |
|---|---|---|---|
| `extraer()` | CSV crudos | Tablas de CEAMSE y AySA | Lee y normaliza números y nombres; descarta subtotales y partidos combinados |
| `transformar()` | Tablas limpias | Tabla por partido | Cruza por partido, calcula cobertura, kg per cápita y los targets |
| `validar_registro()` | Datos de un municipio | Datos validados | Controla rangos y tipos |
| `calcular_features()` | Datos validados | Variables del modelo | `log_poblacion`, `kg_per_capita` |
| `entrenar()` | `partidos_modelo.csv` | 2 modelos + métricas | Regresión logística con estandarización; métricas leave-one-out |
| `predecir()` | Datos de un municipio | Predicciones y confianza | Aplica preprocesamiento e inferencia |

**Modelo seleccionado:** regresión logística. Con 18 observaciones, un modelo simple es lo único razonable; los modelos más complejos sobreajustan.

## 4. Contrato del Actor de inferencia

| Campo | Dirección | Tipo | Descripción |
|---|---|---|---|
| `poblacion` | input | integer | Habitantes del municipio |
| `cobertura_agua_pct` | input | number | Cobertura de agua de red (0 a 100) |
| `toneladas_residuos_anuales` | input | number | Toneladas anuales a disposición final |
| `municipios` | input | array | Lista opcional de municipios |
| `prediccion_alto_generador` | output | integer | 1 si supera la mediana de kg per cápita |
| `confianza_alto_generador_pct` | output | float | Probabilidad estimada (%) |
| `prediccion_riesgo_cobertura` | output | integer | 1 si la cobertura sería menor a 75% |
| `confianza_riesgo_cobertura_pct` | output | float | Probabilidad estimada (%) |

## 5. Métricas

- **Negocio:** personas sin agua de red en los partidos priorizados, medido como porcentaje del déficit total (1.532.263 personas en los 18 partidos). Ver la sección de métrica de negocio del notebook.
- **Modelo** (validación leave-one-out, n = 18): `alto_generador` accuracy 0,56 (baseline 0,50); `riesgo_cobertura` accuracy 0,67 (baseline 0,67), recall 0,17. No superan claramente al baseline: es un modelo exploratorio.

## 6. Costo computacional de una corrida

A completar después de la primera corrida en Apify (Console > Runs > pestaña de uso): tiempo por corrida, memoria y costo en USD.

## 7. Cómo correr el proyecto

1. **Regenerar los datos de entrenamiento** (opcional): `python scripts/generar_dataset_modelo.py`.
2. **Probar el Actor en tu computadora:**
   ```
   cd actor_apify
   python -m venv .venv && source .venv/bin/activate      # en Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   mkdir -p storage/key_value_stores/default
   echo '{"poblacion": 250000, "cobertura_agua_pct": 50, "toneladas_residuos_anuales": 95000}' > storage/key_value_stores/default/INPUT.json
   apify run
   ```
   El resultado queda en `storage/datasets/default/`.
3. **Subirlo a Apify:**
   ```
   npm install -g apify-cli
   apify login
   cd actor_apify
   apify push
   ```
4. En Apify Console, Actors > Mis Actors, abrir el Actor, completar el formulario de entrada y tocar **Start**.
5. Notebook de análisis: abrir `colabs/` en Google Colab.
