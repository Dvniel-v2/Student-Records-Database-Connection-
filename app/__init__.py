"""Application factory for the Student Records application."""

from flask import Flask

from app.config import config
from app.extensions import db, migrate
from app.routes.health import health_bp
from app.routes.main import main_bp


def create_app(config_name: str | None = None, **kwargs) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    selected_config = config_name or "development"
    app.config.from_object(config[selected_config])
    app.config.update(kwargs)

    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(health_bp)
    app.register_blueprint(main_bp)

    return app
