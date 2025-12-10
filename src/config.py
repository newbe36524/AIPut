"""Configuration loader for AIPut"""

import os
from pathlib import Path

def load_env():
    """Load .env file from project root"""
    try:
        from dotenv import load_dotenv

        # Get project root (3 levels up from src/config.py)
        project_root = Path(__file__).parent.parent
        dotenv_path = project_root / '.env'

        if dotenv_path.exists():
            load_dotenv(dotenv_path)
            print(f"[Config] Loaded environment from {dotenv_path}")
        else:
            print("[Config] No .env file found, using system environment variables")

    except ImportError:
        print("[Config] python-dotenv not installed, using system environment variables")
    except Exception as e:
        print(f"[Config] Error loading .env: {e}")

# Load environment variables at import
load_env()

# Export configuration
def get_config(key: str, default=None):
    """Get configuration value from environment"""
    return os.getenv(key, default)