"""
Path utilities for cross-platform compatibility and dynamic path resolution.
Handles user directories, relative paths, and environment variables.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Union

class PathManager:
    """Manages all path operations for the RunwayML automation tool."""

    def __init__(self):
        """Initialize path manager with smart defaults."""
        # Determine the base directory based on execution context
        if getattr(sys, 'frozen', False):
            # Running as compiled executable - use exe location
            self.project_dir = Path(sys.executable).parent
            self.module_dir = self.project_dir / "src"  # For compatibility
        else:
            # Running as Python script
            self.module_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            self.project_dir = self.module_dir.parent

        # Keep script_dir for compatibility but point to project root
        self.script_dir = self.project_dir
        self.home_dir = Path.home()
        self.downloads_dir = self.get_downloads_folder()

    def get_downloads_folder(self) -> Path:
        """
        Get the user's Downloads folder across different platforms.

        Returns:
            Path to the Downloads folder
        """
        # Windows
        if os.name == 'nt':
            import winreg
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
                    downloads_path = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]
                    return Path(downloads_path)
            except:
                pass

        # Fallback to common locations
        possible_paths = [
            self.home_dir / "Downloads",
            self.home_dir / "downloads",
            Path(os.environ.get("USERPROFILE", self.home_dir)) / "Downloads" if os.name == 'nt' else None,
        ]

        for path in possible_paths:
            if path and path.exists():
                return path

        # Final fallback - create Downloads folder if it doesn't exist
        downloads = self.home_dir / "Downloads"
        downloads.mkdir(exist_ok=True)
        return downloads

    def resolve_path(self, path_str: Union[str, Path], base_dir: Optional[Path] = None) -> Path:
        """
        Resolve a path string to an absolute Path object.
        Handles:
        - Relative paths (relative to script directory or base_dir)
        - Absolute paths
        - Tilde expansion (~)
        - Environment variables (%VAR% on Windows, $VAR on Unix)

        Args:
            path_str: Path string to resolve
            base_dir: Base directory for relative paths (defaults to script directory)

        Returns:
            Resolved absolute Path object
        """
        if not path_str:
            return self.script_dir

        # Convert to string if Path object
        path_str = str(path_str)

        # Expand environment variables
        path_str = os.path.expandvars(path_str)

        # Expand tilde
        path_str = os.path.expanduser(path_str)

        # Create Path object
        path = Path(path_str)

        # If already absolute, return as is
        if path.is_absolute():
            return path

        # Otherwise, make it relative to base_dir or script directory
        base = base_dir if base_dir else self.script_dir
        return (base / path).resolve()

    def get_default_driver_video(self) -> Optional[Path]:
        """
        Find a driver video ONLY in the assets folder.
        NEVER scans Downloads or other folders.

        Returns:
            Path to driver video from assets or None if not found
        """
        # ONLY check assets folder in the project directory
        assets_videos = self.get_all_driver_videos()
        if assets_videos:
            # Prefer files with 'driver' in name
            for video in assets_videos:
                if 'driver' in video.name.lower():
                    return video
            # Otherwise return first found in assets
            return assets_videos[0]

        # NO fallback to Downloads or anywhere else
        return None

    def get_all_driver_videos(self) -> list[Path]:
        """
        Get all available driver videos from assets folder.

        Returns:
            List of video paths found in assets folder
        """
        assets_dir = self.project_dir / "assets"
        video_extensions = ['.mp4', '.mov', '.webm', '.avi', '.mkv']
        all_videos = []

        if assets_dir.exists():
            for ext in video_extensions:
                # Case-insensitive search for videos
                all_videos.extend(assets_dir.glob(f"*{ext}"))
                all_videos.extend(assets_dir.glob(f"*{ext.upper()}"))

        # Remove duplicates and sort
        unique_videos = list(set(all_videos))
        return sorted(unique_videos, key=lambda x: x.name)

    def validate_path(self, path: Path, must_exist: bool = True,
                     file_type: Optional[str] = None) -> tuple[bool, str]:
        """
        Validate a path with optional existence and type checks.

        Args:
            path: Path to validate
            must_exist: Whether the path must exist
            file_type: Expected type ('file', 'dir', or None for any)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not path:
            return False, "Path is empty"

        if must_exist and not path.exists():
            return False, f"Path does not exist: {path}"

        if path.exists() and file_type:
            if file_type == 'file' and not path.is_file():
                return False, f"Path is not a file: {path}"
            elif file_type == 'dir' and not path.is_dir():
                return False, f"Path is not a directory: {path}"

        return True, ""

    def ensure_directory_exists(self, path: Path) -> Path:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            path: Directory path to ensure exists

        Returns:
            The path object
        """
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_relative_to_script(self, path: Path) -> str:
        """
        Get a path relative to the script directory if possible.

        Args:
            path: Path to convert

        Returns:
            Relative path string or absolute if not relative to script
        """
        try:
            return str(path.relative_to(self.script_dir))
        except ValueError:
            # Path is not relative to script directory
            return str(path)

# Global instance for convenience
path_manager = PathManager()