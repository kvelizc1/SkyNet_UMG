FROM python:3.12-slim

# Evitar buffers en logs
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements e instalarlos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el todo del proyecto
COPY . /app/

# Exponer el puerto donde correrá Gunicorn (Flask pero para producción)
#EXPOSE 8000
EXPOSE 5050

# Ejecutar el app
CMD ["python", "run.py"]

#Comando de inicio (Gunicorn, usando create_app)
#CMD ["gunicorn", "-b", "0.0.0.0:5050", "run:app"]

