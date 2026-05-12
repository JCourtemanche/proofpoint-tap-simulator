"""
Campaign data generator for Proofpoint TAP API Simulator
"""
import random
from faker import Faker
from .base import generate_campaign_id, generate_iso8601_date, generate_threat_id

fake = Faker()


# Realistic threat actor data
MALWARE_FAMILIES = [
    'Emotet', 'Dridex', 'TrickBot', 'Qakbot', 'IcedID', 'BazarLoader',
    'Cobalt Strike', 'Metasploit', 'Agent Tesla', 'FormBook', 'Lokibot'
]

BRANDS = [
    'Microsoft', 'Google', 'Amazon', 'PayPal', 'DHL', 'FedEx',
    'Apple', 'Facebook', 'LinkedIn', 'Netflix', 'Adobe'
]

THREAT_ACTORS = [
    'TA505', 'APT28', 'APT29', 'Lazarus Group', 'FIN7', 'Wizard Spider',
    'TA542', 'TA551', 'Silent Librarian', 'Sandworm'
]

TECHNIQUES = [
    {'id': 'T1566.001', 'name': 'Spearphishing Attachment'},
    {'id': 'T1566.002', 'name': 'Spearphishing Link'},
    {'id': 'T1204.002', 'name': 'Malicious File'},
    {'id': 'T1059.001', 'name': 'PowerShell'},
    {'id': 'T1059.003', 'name': 'Windows Command Shell'},
    {'id': 'T1047', 'name': 'Windows Management Instrumentation'},
]


def generate_campaign_summary(timestamp=None):
    """
    Generate a campaign summary (ID and timestamp only)

    Args:
        timestamp: Optional specific timestamp

    Returns:
        Dictionary with id and lastUpdatedAt
    """
    return {
        'id': generate_campaign_id(),
        'lastUpdatedAt': timestamp or generate_iso8601_date()
    }


def generate_campaign_details(campaign_id=None, timestamp=None):
    """
    Generate full campaign details

    Args:
        campaign_id: Specific campaign ID, or generate new one
        timestamp: Optional timestamp

    Returns:
        Dictionary with complete campaign information
    """
    if campaign_id is None:
        campaign_id = generate_campaign_id()

    # Generate campaign name based on malware/brand
    malware = random.choice(MALWARE_FAMILIES)
    brand = random.choice(BRANDS) if random.random() < 0.6 else None

    if brand:
        name = f"{malware} - {brand} Impersonation"
        description = f"Campaign delivering {malware} malware via phishing emails impersonating {brand}"
    else:
        name = f"{malware} Distribution Campaign"
        description = f"Mass distribution campaign for {malware} malware"

    # Select 1-3 families
    families = random.sample(MALWARE_FAMILIES, k=random.randint(1, 3))

    # Select 2-4 techniques
    techniques = random.sample(TECHNIQUES, k=random.randint(2, 4))

    # Select 0-2 threat actors (not all campaigns have attributed actors)
    actors = []
    if random.random() < 0.3:
        actors = random.sample(THREAT_ACTORS, k=random.randint(1, 2))

    # Select 0-2 brands
    brands = []
    if brand:
        brands = [brand]
    if random.random() < 0.2:
        brands.extend(random.sample([b for b in BRANDS if b not in brands], k=1))

    campaign = {
        'id': campaign_id,
        'name': name,
        'description': description,
        'startDate': timestamp or generate_iso8601_date(),
        'lastUpdatedAt': timestamp or generate_iso8601_date(),
        'notable': random.choice([True, False]),

        'families': [{'id': f'family_{i}', 'name': fam} for i, fam in enumerate(families)],
        'techniques': techniques,
        'actors': [{'id': f'actor_{i}', 'name': actor} for i, actor in enumerate(actors)],
        'brands': [{'id': f'brand_{i}', 'name': brand} for i, brand in enumerate(brands)],

        'malware': [
            {
                'id': f'malware_{i}',
                'name': random.choice([
                    'Trojan.Generic', 'Backdoor.Agent', 'Downloader.Malicious',
                    'Ransomware.Cryptor', 'Stealer.Credentials'
                ])
            }
            for i in range(random.randint(1, 3))
        ],

        'campaignMembers': []
    }

    # Generate 3-10 campaign members (threats associated with this campaign)
    num_members = random.randint(3, 10)
    for i in range(num_members):
        member = {
            'id': generate_threat_id(),
            'threat': random.choice([
                f"http://malicious-site-{fake.word()}.tk/payload.exe",
                f"http://phishing-{fake.word()}.ru/login",
                generate_threat_id()  # Attachment hash
            ]),
            'type': random.choice(['url', 'attachment'])
        }
        campaign['campaignMembers'].append(member)

    return campaign


def generate_campaigns(count=10, start_time=None, end_time=None):
    """
    Generate multiple campaign summaries

    Args:
        count: Number of campaigns to generate
        start_time: Start of time window
        end_time: End of time window

    Returns:
        List of campaign summary dictionaries
    """
    campaigns = []
    for _ in range(count):
        timestamp = generate_iso8601_date(start_time, end_time)
        campaigns.append(generate_campaign_summary(timestamp))

    return campaigns
