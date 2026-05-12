"""
Message generator for Proofpoint TAP API Simulator
Generates delivered and blocked message events
"""
import random
from faker import Faker
from .base import (
    generate_guid, generate_email, generate_ip, generate_iso8601_date,
    generate_campaign_id, generate_threat_id, generate_message_id,
    generate_malicious_url, generate_sha256, generate_md5
)
from config import Config

fake = Faker()


def generate_threat_info(threat_types=None, threat_statuses=None, timestamp=None):
    """
    Generate a threat info object for threatsInfoMap

    Args:
        threat_types: List of allowed threat types (default: all)
        threat_statuses: List of allowed threat statuses (default: all)
        timestamp: Base timestamp for threat events

    Returns:
        Dictionary representing a threat
    """
    if threat_types is None:
        threat_types = ['url', 'attachment', 'messageText']
    if threat_statuses is None:
        threat_statuses = ['active', 'cleared', 'falsePositive']

    threat_type = random.choice(threat_types)
    threat_status = random.choice(threat_statuses)
    threat_id = generate_threat_id()

    threat_info = {
        'threatID': threat_id,
        'threatStatus': threat_status,
        'threatTime': timestamp or generate_iso8601_date(),
        'threatType': threat_type,
        'threatUrl': f"{Config.TAP_DASHBOARD_URL}/#/threat/detail/{threat_id}",
        'classification': random.choice(['Malware', 'Phish', 'Spam'])
    }

    # Add threat-specific fields
    if threat_type == 'url':
        threat_info['threat'] = generate_malicious_url()
    elif threat_type == 'attachment':
        threat_info['threat'] = generate_sha256()
    elif threat_type == 'messageText':
        threat_info['threat'] = generate_email(hashed=False)

    # Add campaign ID (50% chance)
    if random.random() < 0.5:
        threat_info['campaignID'] = generate_campaign_id()

    return threat_info


def generate_message(message_type='delivered', threat_types=None, threat_statuses=None,
                    start_time=None, end_time=None):
    """
    Generate a message event (delivered or blocked)

    Args:
        message_type: 'delivered' or 'blocked'
        threat_types: List of allowed threat types for filtering
        threat_statuses: List of allowed threat statuses for filtering
        start_time: Start of time window (datetime object)
        end_time: End of time window (datetime object)

    Returns:
        Dictionary representing a message event
    """
    guid = generate_guid()
    qid = fake.bothify(text='??########').upper()
    message_id = generate_message_id()
    message_time = generate_iso8601_date(start_time, end_time)

    sender_email = generate_email(hashed=True)
    recipient_emails = [generate_email(hashed=True) for _ in range(random.randint(1, 3))]
    cc_emails = [generate_email(hashed=True) for _ in range(random.randint(0, 2))] if random.random() < 0.3 else []

    subject = fake.sentence(nb_words=random.randint(4, 10)).rstrip('.')

    message = {
        'GUID': guid,
        'QID': qid,
        'id': guid,
        'messageID': message_id,
        'messageTime': message_time,
        'messageSize': random.randint(5000, 500000),
        'subject': subject,

        # Sender info
        'sender': sender_email,
        'senderIP': generate_ip(internal=False),
        'fromAddress': [sender_email],
        'headerFrom': f'"{fake.name()}" <{sender_email}>',

        # Recipients
        'recipient': recipient_emails,
        'toAddresses': recipient_emails,
        'headerTo': ', '.join([f'"{fake.name()}" <{email}>' for email in recipient_emails]),

        # CC recipients
        'ccAddresses': cc_emails,
        'headerCC': ', '.join([f'"{fake.name()}" <{email}>' for email in cc_emails]) if cc_emails else '',

        # Reply-To (30% chance)
        'replyToAddress': [] if random.random() > 0.3 else [generate_email(hashed=True)],
        'headerReplyTo': '' if random.random() > 0.3 else f'"{fake.name()}" <{generate_email(hashed=True)}>',

        # X-Mailer
        'xmailer': random.choice([
            'Microsoft Outlook 16.0', 'Apple Mail (2.3654.60.0.1)',
            'Mozilla Thunderbird 78.11.0', 'Gmail', ''
        ]),

        # Scores
        'spamScore': random.randint(0, 100),
        'phishScore': random.randint(0, 100),
        'malwareScore': random.randint(0, 100),
        'impostorScore': random.randint(0, 100),

        # Processing info
        'cluster': random.choice(['cluster1', 'cluster2', 'cluster3']),
        'clusterId': random.choice(['hosted', 'on-premise']),
        'modulesRun': random.sample(['av', 'spam', 'dkim', 'spf', 'dmarc', 'urldefense'], k=random.randint(3, 6)),
        'policyRoutes': [random.choice(['default', 'inbound', 'outbound', 'internal'])],

        # Completely rewritten flag
        'completelyRewritten': random.choice(['true', 'false', 'na']),

        # Threats (0-3 threats)
        'threatsInfoMap': []
    }

    # Generate threats (30% no threats, 70% 1-3 threats)
    if random.random() < 0.7:
        num_threats = random.randint(1, 3)
        for _ in range(num_threats):
            threat_info = generate_threat_info(threat_types, threat_statuses, message_time)
            message['threatsInfoMap'].append(threat_info)

    # Add blocked-specific fields
    if message_type == 'blocked':
        message['quarantineFolder'] = random.choice(['Quarantine', 'Spam', 'Malware', 'Phish'])
        message['quarantineRule'] = random.choice(['rule_malware', 'rule_phish', 'rule_spam', 'rule_policy'])

    # Message parts (simplified)
    message['messageParts'] = [
        {
            'disposition': 'inline',
            'contentType': 'text/plain',
            'md5': generate_md5(),
            'sha256': generate_sha256()
        }
    ]

    # Add attachments (20% chance)
    if random.random() < 0.2:
        num_attachments = random.randint(1, 2)
        for i in range(num_attachments):
            filename = fake.file_name(extension=random.choice(['pdf', 'docx', 'xlsx', 'zip', 'exe']))
            message['messageParts'].append({
                'disposition': 'attached',
                'filename': filename,
                'contentType': fake.mime_type(),
                'md5': generate_md5(),
                'sha256': generate_sha256()
            })

    return message


def generate_messages(count=1, message_type='delivered', threat_types=None,
                     threat_statuses=None, start_time=None, end_time=None):
    """
    Generate multiple message events

    Args:
        count: Number of messages to generate
        message_type: 'delivered' or 'blocked'
        threat_types: List of allowed threat types
        threat_statuses: List of allowed threat statuses
        start_time: Start of time window
        end_time: End of time window

    Returns:
        List of message dictionaries
    """
    return [
        generate_message(message_type, threat_types, threat_statuses, start_time, end_time)
        for _ in range(count)
    ]
