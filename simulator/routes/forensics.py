"""
Forensics endpoints for Proofpoint TAP API Simulator
"""
from flask import Blueprint, request, jsonify
from auth import require_basic_auth
from generators.forensics import generate_forensics_report

forensics_bp = Blueprint('forensics', __name__, url_prefix='/v2/forensics')


@forensics_bp.route('', methods=['GET'])
@require_basic_auth
def get_forensics():
    """
    GET /v2/forensics
    Retrieve forensics evidence for a threat or campaign

    Query parameters:
        - threatId: Threat ID (mutually exclusive with campaignId)
        - campaignId: Campaign ID (mutually exclusive with threatId)
        - includeCampaignForensics: Boolean (only valid with threatId)
    """
    try:
        threat_id = request.args.get('threatId')
        campaign_id = request.args.get('campaignId')
        include_campaign = request.args.get('includeCampaignForensics')

        # Validation: threatId and campaignId are mutually exclusive
        if threat_id and campaign_id:
            return jsonify({'error': 'threatId and campaignId are mutually exclusive'}), 400

        # Validation: at least one must be provided
        if not threat_id and not campaign_id:
            return jsonify({'error': 'Either threatId or campaignId must be provided'}), 400

        # Validation: includeCampaignForensics only with threatId
        if include_campaign and campaign_id:
            return jsonify({'error': 'includeCampaignForensics can only be used with threatId'}), 400

        # Generate forensics report
        report = generate_forensics_report(threat_id=threat_id, campaign_id=campaign_id)

        return jsonify(report), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
