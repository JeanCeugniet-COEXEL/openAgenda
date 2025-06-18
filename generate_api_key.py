#!/usr/bin/env python3
import secrets
import os
from dotenv import load_dotenv

def generate_api_key(length=32):
    """Generate a secure random API key"""
    return secrets.token_hex(length)

def update_env_file(api_key):
    """Update .env file with the new API key"""
    # Load existing .env file
    load_dotenv()
    
    # Check if .env file exists
    if os.path.exists('.env'):
        # Read existing content
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Check if API_KEY already exists
        api_key_exists = False
        for i, line in enumerate(lines):
            if line.startswith('API_KEY='):
                lines[i] = f'API_KEY={api_key}\n'
                api_key_exists = True
                break
        
        # Add API_KEY if it doesn't exist
        if not api_key_exists:
            lines.append(f'\n# API Security\nAPI_KEY={api_key}\n')
        
        # Write back to .env file
        with open('.env', 'w') as f:
            f.writelines(lines)
    else:
        # Create new .env file
        with open('.env', 'w') as f:
            f.write(f'# API Security\nAPI_KEY={api_key}\n')
    
    return True

if __name__ == "__main__":
    # Generate a new API key
    api_key = generate_api_key()
    
    # Update .env file
    if update_env_file(api_key):
        print(f"API key generated and saved to .env file")
        print(f"Your new API key is: {api_key}")
        print("Keep this key secure and use it in your API requests with the X-API-Key header")
    else:
        print("Failed to update .env file") 