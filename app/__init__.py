"""Application factory for the Flask starter project."""

from flask import Flask

from app.config import config
from app.extensions import db
from app.routes.main import main_bp


def create_app(config_name: str | None = None, **kwargs) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    selected_config = config_name or "development"
    app.config.from_object(config[selected_config])
    app.config.update(kwargs)

    db.init_app(app)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app
