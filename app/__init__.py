from flask import Flask

from .config import get_config
from .extensions import db, migrate


def create_app() -> Flask:
    app = Flask(__name__)

    config_class = get_config()
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes.main import bp as main_bp
    from .routes.shop import bp as shop_bp
    from .routes.auth import bp as auth_bp
    from .routes.admin import bp as admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(shop_bp, url_prefix="/shop")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
