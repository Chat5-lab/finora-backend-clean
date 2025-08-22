
#!/usr/bin/env python3
"""
Script to help set up secrets for the Finora application.
Run this to see what secrets need to be configured.
"""

import os
from settings import settings

def check_secrets():
    """Check if required secrets are properly configured."""
    required_secrets = {
        'DATABASE_URL': 'Database connection string',
        'SECRET_KEY': 'JWT signing key (use a strong random string)',
    }
    
    missing = []
    for key, description in required_secrets.items():
        value = os.getenv(key)
        if not value or value == getattr(settings, key.lower(), None):
            missing.append(f"  {key}: {description}")
    
    if missing:
        print("❌ Missing or default secrets detected:")
        print("\n".join(missing))
        print("\nPlease add these secrets using Replit's Secrets tool:")
        print("1. Open the Tools pane")
        print("2. Select 'Secrets'")
        print("3. Add each required secret with a secure value")
        return False
    else:
        print("✅ All required secrets are configured!")
        return True

if __name__ == "__main__":
    check_secrets()
