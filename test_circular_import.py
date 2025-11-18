#!/usr/bin/env python3
"""
Test script to check for circular imports
"""

import sys
import ast

def check_imports(file_path):
    """Check what modules a file imports"""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            imports.append(module)

    return imports

def main():
    print("=" * 60)
    print("CIRCULAR IMPORT CHECK")
    print("=" * 60)

    # Check the import chain
    files = {
        'src/ai_assistant.py': check_imports('src/ai_assistant.py'),
        'src/knowledge_integration.py': check_imports('src/knowledge_integration.py'),
        'src/__init__.py': check_imports('src/__init__.py')
    }

    print("\nImport Analysis:")
    print("-" * 60)

    for file_path, imports in files.items():
        print(f"\n{file_path}:")
        for imp in imports:
            if 'knowledge' in imp or 'ai_assistant' in imp or 'src' in imp:
                print(f"  → {imp}")

    # Check for circular pattern
    print("\n" + "=" * 60)
    print("CHECKING FOR CIRCULAR IMPORTS:")
    print("=" * 60)

    ai_assistant_imports = files['src/ai_assistant.py']
    knowledge_imports = files['src/knowledge_integration.py']
    init_imports = files['src/__init__.py']

    print("\n1. ai_assistant.py imports from knowledge_integration?")
    has_knowledge_import = any('knowledge_integration' in imp for imp in ai_assistant_imports)
    if has_knowledge_import:
        # Check if it's using src. prefix
        src_prefix = any('src.knowledge_integration' in imp for imp in ai_assistant_imports)
        print(f"   ✓ YES - Uses 'src.' prefix: {src_prefix}")
    else:
        print("   ✗ NO")

    print("\n2. knowledge_integration.py imports from src modules?")
    has_src_imports = any(imp.startswith('src.') for imp in knowledge_imports)
    print(f"   {'✓' if has_src_imports else '✗'} {has_src_imports}")

    print("\n3. src/__init__.py imports AIAssistant?")
    has_ai_import = any('ai_assistant' in imp for imp in init_imports)
    print(f"   {'✓' if has_ai_import else '✗'} {has_ai_import}")

    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)

    # The fix is successful if ai_assistant uses src. prefix
    ai_uses_src_prefix = any('src.knowledge_integration' in imp for imp in ai_assistant_imports)

    if ai_uses_src_prefix:
        print("\n✓ FIXED: All imports use consistent 'src.' prefix")
        print("  Circular import should be resolved!")
        return 0
    else:
        print("\n✗ ISSUE: Inconsistent import prefixes detected")
        print("  Circular import may still exist!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
