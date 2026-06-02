from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    from app.routes.chat import chat_bp
    from app.routes.health import health_bp
    app.register_blueprint(chat_bp)
    app.register_blueprint(health_bp)
    return app
