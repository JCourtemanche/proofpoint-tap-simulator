"""
Utility endpoints for Proofpoint TAP API Simulator
"""
import re
from urllib.parse import unquote
from flask import Blueprint, request, jsonify
from auth import require_basic_auth

utils_bp = Blueprint('utils', __name__, url_prefix='/v2/url')


@utils_bp.route('/decode', methods=['POST'])
@require_basic_auth
def decode_urls():
    """
    POST /v2/url/decode
    Decode Proofpoint-rewritten URLs

    Request body:
        {
          "urls": ["encoded_url1", "encoded_url2", ...]
        }

    Response:
        {
          "urls": [
            {
              "encodedUrl": "...",
              "decodedUrl": "...",
              "success": true
            },
            ...
          ]
        }
    """
    try:
        # Parse request body
        data = request.get_json()

        if not data or 'urls' not in data:
            return jsonify({'error': 'Request body must contain "urls" array'}), 400

        urls = data['urls']

        if not isinstance(urls, list):
            return jsonify({'error': '"urls" must be an array'}), 400

        # Process each URL
        results = []

        for encoded_url in urls:
            decoded_url = decode_proofpoint_url(encoded_url)

            result = {
                'encodedUrl': encoded_url,
                'decodedUrl': decoded_url,
                'success': True
            }

            results.append(result)

        response = {
            'urls': results
        }

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


def decode_proofpoint_url(encoded_url):
    """
    Decode a Proofpoint URL-rewritten link

    Proofpoint URLs typically look like:
    https://urldefense.proofpoint.com/v2/url?u=http-3A__example.com&d=...&c=...

    This function extracts the original URL from the 'u' parameter.

    Args:
        encoded_url: Proofpoint-encoded URL

    Returns:
        Decoded original URL
    """
    # Check if it's a Proofpoint URL
    if 'urldefense.proofpoint.com' not in encoded_url and 'urldefense.com' not in encoded_url:
        # Not a Proofpoint URL, return as-is
        return encoded_url

    # Extract the 'u' parameter
    match = re.search(r'[?&]u=([^&]+)', encoded_url)

    if not match:
        # Can't find 'u' parameter, return as-is
        return encoded_url

    encoded_part = match.group(1)

    # Decode URL encoding
    decoded = unquote(encoded_part)

    # Replace Proofpoint encoding: -3A → :, __→ /, -2E → .
    decoded = decoded.replace('-3A', ':')
    decoded = decoded.replace('__', '/')
    decoded = decoded.replace('_', '/')
    decoded = decoded.replace('-2E', '.')
    decoded = decoded.replace('-2D', '-')
    decoded = decoded.replace('-5F', '_')

    # Handle http-3A pattern
    decoded = re.sub(r'http-3A', 'http:', decoded)
    decoded = re.sub(r'https-3A', 'https:', decoded)

    return decoded
