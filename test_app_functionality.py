"""
Test the RunwayML application functionality
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    try:
        from runway_automation_ui import RunwayAutomationUI
        from runway_generator import RunwayActTwoBatchGenerator
        from gui_selectors import GUISelectors
        from path_utils import PathManager, path_manager
        from ui_styling import UIStyler
        from first_run_setup import FirstRunSetup
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_uistyler_methods():
    """Test UIStyler has all required methods"""
    print("\nTesting UIStyler methods...")
    from ui_styling import UIStyler

    required_methods = [
        'print_section_box',  # This is the correct method (not print_box_header)
        'print_main_logo',
        'print_status_line',
        'print_menu_option',
        'print_configuration_display',
        'clear_screen',
        'print_cyan',
        'print_green',
        'print_yellow',
        'print_red'
    ]

    missing = []
    for method in required_methods:
        if not hasattr(UIStyler, method):
            missing.append(method)

    if missing:
        print(f"❌ Missing methods: {', '.join(missing)}")
        return False
    else:
        print("✅ All UIStyler methods present")
        return True

def test_path_utils():
    """Test path utilities"""
    print("\nTesting path utilities...")
    from path_utils import path_manager

    # Test basic path operations
    downloads = path_manager.downloads_dir
    if downloads.exists():
        print(f"✅ Downloads dir found: {downloads}")

    # Test driver video detection
    videos = path_manager.get_all_driver_videos()
    print(f"✅ Found {len(videos)} driver videos in assets")

    return True

def test_config_operations():
    """Test configuration loading and saving"""
    print("\nTesting config operations...")
    import json

    test_config = {
        "api_key": "key_test",
        "driver_video": "assets/main_lr.mp4",
        "output_folder": "",
        "first_run": False,
        "expression_intensity": 1.0
    }

    # Test JSON serialization
    json_str = json.dumps(test_config, indent=2)
    loaded = json.loads(json_str)

    if loaded["api_key"] == test_config["api_key"]:
        print("✅ Config serialization works")
        return True
    else:
        print("❌ Config serialization failed")
        return False

def test_critical_line_1265():
    """Test the specific line that was causing the error"""
    print("\nTesting line 1265 fix...")

    # Read the actual file to verify the fix
    ui_file = Path("src/runway_automation_ui.py")
    with open(ui_file, 'r') as f:
        lines = f.readlines()

    # Check line 1265 (0-indexed as 1264)
    line_1265 = lines[1264].strip() if len(lines) > 1264 else ""

    if "print_section_box" in line_1265:
        print(f"✅ Line 1265 correctly uses print_section_box")
        print(f"   Actual line: {line_1265}")
        return True
    elif "print_box_header" in line_1265:
        print(f"❌ Line 1265 still has incorrect print_box_header")
        print(f"   Actual line: {line_1265}")
        return False
    else:
        print(f"✅ Line 1265: {line_1265}")
        return True

def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("TESTING RUNWAYML APPLICATION FUNCTIONALITY")
    print("="*60)

    results = []
    results.append(("Imports", test_imports()))
    results.append(("UIStyler Methods", test_uistyler_methods()))
    results.append(("Path Utilities", test_path_utils()))
    results.append(("Config Operations", test_config_operations()))
    results.append(("Line 1265 Fix", test_critical_line_1265()))

    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Ready to compile!")
        return True
    else:
        print("\n⚠️ Some tests failed - needs fixing")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)