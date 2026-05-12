"""
People endpoints for Proofpoint TAP API Simulator
Handles VAP and Top Clickers endpoints
"""
import random
from flask import Blueprint, request, jsonify
from auth import require_basic_auth
from validators.params import validate_window, validate_pagination
from generators.people import generate_vap_response, generate_top_clickers_response
from config import Config

people_bp = Blueprint('people', __name__, url_prefix='/v2/people')


@people_bp.route('/vap', methods=['GET'])
@require_basic_auth
def get_vap():
    """
    GET /v2/people/vap
    Retrieve Very Attacked People (most attacked users)

    Query parameters:
        - window: Time window in days ('14', '30', '90') - required
        - page: Page number (optional, default 1)
        - size: Page size (optional, default 1000)
    """
    try:
        # Validate window parameter
        window = request.args.get('window')
        if not window:
            return jsonify({'error': 'window parameter is required'}), 400

        window = validate_window(window)

        # Parse pagination
        page_str = request.args.get('page', '1')
        size_str = request.args.get('size', '1000')

        page, size = validate_pagination(page_str, size_str, max_size=10000)

        # Generate VAP users
        total_users = random.randint(Config.MIN_USERS, Config.MAX_USERS)

        # Apply pagination
        start_idx = (page - 1) * size
        actual_count = min(size, max(0, total_users - start_idx))

        response = generate_vap_response(actual_count, window)
        response['totalVapUsers'] = total_users

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@people_bp.route('/top-clickers', methods=['GET'])
@require_basic_auth
def get_top_clickers():
    """
    GET /v2/people/top-clickers
    Retrieve top clickers (users who click on the most threats)

    Query parameters:
        - window: Time window in days ('14', '30', '90') - required
        - page: Page number (optional, default 1)
        - size: Page size (optional, default 100, max 200)
    """
    try:
        # Validate window parameter
        window = request.args.get('window')
        if not window:
            return jsonify({'error': 'window parameter is required'}), 400

        window = validate_window(window)

        # Parse pagination
        page_str = request.args.get('page', '1')
        size_str = request.args.get('size', '100')

        page, size = validate_pagination(page_str, size_str, max_size=200)

        # Generate top clickers
        total_users = random.randint(Config.MIN_USERS, Config.MAX_USERS)

        # Apply pagination
        start_idx = (page - 1) * size
        actual_count = min(size, max(0, total_users - start_idx))

        response = generate_top_clickers_response(actual_count, window)
        response['totalTopClickers'] = total_users

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
