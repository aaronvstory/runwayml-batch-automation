import os
import base64
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import requests
import logging
from PIL import Image

# Import path utilities
from path_utils import path_manager

# Get logger instance (don't configure here - let UI handle it)
logger = logging.getLogger(__name__)

class RunwayActTwoBatchGenerator:
    # Available Act Two API ratios with dimensions
    AVAILABLE_RATIOS = {
        "16:9": {"api_value": "1280:720", "width": 1280, "height": 720, "aspect": 16/9},
        "9:16": {"api_value": "720:1280", "width": 720, "height": 1280, "aspect": 9/16},
        "1:1": {"api_value": "960:960", "width": 960, "height": 960, "aspect": 1.0},
        "4:3": {"api_value": "1104:832", "width": 1104, "height": 832, "aspect": 4/3},
        "3:4": {"api_value": "832:1104", "width": 832, "height": 1104, "aspect": 3/4},
        "21:9": {"api_value": "1584:672", "width": 1584, "height": 672, "aspect": 21/9}
    }

    def __init__(self, api_key: str, verbose: bool = True, driver_video_path: Optional[str] = None):
        self.api_key = api_key
        self.verbose = verbose

        # Use provided driver video or find default
        if driver_video_path:
            self.driver_video_path = str(path_manager.resolve_path(driver_video_path))
        else:
            default_video = path_manager.get_default_driver_video()
            self.driver_video_path = str(default_video) if default_video else ""

        self.driver_video_data_uri = None  # Will store encoded driver video
        self.base_url = "https://api.dev.runwayml.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"
        }
        # Downloads folder for duplicate checking
        self.downloads_folder = str(path_manager.downloads_dir)
        
    def encode_image_to_data_uri(self, image_path: str) -> str:
        """Convert local image file to base64 data URI"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Determine image format
            ext = Path(image_path).suffix.lower()
            if ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif ext == '.png':
                mime_type = 'image/png'
            elif ext == '.webp':
                mime_type = 'image/webp'
            else:
                mime_type = 'image/jpeg'  # Default
            
            # Encode to base64
            encoded = base64.b64encode(image_data).decode('utf-8')
            return f"data:{mime_type};base64,{encoded}"
            
        except Exception as e:
            if self.verbose:
                logger.error(f"Error encoding image {image_path}: {str(e)}")
            return None
    
    def encode_video_to_data_uri(self, video_path: str) -> str:
        """Convert local video file to base64 data URI"""
        try:
            with open(video_path, 'rb') as f:
                video_data = f.read()
            
            # Determine video format 
            ext = Path(video_path).suffix.lower()
            if ext == '.mp4':
                mime_type = 'video/mp4'
            elif ext == '.mov':
                mime_type = 'video/quicktime'
            elif ext == '.webm':
                mime_type = 'video/webm'
            else:
                mime_type = 'video/mp4'  # Default
            
            # Encode to base64
            encoded = base64.b64encode(video_data).decode('utf-8')
            return f"data:{mime_type};base64,{encoded}"
            
        except Exception as e:
            logger.error(f"Error encoding video {video_path}: {str(e)}")
            return None

    def analyze_image_aspect_ratio(self, image_path: str) -> Tuple[float, int, int]:
        """
        Analyze the aspect ratio of an input image

        Returns:
            Tuple of (aspect_ratio, width, height)
        """
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                aspect_ratio = width / height
                logger.info(f"Image {Path(image_path).name}: {width}x{height}, aspect ratio: {aspect_ratio:.3f}")
                return aspect_ratio, width, height
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return 1.0, 0, 0

    def select_best_ratio(self, image_aspect: float) -> dict:
        """
        Select the API ratio that best matches the input image aspect ratio
        This minimizes cropping/distortion

        Args:
            image_aspect: The aspect ratio of the input image

        Returns:
            Dict with the best matching ratio configuration
        """
        best_ratio = None
        min_difference = float('inf')

        for ratio_name, ratio_config in self.AVAILABLE_RATIOS.items():
            # Calculate the difference between image aspect and this ratio
            difference = abs(image_aspect - ratio_config["aspect"])

            if difference < min_difference:
                min_difference = difference
                best_ratio = {
                    "name": ratio_name,
                    **ratio_config
                }

        logger.info(f"Selected ratio {best_ratio['name']} (aspect: {best_ratio['aspect']:.3f}) "
                   f"for image aspect {image_aspect:.3f}")
        return best_ratio

    def resize_image_smart(self, image_path: str, target_ratio: dict, temp_folder: str = "temp_resized") -> str:
        """
        Resize image to match the selected API ratio with minimal cropping

        Args:
            image_path: Path to original image
            target_ratio: Target ratio configuration dict
            temp_folder: Temporary folder for resized images

        Returns:
            Path to resized image
        """
        try:
            # Create temp folder if it doesn't exist
            temp_path = Path(temp_folder)
            temp_path.mkdir(exist_ok=True)

            # Open the image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                original_width, original_height = img.size
                target_width = target_ratio["width"]
                target_height = target_ratio["height"]
                target_aspect = target_ratio["aspect"]
                current_aspect = original_width / original_height

                logger.info(f"Resizing from {original_width}x{original_height} to {target_width}x{target_height}")

                # Calculate crop to match target aspect ratio
                if current_aspect > target_aspect:
                    # Image is wider than target, crop width
                    new_width = int(original_height * target_aspect)
                    new_height = original_height
                    left = (original_width - new_width) // 2
                    top = 0
                    right = left + new_width
                    bottom = original_height

                    crop_percent = ((original_width - new_width) / original_width) * 100
                    logger.info(f"Cropping {crop_percent:.1f}% from width (centered)")
                else:
                    # Image is taller than target, crop height
                    new_width = original_width
                    new_height = int(original_width / target_aspect)
                    left = 0
                    top = (original_height - new_height) // 2
                    right = original_width
                    bottom = top + new_height

                    crop_percent = ((original_height - new_height) / original_height) * 100
                    logger.info(f"Cropping {crop_percent:.1f}% from height (centered)")

                # Crop the image
                cropped_img = img.crop((left, top, right, bottom))

                # Resize to target resolution
                resized_img = cropped_img.resize((target_width, target_height), Image.LANCZOS)

                # Save the resized image
                original_name = Path(image_path).stem
                ratio_name = target_ratio["name"].replace(":", "x")
                resized_path = temp_path / f"{original_name}_{ratio_name}.jpg"
                resized_img.save(resized_path, "JPEG", quality=95)

                logger.info(f"Resized image saved: {resized_path}")
                return str(resized_path)

        except Exception as e:
            logger.error(f"Error resizing image {image_path}: {str(e)}")
            return image_path  # Return original if resizing fails

    def resize_image_to_16_9(self, image_path: str, temp_folder: str = "temp_resized") -> str:
        """
        Resize image to 16:9 aspect ratio and return path to resized image
        
        Args:
            image_path: Path to original image
            temp_folder: Temporary folder for resized images
        """
        try:
            # Create temp folder if it doesn't exist
            temp_path = Path(temp_folder)
            temp_path.mkdir(exist_ok=True)
            
            # Open the image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (handles RGBA, P, etc.)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                original_width, original_height = img.size
                logger.info(f"Original image size: {original_width}x{original_height}")
                
                # Calculate 16:9 dimensions
                target_aspect = 16 / 9
                current_aspect = original_width / original_height
                
                if current_aspect > target_aspect:
                    # Image is wider than 16:9, crop width
                    new_width = int(original_height * target_aspect)
                    new_height = original_height
                    left = (original_width - new_width) // 2
                    top = 0
                    right = left + new_width
                    bottom = original_height
                else:
                    # Image is taller than 16:9, crop height
                    new_width = original_width
                    new_height = int(original_width / target_aspect)
                    left = 0
                    top = (original_height - new_height) // 2
                    right = original_width
                    bottom = top + new_height
                
                # Crop the image to 16:9
                cropped_img = img.crop((left, top, right, bottom))
                
                # Resize to standard resolution (1280x720 for 16:9)
                resized_img = cropped_img.resize((1280, 720), Image.LANCZOS)
                
                # Save the resized image
                original_name = Path(image_path).stem
                resized_path = temp_path / f"{original_name}_16x9.jpg"
                resized_img.save(resized_path, "JPEG", quality=95)
                
                logger.info(f"Resized image saved: {resized_path} (1280x720)")
                return str(resized_path)
                
        except Exception as e:
            logger.error(f"Error resizing image {image_path}: {str(e)}")
            # Return original path if resizing fails
            return image_path        
    def extract_name_from_genx_filename(self, filename: str) -> str:
        """Extract first and last name from genx filename like 'genx CIRILA MUNYON self.jpg'"""
        try:
            # Remove file extension
            name_part = Path(filename).stem
            
            # Remove 'genx' prefix and 'self' suffix, keep the middle part
            parts = name_part.split()
            if len(parts) >= 3 and parts[0].lower() == 'genx' and parts[-1].lower() == 'self':
                # Join the middle parts (first name, last name, etc.)
                return ' '.join(parts[1:-1])
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting name from filename {filename}: {str(e)}")
            return None
    
    def check_existing_videos(self, name: str, downloads_folder: str = None) -> bool:
        """Check if videos already exist for this person in downloads folder"""
        if downloads_folder is None:
            downloads_folder = self.downloads_folder
            
        try:
            downloads_path = Path(downloads_folder)
            if not downloads_path.exists():
                logger.warning(f"Downloads folder does not exist: {downloads_folder}")
                return False
            
            # Look for any video files containing this person's name
            name_parts = name.split()
            logger.info(f"🔍 Checking for existing videos with name parts: {name_parts}")
            
            # Search for video files (mp4, mov, etc.) recursively
            video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
            
            for video_ext in video_extensions:
                for video_file in downloads_path.rglob(f'*{video_ext}'):
                    video_name = video_file.stem.upper()
                    logger.info(f"   Checking video: {video_file.name} (stem: {video_name})")
                    # Check if all name parts are in the video filename
                    if all(part.upper() in video_name for part in name_parts):
                        logger.info(f"🔍 DUPLICATE DETECTED: Found existing video for {name}: {video_file.name}")
                        return True
            
            logger.info(f"✅ NO DUPLICATES: No existing videos found for {name}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking existing videos for {name}: {str(e)}")
            return False

    def get_genx_image_files(self, folder_path: str, search_pattern: str = 'genx', exact_match: bool = False) -> List[str]:
        """Get all image files matching the search pattern, excluding duplicates"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff', '.tif'}
        matching_image_files = []
        pattern_lower = search_pattern.lower()

        folder = Path(folder_path)
        if not folder.exists():
            logger.warning(f"Folder {folder_path} does not exist")
            return matching_image_files

        for file_path in folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                filename_lower = file_path.name.lower()

                # Check if filename matches pattern
                matches = False
                if exact_match:
                    import re
                    # Pattern should match as a complete segment
                    pattern_regex = r'(^|[^a-z0-9])' + re.escape(pattern_lower) + r'([^a-z0-9]|$)'
                    if re.search(pattern_regex, filename_lower):
                        matches = True
                else:
                    if pattern_lower in filename_lower:
                        matches = True

                if matches:
                    # Extract name from filename and check for existing videos
                    person_name = self.extract_name_from_genx_filename(file_path.name)
                    if person_name:
                        if self.check_existing_videos(person_name):
                            logger.info(f"⏭️  SKIPPING: {file_path.name} - Videos already exist for {person_name}")
                            continue
                        else:
                            logger.info(f"✅ ADDING: {file_path.name} - No existing videos found for {person_name}")
                    else:
                        logger.warning(f"⚠️  Could not extract name from: {file_path.name} - Processing anyway")

                    matching_image_files.append(str(file_path))

        logger.info(f"Found {len(matching_image_files)} new images matching '{search_pattern}' to process in {folder_path}")
        return matching_image_files    
    def get_all_folders(self, root_directory: str) -> List[str]:
        """Get all folders in the root directory, sorted alphabetically"""
        folders = []
        root_path = Path(root_directory)
        
        if not root_path.exists():
            logger.error(f"Root directory {root_directory} does not exist")
            return folders
        
        # Get all direct subdirectories
        for folder_path in root_path.iterdir():
            if folder_path.is_dir():
                folders.append(str(folder_path))
        
        # Sort alphabetically by folder name
        folders.sort(key=lambda x: Path(x).name.upper())
        
        for folder_path in folders:
            logger.info(f"Found folder: {folder_path}")
        
        return folders        
    def create_act_two_generation(self, character_image_path: str, output_folder: str, config: Optional[Dict] = None) -> Optional[str]:
        """
        Generate Act-Two video using driver video and character image with configuration

        Args:
            character_image_path: Path to character image
            output_folder: Folder to save generated video
            config: Optional configuration dictionary with all settings
        """
        try:
            # Check if driver video exists
            if not Path(self.driver_video_path).exists():
                logger.error(f"Driver video not found: {self.driver_video_path}")
                return None

            # Encode driver video to data URI if not already done
            if not hasattr(self, 'driver_video_data_uri') or not self.driver_video_data_uri:
                logger.info(f"Encoding driver video to data URI: {self.driver_video_path}")
                self.driver_video_data_uri = self.encode_video_to_data_uri(self.driver_video_path)
                if not self.driver_video_data_uri:
                    logger.error("Failed to encode driver video")
                    return None

            # Use config if provided, otherwise use defaults
            if config is None:
                config = {}

            # Determine aspect ratio mode
            aspect_mode = config.get('aspect_ratio_mode', 'smart')

            if aspect_mode == 'smart':
                # Smart selection - analyze image and select best ratio
                image_aspect, _, _ = self.analyze_image_aspect_ratio(character_image_path)
                target_ratio = self.select_best_ratio(image_aspect)
                logger.info(f"Smart aspect ratio selection: Using {target_ratio['name']} to minimize cropping")
            else:
                # Fixed ratio from config
                fixed_ratio = config.get('fixed_aspect_ratio', '16:9')
                if fixed_ratio in self.AVAILABLE_RATIOS:
                    target_ratio = self.AVAILABLE_RATIOS[fixed_ratio]
                    logger.info(f"Using fixed aspect ratio: {fixed_ratio}")
                else:
                    # Fallback to 16:9 if invalid ratio
                    target_ratio = self.AVAILABLE_RATIOS["16:9"]
                    logger.warning(f"Invalid fixed ratio {fixed_ratio}, using 16:9")

            # Resize image to selected ratio
            logger.info(f"Resizing image to {target_ratio['name']} ({target_ratio['api_value']})")
            resized_image_path = self.resize_image_smart(character_image_path, target_ratio)

            # Encode character image to data URI
            logger.info(f"Encoding character image to data URI: {resized_image_path}")
            character_image_data_uri = self.encode_image_to_data_uri(resized_image_path)
            if not character_image_data_uri:
                logger.error(f"Failed to encode character image: {resized_image_path}")
                return None

            # Create output filename with ratio info
            image_name = Path(character_image_path).stem
            ratio_suffix = target_ratio["name"].replace(":", "x")
            output_path = Path(output_folder) / f"{image_name}_act_two_{ratio_suffix}.mp4"

            logger.info(f"Starting Act-Two generation for: {character_image_path}")
            logger.info(f"Using ratio: {target_ratio['name']} ({target_ratio['api_value']})")

            # Build Act-Two generation payload with all config parameters
            payload = {
                "character": {
                    "type": "image",
                    "uri": character_image_data_uri
                },
                "reference": {
                    "type": "video",
                    "uri": self.driver_video_data_uri
                },
                "bodyControl": config.get('body_control', False),
                "expressionIntensity": config.get('expression_intensity', 1.0),
                "model": config.get('model_version', 'act_two'),
                "ratio": target_ratio["api_value"]  # Use selected ratio
            }

            # Add optional body control parameters if enabled
            if config.get('body_control', False):
                payload["motionStrength"] = config.get('motion_strength', 1.0)
                payload["stabilization"] = config.get('stabilization', True)
                payload["preservePose"] = config.get('preserve_pose', False)
                payload["motionSmoothing"] = config.get('motion_smoothing', 0.5)

            # Add quality settings if specified
            if config.get('quality'):
                payload["quality"] = config.get('quality', 'standard')

            # Add seed if specified
            if config.get('seed') is not None:
                payload["seed"] = config.get('seed')

            # Add prompts if specified
            if config.get('prompt'):
                payload["prompt"] = config.get('prompt')
            if config.get('negative_prompt'):
                payload["negativePrompt"] = config.get('negative_prompt')

            logger.info(f"API Payload settings: Expression={payload.get('expressionIntensity')}, "
                       f"BodyControl={payload.get('bodyControl')}, Model={payload.get('model')}")            
            response = requests.post(
                f"{self.base_url}/character_performance",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to create Act-Two task: {response.text}")
                return None
            
            task_data = response.json()
            task_id = task_data['id']
            logger.info(f"Act-Two task created. Task ID: {task_id}")
            
            # Wait for completion (polling)
            max_wait = 600  # 10 minutes
            wait_time = 0
            
            while wait_time < max_wait:
                time.sleep(10)  # Check every 10 seconds
                wait_time += 10
                
                # Check task status
                status_response = requests.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=self.headers
                )
                
                if status_response.status_code != 200:
                    logger.error(f"Failed to check task status: {status_response.text}")
                    return None
                
                status_data = status_response.json()
                status = status_data.get('status', 'UNKNOWN')
                
                logger.info(f"Task {task_id} status: {status}")
                
                if status == 'SUCCEEDED':
                    # Get video URL
                    video_url = status_data.get('output', [None])[0]
                    if video_url:
                        logger.info(f"Act-Two generation completed! URL: {video_url}")
                        
                        # Download the video
                        video_response = requests.get(video_url)
                        if video_response.status_code == 200:
                            # Ensure output directory exists
                            output_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            with open(output_path, 'wb') as f:
                                f.write(video_response.content)

                            logger.info(f"✅ Video saved to: {output_path}")
                            logger.info(f"   Output resolution: {target_ratio['width']}x{target_ratio['height']}")
                            return str(output_path)
                        else:
                            logger.error(f"Failed to download video: {video_response.status_code}")
                    else:
                        logger.error("No video URL in response")
                    return None
                    
                elif status == 'FAILED':
                    logger.error(f"Task {task_id} failed: {status_data.get('error', 'Unknown error')}")
                    return None
            
            logger.error(f"Task {task_id} timed out after {max_wait} seconds")
            return None
            
        except Exception as e:
            logger.error(f"Error in Act-Two generation for {character_image_path}: {str(e)}")
            return None        
    def process_all_images(self, target_directory: str, output_directory: str = r"C:\Users\ashrv\Downloads",
                          delay_between_generations: int = 1, co_located_output: bool = False):
        """
        Main function to process all images in genx folders using Act-Two
        NOW WITH DUPLICATE DETECTION!

        Args:
            target_directory: Root directory to search for genx folders
            output_directory: Directory to save generated videos (used when co_located_output=False)
            delay_between_generations: Seconds to wait between API calls
            co_located_output: If True, save videos in same folder as source images
        """
        
        logger.info("=== RUNWAY ACT-TWO BATCH GENERATOR WITH DUPLICATE DETECTION ===")
        logger.info(f"Driver video: {self.driver_video_path}")
        logger.info(f"Searching for images with 'genx' in filename in: {target_directory}")
        if co_located_output:
            logger.info("Output location: Same folder as source images (co-located)")
        else:
            logger.info(f"Output directory: {output_directory}")
        logger.info(f"Downloads folder for duplicate checking: {self.downloads_folder}")
        logger.info("🔍 Duplicate detection is ENABLED - checking for existing videos")
        logger.info("=" * 70)
        
        # ANSI color codes
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        RESET = '\033[0m'
        
        # Check if driver video exists
        if not Path(self.driver_video_path).exists():
            logger.error(f"Driver video not found: {self.driver_video_path}")
            print(f"{RED}Driver video not found: {self.driver_video_path}{RESET}")
            return
        
        # Get all folders in the target directory
        all_folders = self.get_all_folders(target_directory)
        
        if not all_folders:
            logger.warning("No folders found in target directory!")
            print(f"{YELLOW}No folders found in target directory!{RESET}")
            return        
        # Process each folder looking for genx images
        total_images = 0
        successful_generations = 0
        failed_generations = 0
        skipped_duplicates = 0
        
        for folder in all_folders:
            logger.info(f"\nProcessing folder: {folder}")
            print(f"\n{CYAN}🔍 Processing folder: {Path(folder).name}{RESET}")
            
            # Get all genx images in this folder (with duplicate filtering)
            genx_image_files = self.get_genx_image_files(folder)
            total_found = len([f for f in Path(folder).iterdir() 
                              if f.is_file() and 'genx' in f.name.lower() 
                              and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff', '.tif'}])
            skipped_in_folder = total_found - len(genx_image_files)
            total_images += len(genx_image_files)
            skipped_duplicates += skipped_in_folder
            
            if not genx_image_files and total_found == 0:
                logger.info(f"No genx image files found in {folder}")
                print(f"{YELLOW}No genx images found in {Path(folder).name}{RESET}")
                continue
            elif not genx_image_files and total_found > 0:
                logger.info(f"All {total_found} genx images in {folder} were duplicates - skipped")
                print(f"{YELLOW}All {total_found} genx images were duplicates - skipped{RESET}")
                continue
            
            print(f"{GREEN}Found {len(genx_image_files)} NEW genx images in {Path(folder).name}{RESET}")
            if skipped_in_folder > 0:
                print(f"{YELLOW}⏭️  Skipped {skipped_in_folder} duplicates{RESET}")
            
            # Process each genx image
            for i, image_path in enumerate(genx_image_files, 1):
                logger.info(f"\n[{i}/{len(genx_image_files)}] Processing: {Path(image_path).name}")
                print(f"\n{MAGENTA}[{i}/{len(genx_image_files)}] Processing: {Path(image_path).name}{RESET}")

                # Determine output folder based on co_located_output setting
                if co_located_output:
                    # Save to same folder as source image
                    specific_output = Path(image_path).parent
                    logger.info(f"Output will be saved to source folder: {specific_output}")
                else:
                    # Save to centralized output directory
                    specific_output = Path(output_directory)

                result = self.create_act_two_generation(
                    character_image_path=image_path,
                    output_folder=str(specific_output)
                )
                
                if result:
                    successful_generations += 1
                    logger.info(f"Success: {Path(result).name}")
                    print(f"{GREEN}✅ Success: {Path(result).name}{RESET}")
                else:
                    failed_generations += 1
                    logger.error(f"Failed: {Path(image_path).name}")
                    print(f"{RED}❌ Failed: {Path(image_path).name}{RESET}")
                
                # Add delay between API calls to avoid rate limiting
                if i < len(genx_image_files) and delay_between_generations > 0:
                    logger.info(f"Waiting {delay_between_generations} seconds before next generation...")
                    print(f"{BLUE}⏳ Waiting {delay_between_generations} seconds...{RESET}")
                    time.sleep(delay_between_generations)        
        # Final summary
        logger.info("\n" + "=" * 70)
        logger.info("=== BATCH PROCESSING COMPLETE WITH DUPLICATE DETECTION ===")
        logger.info(f"Total NEW images processed: {total_images}")
        logger.info(f"Duplicates skipped: {skipped_duplicates}")
        logger.info(f"Successful generations: {successful_generations}")
        logger.info(f"Failed generations: {failed_generations}")
        logger.info(f"Success rate: {(successful_generations/total_images*100):.1f}%" if total_images > 0 else "N/A")
        logger.info("=" * 70)
        
        print("\n" + CYAN + "=" * 70 + RESET)
        print(GREEN + "🎉 BATCH PROCESSING COMPLETE WITH DUPLICATE DETECTION!" + RESET)
        print(f"{BLUE}📊 Total NEW images processed: {total_images}{RESET}")
        print(f"{YELLOW}⏭️  Duplicates skipped: {skipped_duplicates}{RESET}")
        print(f"{GREEN}✅ Successful generations: {successful_generations}{RESET}")
        print(f"{RED}❌ Failed generations: {failed_generations}{RESET}")
        print(f"{MAGENTA}📈 Success rate: {(successful_generations/total_images*100):.1f}%{RESET}" if total_images > 0 else f"{MAGENTA}N/A{RESET}")
        print(f"{CYAN}🔍 Duplicate detection saved you from processing {skipped_duplicates} existing videos!{RESET}")
        print(CYAN + "=" * 70 + RESET)


def main():
    """Main function to run the batch generator"""
    
    # ANSI color codes
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ORANGE = '\033[38;5;208m'
    RESET = '\033[0m'
    
    # Configuration
    API_KEY = "key_bd089604ad733171ce9bdb91e11ccbd18690542c8519922bfb242bca7db3fb95e3e86ac3fc6c33065c67108988deeede0841ac90050394f46518d0d8c83c97f8"
    
    # Get user input for directories
    while True:
        target_directory = input(f"\n{GREEN}Enter the target directory path to search for 'genx' folders: {RESET}").strip()
        if target_directory and Path(target_directory).exists():
            break
        print(f"{RED}Invalid directory path. Please try again.{RESET}")
    
    output_directory = r"C:\Users\ashrv\Downloads"
    delay = 1  # Fixed 1-second delay
    
    # Create and run generator
    try:
        generator = RunwayActTwoBatchGenerator(API_KEY)
        generator.process_all_images(
            target_directory=target_directory,
            output_directory=output_directory,
            delay_between_generations=delay
        )
        
        print(f"\n{GREEN}All done! Check your videos in: {output_directory}{RESET}")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"{RED}Fatal error: {str(e)}{RESET}")
        print(f"{WHITE}Please check your API key and network connection.{RESET}")


if __name__ == "__main__":
    # Add Windows console color support
    os.system('color')    
    # ANSI color codes
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ORANGE = '\033[38;5;208m'
    LIGHT_PINK = '\033[38;5;217m'  # Light pink color
    RESET = '\033[0m'
    
    print(CYAN + "=" * 70 + RESET)
    print(LIGHT_PINK + "🚀 RUNWAY ACT-TWO BATCH GENERATOR WITH DUPLICATE DETECTION 🚀" + RESET)
    print(CYAN + "=" * 70 + RESET)
    print(GREEN + "This script will:" + RESET)
    print(BLUE + "1." + RESET + YELLOW + " Use your driver video for Act Two generation" + RESET)
    print(BLUE + "2." + RESET + YELLOW + " Search all folders for images containing 'genx' in their filename" + RESET)  
    print(BLUE + "3." + RESET + YELLOW + " 🔍 CHECK FOR DUPLICATES in Downloads folder and SKIP existing videos" + RESET)
    print(BLUE + "4." + RESET + YELLOW + " Resize NEW images to 16:9 aspect ratio" + RESET)
    print(BLUE + "5." + RESET + YELLOW + " Generate Act-Two videos ONLY for new images" + RESET)
    print(BLUE + "6." + RESET + YELLOW + " Save videos organized by source folder" + RESET)
    print(CYAN + "=" * 70 + RESET)
    print(GREEN + "🎯 NEW FEATURE: Duplicate detection prevents wasting API calls!" + RESET)
    from pathlib import Path
    downloads_path = str(Path.home() / "Downloads")
    print(YELLOW + f"📁 Checks: {downloads_path} for existing videos" + RESET)
    print(CYAN + "=" * 70 + RESET)
    
    # Check if required packages are available
    try:
        from PIL import Image
        main()
    except ImportError:
        print(RED + "Error: Pillow package not installed" + RESET)
        print(WHITE + "Please install it with: pip install Pillow" + RESET)
        print(WHITE + "Then run this script again." + RESET)