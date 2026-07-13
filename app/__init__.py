"""Application factory for UniRecords."""

from flask import Flask

from app.config import config
from app.extensions import db
from app.routes.health import health_bp
from app.routes.main import main_bp
from app.security.csrf import csrf_token


def create_app(config_name: str | None = None, **kwargs) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    selected_config = config_name or "development"
    app.config.from_object(config[selected_config])
    app.config.update(kwargs)

    db.init_app(app)
    app.jinja_env.globals["csrf_token"] = csrf_token
    app.register_blueprint(health_bp)
    app.register_blueprint(main_bp)

    return app
