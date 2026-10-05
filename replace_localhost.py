import os
import glob
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Replace "http://localhost:8000/something" with `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/something`
    content = re.sub(
        r'\"http://localhost:8000([^\"]*)\"',
        r'`${process.env.NEXT_PUBLIC_API_URL || \'http://localhost:8000\'}\1`',
        content
    )
    
    # Replace `http://localhost:8000/something` with `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/something`
    content = re.sub(
        r'`http://localhost:8000([^`]*)`',
        r'`${process.env.NEXT_PUBLIC_API_URL || \'http://localhost:8000\'}\1`',
        content
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

for filepath in glob.glob('src/**/*.tsx', recursive=True) + glob.glob('src/**/*.ts', recursive=True):
    fix_file(filepath)

print('Replaced localhost with NEXT_PUBLIC_API_URL')
