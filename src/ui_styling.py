"""
Unified UI styling module for RunwayML Batch Automation
Based on iOS-Vcam-server terminal UI patterns
"""

import os
import sys
from typing import Optional, List, Tuple
from pathlib import Path

class UIStyler:
    """Provides consistent terminal UI styling across all modules"""

    # Terminal width standard
    TERMINAL_WIDTH = 89
    SEPARATOR_WIDTH = 89
    CONTENT_WIDTH = 85

    # Box drawing characters for professional borders
    BOX_TOP_LEFT = "╔"
    BOX_TOP_RIGHT = "╗"
    BOX_BOTTOM_LEFT = "╚"
    BOX_BOTTOM_RIGHT = "╝"
    BOX_HORIZONTAL = "═"
    BOX_VERTICAL = "║"
    BOX_CROSS = "╬"
    BOX_T_DOWN = "╦"
    BOX_T_UP = "╩"
    BOX_T_RIGHT = "╠"
    BOX_T_LEFT = "╣"

    # Separator styles
    MAJOR_SEP = "═" * SEPARATOR_WIDTH
    SECTION_SEP = "─" * SEPARATOR_WIDTH
    MINOR_SEP = "─" * (SEPARATOR_WIDTH - 4)

    # Status indicators (text-based for compatibility)
    STATUS_OK = "[OK]"
    STATUS_ERROR = "[ERROR]"
    STATUS_WARN = "[WARN]"
    STATUS_INFO = "[INFO]"
    STATUS_RUNNING = "[RUNNING]"
    STATUS_PENDING = "[PENDING]"
    STATUS_COMPLETE = "[COMPLETE]"

    @staticmethod
    def clear_screen():
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_color(text: str, color_code: str):
        """Print text with ANSI color code"""
        print(f"\033[{color_code}m{text}\033[0m")

    @staticmethod
    def print_cyan(text: str):
        """Print text in cyan"""
        UIStyler.print_color(text, "96")

    @staticmethod
    def print_green(text: str):
        """Print text in green"""
        UIStyler.print_color(text, "92")

    @staticmethod
    def print_yellow(text: str):
        """Print text in yellow"""
        UIStyler.print_color(text, "93")

    @staticmethod
    def print_red(text: str):
        """Print text in red"""
        UIStyler.print_color(text, "91")

    @staticmethod
    def print_magenta(text: str):
        """Print text in magenta"""
        UIStyler.print_color(text, "95")

    @staticmethod
    def print_blue(text: str):
        """Print text in blue"""
        UIStyler.print_color(text, "94")

    @staticmethod
    def print_white(text: str):
        """Print text in white/bright"""
        UIStyler.print_color(text, "97")

    @staticmethod
    def print_gray(text: str):
        """Print text in gray"""
        UIStyler.print_color(text, "90")

    @staticmethod
    def center_text(text: str, width: int = None) -> str:
        """Center text within given width"""
        if width is None:
            width = UIStyler.TERMINAL_WIDTH
        padding = (width - len(text)) // 2
        return " " * padding + text

    @staticmethod
    def print_section_box(title: str, color: str = "cyan", box_type: str = "full"):
        """Print a section box header with proper alignment

        Args:
            title: The title text to display
            color: Color for the box (cyan, magenta, green, yellow, blue, red)
            box_type: 'top' for top only, 'bottom' for bottom only, 'full' for complete box
        """
        # Box is 71 chars wide (69 + 2 for borders)
        box_width = 69
        box_line_top = f"  {UIStyler.BOX_TOP_LEFT}{UIStyler.BOX_HORIZONTAL * box_width}{UIStyler.BOX_TOP_RIGHT}"
        box_line_bottom = f"  {UIStyler.BOX_BOTTOM_LEFT}{UIStyler.BOX_HORIZONTAL * box_width}{UIStyler.BOX_BOTTOM_RIGHT}"

        # Calculate padding for centered title - shift left by 1
        title_len = len(title)
        total_space = box_width - 2  # Space inside the box (minus the 2 spaces for borders)
        left_padding = (total_space - title_len) // 2
        right_padding = total_space - title_len - left_padding

        title_line = f"  {UIStyler.BOX_VERTICAL} {' ' * left_padding}{title}{' ' * right_padding} {UIStyler.BOX_VERTICAL}"

        # Print based on box type
        if box_type == "top":
            if color == "cyan":
                UIStyler.print_cyan(box_line_top)
                UIStyler.print_cyan(title_line)
            elif color == "magenta":
                UIStyler.print_magenta(box_line_top)
                UIStyler.print_magenta(title_line)
            elif color == "green":
                UIStyler.print_green(box_line_top)
                UIStyler.print_green(title_line)
            elif color == "yellow":
                UIStyler.print_yellow(box_line_top)
                UIStyler.print_yellow(title_line)
            elif color == "blue":
                UIStyler.print_blue(box_line_top)
                UIStyler.print_blue(title_line)
            elif color == "red":
                UIStyler.print_red(box_line_top)
                UIStyler.print_red(title_line)
            else:
                print(box_line_top)
                print(title_line)
        elif box_type == "bottom":
            if color == "cyan":
                UIStyler.print_cyan(box_line_bottom)
            elif color == "magenta":
                UIStyler.print_magenta(box_line_bottom)
            elif color == "green":
                UIStyler.print_green(box_line_bottom)
            elif color == "yellow":
                UIStyler.print_yellow(box_line_bottom)
            elif color == "blue":
                UIStyler.print_blue(box_line_bottom)
            elif color == "red":
                UIStyler.print_red(box_line_bottom)
            else:
                print(box_line_bottom)
        else:  # full box
            if color == "cyan":
                UIStyler.print_cyan(box_line_top)
                UIStyler.print_cyan(title_line)
                UIStyler.print_cyan(box_line_bottom)
            elif color == "magenta":
                UIStyler.print_magenta(box_line_top)
                UIStyler.print_magenta(title_line)
                UIStyler.print_magenta(box_line_bottom)
            elif color == "green":
                UIStyler.print_green(box_line_top)
                UIStyler.print_green(title_line)
                UIStyler.print_green(box_line_bottom)
            elif color == "yellow":
                UIStyler.print_yellow(box_line_top)
                UIStyler.print_yellow(title_line)
                UIStyler.print_yellow(box_line_bottom)
            elif color == "blue":
                UIStyler.print_blue(box_line_top)
                UIStyler.print_blue(title_line)
                UIStyler.print_blue(box_line_bottom)
            elif color == "red":
                UIStyler.print_red(box_line_top)
                UIStyler.print_red(title_line)
                UIStyler.print_red(box_line_bottom)
            else:
                print(box_line_top)
                print(title_line)
                print(box_line_bottom)

    @staticmethod
    def print_section_header(title: str, separator_char: str = "─"):
        """Print a section header with separators"""
        separator = separator_char * ((UIStyler.SEPARATOR_WIDTH - len(title) - 2) // 2)
        header = f"{separator} {title} {separator}"
        if len(header) < UIStyler.SEPARATOR_WIDTH:
            header += separator_char
        UIStyler.print_cyan(header[:UIStyler.SEPARATOR_WIDTH])

    @staticmethod
    def print_status_line(label: str, value: str, status: str = "ok"):
        """Print a formatted status line with label and value"""
        indent = "  "

        if status == "ok":
            status_indicator = UIStyler.STATUS_OK
            print(f"{indent}\033[92m{status_indicator}\033[0m {label}: \033[97m{value}\033[0m")
        elif status == "error":
            status_indicator = UIStyler.STATUS_ERROR
            print(f"{indent}\033[91m{status_indicator}\033[0m {label}: \033[91m{value}\033[0m")
        elif status == "warn":
            status_indicator = UIStyler.STATUS_WARN
            print(f"{indent}\033[93m{status_indicator}\033[0m {label}: \033[93m{value}\033[0m")
        else:
            status_indicator = UIStyler.STATUS_INFO
            print(f"{indent}\033[96m{status_indicator}\033[0m {label}: \033[96m{value}\033[0m")

    @staticmethod
    def print_menu_option(key: str, description: str, status: str = None):
        """Print a formatted menu option"""
        indent = "  "
        if status:
            print(f"{indent}\033[93m[{key}]\033[0m {description} \033[90m({status})\033[0m")
        else:
            print(f"{indent}\033[93m[{key}]\033[0m {description}")

    @staticmethod
    def print_submenu_option(key: str, description: str, indent_level: int = 1):
        """Print a formatted submenu option with additional indentation"""
        indent = "    " * indent_level
        print(f"{indent}• \033[93m{key}\033[0m - {description}")

    @staticmethod
    def print_progress_bar(current: int, total: int, width: int = 50, label: str = ""):
        """Print a progress bar with percentage"""
        percent = (current / total) * 100 if total > 0 else 0
        filled = int((current / total) * width) if total > 0 else 0
        bar = "█" * filled + "░" * (width - filled)

        if label:
            print(f"\r  {label}: [{bar}] {percent:.1f}% ({current}/{total})", end="")
        else:
            print(f"\r  Progress: [{bar}] {percent:.1f}% ({current}/{total})", end="")

    @staticmethod
    def print_main_logo():
        """Print the main RunwayML Batch ASCII art logo - original style"""
        # Top border
        print("=" * UIStyler.SEPARATOR_WIDTH)
        print()

        # Original ASCII art logo
        logo_lines = [
            "╦═╗╦ ╦╔╗╔╦ ╦╔═╗╦ ╦╔╦╗╦     ╔╗ ╔═╗╔╦╗╔═╗╦ ╦",
            "╠╦╝║ ║║║║║║║╠═╣╚╦╝║║║║     ╠╩╗╠═╣ ║ ║  ╠═╣",
            "╩╚═╚═╝╝╚╝╚╩╝╩ ╩ ╩ ╩ ╩╩═╝   ╚═╝╩ ╩ ╩ ╚═╝╩ ╩"
        ]

        for line in logo_lines:
            UIStyler.print_cyan(UIStyler.center_text(line))

        print()
        # Bottom border
        print("=" * UIStyler.SEPARATOR_WIDTH)

    @staticmethod
    def print_configuration_display(config: dict):
        """Print the current configuration in a formatted box"""
        UIStyler.print_section_box("CURRENT CONFIGURATION", "cyan", "full")
        print()

        # API Key Status
        api_key = config.get('api_key', '')
        if api_key:
            UIStyler.print_status_line("RunwayML API Key", "Configured", "ok")
        else:
            UIStyler.print_status_line("RunwayML API Key", "NOT CONFIGURED", "error")

        # Driver Video Status
        driver_video = config.get('driver_video', '')
        if driver_video and Path(driver_video).exists():
            video_name = Path(driver_video).name
            UIStyler.print_status_line("Driver Video", video_name, "ok")
            print(f"      \033[90mPath: {driver_video}\033[0m")
        else:
            UIStyler.print_status_line("Driver Video", "NOT CONFIGURED", "error")

        # Output Configuration
        output_location = config.get('output_location', 'centralized')
        if output_location == 'co-located':
            UIStyler.print_status_line("Output Mode", "Co-located with source images", "ok")
        else:
            output_folder = config.get('output_folder', '')
            if output_folder and Path(output_folder).exists():
                UIStyler.print_status_line("Output Folder", Path(output_folder).name, "ok")
                print(f"      \033[90mPath: {output_folder}\033[0m")
            else:
                UIStyler.print_status_line("Output Folder", "NOT CONFIGURED", "error")

        # Image Search Pattern
        pattern = config.get('image_search_pattern', 'genx')
        exact = config.get('exact_match', False)
        mode = "Exact Match" if exact else "Contains Pattern"
        UIStyler.print_status_line("Image Pattern", f'"{pattern}" ({mode})', "info")

        # Advanced Settings
        verbose = config.get('verbose_logging', False)
        duplicate = config.get('duplicate_detection', True)
        delay = config.get('delay_between_generations', 1)

        UIStyler.print_status_line("Verbose Logging", "ON" if verbose else "OFF", "info")
        UIStyler.print_status_line("Duplicate Detection", "ON" if duplicate else "OFF", "info")
        UIStyler.print_status_line("Generation Delay", f"{delay}s", "info")

        print()

    @staticmethod
    def print_processing_status(current_file: str, current: int, total: int, status: str = "processing"):
        """Print processing status with progress"""
        print("\n" + UIStyler.SECTION_SEP)
        UIStyler.print_cyan(f"  PROCESSING STATUS")
        print(UIStyler.SECTION_SEP)

        # File being processed
        print(f"\n  Current: \033[97m{current_file}\033[0m")

        # Status indicator
        if status == "processing":
            print(f"  Status: \033[93m{UIStyler.STATUS_RUNNING} Generating video...\033[0m")
        elif status == "complete":
            print(f"  Status: \033[92m{UIStyler.STATUS_COMPLETE} Video generated successfully\033[0m")
        elif status == "error":
            print(f"  Status: \033[91m{UIStyler.STATUS_ERROR} Generation failed\033[0m")
        elif status == "duplicate":
            print(f"  Status: \033[90m[SKIP] Duplicate detected\033[0m")

        # Progress bar
        UIStyler.print_progress_bar(current, total, label="Overall Progress")
        print("\n")