"""
People data generator for Proofpoint TAP API Simulator
Generates VAP (Very Attacked People) and Top Clickers data
"""
import random
from faker import Faker
from .base import generate_email, generate_iso8601_date
from .campaigns import MALWARE_FAMILIES

fake = Faker()


def generate_vap_user():
    """
    Generate a VAP (Very Attacked Person) user

    Returns:
        Dictionary with user identity and threat statistics
    """
    user = {
        'identity': {
            'emails': [generate_email(hashed=False) for _ in range(random.randint(1, 2))]
        },
        'threatStatistics': {
            'families': []
        }
    }

    # Generate 1-5 threat families with scores
    num_families = random.randint(1, 5)
    for _ in range(num_families):
        family = {
            'name': random.choice(MALWARE_FAMILIES),
            'score': random.randint(10, 100)
        }
        user['threatStatistics']['families'].append(family)

    return user


def generate_top_clicker():
    """
    Generate a Top Clicker user

    Returns:
        Dictionary with user identity and click statistics
    """
    user = {
        'identity': {
            'emails': [generate_email(hashed=False) for _ in range(random.randint(1, 2))]
        },
        'clickStatistics': {
            'families': []
        }
    }

    # Generate 1-5 threat families with click counts
    num_families = random.randint(1, 5)
    for _ in range(num_families):
        family = {
            'name': random.choice(MALWARE_FAMILIES),
            'score': random.randint(1, 20)
        }
        user['clickStatistics']['families'].append(family)

    return user


def generate_vap_response(count=10, window='30'):
    """
    Generate VAP API response

    Args:
        count: Number of users to generate
        window: Time window in days (14, 30, 90)

    Returns:
        Dictionary with VAP response structure
    """
    users = [generate_vap_user() for _ in range(count)]

    # Calculate average attack index and threshold
    all_scores = []
    for user in users:
        for family in user['threatStatistics']['families']:
            all_scores.append(family['score'])

    average_attack_index = sum(all_scores) / len(all_scores) if all_scores else 50
    vap_threshold = average_attack_index * 1.5

    return {
        'users': users,
        'totalVapUsers': count,
        'interval': f"P{window}D",
        'averageAttackIndex': round(average_attack_index, 2),
        'vapAttackIndexThreshold': round(vap_threshold, 2)
    }


def generate_top_clickers_response(count=10, window='30'):
    """
    Generate Top Clickers API response

    Args:
        count: Number of users to generate
        window: Time window in days (14, 30, 90)

    Returns:
        Dictionary with Top Clickers response structure
    """
    users = [generate_top_clicker() for _ in range(count)]

    return {
        'users': users,
        'totalTopClickers': count,
        'interval': f"P{window}D"
    }
