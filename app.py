from flask import Flask
import os
import uuid
from config.prod import config
from extensions import celery_init_app


# Initialize Flask app
def create_app(config_class) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(config_class)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    from views import main
    app.register_blueprint(main)
    return app

app = create_app(config)
celery_app = celery_init_app(app)


# Gunicorn entry point
if __name__ != "__main__":
    gunicorn_app = app
