import os
import re
import argparse

def update_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Update node() calls: node("var", "Label") -> node("Label", variable="var")
    node_pattern = r'node\(\s*(["\'])(\w+)\1\s*,\s*(["\'])([\w:]+)\3\s*\)'
    node_replacement = r'node(\3\4\3, variable=\1\2\1)'
    content = re.sub(node_pattern, node_replacement, content)

    # Update relationship() calls: relationship("var", "TYPE") -> relationship("TYPE", variable="var")
    rel_pattern = r'relationship\(\s*(["\'])(\w+)\1\s*,\s*(["\'])(\w+)\3\s*\)'
    rel_replacement = r'relationship(\3\4\3, variable=\1\2\1)'
    content = re.sub(rel_pattern, rel_replacement, content)

    # Update path() calls: path("var", ...) -> path(..., variable="var")
    path_pattern = r'path\(\s*(["\'])(\w+)\1\s*,\s*(.*?)\)'
    path_replacement = r'path(\2, variable=\1\3\1)'
    content = re.sub(path_pattern, path_replacement, content, flags=re.DOTALL)

    with open(file_path, 'w') as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description='Update test syntax for super-sniffle project')
    parser.add_argument('--path', default='tests/unit', help='Path to test files directory')
    args = parser.parse_args()

    for root, _, files in os.walk(args.path):
        for file in files:
            if file.endswith('.py'):
                update_file(os.path.join(root, file))
    print(f"Updated syntax in {args.path} directory")

if __name__ == '__main__':
    main()
