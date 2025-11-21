from flask import Flask
from .extensions import db, migrate, jwt, mail
from .config import Config
from app.routes.frontend import frontend_bp
from app.models import client, visit
from app.routes.clients import clients_bp
from app.routes.visits import visits_bp
from app.routes.users import users_bp



def create_app():
    app = Flask(__name__)
    # Configurar la aplicación usando la clase app/config.py
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    #DEGUB! 
    print(f"[DEBUG] Base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Importar modelos
    from app.models import user

    # Registrar blueprints
    
    app.register_blueprint(users_bp, url_prefix="/api/users")

    @app.route('/')
    def home():
        return "SkyNetApp: autenticación JWT activa (fue horrible)... agregando más funcionalidades."
    
    # Aquí se registran las rutas del frontend
    # basicamente haciendo a este blueprint el "frontend" de la app
    app.register_blueprint(frontend_bp)

    app.register_blueprint(clients_bp, url_prefix="/api/clients")

    app.register_blueprint(visits_bp, url_prefix="/api/visits")

    return app


'''from flask import Flask
from .extensions import db, migrate, jwt
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)'''



'''
    # Ruta temporal para probar
    @app.route('/')
    def home():
        return "Servidor Flask + Base de Datos inicializada correctamente "

    from app.models import user  # Importar los modelos para que Flask-Migrate los detecte

    return app'''



'''
    # Importar modelos
    from app.models import user

    # Registrar rutas (blueprints)
    from app.routes.users import users_bp
    app.register_blueprint(users_bp, url_prefix="/api/users")

    @app.route('/')
    def home():
        return "SkyNetApp: autenticación JWT agregada, al menos"

    return app
'''