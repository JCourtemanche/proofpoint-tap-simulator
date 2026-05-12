"""
Base generators for common data types used across all Proofpoint TAP responses
"""
import uuid
import random
import hashlib
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()


def generate_guid():
    """Generate a unique GUID (UUID4 format)"""
    return str(uuid.uuid4())


def generate_email(hashed=False, domain=None):
    """
    Generate an email address

    Args:
        hashed: If True, hash the user part (Proofpoint behavior for privacy)
        domain: Specific domain to use, or None for random

    Returns:
        Email address string
    """
    if domain is None:
        domain = random.choice([
            'example.com', 'company.com', 'business.org', 'enterprise.net',
            'acme.com', 'widgets.io', 'services.co'
        ])

    if hashed:
        user_part = hashlib.sha256(fake.user_name().encode()).hexdigest()[:16]
    else:
        user_part = fake.user_name()

    return f"{user_part}@{domain}"


def generate_ip(internal=False):
    """
    Generate an IP address

    Args:
        internal: If True, generate private IP (10.x.x.x, 192.168.x.x)
                 If False, generate public IP

    Returns:
        IP address string
    """
    if internal:
        return fake.ipv4_private()
    else:
        return fake.ipv4_public()


def generate_iso8601_date(start_time=None, end_time=None):
    """
    Generate an ISO8601 formatted date

    Args:
        start_time: datetime object for range start (default: 1 hour ago)
        end_time: datetime object for range end (default: now)

    Returns:
        ISO8601 formatted date string (e.g., "2021-04-27T12:30:00Z")
    """
    if end_time is None:
        end_time = datetime.utcnow()
    if start_time is None:
        start_time = end_time - timedelta(hours=1)

    random_date = fake.date_time_between(start_date=start_time, end_date=end_time)
    return random_date.strftime('%Y-%m-%dT%H:%M:%SZ')


def generate_sha256():
    """Generate a random SHA256 hash"""
    return hashlib.sha256(fake.binary(length=32)).hexdigest()


def generate_md5():
    """Generate a random MD5 hash"""
    return hashlib.md5(fake.binary(length=16)).hexdigest()


def random_choice_with_weights(choices, weights=None):
    """
    Select a random choice with optional weights

    Args:
        choices: List of options
        weights: List of weights (same length as choices), or None for uniform

    Returns:
        Selected choice
    """
    if weights is None:
        return random.choice(choices)
    return random.choices(choices, weights=weights, k=1)[0]


def generate_user_agent():
    """Generate a realistic User-Agent string"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    ]
    return random.choice(user_agents)


def generate_malicious_url():
    """Generate a fake malicious URL"""
    domains = [
        'malicious-site.tk', 'phishing-example.ru', 'bad-domain.xyz',
        'evil-corp.ml', 'scam-page.ga', 'threat-actor.cf'
    ]
    paths = [
        '/login.php', '/verify.html', '/update', '/secure/login',
        '/account/verify', '/payment/confirm', '/download/file.exe'
    ]
    return f"http://{random.choice(domains)}{random.choice(paths)}"


def generate_campaign_id():
    """Generate a campaign ID (format: hexadecimal string)"""
    return fake.hexify(text='^^' * 20, upper=False)


def generate_threat_id():
    """Generate a threat ID (format: hexadecimal string)"""
    return fake.hexify(text='^^' * 16, upper=False)


def generate_message_id():
    """Generate a Message-ID header value"""
    domain = random.choice(['mail.example.com', 'smtp.company.com', 'mx.business.org'])
    unique_id = fake.hexify(text='^^' * 8, upper=False)
    timestamp = int(datetime.utcnow().timestamp())
    return f"<{unique_id}.{timestamp}@{domain}>"


def parse_iso8601_interval(interval_str):
    """
    Parse ISO8601 interval string to datetime objects

    Args:
        interval_str: String like "2021-04-27T09:00:00Z/2021-04-27T10:00:00Z"
                     or "PT30M/2021-04-27T12:30:00Z" (duration/end)
                     or "2021-04-27T05:00:00-0700/PT30M" (start/duration)

    Returns:
        Tuple of (start_time, end_time) as datetime objects
    """
    parts = interval_str.split('/')

    if len(parts) != 2:
        raise ValueError(f"Invalid interval format: {interval_str}")

    start_part, end_part = parts

    # Parse start
    if start_part.startswith('PT'):
        # Duration/end format
        duration = parse_duration(start_part)
        end_time = _parse_datetime(end_part)
        start_time = end_time - duration
    else:
        # Start date
        start_time = _parse_datetime(start_part)

    # Parse end
    if end_part.startswith('PT'):
        # Start/duration format
        duration = parse_duration(end_part)
        end_time = start_time + duration
    else:
        # End date
        end_time = _parse_datetime(end_part)

    return (start_time, end_time)


def _parse_datetime(date_str):
    """
    Parse a datetime string in various ISO8601 formats

    Args:
        date_str: ISO8601 formatted date string

    Returns:
        datetime object
    """
    # Remove timezone info for simpler parsing
    if date_str.endswith('Z'):
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')

    # Try with timezone offset
    if '+' in date_str or date_str.count('-') > 2:
        try:
            # Remove timezone offset
            base_date = date_str.split('+')[0].split('-', 3)[:3]
            time_part = date_str.split('T')[1].split('+')[0].split('-')[0]
            clean_date = '-'.join(base_date[:3]) + 'T' + time_part.split('.')[0] + 'Z'
            return datetime.strptime(clean_date, '%Y-%m-%dT%H:%M:%SZ')
        except:
            pass

    # Fallback to basic parsing
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')


def parse_duration(duration_str):
    """
    Parse ISO8601 duration (e.g., "PT30M", "PT1H", "PT90S")

    Returns:
        timedelta object
    """
    if not duration_str.startswith('PT'):
        raise ValueError(f"Invalid duration format: {duration_str}")

    duration_str = duration_str[2:]  # Remove 'PT'

    total_seconds = 0

    if 'H' in duration_str:
        hours, duration_str = duration_str.split('H')
        total_seconds += int(hours) * 3600

    if 'M' in duration_str:
        minutes, duration_str = duration_str.split('M')
        total_seconds += int(minutes) * 60

    if 'S' in duration_str:
        seconds = duration_str.replace('S', '')
        if seconds:
            total_seconds += int(seconds)

    return timedelta(seconds=total_seconds)
