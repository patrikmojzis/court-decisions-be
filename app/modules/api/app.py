import os

from flask import Flask
from flask_cors import CORS

from app.http_files.controllers.research_websocket_controller import init_socketio
from app.http_files.routes.api import init_routes

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    CORS(app)

    if os.getenv('TEST_ENV'):
        app.config['TESTING'] = True

    init_routes(app)
    init_socketio(app)
    
    return app


def run():
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True if os.getenv('ENV') == "debug" else False)
