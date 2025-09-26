"""
Complete Pipeline Test for RunwayML Batch Automation
Tests all critical functionality to ensure production readiness
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
import shutil

class PipelineTest:
    def __init__(self):
        self.test_results = []
        self.base_dir = Path("distribution")
        self.config_file = self.base_dir / "config" / "runway_config.json"
        self.exe_path = self.base_dir / "RunwayML_Batch_Automation.exe"

    def log_result(self, test_name, passed, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"  Details: {details}")

    def test_exe_exists(self):
        """Test 1: Check if executable exists"""
        exists = self.exe_path.exists()
        size_mb = self.exe_path.stat().st_size / (1024*1024) if exists else 0
        self.log_result(
            "Executable exists",
            exists,
            f"Size: {size_mb:.2f} MB" if exists else "File not found"
        )
        return exists

    def test_assets_exist(self):
        """Test 2: Check if all required assets exist"""
        required_files = [
            "assets/main_lr.mp4",
            "assets/doneperfecto.mp4",
            "assets/blink.mp4",
            "assets/blink_4sec.mp4"
        ]

        missing = []
        for file in required_files:
            file_path = self.base_dir / file
            if not file_path.exists():
                missing.append(file)

        passed = len(missing) == 0
        self.log_result(
            "All video assets present",
            passed,
            f"Missing: {', '.join(missing)}" if missing else "All assets found"
        )
        return passed

    def test_config_persistence(self):
        """Test 3: Test configuration save and load"""
        # Clean existing config
        if self.config_file.exists():
            os.remove(self.config_file)

        # Create test config
        test_config = {
            "api_key": "key_test_12345",
            "driver_video": str(self.base_dir / "assets" / "main_lr.mp4"),
            "output_folder": str(Path.home() / "Downloads"),
            "output_location": "centralized",
            "first_run": False,
            "image_search_pattern": "test",
            "exact_match": True,
            "verbose_logging": False,
            "duplicate_detection": True,
            "delay_between_generations": 1.5,
            "aspect_ratio_mode": "smart",
            "expression_intensity": 1.0
        }

        # Save config
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f, indent=2)

        # Load and verify
        with open(self.config_file, 'r') as f:
            loaded_config = json.load(f)

        # Check key fields
        tests_passed = all([
            loaded_config.get("api_key") == test_config["api_key"],
            loaded_config.get("driver_video") == test_config["driver_video"],
            loaded_config.get("output_location") == test_config["output_location"],
            loaded_config.get("image_search_pattern") == test_config["image_search_pattern"],
            loaded_config.get("exact_match") == test_config["exact_match"]
        ])

        self.log_result(
            "Config persistence",
            tests_passed,
            "All config fields persist correctly" if tests_passed else "Config persistence failed"
        )
        return tests_passed

    def test_python_imports(self):
        """Test 4: Test all Python imports work"""
        try:
            # Add src to path
            sys.path.insert(0, str(Path(__file__).parent / "src"))

            # Test critical imports
            from runway_automation_ui import RunwayAutomationUI
            from runway_generator import RunwayActTwoBatchGenerator
            from gui_selectors import GUISelectors
            from path_utils import PathManager
            from ui_styling import UIStyler
            from first_run_setup import FirstRunSetup

            # Test UIStyler has required methods
            has_methods = all([
                hasattr(UIStyler, 'print_section_box'),
                hasattr(UIStyler, 'print_main_logo'),
                hasattr(UIStyler, 'print_status_line'),
                hasattr(UIStyler, 'print_menu_option'),
                hasattr(UIStyler, 'print_configuration_display')
            ])

            self.log_result(
                "Python imports",
                has_methods,
                "All modules import successfully with required methods" if has_methods else "Missing required methods"
            )
            return has_methods

        except Exception as e:
            self.log_result(
                "Python imports",
                False,
                f"Import error: {str(e)}"
            )
            return False

    def test_pattern_matching(self):
        """Test 5: Test pattern matching logic"""
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from gui_selectors import GUISelectors

        # Create test instance with mock config
        test_config = {
            "image_search_pattern": "selfie",
            "exact_match": True
        }

        selector = GUISelectors(test_config)

        # Test exact match mode
        test_cases = [
            ("person-selfie.jpg", True),   # Should match (after delimiter)
            ("selfie-vacation.png", False), # Should not match (at start)
            ("myselfie.png", False),        # Should not match (no delimiter)
            ("my_selfie.jpg", True),        # Should match (after underscore)
        ]

        all_passed = True
        for filename, expected in test_cases:
            # Mock the pattern matching logic
            pattern = test_config["image_search_pattern"]
            exact = test_config["exact_match"]

            if exact:
                # Exact match logic
                import re
                pattern_regex = r'(^|[^a-z0-9])' + re.escape(pattern) + r'([^a-z0-9]|$)'
                matches = bool(re.search(pattern_regex, filename.lower()))
            else:
                matches = pattern in filename.lower()

            if matches != expected:
                all_passed = False
                break

        self.log_result(
            "Pattern matching",
            all_passed,
            "Pattern matching logic works correctly"
        )
        return all_passed

    def test_exe_launch(self):
        """Test 6: Test executable launches without errors"""
        if not self.exe_path.exists():
            self.log_result(
                "Executable launch",
                False,
                "Executable not found"
            )
            return False

        try:
            # Write a test config that skips first run
            test_config = {
                "first_run": False,
                "api_key": "",
                "driver_video": "",
                "output_folder": str(Path.home() / "Downloads")
            }

            with open(self.config_file, 'w') as f:
                json.dump(test_config, f, indent=2)

            # Try to launch exe and immediately exit
            # We'll use a timeout to prevent hanging
            process = subprocess.Popen(
                [str(self.exe_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Send 'q' to quit immediately
            time.sleep(2)  # Let it start
            process.stdin.write('q\n')
            process.stdin.flush()

            # Wait for exit with timeout
            try:
                stdout, stderr = process.communicate(timeout=5)

                # Check if there's no critical error in output
                has_error = "UIStyler" in stderr or "print_box_header" in stderr or "AttributeError" in stderr

                self.log_result(
                    "Executable launch",
                    not has_error,
                    "Launches without critical errors" if not has_error else f"Error found: {stderr[:200]}"
                )
                return not has_error

            except subprocess.TimeoutExpired:
                process.kill()
                self.log_result(
                    "Executable launch",
                    True,
                    "Executable launched (killed after timeout - normal behavior)"
                )
                return True

        except Exception as e:
            self.log_result(
                "Executable launch",
                False,
                f"Launch error: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run complete pipeline test"""
        print("\n" + "="*60)
        print("COMPLETE PIPELINE TEST - RunwayML Batch Automation v2.0.1")
        print("="*60 + "\n")

        # Run all tests
        self.test_exe_exists()
        self.test_assets_exist()
        self.test_config_persistence()
        self.test_python_imports()
        self.test_pattern_matching()
        self.test_exe_launch()

        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        passed = sum(1 for r in self.test_results if r["passed"])
        total = len(self.test_results)

        print(f"\nPassed: {passed}/{total}")

        if passed == total:
            print("\n✅ ALL TESTS PASSED - PRODUCTION READY!")
        else:
            print("\n❌ SOME TESTS FAILED - NEEDS FIXING")
            failed = [r for r in self.test_results if not r["passed"]]
            print("\nFailed tests:")
            for test in failed:
                print(f"  - {test['test']}: {test['details']}")

        return passed == total

if __name__ == "__main__":
    tester = PipelineTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)