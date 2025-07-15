import os
import re
import argparse

def fix_node_rendering(file_path):
    """Fix node variable rendering in test files"""
    with open(file_path, 'r') as f:
        content = f.read()

    # Fix incorrect node variable rendering
    content = re.sub(r'\(:(\w+)\)', r'(\1)', content)

    # Fix incorrect node variable rendering in chained patterns
    content = re.sub(r'\(:(\w+)([-\]\[])', r'(\1\2', content)

    with open(file_path, 'w') as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description='Fix node variable rendering in test files')
    parser.add_argument('--path', default='tests/unit', help='Path to test files directory')
    args = parser.parse_args()

    for root, _, files in os.walk(args.path):
        for file in files:
            if file.endswith('.py'):
                fix_node_rendering(os.path.join(root, file))
    print(f"Fixed node variable rendering in {args.path} directory")

if __name__ == '__main__':
    main()
