import os
from anthropic import Anthropic

def get_anthropic_client():
    """
    Get configured Anthropic client

    Returns:
        Anthropic: Configured Anthropic client instance
    """
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    return Anthropic(api_key=api_key)
