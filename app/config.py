# Ajustes que afectan el comportamiento GLOBAL del app.
import os
# Para leer variables de entorno desde un archivo .env
import os
from dotenv import load_dotenv

#Carga las variables de entorno desde el archivo .env en la raíz del proyecto
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Guardar datos de sesión entre peticiones (session["user"])
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-dev")
    # String de conexión a la base de datos 
    # Use DATABASE_URL si existe; si no, usa el otro valor por defecto.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, '..','instance', 'skynet.db')}")
    #SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///instance/skynet.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-clave-secreta")
    # Clave para el API de Google Maps
    GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    # Envío de correos
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
    # URL del backend, para el cliente API
    BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")





'''
# Ajustes que afectan el comportamiento GLOBAL del app.
import os
# Para leer variables de entorno desde un archivo .env
from dotenv import load_dotenv

#Carga las variables de entorno desde el archivo .env en la raíz del proyecto
load_dotenv() 

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-dev")
    # String de conexión a la base de datos 
    # Use DATABASE_URL si existe; si no, usa el otro valor por defecto.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, '..','instance', 'skynet.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-clave-secreta")
'''


# Alternativa simple (sin usar dotenv)
'''
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///skynet.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False'''

