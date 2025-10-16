#!/usr/bin/env python3
"""
Script to replace all remaining config() calls with os.environ.get() in settings.py
"""
import re

# Read the settings file
with open('mifumo/settings.py', 'r') as f:
    content = f.read()

# Replace config() calls with os.environ.get()
# Pattern: config('KEY', default=value, cast=type) -> os.environ.get('KEY', 'value')
def replace_config(match):
    key = match.group(1)
    default = match.group(2)
    cast_type = match.group(3) if match.group(3) else None
    
    if cast_type:
        if cast_type == 'int':
            return f"int(os.environ.get('{key}', '{default}'))"
        elif cast_type == 'float':
            return f"float(os.environ.get('{key}', '{default}'))"
        elif cast_type == 'bool':
            return f"os.environ.get('{key}', '{default}').lower() in ('true', '1', 'yes', 'on')"
        else:
            return f"{cast_type}(os.environ.get('{key}', '{default}'))"
    else:
        return f"os.environ.get('{key}', '{default}')"

# Pattern to match config() calls
pattern = r"config\('([^']+)',\s*default=([^,)]+)(?:,\s*cast=(\w+))?\)"

# Replace all matches
new_content = re.sub(pattern, replace_config, content)

# Write the updated content
with open('mifumo/settings.py', 'w') as f:
    f.write(new_content)

print("All config() calls replaced with os.environ.get()!")
