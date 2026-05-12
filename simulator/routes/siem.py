"""
SIEM endpoints for Proofpoint TAP API Simulator
Handles all /v2/siem/* endpoints
"""
import random
from flask import Blueprint, request, jsonify
from auth import require_basic_auth
from validators.params import (
    validate_time_params, validate_threat_type, validate_threat_status,
    validate_format, parse_since_time, parse_since_seconds
)
from generators.base import parse_iso8601_interval
from generators.messages import generate_messages
from generators.clicks import generate_clicks
from config import Config

siem_bp = Blueprint('siem', __name__, url_prefix='/v2/siem')


def parse_time_parameters():
    """
    Parse and validate time parameters from request

    Returns:
        Tuple of (start_time, end_time) as datetime objects

    Raises:
        ValueError: If parameters are invalid
    """
    interval = request.args.get('interval')
    since_time = request.args.get('sinceTime')
    since_seconds = request.args.get('sinceSeconds')

    param_name, param_value = validate_time_params(interval, since_time, since_seconds)

    if param_name == 'interval':
        start_time, end_time = parse_iso8601_interval(param_value)
    elif param_name == 'sinceTime':
        start_time = parse_since_time(param_value)
        from datetime import datetime
        end_time = datetime.utcnow()
    elif param_name == 'sinceSeconds':
        start_time, end_time = parse_since_seconds(param_value)

    return (start_time, end_time)


@siem_bp.route('/all', methods=['GET'])
@require_basic_auth
def get_all_events():
    """
    GET /v2/siem/all
    Returns all SIEM events (messages and clicks, both delivered/blocked and permitted/blocked)
    """
    try:
        # Validate format parameter
        format_param = request.args.get('format', 'json')
        validate_format(format_param)

        # Parse time parameters
        start_time, end_time = parse_time_parameters()

        # Parse threat filters (optional)
        threat_type = request.args.get('threatType')
        threat_status = request.args.get('threatStatus')

        threat_types = None
        threat_statuses = None

        if threat_type:
            threat_types = validate_threat_type(threat_type.split(','))

        if threat_status:
            threat_statuses = validate_threat_status(threat_status.split(','))

        # Generate random counts for each event type
        delivered_count = random.randint(Config.MIN_EVENTS_COUNT, Config.MAX_EVENTS_COUNT)
        blocked_count = random.randint(Config.MIN_EVENTS_COUNT, Config.MAX_EVENTS_COUNT)
        clicks_permitted_count = random.randint(Config.MIN_EVENTS_COUNT, Config.MAX_EVENTS_COUNT)
        clicks_blocked_count = random.randint(Config.MIN_EVENTS_COUNT, Config.MAX_EVENTS_COUNT)

        # Generate events
        response = {
            'messagesDelivered': generate_messages(
                delivered_count, 'delivered', threat_types, threat_statuses, start_time, end_time
            ),
            'messagesBlocked': generate_messages(
                blocked_count, 'blocked', threat_types, threat_statuses, start_time, end_time
            ),
            'clicksPermitted': generate_clicks(
                clicks_permitted_count, 'permitted', threat_statuses, start_time, end_time
            ),
            'clicksBlocked': generate_clicks(
                clicks_blocked_count, 'blocked', threat_statuses, start_time, end_time
            )
        }

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@siem_bp.route('/issues', methods=['GET'])
@require_basic_auth
def get_issues():
    """
    GET /v2/siem/issues
    Returns issues (delivered messages with threats and permitted clicks)
    """
    try:
        validate_format(request.args.get('format', 'json'))
        start_time, end_time = parse_time_parameters()

        threat_type = request.args.get('threatType')
        threat_status = request.args.get('threatStatus')

        threat_types = validate_threat_type(threat_type.split(',')) if threat_type else None
        threat_statuses = validate_threat_status(threat_status.split(',')) if threat_status else None

        delivered_count = random.randint(Config.MIN_EVENTS_COUNT, Config.MAX_EVENTS_COUNT)
        clicks_permitted_count = random.randint(Config.MIN_EVENTS_COUNT, Config.MAX_EVENTS_COUNT)

        response = {
            'messagesDelivered': generate_messages(
                delivered_count, 'delivered', threat_types, threat_statuses, start_time, end_time
            ),
            'clicksPermitted': generate_clicks(
                clicks_permitted_count, 'permitted', threat_statuses, start_time, end_time
            )
        }

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@siem_bp.route('/clicks/permitted', methods=['GET'])
@require_basic_auth
def get_clicks_permitted():
    """GET /v2/siem/clicks/permitted"""
    try:
        validate_format(request.args.get('format', 'json'))
        start_time, end_time = parse_time_parameters()

        threat_status = request.args.get('threatStatus')
        threat_statuses = validate_threat_status(threat_status.split(',')) if threat_status else None

        count = random.randint(Config.MIN_EVENTS_COUNT, Config.MAX_EVENTS_COUNT)

        response = {
            'clicksPermitted': generate_clicks(count, 'permitted', threat_statuses, start_time, end_time)
        }

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@siem_bp.route('/clicks/blocked', methods=['GET'])
@require_basic_auth
def get_clicks_blocked():
    """GET /v2/siem/clicks/blocked"""
    try:
        validate_format(request.args.get('format', 'json'))
        start_time, end_time = parse_time_parameters()

        threat_status = request.args.get('threatStatus')
        threat_statuses = validate_threat_status(threat_status.split(',')) if threat_status else None

        count = random.randint(Config.MIN_EVENTS_COUNT, Config.MAX_EVENTS_COUNT)

        response = {
            'clicksBlocked': generate_clicks(count, 'blocked', threat_statuses, start_time, end_time)
        }

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@siem_bp.route('/messages/delivered', methods=['GET'])
@require_basic_auth
def get_messages_delivered():
    """GET /v2/siem/messages/delivered"""
    try:
        validate_format(request.args.get('format', 'json'))
        start_time, end_time = parse_time_parameters()

        threat_type = request.args.get('threatType')
        threat_status = request.args.get('threatStatus')

        threat_types = validate_threat_type(threat_type.split(',')) if threat_type else None
        threat_statuses = validate_threat_status(threat_status.split(',')) if threat_status else None

        count = random.randint(Config.MIN_EVENTS_COUNT, Config.MAX_EVENTS_COUNT)

        response = {
            'messagesDelivered': generate_messages(
                count, 'delivered', threat_types, threat_statuses, start_time, end_time
            )
        }

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@siem_bp.route('/messages/blocked', methods=['GET'])
@require_basic_auth
def get_messages_blocked():
    """GET /v2/siem/messages/blocked"""
    try:
        validate_format(request.args.get('format', 'json'))
        start_time, end_time = parse_time_parameters()

        threat_type = request.args.get('threatType')
        threat_status = request.args.get('threatStatus')

        threat_types = validate_threat_type(threat_type.split(',')) if threat_type else None
        threat_statuses = validate_threat_status(threat_status.split(',')) if threat_status else None

        count = random.randint(Config.MIN_EVENTS_COUNT, Config.MAX_EVENTS_COUNT)

        response = {
            'messagesBlocked': generate_messages(
                count, 'blocked', threat_types, threat_statuses, start_time, end_time
            )
        }

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
