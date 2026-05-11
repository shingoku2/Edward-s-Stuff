# test_imports.py
import importlib
import os
import sys

def test_no_circular_imports():
    """Test that all modules can be imported without circular deps"""
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    
    # Get all .py files in src/ (recursively) but we will try to import top-level and direct submodules first
    # A simple approach is to list files in src/
    
    # We want to test modules like src.game_profile, src.ai_assistant, etc.
    
    modules_to_test = []
    
    for root, dirs, files in os.walk(src_dir):
        for f in files:
            if f.endswith('.py') and f != '__init__.py':
                # Construct module path from file path
                rel_path = os.path.relpath(os.path.join(root, f), os.path.dirname(src_dir))
                module_name = rel_path.replace(os.path.sep, '.')[:-3] # remove .py
                modules_to_test.append(module_name)
    
    print(f"Testing imports for {len(modules_to_test)} modules...")
    
    failed = []
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            # print(f"✅ {module_name}")
        except ImportError as e:
            print(f"FAIL: {module_name}: {e}")
            failed.append(module_name)
        except Exception as e:
            print(f"FAIL: {module_name}: {e} (Runtime Error during import)")
            failed.append(module_name)

    if failed:
        print(f"\nFailed to import {len(failed)} modules.")
        sys.exit(1)
    else:
        print("\nAll modules imported successfully.")
        sys.exit(0)

if __name__ == '__main__':
    # Ensure current directory is in python path
    sys.path.insert(0, os.path.dirname(__file__))
    test_no_circular_imports()
