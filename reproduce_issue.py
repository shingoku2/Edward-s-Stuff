
from omnix.game_detector import GameDetector
import sys

try:
    detector = GameDetector()
    if not hasattr(detector, 'add_custom_game'):
        print("FAIL: add_custom_game method is missing!")
        sys.exit(1)
    
    print("Calling add_custom_game...")
    result = detector.add_custom_game("TestGame", ["test.exe"])
    print(f"Result: {result}")
    print("SUCCESS: add_custom_game exists and ran.")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
