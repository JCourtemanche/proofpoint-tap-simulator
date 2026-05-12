"""
Click event generator for Proofpoint TAP API Simulator
Generates permitted and blocked click events
"""
import random
from faker import Faker
from .base import (
    generate_guid, generate_email, generate_ip, generate_iso8601_date,
    generate_campaign_id, generate_threat_id, generate_message_id,
    generate_malicious_url, generate_user_agent
)
from config import Config

fake = Faker()


def generate_click(click_type='permitted', threat_statuses=None,
                  start_time=None, end_time=None):
    """
    Generate a click event (permitted or blocked)

    Args:
        click_type: 'permitted' or 'blocked'
        threat_statuses: List of allowed threat statuses for filtering
        start_time: Start of time window (datetime object)
        end_time: End of time window (datetime object)

    Returns:
        Dictionary representing a click event
    """
    if threat_statuses is None:
        threat_statuses = ['active', 'cleared', 'falsePositive']

    guid = generate_guid()
    threat_id = generate_threat_id()
    message_id = generate_message_id()

    click_time = generate_iso8601_date(start_time, end_time)
    threat_time = generate_iso8601_date(start_time, end_time)

    sender_email = generate_email(hashed=True)
    recipient_email = generate_email(hashed=True)

    click = {
        'GUID': guid,
        'id': guid,
        'messageID': message_id,

        # URL information
        'url': generate_malicious_url(),
        'classification': random.choice(['Malware', 'Phish', 'Spam']),

        # Timestamps
        'clickTime': click_time,
        'threatTime': threat_time,

        # Threat information
        'threatID': threat_id,
        'threatStatus': random.choice(threat_statuses),
        'threatURL': f"{Config.TAP_DASHBOARD_URL}/#/threat/detail/{threat_id}",

        # Sender/Recipient
        'sender': sender_email,
        'senderIP': generate_ip(internal=False),
        'recipient': recipient_email,

        # Click source
        'clickIP': generate_ip(internal=False),
        'userAgent': generate_user_agent()
    }

    # Add campaign ID (50% chance)
    if random.random() < 0.5:
        click['campaignId'] = generate_campaign_id()

    return click


def generate_clicks(count=1, click_type='permitted', threat_statuses=None,
                   start_time=None, end_time=None):
    """
    Generate multiple click events

    Args:
        count: Number of clicks to generate
        click_type: 'permitted' or 'blocked'
        threat_statuses: List of allowed threat statuses
        start_time: Start of time window
        end_time: End of time window

    Returns:
        List of click dictionaries
    """
    return [
        generate_click(click_type, threat_statuses, start_time, end_time)
        for _ in range(count)
    ]
