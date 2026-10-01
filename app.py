from flask import Flask
from config import Config
from extensions import db, migrate, mail
# from scheduler import start_scheduler
from datetime import datetime


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Import Models
    from models.store import Store
    from models.category import Category
    from models.deal import Deal
    from models.blog import Blog
    from models.product_queue import ProductQueue

    # Register Blueprints  3JwhiPJZw1qofnRjeEgSjgxL6r9_4KGtY3HakR5ZvczaFPJeL
    from routes.admin import admin
    from routes.main import main
    from routes.api import api
    from routes.ai_api import ai_api

    app.register_blueprint(admin)
    app.register_blueprint(main)
    app.register_blueprint(api)
    app.register_blueprint(ai_api)

    # Scheduler disabled - runs separately when explicitly required.
    pass

    # ====================================
    # Global Categories
    # ====================================
    @app.context_processor
    def inject_categories():

        categories = Category.query.order_by(Category.name).all()

        return dict(categories=categories)

    # ====================================
    # Current Year
    # ====================================
    @app.context_processor
    def inject_year():

        return dict(current_year=datetime.now().year)

    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
