FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements e instalarlos
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el todo del proyecto
COPY . .

# Exponer el puerto donde correrá Gunicorn (Flask pero para producción)
EXPOSE 8000

# Comando de inicio (Gunicorn, usando tu create_app)
CMD ["gunicorn", "-b", "0.0.0.0:8000", "run:app"]
