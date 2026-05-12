"""
Forensics data generator for Proofpoint TAP API Simulator
"""
import random
from faker import Faker
from .base import (
    generate_iso8601_date, generate_ip, generate_sha256,
    generate_md5, generate_malicious_url
)

fake = Faker()


def generate_forensic_event(event_type=None):
    """
    Generate a single forensic event of specified type

    Args:
        event_type: Type of forensic event (attachment, url, dns, file, process, etc.)
                   If None, randomly selected

    Returns:
        Dictionary representing a forensic event
    """
    if event_type is None:
        event_type = random.choice([
            'attachment', 'url', 'dns', 'file', 'process',
            'network', 'registry', 'mutex', 'ids', 'behavior'
        ])

    base_event = {
        'type': event_type,
        'time': f"+{random.randint(0, 300)}s",  # Relative time
        'display': '',
        'malicious': random.choice([True, False]),
        'platforms': [{
            'name': random.choice(['Win7', 'Win10', 'WinXP']),
            'os': 'windows',
            'version': random.choice(['7', '10', 'XP'])
        }]
    }

    what = {}

    if event_type == 'attachment':
        what = {
            'sha256': generate_sha256(),
            'md5': generate_md5(),
            'blacklisted': random.randint(0, 5),
            'offset': 0,
            'size': random.randint(10000, 5000000)
        }
        base_event['display'] = f"Attachment: {what['sha256'][:16]}..."

    elif event_type == 'url':
        url = generate_malicious_url()
        what = {
            'url': url,
            'blacklisted': random.choice([True, False]),
            'sha256': generate_sha256(),
            'md5': generate_md5(),
            'size': random.randint(1000, 100000),
            'httpStatus': random.choice([200, 301, 302, 404]),
            'ip': generate_ip()
        }
        base_event['display'] = f"URL: {url}"

    elif event_type == 'dns':
        host = f"{fake.word()}.{random.choice(['com', 'net', 'org', 'ru', 'xyz'])}"
        what = {
            'host': host,
            'cnames': [f"{fake.word()}.{random.choice(['com', 'net'])}" for _ in range(random.randint(0, 2))],
            'ips': [generate_ip() for _ in range(random.randint(1, 3))],
            'nameservers': [f"ns{i}.{fake.word()}.com" for i in range(1, 3)],
            'nameserversList': [generate_ip() for _ in range(2)]
        }
        base_event['display'] = f"DNS: {host}"

    elif event_type == 'file':
        filename = fake.file_name(extension=random.choice(['exe', 'dll', 'bat', 'ps1', 'doc']))
        path = f"C:\\Users\\{fake.user_name()}\\{random.choice(['AppData', 'Temp', 'Downloads'])}\\{filename}"
        what = {
            'path': path,
            'action': random.choice(['create', 'modify', 'delete']),
            'rule': f"rule_{random.randint(1000, 9999)}",
            'sha256': generate_sha256(),
            'md5': generate_md5(),
            'size': random.randint(1000, 10000000)
        }
        base_event['display'] = f"File {what['action']}: {path}"

    elif event_type == 'process':
        exe_name = random.choice(['powershell.exe', 'cmd.exe', 'rundll32.exe', 'svchost.exe', 'malware.exe'])
        path = f"C:\\Windows\\System32\\{exe_name}"
        what = {
            'action': random.choice(['create', 'terminate']),
            'path': path
        }
        base_event['display'] = f"Process {what['action']}: {exe_name}"

    elif event_type == 'network':
        what = {
            'action': random.choice(['connect', 'listen']),
            'ip': generate_ip(),
            'port': str(random.choice([80, 443, 8080, 4444, 1234])),
            'type': random.choice(['tcp', 'udp'])
        }
        base_event['display'] = f"Network {what['action']}: {what['ip']}:{what['port']}"

    elif event_type == 'registry':
        key_path = f"HKEY_LOCAL_MACHINE\\SOFTWARE\\{fake.word()}\\{fake.word()}"
        what = {
            'name': fake.word(),
            'action': random.choice(['create', 'set']),
            'key': key_path,
            'value': fake.word()
        }
        base_event['display'] = f"Registry {what['action']}: {key_path}"

    elif event_type == 'mutex':
        mutex_name = f"Global\\{fake.word().upper()}_{random.randint(1000, 9999)}"
        what = {
            'name': mutex_name,
            'path': f"\\BaseNamedObjects\\{mutex_name}"
        }
        base_event['display'] = f"Mutex: {mutex_name}"

    elif event_type == 'ids':
        what = {
            'name': random.choice(['ET MALWARE', 'ET TROJAN', 'SURICATA EXPLOIT']),
            'signatureId': str(random.randint(2000000, 2999999))
        }
        base_event['display'] = f"IDS: {what['name']} [{what['signatureId']}]"

    elif event_type == 'behavior':
        what = {
            'path': fake.file_path(depth=random.randint(2, 4), extension='exe'),
            'url': generate_malicious_url()
        }
        base_event['display'] = f"Behavior: {what['path']}"

    base_event['what'] = what
    return base_event


def generate_forensics_report(threat_id=None, campaign_id=None):
    """
    Generate a forensics report

    Args:
        threat_id: Optional threat ID
        campaign_id: Optional campaign ID

    Returns:
        Dictionary with forensics report structure
    """
    report_id = threat_id or campaign_id or fake.hexify(text='^^' * 16, upper=False)

    report = {
        'id': report_id,
        'type': random.choice(['attachment', 'url', 'hybrid']),
        'scope': 'threat' if threat_id else 'campaign',
        'forensics': []
    }

    # Generate 5-15 forensic events
    num_events = random.randint(5, 15)
    for _ in range(num_events):
        event = generate_forensic_event()
        report['forensics'].append(event)

    return {'reports': [report]}
