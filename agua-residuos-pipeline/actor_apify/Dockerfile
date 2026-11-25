# Imagen base de Apify para Python
FROM apify/actor-python:3.12

# Dependencias
COPY requirements.txt ./
RUN echo "Versiones de Python y pip:" && python --version && pip --version \
    && pip install -r requirements.txt

# Código y datos de entrenamiento
COPY . ./

# El modelo se entrena al iniciar (18 filas: tarda milisegundos), así no hay archivos binarios
# que dependan de la versión de scikit-learn.
CMD ["python3", "-m", "src"]
