"""
GUI file and folder selectors using tkinter.
Provides easy file/folder selection with validation and video duration detection.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

# Try to import video duration libraries
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    from moviepy.editor import VideoFileClip
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False

try:
    from .path_utils import path_manager
except ImportError:
    from path_utils import path_manager

class VideoInfo:
    """Utility class for video file information."""

    @staticmethod
    def get_duration_ffprobe(video_path: str) -> Optional[float]:
        """Get video duration using ffprobe (if available)."""
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except (subprocess.SubprocessError, ValueError, FileNotFoundError):
            pass
        return None

    @staticmethod
    def get_duration_cv2(video_path: str) -> Optional[float]:
        """Get video duration using OpenCV."""
        if not HAS_CV2:
            return None
        try:
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            if fps > 0:
                return frame_count / fps
        except:
            pass
        return None

    @staticmethod
    def get_duration_moviepy(video_path: str) -> Optional[float]:
        """Get video duration using MoviePy."""
        if not HAS_MOVIEPY:
            return None
        try:
            clip = VideoFileClip(str(video_path))
            duration = clip.duration
            clip.close()
            return duration
        except:
            pass
        return None

    @staticmethod
    def get_duration(video_path: str) -> Tuple[Optional[float], str]:
        """
        Get video duration using available methods.

        Returns:
            Tuple of (duration_in_seconds, formatted_string)
        """
        if not video_path or not Path(video_path).exists():
            return None, "File not found"

        # Try different methods in order of preference
        methods = [
            ('ffprobe', VideoInfo.get_duration_ffprobe),
            ('opencv', VideoInfo.get_duration_cv2),
            ('moviepy', VideoInfo.get_duration_moviepy),
        ]

        for method_name, method_func in methods:
            duration = method_func(video_path)
            if duration is not None:
                # Format duration nicely
                if duration < 60:
                    formatted = f"{duration:.1f}s"
                else:
                    minutes = int(duration // 60)
                    seconds = int(duration % 60)
                    formatted = f"{minutes}:{seconds:02d}"
                return duration, formatted

        # If no method worked, return file size as fallback info
        try:
            size_mb = Path(video_path).stat().st_size / (1024 * 1024)
            return None, f"{size_mb:.1f}MB"
        except:
            return None, "Unknown"


class GUISelectors:
    """GUI file and folder selection dialogs."""

    def __init__(self, config: dict = None):
        """Initialize GUI selectors with optional config."""
        self.root = None
        self.config_file = "runway_config.json"
        self.config = config or {}

    def _ensure_tk_root(self):
        """Ensure tkinter root window exists."""
        if not self.root:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the main window
            self.root.title("RunwayML Automation - File Selector")
            # Center the dialogs on screen
            self.root.eval('tk::PlaceWindow . center')

    def _cleanup_tk(self):
        """Clean up tkinter resources."""
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
            self.root = None

    def _matches_pattern(self, filename: str, pattern: str, exact_match: bool = False) -> bool:
        """
        Check if a filename matches the search pattern.

        Args:
            filename: The filename to check
            pattern: The pattern to search for
            exact_match: If True, pattern must match as complete word segment

        Returns:
            True if the filename matches the pattern
        """
        filename_lower = filename.lower()
        pattern_lower = pattern.lower()

        if exact_match:
            import re
            # Remove file extension for matching
            name_without_ext = filename_lower.rsplit('.', 1)[0] if '.' in filename_lower else filename_lower

            # Special handling for patterns with leading delimiters like "-selfie"
            if pattern_lower.startswith('-') or pattern_lower.startswith('_'):
                delimiter = pattern_lower[0]
                word = pattern_lower[1:]  # Remove the delimiter

                # The pattern should match only when the word appears after the delimiter
                # and not at the beginning of the filename
                # Examples: "person-selfie" matches, "selfie-vacation" doesn't match

                # Look for the exact pattern with delimiter
                if pattern_lower in name_without_ext:
                    # Check if it's preceded by other characters (not at start)
                    pos = name_without_ext.find(pattern_lower)
                    if pos > 0:  # Must have something before it
                        # Also check it's not immediately followed by more letters
                        # to ensure word boundary
                        end_pos = pos + len(pattern_lower)
                        if end_pos >= len(name_without_ext) or not name_without_ext[end_pos].isalnum():
                            return True
                return False
            else:
                # Pattern doesn't include delimiter, look for exact word match
                # Split by common delimiters and check segments
                segments = re.split(r'[-_\s.]+', name_without_ext)
                return pattern_lower in segments
        else:
            # Simple substring match
            return pattern_lower in filename_lower

    def select_driver_video(self, current_video: Optional[str] = None) -> Optional[str]:
        """
        Open file dialog to select driver video.

        Args:
            current_video: Currently selected video path

        Returns:
            Selected video path or None if cancelled
        """
        self._ensure_tk_root()

        # Set initial directory
        if current_video and Path(current_video).exists():
            initial_dir = str(Path(current_video).parent)
        else:
            initial_dir = str(path_manager.downloads_dir)

        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Driver Video for Act Two Generation",
            initialdir=initial_dir,
            filetypes=[
                ("Video Files", "*.mp4 *.mov *.webm *.avi *.mkv"),
                ("MP4 Files", "*.mp4"),
                ("MOV Files", "*.mov"),
                ("WebM Files", "*.webm"),
                ("All Files", "*.*")
            ]
        )

        self._cleanup_tk()

        if file_path:
            # Validate video file
            path = Path(file_path)
            if path.exists() and path.is_file():
                # Get video duration
                duration, formatted = VideoInfo.get_duration(file_path)

                # Show info dialog
                self._ensure_tk_root()

                # Show video information without strict requirements
                if duration:
                    message = f"✓ Video selected successfully!\n\nFile: {path.name}\nDuration: {formatted}"
                    icon = "info"
                else:
                    message = f"✓ Video selected successfully!\n\nFile: {path.name}\nSize: {formatted}"
                    icon = "info"

                messagebox.showinfo("Video Selected", message, icon=icon)
                self._cleanup_tk()

                return str(path)

        return None

    def select_output_folder(self, current_folder: Optional[str] = None) -> Optional[str]:
        """
        Open dialog to select output folder.

        Args:
            current_folder: Currently selected folder path

        Returns:
            Selected folder path or None if cancelled
        """
        self._ensure_tk_root()

        # Set initial directory
        if current_folder and Path(current_folder).exists():
            initial_dir = str(Path(current_folder))
        else:
            initial_dir = str(path_manager.downloads_dir)

        # Open folder dialog
        folder_path = filedialog.askdirectory(
            title="Select Output Folder for Generated Videos",
            initialdir=initial_dir,
            mustexist=False
        )

        self._cleanup_tk()

        if folder_path:
            path = Path(folder_path)

            # Create folder if it doesn't exist
            if not path.exists():
                self._ensure_tk_root()
                result = messagebox.askyesno(
                    "Create Folder",
                    f"Folder doesn't exist:\n{path}\n\nCreate it?",
                    icon="question"
                )
                self._cleanup_tk()

                if result:
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                        return str(path)
                    except Exception as e:
                        self._ensure_tk_root()
                        messagebox.showerror("Error", f"Failed to create folder:\n{e}")
                        self._cleanup_tk()
                        return None
            else:
                return str(path)

        return None

    def select_input_folder(self) -> Optional[Tuple[str, int]]:
        """
        Simple folder selection without scanning.

        Returns:
            Tuple of (folder_path, 0) or None if cancelled
        """
        self._ensure_tk_root()

        folder_path = filedialog.askdirectory(
            title="Select folder containing images",
            initialdir=os.getcwd(),
            mustexist=True
        )

        self._cleanup_tk()

        if folder_path:
            return str(folder_path), 0
        return None

    def select_input_folder_with_scan(self, current_folder: Optional[str] = None) -> Optional[Tuple[str, int]]:
        """
        Open dialog to select input folder and scan for images.

        Args:
            current_folder: Currently selected folder path

        Returns:
            Tuple of (folder_path, image_count) or None if cancelled
        """
        self._ensure_tk_root()

        # Set initial directory
        if current_folder and Path(current_folder).exists():
            initial_dir = str(Path(current_folder))
        else:
            initial_dir = str(path_manager.downloads_dir)

        # Open folder dialog
        folder_path = filedialog.askdirectory(
            title="Select Input Folder Containing Images to Process",
            initialdir=initial_dir,
            mustexist=True
        )

        self._cleanup_tk()

        if folder_path:
            path = Path(folder_path)

            # Scan for images recursively
            image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
            image_files = []

            for ext in image_extensions:
                image_files.extend(path.rglob(f"*{ext}"))

            # Filter for images matching configured pattern (default to 'genx' if not configured)
            search_pattern = self.config.get('image_search_pattern', 'genx').lower()
            exact_match = self.config.get('exact_match', False)

            matching_images = []
            for img in image_files:
                if self._matches_pattern(img.name, search_pattern, exact_match):
                    matching_images.append(img)

            # Show scan results in console instead of messagebox
            if matching_images:
                pattern_display = f'"{search_pattern}"' + (" (exact)" if exact_match else " (contains)")

                # Print to console with rich formatting
                from rich.console import Console
                from rich.panel import Panel
                from rich.text import Text

                console = Console()

                # Create summary text
                summary = Text()
                summary.append("📁 Folder Scan Complete\n", style="bold cyan")
                summary.append(f"✓ Found {len(matching_images)} images matching ", style="green")
                summary.append(f"{pattern_display}\n\n", style="yellow")
                summary.append(f"Folder: {path.name}\n", style="white")
                summary.append(f"Full path: {path}\n", style="dim white")
                summary.append(f"Matching images: {len(matching_images)}\n", style="green")
                summary.append(f"Filtered out: {len(image_files) - len(matching_images)}\n", style="red")
                summary.append(f"Total images scanned: {len(image_files)}", style="white")

                console.print(Panel(summary, title="Image Discovery Results", border_style="green"))

                # Show first few matching files as examples
                if len(matching_images) > 0:
                    console.print("\n[cyan]Sample matches (first 5):[/cyan]")
                    for i, img in enumerate(matching_images[:5], 1):
                        console.print(f"  {i}. {img.name}")
                    if len(matching_images) > 5:
                        console.print(f"  ... and {len(matching_images) - 5} more")

                return str(path), len(matching_images)
            elif image_files:
                # No matching images but other images found - show in console
                from rich.console import Console
                from rich.panel import Panel
                from rich.text import Text
                from rich.prompt import Confirm

                console = Console()
                pattern_display = f'"{search_pattern}"' + (" (exact)" if exact_match else " (contains)")

                # Create warning text
                warning = Text()
                warning.append("⚠️  No Matching Images\n\n", style="bold yellow")
                warning.append(f"No images found matching {pattern_display}\n", style="white")
                warning.append(f"But found {len(image_files)} other images in the folder\n\n", style="white")

                console.print(Panel(warning, title="Pattern Match Results", border_style="yellow"))

                # Show some of the non-matching files
                console.print("\n[yellow]Non-matching images found (first 5):[/yellow]")
                for i, img in enumerate(image_files[:5], 1):
                    console.print(f"  {i}. {img.name}")
                if len(image_files) > 5:
                    console.print(f"  ... and {len(image_files) - 5} more")

                # Ask if they want to process all
                result = Confirm.ask(f"\n[cyan]Process all [yellow]{len(image_files)}[/yellow] images anyway?[/cyan]")

                if result:
                    return str(path), len(image_files)
            else:
                # No images at all - show in console
                from rich.console import Console
                from rich.panel import Panel

                console = Console()
                console.print(Panel(
                    f"[red]No image files found in:[/red]\n{path}\n\n[yellow]Please select a folder with images.[/yellow]",
                    title="No Images Found",
                    border_style="red"
                ))
                console.print("\n[dim]Press Enter to continue...[/dim]")
                input()

        return None

    def show_current_settings(self, config: dict):
        """
        Display current configuration settings in a dialog.

        Args:
            config: Current configuration dictionary
        """
        self._ensure_tk_root()

        # Build settings text
        lines = ["Current Configuration:\n" + "=" * 40 + "\n"]

        # Driver Video
        driver_video = config.get("driver_video", "")
        if driver_video and Path(driver_video).exists():
            video_name = Path(driver_video).name
            duration, formatted = VideoInfo.get_duration(driver_video)
            lines.append(f"✓ Driver Video: {video_name}")
            lines.append(f"  Duration: {formatted}")
            lines.append(f"  Location: {driver_video}")
        else:
            lines.append("✗ Driver Video: Not configured")

        lines.append("")

        # Output Folder
        output_folder = config.get("output_folder", "")
        if output_folder and Path(output_folder).exists():
            lines.append(f"✓ Output Folder: {output_folder}")
            # Check free space
            try:
                import shutil
                free_gb = shutil.disk_usage(output_folder).free / (1024**3)
                lines.append(f"  Free Space: {free_gb:.1f} GB")
            except:
                pass
        else:
            lines.append("✗ Output Folder: Not configured")

        lines.append("")

        # API Key
        api_key = config.get("api_key", "")
        if api_key:
            masked = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 20 else "***"
            lines.append(f"✓ API Key: {masked}")
        else:
            lines.append("✗ API Key: Not configured")

        lines.append("\n" + "=" * 40)
        lines.append("\nSettings:")
        lines.append(f"• Verbose Logging: {'Enabled' if config.get('verbose_logging') else 'Disabled'}")
        lines.append(f"• Duplicate Detection: {'Enabled' if config.get('duplicate_detection') else 'Disabled'}")
        lines.append(f"• Generation Delay: {config.get('delay_between_generations', 1)} seconds")

        message = "\n".join(lines)

        messagebox.showinfo("Current Settings", message)
        self._cleanup_tk()

    def update_config(self, key: str, value: any) -> bool:
        """
        Update configuration file with new value.

        Args:
            key: Configuration key to update
            value: New value for the key

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load current config
            config_path = path_manager.resolve_path(self.config_file)

            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}

            # Update value
            config[key] = value

            # Mark as configured
            if "first_run" in config:
                config["first_run"] = False

            # Save config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            return True

        except Exception as e:
            self._ensure_tk_root()
            messagebox.showerror("Configuration Error", f"Failed to update configuration:\n{e}")
            self._cleanup_tk()
            return False


# Convenience functions for direct use
def select_driver_video_gui(current_video: Optional[str] = None) -> Optional[str]:
    """Quick function to select driver video via GUI."""
    selector = GUISelectors()
    result = selector.select_driver_video(current_video)

    if result:
        # Update configuration
        selector.update_config("driver_video", result)

    return result


def select_output_folder_gui(current_folder: Optional[str] = None) -> Optional[str]:
    """Quick function to select output folder via GUI."""
    selector = GUISelectors()
    result = selector.select_output_folder(current_folder)

    if result:
        # Update configuration
        selector.update_config("output_folder", result)

    return result


def show_settings_gui(config: dict):
    """Quick function to show current settings."""
    selector = GUISelectors()
    selector.show_current_settings(config)


if __name__ == "__main__":
    # Test the GUI selectors
    print("Testing GUI Selectors...")

    # Test video selection
    video = select_driver_video_gui()
    if video:
        print(f"Selected video: {video}")
        duration, formatted = VideoInfo.get_duration(video)
        print(f"Duration: {formatted}")

    # Test folder selection
    folder = select_output_folder_gui()
    if folder:
        print(f"Selected folder: {folder}")

    # Test settings display
    test_config = {
        "driver_video": video or "",
        "output_folder": folder or "",
        "api_key": "test_key_12345",
        "verbose_logging": False,
        "duplicate_detection": True,
        "delay_between_generations": 1
    }
    show_settings_gui(test_config)