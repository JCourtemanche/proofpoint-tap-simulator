"""
Parameter validators for Proofpoint TAP API endpoints
"""
from datetime import datetime


def validate_interval(interval_str):
    """
    Validate ISO8601 interval format

    Args:
        interval_str: String like "2021-04-27T09:00:00Z/2021-04-27T10:00:00Z"

    Returns:
        True if valid

    Raises:
        ValueError: If format is invalid
    """
    if not interval_str or '/' not in interval_str:
        raise ValueError("Interval must be in ISO8601 format (start/end)")

    parts = interval_str.split('/')
    if len(parts) != 2:
        raise ValueError("Interval must contain exactly one '/' separator")

    return True


def validate_time_params(interval=None, since_time=None, since_seconds=None):
    """
    Validate that only one time parameter is provided

    Args:
        interval: ISO8601 interval string
        since_time: ISO8601 date string
        since_seconds: Integer seconds

    Returns:
        The parameter name and value that was provided

    Raises:
        ValueError: If multiple parameters are provided or none are provided
    """
    provided_params = []

    if interval:
        provided_params.append(('interval', interval))
    if since_time:
        provided_params.append(('sinceTime', since_time))
    if since_seconds:
        provided_params.append(('sinceSeconds', since_seconds))

    if len(provided_params) == 0:
        raise ValueError("One of interval, sinceTime, or sinceSeconds must be provided")

    if len(provided_params) > 1:
        raise ValueError("Only one of interval, sinceTime, or sinceSeconds can be provided")

    return provided_params[0]


def validate_threat_type(threat_type):
    """
    Validate threat type value(s)

    Args:
        threat_type: String or list of strings

    Returns:
        List of valid threat types

    Raises:
        ValueError: If any value is invalid
    """
    valid_types = ['url', 'attachment', 'messageText', 'message']

    if isinstance(threat_type, str):
        threat_types = [threat_type]
    else:
        threat_types = threat_type

    for tt in threat_types:
        if tt not in valid_types:
            raise ValueError(f"Invalid threat type: {tt}. Must be one of {valid_types}")

    return threat_types


def validate_threat_status(threat_status):
    """
    Validate threat status value(s)

    Args:
        threat_status: String or list of strings

    Returns:
        List of valid threat statuses

    Raises:
        ValueError: If any value is invalid
    """
    valid_statuses = ['active', 'cleared', 'falsePositive']

    if isinstance(threat_status, str):
        threat_statuses = [threat_status]
    else:
        threat_statuses = threat_status

    for ts in threat_statuses:
        if ts not in valid_statuses:
            raise ValueError(f"Invalid threat status: {ts}. Must be one of {valid_statuses}")

    return threat_statuses


def validate_window(window):
    """
    Validate window parameter for people endpoints

    Args:
        window: String representing days

    Returns:
        String window value if valid

    Raises:
        ValueError: If value is invalid
    """
    valid_windows = ['14', '30', '90']

    if window not in valid_windows:
        raise ValueError(f"Invalid window: {window}. Must be one of {valid_windows}")

    return window


def validate_pagination(page, size, max_size=200):
    """
    Validate and parse pagination parameters

    Args:
        page: String or int page number (1-indexed)
        size: String or int page size
        max_size: Maximum allowed size (default 200)

    Returns:
        Tuple of (page_int, size_int)

    Raises:
        ValueError: If values are invalid
    """
    try:
        page_int = int(page) if page else 1
        size_int = int(size) if size else 100
    except (ValueError, TypeError):
        raise ValueError("Page and size must be integers")

    if page_int < 1:
        raise ValueError("Page must be >= 1")

    if size_int < 1:
        raise ValueError("Size must be >= 1")

    if size_int > max_size:
        raise ValueError(f"Size must be <= {max_size}")

    return (page_int, size_int)


def validate_format(format_param):
    """
    Validate format parameter (must be 'json')

    Args:
        format_param: Format string

    Raises:
        ValueError: If format is not 'json'
    """
    if format_param and format_param != 'json':
        raise ValueError("Format must be 'json'")

    return True


def parse_since_time(since_time):
    """
    Parse ISO8601 date string

    Args:
        since_time: ISO8601 date string

    Returns:
        datetime object

    Raises:
        ValueError: If format is invalid
    """
    try:
        if since_time.endswith('Z'):
            return datetime.strptime(since_time, '%Y-%m-%dT%H:%M:%SZ')
        else:
            return datetime.fromisoformat(since_time.replace('Z', '+00:00'))
    except Exception as e:
        raise ValueError(f"Invalid sinceTime format: {since_time}. Must be ISO8601 format.")


def parse_since_seconds(since_seconds):
    """
    Parse sinceSeconds to datetime range

    Args:
        since_seconds: Integer seconds from now

    Returns:
        Tuple of (start_time, end_time) as datetime objects
    """
    from datetime import timedelta

    try:
        seconds = int(since_seconds)
    except (ValueError, TypeError):
        raise ValueError("sinceSeconds must be an integer")

    if seconds < 0:
        raise ValueError("sinceSeconds must be positive")

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(seconds=seconds)

    return (start_time, end_time)
