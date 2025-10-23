#!/usr/bin/env python3
"""
Script to update CORS settings in production environment.
This script helps fix the CORS issue with Lovable preview domain.
"""

import os
import sys
from pathlib import Path

def update_production_env():
    """Update the production environment file with correct CORS settings."""
    
    # Look for production environment files
    env_files = [
        'production.env',
        '.env.production',
        '.env',
        'production.env.local'
    ]
    
    found_files = []
    for env_file in env_files:
        if os.path.exists(env_file):
            found_files.append(env_file)
    
    if not found_files:
        print("No production environment file found.")
        print("Available files to check:")
        for env_file in env_files:
            print(f"  - {env_file}")
        print("\nPlease create a production.env file based on production.env.example")
        return False
    
    print(f"Found environment files: {', '.join(found_files)}")
    
    # Update each found file
    for env_file in found_files:
        print(f"\nUpdating {env_file}...")
        
        try:
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Check if CORS_ALLOWED_ORIGINS exists
            if 'CORS_ALLOWED_ORIGINS=' in content:
                # Update existing CORS_ALLOWED_ORIGINS
                lines = content.split('\n')
                updated_lines = []
                
                for line in lines:
                    if line.startswith('CORS_ALLOWED_ORIGINS='):
                        # Extract existing origins
                        existing_origins = line.split('=', 1)[1].strip()
                        origins_list = [origin.strip() for origin in existing_origins.split(',')]
                        
                        # Add missing origins
                        required_origins = [
                            'https://mifumosms.servehttp.com',
                            'https://preview--mifumo-connect.lovable.app',
                            'http://localhost:3000',
                            'http://127.0.0.1:8080'
                        ]
                        
                        for origin in required_origins:
                            if origin not in origins_list:
                                origins_list.append(origin)
                        
                        # Create new line
                        new_line = f"CORS_ALLOWED_ORIGINS={','.join(origins_list)}"
                        updated_lines.append(new_line)
                        print(f"  Updated CORS_ALLOWED_ORIGINS")
                    else:
                        updated_lines.append(line)
                
                # Write back to file
                with open(env_file, 'w') as f:
                    f.write('\n'.join(updated_lines))
                
                print(f"  Successfully updated {env_file}")
                
            else:
                # Add CORS_ALLOWED_ORIGINS if it doesn't exist
                cors_line = "CORS_ALLOWED_ORIGINS=https://mifumosms.servehttp.com,https://preview--mifumo-connect.lovable.app,http://104.131.116.55,http://104.131.116.55:8000,http://localhost:3000,http://127.0.0.1:3000"
                
                with open(env_file, 'a') as f:
                    f.write(f"\n# CORS Settings\n{cors_line}\n")
                
                print(f"  Added CORS_ALLOWED_ORIGINS to {env_file}")
                
        except Exception as e:
            print(f"  Error updating {env_file}: {e}")
            return False
    
    return True

def test_cors_configuration():
    """Test the CORS configuration."""
    print("\nTesting CORS configuration...")
    
    try:
        import django
        from django.conf import settings
        
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
        django.setup()
        
        print(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
        print(f"CORS_ALLOWED_ORIGIN_REGEXES: {settings.CORS_ALLOWED_ORIGIN_REGEXES}")
        print(f"CORS_ALLOW_CREDENTIALS: {settings.CORS_ALLOW_CREDENTIALS}")
        
        # Check if Lovable domain is allowed
        lovable_domain = "https://preview--mifumo-connect.lovable.app"
        if lovable_domain in settings.CORS_ALLOWED_ORIGINS:
            print(f"SUCCESS: {lovable_domain} is in CORS_ALLOWED_ORIGINS")
        else:
            print(f"ERROR: {lovable_domain} is NOT in CORS_ALLOWED_ORIGINS")
            
        # Check regex pattern
        import re
        for pattern in settings.CORS_ALLOWED_ORIGIN_REGEXES:
            if re.match(pattern, lovable_domain):
                print(f"SUCCESS: {lovable_domain} matches regex pattern: {pattern}")
                break
        else:
            print(f"ERROR: {lovable_domain} does not match any regex patterns")
            
    except Exception as e:
        print(f"ERROR: Error testing CORS configuration: {e}")

if __name__ == "__main__":
    print("CORS Configuration Update Tool")
    print("=" * 50)
    
    if update_production_env():
        print("\nSUCCESS: Environment files updated successfully!")
        test_cors_configuration()
        
        print("\nNext steps:")
        print("1. Restart your Django server")
        print("2. Test the CORS configuration with:")
        print("   curl -i -X OPTIONS https://mifumosms.servehttp.com/api/auth/login/ \\")
        print("     -H \"Origin: https://preview--mifumo-connect.lovable.app\" \\")
        print("     -H \"Access-Control-Request-Method: POST\" \\")
        print("     -H \"Access-Control-Request-Headers: Content-Type, Authorization\"")
        print("3. Check that the response includes 'Access-Control-Allow-Origin' header")
    else:
        print("\nERROR: Failed to update environment files")
        sys.exit(1)
