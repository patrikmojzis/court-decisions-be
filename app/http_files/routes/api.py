from flask import Flask

from app.http_files.controllers import user_controller, sign_in_with_apple_controller, sign_in_with_google_controller, \
    auth_controller, research_controller


def init_routes(app: Flask) -> None:
    
    app.route('/user', methods=['GET'])(user_controller.current)
    app.route('/user', methods=['DELETE'])(user_controller.destroy)
    app.route('/user', methods=['PATCH'])(user_controller.update)
    app.route('/auth', methods=['DELETE'])(auth_controller.destroy)
    app.route('/auth/password', methods=['POST'])(auth_controller.sign_in_with_password) 
    app.route('/auth/apple', methods=['POST'], endpoint='apple_signin')(sign_in_with_apple_controller.store)
    app.route('/auth/google', methods=['POST'], endpoint='google_signin')(sign_in_with_google_controller.store)
    
    app.route('/research', methods=['POST'])(research_controller.store)
    app.route('/research', methods=['GET'])(research_controller.index)
    app.route('/research/<research_id>', methods=['GET'])(research_controller.show)
    app.route('/research/<research_id>', methods=['DELETE'])(research_controller.destroy)
    
    

