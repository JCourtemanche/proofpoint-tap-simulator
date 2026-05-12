"""
Campaign endpoints for Proofpoint TAP API Simulator
"""
import random
from flask import Blueprint, request, jsonify
from auth import require_basic_auth
from validators.params import validate_pagination, validate_format
from generators.base import parse_iso8601_interval
from generators.campaigns import generate_campaigns, generate_campaign_details
from config import Config

campaigns_bp = Blueprint('campaigns', __name__, url_prefix='/v2/campaign')


@campaigns_bp.route('/ids', methods=['GET'])
@require_basic_auth
def get_campaign_ids():
    """
    GET /v2/campaign/ids
    Retrieve list of campaign IDs active in a time window

    Query parameters:
        - format: 'json' (required)
        - interval: ISO8601 interval (required)
        - page: Page number (optional, default 1)
        - size: Page size (optional, default 100, max 200)
    """
    try:
        # Validate format
        format_param = request.args.get('format', 'json')
        validate_format(format_param)

        # Parse interval
        interval = request.args.get('interval')
        if not interval:
            return jsonify({'error': 'interval parameter is required'}), 400

        start_time, end_time = parse_iso8601_interval(interval)

        # Parse pagination
        page_str = request.args.get('page', '1')
        size_str = request.args.get('size', '100')

        page, size = validate_pagination(page_str, size_str, max_size=200)

        # Generate campaigns
        total_campaigns = random.randint(Config.MIN_CAMPAIGNS, Config.MAX_CAMPAIGNS)
        all_campaigns = generate_campaigns(total_campaigns, start_time, end_time)

        # Apply pagination
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_campaigns = all_campaigns[start_idx:end_idx]

        response = {
            'campaigns': paginated_campaigns
        }

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@campaigns_bp.route('/<campaign_id>', methods=['GET'])
@require_basic_auth
def get_campaign(campaign_id):
    """
    GET /v2/campaign/{campaign_id}
    Retrieve details of a specific campaign
    """
    try:
        # Generate campaign details
        campaign = generate_campaign_details(campaign_id)

        return jsonify(campaign), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
