import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'logo'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'favicon'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'classifications'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.routes.auth import bp as auth_bp
    from app.routes.main import bp as main_bp
    from app.routes.schools import bp as schools_bp
    from app.routes.classes import bp as classes_bp
    from app.routes.teachers import bp as teachers_bp
    from app.routes.assignments import bp as assignments_bp
    from app.routes.reports import bp as reports_bp
    from app.routes.users import bp as users_bp
    from app.routes.settings import bp as settings_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(schools_bp, url_prefix='/schools')
    app.register_blueprint(classes_bp, url_prefix='/classes')
    app.register_blueprint(teachers_bp, url_prefix='/teachers')
    app.register_blueprint(assignments_bp, url_prefix='/assignments')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(settings_bp, url_prefix='/settings')

    with app.app_context():
        from app import models
        db.create_all()
        models.seed_admin()

    from app.utils.context_processors import inject_settings
    app.context_processor(inject_settings)

    return app
