#!/usr/bin/env python3
"""
Utility functions for AI News Aggregator
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List

def setup_logging():
    """
    Setup logging configuration
    
    Returns:
        Logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Setup logging
    log_file = os.path.join(log_dir, f"ai_news_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def load_config() -> Dict:
    """
    Load configuration from JSON files
    
    Returns:
        Combined configuration dictionary
    """
    config = {}
    
    # Load sources configuration
    sources_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'sources.json')
    try:
        with open(sources_path, 'r', encoding='utf-8') as f:
            sources_config = json.load(f)
            config['sources'] = sources_config.get('sources', [])
    except FileNotFoundError:
        print(f"❌ Sources config file not found: {sources_path}")
        config['sources'] = []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in sources config: {e}")
        config['sources'] = []
    
    # Load recipients configuration
    recipients_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'recipients.json')
    try:
        with open(recipients_path, 'r', encoding='utf-8') as f:
            recipients_config = json.load(f)
            config['recipients'] = recipients_config.get('recipients', [])
    except FileNotFoundError:
        print(f"❌ Recipients config file not found: {recipients_path}")
        config['recipients'] = []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in recipients config: {e}")
        config['recipients'] = []
    
    return config

def validate_email(email: str) -> bool:
    """
    Basic email validation
    
    Args:
        email: Email address to validate
    
    Returns:
        True if email appears valid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_url(url: str) -> bool:
    """
    Basic URL validation
    
    Args:
        url: URL to validate
    
    Returns:
        True if URL appears valid
    """
    import re
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
    return re.match(pattern, url) is not None

def get_env_variable(var_name: str, required: bool = True) -> str:
    """
    Get environment variable with validation
    
    Args:
        var_name: Name of environment variable
        required: Whether the variable is required
    
    Returns:
        Environment variable value
    
    Raises:
        ValueError: If required variable is missing
    """
    value = os.environ.get(var_name)
    
    if required and not value:
        raise ValueError(f"Required environment variable {var_name} is not set")
    
    return value or ""

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def create_backup_config():
    """
    Create backup configuration files if they don't exist
    """
    config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
    os.makedirs(config_dir, exist_ok=True)
    
    # Default sources configuration
    sources_file = os.path.join(config_dir, 'sources.json')
    if not os.path.exists(sources_file):
        default_sources = {
            "sources": [
                {
                    "name": "MIT Technology Review",
                    "rss_url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
                    "weight": 10
                },
                {
                    "name": "TechCrunch AI",
                    "rss_url": "https://techcrunch.com/category/artificial-intelligence/feed/",
                    "weight": 9
                },
                {
                    "name": "VentureBeat AI",
                    "rss_url": "https://venturebeat.com/ai/feed/",
                    "weight": 9
                }
            ]
        }
        
        with open(sources_file, 'w', encoding='utf-8') as f:
            json.dump(default_sources, f, indent=2)
        
        print(f"✅ Created default sources config: {sources_file}")
    
    # Default recipients configuration
    recipients_file = os.path.join(config_dir, 'recipients.json')
    if not os.path.exists(recipients_file):
        default_recipients = {
            "recipients": [
                "your-email@gmail.com"
            ]
        }
        
        with open(recipients_file, 'w', encoding='utf-8') as f:
            json.dump(default_recipients, f, indent=2)
        
        print(f"✅ Created default recipients config: {recipients_file}")
        print("⚠️  Remember to update recipients.json with your actual email addresses!")

def print_system_info():
    """
    Print system information for debugging
    """
    import sys
    import platform
    
    print("🔧 System Information:")
    print(f"   Python Version: {sys.version}")
    print(f"   Platform: {platform.platform()}")
    print(f"   Working Directory: {os.getcwd()}")
    
    # Check environment variables
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_pass = os.environ.get('GMAIL_PASS')
    
    print("📧 Email Configuration:")
    print(f"   Gmail User: {'✅ Set' if gmail_user else '❌ Not set'}")
    print(f"   Gmail Pass: {'✅ Set' if gmail_pass else '❌ Not set'}")

if __name__ == "__main__":
    # Test utility functions
    print("🧪 Testing utility functions...")
    
    # Test logging
    logger = setup_logging()
    logger.info("Logging test successful")
    
    # Test configuration loading
    config = load_config()
    print(f"Loaded {len(config.get('sources', []))} sources")
    print(f"Loaded {len(config.get('recipients', []))} recipients")
    
    # Test email validation
    test_emails = ["test@example.com", "invalid-email", "user@domain.org"]
    for email in test_emails:
        result = validate_email(email)
        print(f"Email '{email}': {'✅ Valid' if result else '❌ Invalid'}")
    
    # Print system info
    print_system_info()
    
    print("✅ Utility tests completed")
