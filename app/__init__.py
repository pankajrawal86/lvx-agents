from flask import Flask

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    # This is a good place to load configurations from a config file or environment variables
    # For example: app.config.from_object('config.Config')

    # Register blueprints
    from .blueprints import analysis
    app.register_blueprint(analysis.bp)

    # Register the API blueprint
    from .api.routes import api_bp
    app.register_blueprint(api_bp)

    return app
