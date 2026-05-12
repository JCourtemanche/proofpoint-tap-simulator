"""
Proofpoint TAP API Simulator
Main Flask application
"""
import logging
from flask import Flask, jsonify
from config import Config

# Import blueprints
from routes.siem import siem_bp
from routes.forensics import forensics_bp
from routes.campaigns import campaigns_bp
from routes.people import people_bp
from routes.utils import utils_bp


def create_app():
    """Create and configure the Flask application"""

    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO if Config.DEBUG else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting Proofpoint TAP API Simulator")
    logger.info(f"Debug mode: {Config.DEBUG}")
    logger.info(f"Listening on {Config.HOST}:{Config.PORT}")

    # Register blueprints
    app.register_blueprint(siem_bp)
    app.register_blueprint(forensics_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(people_bp)
    app.register_blueprint(utils_bp)

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'Proofpoint TAP API Simulator',
            'version': '1.0.0'
        }), 200

    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint"""
        return jsonify({
            'service': 'Proofpoint TAP API Simulator',
            'version': '1.0.0',
            'endpoints': {
                'siem': {
                    'GET /v2/siem/all': 'Get all SIEM events',
                    'GET /v2/siem/issues': 'Get issues',
                    'GET /v2/siem/clicks/permitted': 'Get permitted clicks',
                    'GET /v2/siem/clicks/blocked': 'Get blocked clicks',
                    'GET /v2/siem/messages/delivered': 'Get delivered messages',
                    'GET /v2/siem/messages/blocked': 'Get blocked messages'
                },
                'forensics': {
                    'GET /v2/forensics': 'Get forensics evidence'
                },
                'campaigns': {
                    'GET /v2/campaign/ids': 'List campaign IDs',
                    'GET /v2/campaign/{id}': 'Get campaign details'
                },
                'people': {
                    'GET /v2/people/vap': 'Get Very Attacked People',
                    'GET /v2/people/top-clickers': 'Get top clickers'
                },
                'utils': {
                    'POST /v2/url/decode': 'Decode Proofpoint URLs'
                }
            },
            'authentication': 'HTTP Basic Auth required',
            'default_credentials': {
                'username': Config.AUTH_USERNAME,
                'password': '***'
            }
        }), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

    return app


# Create the application instance
app = create_app()


if __name__ == '__main__':
    # Run the application
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
