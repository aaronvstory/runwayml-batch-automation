"""
First-run setup wizard for RunwayML Automation Tool.
Guides users through initial configuration with validation and GUI file selection.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple
import json
import time

from path_utils import path_manager
from gui_selectors import GUISelectors, VideoInfo
from ui_styling import UIStyler

class FirstRunSetup:
    """Interactive setup wizard for first-time users."""

    def __init__(self):
        """Initialize the setup wizard."""
        self.config = {}
        # Determine the base directory based on execution context
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_dir = Path(sys.executable).parent
        else:
            # Running as Python script
            base_dir = Path(__file__).parent.parent
        self.config_file = str(base_dir / "config" / "runway_config.json")

    def print_cyan(self, text):
        """Print text in cyan color"""
        print(f"\033[96m{text}\033[0m")

    def print_green(self, text):
        """Print text in green color"""
        print(f"\033[92m{text}\033[0m")

    def print_yellow(self, text):
        """Print text in yellow color"""
        print(f"\033[93m{text}\033[0m")

    def print_red(self, text):
        """Print text in red color"""
        print(f"\033[91m{text}\033[0m")

    def print_magenta(self, text):
        """Print text in magenta color"""
        print(f"\033[95m{text}\033[0m")

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_welcome(self):
        """Display welcome message for first-time users."""
        UIStyler.clear_screen()
        UIStyler.print_main_logo()

        # Welcome banner
        UIStyler.print_section_box("FIRST-TIME SETUP WIZARD", "magenta", "full")
        print()
        UIStyler.print_yellow(UIStyler.center_text("Welcome to RunwayML Batch Automation!"))
        UIStyler.print_yellow(UIStyler.center_text("Let's configure your settings to get started."))
        print()
        print(UIStyler.SECTION_SEP)
        print()

    def get_api_key(self) -> str:
        """Get and validate API key from user."""
        print()
        UIStyler.print_section_box("STEP 1 OF 3: RUNWAYML API KEY", "cyan", "full")
        print()
        print("  You'll need a RunwayML API key to use this tool.")
        print("  Get your API key from: \033[96mhttps://app.runwayml.com/api\033[0m")
        print()
        print(UIStyler.MINOR_SEP)
        print()

        while True:
            api_key = input("Enter your RunwayML API key (or 'skip' to add later): ").strip()

            if api_key.lower() == 'skip':
                self.print_yellow("⚠ You'll need to add your API key to runway_config.json before using the tool.")
                return ""

            if api_key.startswith("key_") and len(api_key) > 20:
                self.print_green("✓ API key format looks valid!")
                return api_key
            else:
                self.print_red("✗ Invalid API key format. RunwayML keys start with 'key_'")
                retry = input("Try again? (y/n): ").lower()
                if retry != 'y':
                    return ""

    def select_driver_video(self) -> str:
        """Help user select driver video with GUI browser option."""
        print("\n" + "-" * 60)
        self.print_cyan("STEP 2: Driver Video Selection")
        print("-" * 60)
        print()
        print("Select a driver video for Act Two generation.")
        print()

        # FIRST check for videos in assets folder
        assets_videos = path_manager.get_all_driver_videos()

        if assets_videos:
            self.print_green(f"✓ Found {len(assets_videos)} video(s) in assets folder:")
            print()
            for i, video in enumerate(assets_videos, 1):
                duration, formatted = VideoInfo.get_duration(str(video))
                duration_str = f" ({formatted})" if duration else ""
                print(f"  {i}. {video.name}{duration_str}")

            print("\nOptions:")
            print(f"  1-{len(assets_videos)} = Select from assets folder")
            print("  B = Browse for different video (GUI)")
            print("  M = Manual path entry")
            print("  D = Search Downloads folder")
            print("  S = Skip for now")

            choice = input("\nYour choice: ").strip().lower()

            # Handle numeric selection
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(assets_videos):
                    selected = str(assets_videos[idx])
                    self.print_green(f"✓ Selected: {assets_videos[idx].name}")
                    return selected
                else:
                    self.print_red("Invalid selection. Try again.")
                    return self.select_driver_video()
            elif choice == 's':
                return ""
            elif choice == 'm':
                # Fall through to manual entry
                choice = '2'
            elif choice == 'd':
                # Fall through to downloads search
                choice = '3'
            elif choice == 'b':
                # Fall through to GUI browser
                choice = '1'
            else:
                # Invalid choice, show options again
                pass

        else:
            # No videos in assets, check other locations
            default_video = path_manager.get_default_driver_video()

            if default_video:
                self.print_green(f"✓ Found potential driver video: {default_video.name}")
                duration, formatted = VideoInfo.get_duration(str(default_video))
                if duration:
                    print(f"  Duration: {formatted}")

                use_default = input("\nUse this video? (y/n): ").lower()
                if use_default == 'y':
                    return str(default_video)

        # Show alternative options if not selected from assets
        if not assets_videos or choice in ['1', '2', '3', 'b', 'm', 'd']:
            print("\nOptions:")
            print("1. \033[92mBrowse for video file (GUI)\033[0m - Recommended")
            print("2. Enter path manually")
            print("3. Search Downloads folder")
            print("4. Skip for now (add later)")

        choice = input("\nSelect option (1-4): ").strip()

        if choice == '1':
            # GUI Browser option
            self.print_cyan("\n🎬 Opening file browser...")
            print("Please select your driver video file in the dialog window.")

            gui = GUISelectors()
            selected = gui.select_driver_video(str(default_video) if default_video else None)

            if selected:
                self.print_green(f"✓ Video selected: {Path(selected).name}")

                # Show duration
                duration, formatted = VideoInfo.get_duration(selected)
                if duration:
                    print(f"  Duration: {formatted}")

                return selected
            else:
                self.print_yellow("No file selected.")
                return self.select_driver_video()  # Ask again

        elif choice == '2':
            # Manual entry
            while True:
                video_path = input("Enter full path to driver video: ").strip()
                if video_path:
                    resolved = path_manager.resolve_path(video_path)
                    if resolved.exists() and resolved.is_file():
                        self.print_green(f"✓ Video found: {resolved.name}")

                        # Show duration
                        duration, formatted = VideoInfo.get_duration(str(resolved))
                        if duration:
                            print(f"  Duration: {formatted}")

                        return str(resolved)
                    else:
                        self.print_red("✗ File not found. Please check the path.")
                else:
                    break

        elif choice == '3':
            # Search Downloads folder
            downloads = path_manager.downloads_dir
            videos = list(downloads.glob("*.mp4")) + list(downloads.glob("*.mov")) + list(downloads.glob("*.webm"))

            if videos:
                print("\nFound videos in Downloads folder:")
                for i, video in enumerate(videos[:10], 1):
                    duration, formatted = VideoInfo.get_duration(str(video))
                    duration_str = f" ({formatted})" if duration else ""
                    print(f"{i}. {video.name}{duration_str}")

                selection = input("\nSelect video number (or 0 to go back): ").strip()
                try:
                    idx = int(selection) - 1
                    if 0 <= idx < len(videos):
                        selected = str(videos[idx])
                        self.print_green(f"✓ Selected: {videos[idx].name}")
                        return selected
                    elif int(selection) == 0:
                        return self.select_driver_video()
                except:
                    pass
            else:
                self.print_yellow("No video files found in Downloads folder.")
                return self.select_driver_video()

        self.print_yellow("⚠ No driver video selected. You'll need to add one before generating.")
        return ""

    def select_output_folder(self) -> str:
        """Help user select output folder with GUI browser option."""
        print("\n" + "-" * 60)
        self.print_cyan("STEP 3: Output Folder")
        print("-" * 60)
        print()
        print("Where should generated videos be saved?")
        print()

        default_output = path_manager.downloads_dir
        self.print_green(f"Current default: {default_output}")

        # Check free space
        try:
            import shutil
            free_gb = shutil.disk_usage(str(default_output)).free / (1024**3)
            print(f"  Free space: {free_gb:.1f} GB")
        except:
            pass

        print("\nOptions:")
        print("1. \033[92mBrowse for folder (GUI)\033[0m - Recommended")
        print("2. Use Downloads folder (default)")
        print("3. Enter path manually")
        print("4. Create new folder")
        print("5. \033[93mSave videos with source images (co-located)\033[0m")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == '1':
            # GUI Browser option
            self.print_cyan("\n📁 Opening folder browser...")
            print("Please select the output folder in the dialog window.")

            gui = GUISelectors()
            selected = gui.select_output_folder(str(default_output))

            if selected:
                self.print_green(f"✓ Folder selected: {selected}")

                # Check free space
                try:
                    import shutil
                    free_gb = shutil.disk_usage(selected).free / (1024**3)
                    print(f"  Free space: {free_gb:.1f} GB")

                    if free_gb < 10:
                        self.print_yellow("  ⚠ Low disk space. Generated videos may require more space.")
                except:
                    pass

                return selected
            else:
                self.print_yellow("No folder selected.")
                return self.select_output_folder()  # Ask again

        elif choice == '2':
            # Use Downloads folder
            self.print_green(f"✓ Using Downloads folder: {default_output}")
            return str(default_output)

        elif choice == '3':
            # Manual entry
            while True:
                folder_path = input("Enter folder path: ").strip()
                if folder_path:
                    resolved = path_manager.resolve_path(folder_path)
                    if resolved.exists() and resolved.is_dir():
                        self.print_green(f"✓ Using folder: {resolved}")
                        return str(resolved)
                    elif not resolved.exists():
                        create = input("Folder doesn't exist. Create it? (y/n): ").lower()
                        if create == 'y':
                            path_manager.ensure_directory_exists(resolved)
                            self.print_green(f"✓ Created folder: {resolved}")
                            return str(resolved)
                    else:
                        self.print_red("✗ Path is not a folder.")
                else:
                    break

        elif choice == '4':
            # Create new folder
            parent_path = input("Enter parent folder path (or press Enter for Documents): ").strip()
            if not parent_path:
                parent_path = str(Path.home() / "Documents")

            parent = path_manager.resolve_path(parent_path)
            if parent.exists() and parent.is_dir():
                folder_name = input("Enter new folder name: ").strip()
                if folder_name:
                    new_folder = parent / folder_name
                    if new_folder.exists():
                        self.print_yellow(f"Folder already exists: {new_folder}")
                        use_existing = input("Use this existing folder? (y/n): ").lower()
                        if use_existing == 'y':
                            return str(new_folder)
                    else:
                        path_manager.ensure_directory_exists(new_folder)
                        self.print_green(f"✓ Created folder: {new_folder}")
                        return str(new_folder)
            else:
                self.print_red("✗ Parent folder doesn't exist.")
                return self.select_output_folder()

        elif choice == '5':
            # Co-located mode - save videos with their source images
            self.print_green("\n✓ Co-located mode selected")
            print("Videos will be saved in the same folder as their source images.")
            print("This means each video will be saved next to the image it was generated from.")

            # Return special marker for co-located mode
            return "CO-LOCATED"

        return str(default_output)

    def configure_settings(self) -> dict:
        """Configure additional settings."""
        print("\n" + "-" * 60)
        self.print_cyan("STEP 4: Additional Settings")
        print("-" * 60)
        print()

        settings = {
            "verbose_logging": False,
            "duplicate_detection": True,
            "delay_between_generations": 1
        }

        # Verbose logging
        verbose = input("Enable verbose logging? (y/N): ").lower()
        settings["verbose_logging"] = (verbose == 'y')

        # Duplicate detection
        duplicates = input("Enable duplicate detection? (Y/n): ").lower()
        settings["duplicate_detection"] = (duplicates != 'n')

        # Delay between generations
        print("\nDelay between API calls (seconds):")
        print("Recommended: 1-2 seconds to avoid rate limits")
        delay_input = input("Enter delay (default: 1): ").strip()

        try:
            delay = float(delay_input) if delay_input else 1
            settings["delay_between_generations"] = max(0, delay)
        except:
            settings["delay_between_generations"] = 1

        return settings

    def save_configuration(self, config: dict) -> bool:
        """Save configuration to file."""
        try:
            config_path = Path(self.config_file)
            # Ensure config directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            self.print_red(f"Error saving configuration: {e}")
            return False

    def display_summary(self, config: dict):
        """Display configuration summary."""
        print("\n" + "=" * 80)
        self.print_cyan("CONFIGURATION SUMMARY")
        print("=" * 80)
        print()

        # API Key
        if config.get("api_key"):
            masked_key = config["api_key"][:10] + "..." + config["api_key"][-4:]
            self.print_green(f"✓ API Key: {masked_key}")
        else:
            self.print_yellow("⚠ API Key: Not configured")

        # Driver Video
        if config.get("driver_video"):
            video_name = Path(config["driver_video"]).name
            self.print_green(f"✓ Driver Video: {video_name}")
        else:
            self.print_yellow("⚠ Driver Video: Not configured")

        # Output Folder
        self.print_green(f"✓ Output Folder: {config.get('output_folder', 'Not set')}")

        # Settings
        print("\nSettings:")
        print(f"  • Verbose Logging: {'Enabled' if config.get('verbose_logging') else 'Disabled'}")
        print(f"  • Duplicate Detection: {'Enabled' if config.get('duplicate_detection') else 'Disabled'}")
        print(f"  • Generation Delay: {config.get('delay_between_generations', 1)} seconds")
        print()

    def run(self, preserve_existing=True) -> dict:
        """Run the complete setup wizard."""
        self.display_welcome()

        # Load existing config if it exists (to preserve settings)
        existing_config = {}
        if preserve_existing:
            try:
                config_path = Path(self.config_file)
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        existing_config = json.load(f)
            except:
                pass

        # Collect configuration
        output_selection = self.select_output_folder()

        # Handle co-located mode
        if output_selection == "CO-LOCATED":
            output_folder = ""  # Empty string for co-located
            output_location = "co-located"
        else:
            output_folder = output_selection
            output_location = "centralized"

        # Start with existing config to preserve ALL settings
        config = existing_config.copy() if existing_config else {}

        # Update with wizard selections (overriding existing values)
        config.update({
            "api_key": self.get_api_key(),
            "driver_video": self.select_driver_video(),
            "output_folder": output_folder,
            "output_location": output_location,  # Set based on selection
            "first_run": False,  # Mark as configured
        })

        # Preserve pattern settings if not already set
        if "image_search_pattern" not in config:
            config["image_search_pattern"] = "genx"
        if "exact_match" not in config:
            config["exact_match"] = False

        # Add additional settings (these will update existing ones)
        config.update(self.configure_settings())

        # Display summary
        self.display_summary(config)

        # Save configuration
        print("-" * 80)
        if self.save_configuration(config):
            self.print_green("✓ Configuration saved successfully!")

            # Check if running as executable or script
            if getattr(sys, 'frozen', False):
                # Running as compiled executable - will auto-continue
                print("\nConfiguration complete! The application will now start...")
            else:
                # Running as Python script
                print("\nYou can now run the tool using: python runway_automation_ui.py")
        else:
            self.print_red("✗ Failed to save configuration.")
            print("\nPlease create runway_config.json manually with your settings.")

        print()
        input("Press Enter to continue...")
        return config


if __name__ == "__main__":
    # Run setup wizard if executed directly
    wizard = FirstRunSetup()
    wizard.run()