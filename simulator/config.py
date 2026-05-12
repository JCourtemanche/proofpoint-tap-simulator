"""
Configuration module for Proofpoint TAP API Simulator
"""
import os

class Config:
    """Application configuration"""

    # Flask configuration
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8080))

    # Authentication credentials
    AUTH_USERNAME = os.environ.get('AUTH_USERNAME', 'test-principal')
    AUTH_PASSWORD = os.environ.get('AUTH_PASSWORD', 'test-secret')

    # Data generation parameters
    MIN_EVENTS_COUNT = int(os.environ.get('MIN_EVENTS_COUNT', 1))
    MAX_EVENTS_COUNT = int(os.environ.get('MAX_EVENTS_COUNT', 10))

    # Proofpoint TAP dashboard base URL (for threatUrl fields)
    TAP_DASHBOARD_URL = os.environ.get('TAP_DASHBOARD_URL', 'https://threatinsight.proofpoint.com')

    # Campaign generation
    MIN_CAMPAIGNS = int(os.environ.get('MIN_CAMPAIGNS', 5))
    MAX_CAMPAIGNS = int(os.environ.get('MAX_CAMPAIGNS', 20))

    # People generation
    MIN_USERS = int(os.environ.get('MIN_USERS', 10))
    MAX_USERS = int(os.environ.get('MAX_USERS', 50))
