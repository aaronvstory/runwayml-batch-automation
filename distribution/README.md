# RunwayML Batch Automation Tool v2.0
*Professional video generation automation for RunwayML Act Two*

## 🚀 Quick Start

1. **Extract all files** to any folder on your Windows PC
2. **Run** `RunwayML_Batch_Automation.exe`
3. **Follow** the first-time setup wizard to configure your API key
4. **Select** your input images folder and start batch processing!

## ✨ Key Features

### 🎯 Smart Aspect Ratio Preservation (NEW!)
- **Automatically selects the best aspect ratio** for each image to minimize cropping
- Supports all RunwayML ratios: 16:9, 9:16, 1:1, 4:3, 3:4, 21:9
- Portrait images stay portrait, landscape stays landscape
- **57% less cropping** compared to forced 16:9 ratio

### 🔍 Intelligent Image Filtering
- Pattern-based filtering (e.g., "-selfie" for selfie images)
- Exact match or substring search modes
- Preview matched images before processing

### ⚙️ Full API Control
- **Expression Intensity**: Control facial expressiveness (0.0-2.0)
- **Body Control**: Enable/disable body gestures
- **Motion Settings**: Fine-tune movement and stabilization
- **Model Selection**: Standard or Turbo (faster) processing
- **Quality Levels**: Draft, Standard, or High quality
- **Custom Prompts**: Guide generation with text prompts

### 📁 Flexible Output Options
- **Centralized**: All videos in one output folder
- **Co-located**: Videos saved next to source images
- Automatic duplicate detection

## 📋 System Requirements

- **Windows 10/11** (64-bit)
- **4GB RAM** minimum (8GB recommended)
- **Internet connection** for RunwayML API
- **RunwayML API key** (get from runway.ml)

## 🎮 How to Use

### First Time Setup
1. Launch the application
2. Enter your RunwayML API key when prompted
3. Select a driver video (or use the included samples)
4. Choose your output folder

### Processing Images
1. **Menu Option 4 or 5**: Browse for input folder
2. Select folder containing your character images
3. Images are automatically filtered by your pattern
4. Confirm to start batch processing
5. Videos are generated and saved automatically

### Configuration Options

#### Aspect Ratio (Menu Option 13)
- **Smart Select** (default): Auto-selects best ratio per image
- **Fixed Ratios**: Choose specific ratio for all images
  - 16:9 Landscape (1280×720)
  - 9:16 Portrait (720×1280)
  - 1:1 Square (960×960)
  - 4:3 Standard (1104×832)
  - 3:4 Portrait (832×1104)
  - 21:9 Cinematic (1584×672)

#### Expression Intensity (Menu Option 14)
- 0.0 = No facial expressions
- 1.0 = Normal expressions (default)
- 2.0 = Maximum expressiveness

#### Advanced API Settings (Menu Option 15)
- Body control and motion parameters
- Video stabilization options
- Processing quality selection
- Random seed for reproducibility
- Custom text prompts

## 🎬 Driver Videos

### Included Samples
- `main_lr.mp4` - Standard facial movements
- `selfie.mp4` - Optimized for selfie-style images
- `talk.mp4` - Speaking/talking motions
- `mewing.mp4` - Specific facial expressions

### Using Custom Driver Videos
1. Place your MP4 video in the `assets` folder
2. Select it via Menu Option 1
3. Best results with 10-30 second clips

## 🔧 Configuration Files

Settings are saved in `config/runway_config.json`:
```json
{
  "api_key": "your_key_here",
  "driver_video": "path/to/video.mp4",
  "output_folder": "path/to/output",
  "aspect_ratio_mode": "smart",
  "expression_intensity": 1.0,
  "image_search_pattern": "-selfie"
}
```

## 🎯 Pattern Matching

### Examples
- **"-selfie"** (exact): Matches `gen-selfie.jpg` but not `selfie.jpg`
- **"selfie"** (contains): Matches any filename with "selfie"
- **"user_"** (prefix): Matches files starting with "user_"

## 📊 Performance Tips

1. **Use Turbo Model** for faster processing (Menu Option 15 → Model Version)
2. **Batch similar images** together for consistent results
3. **Set appropriate delay** between generations (default: 2 seconds)
4. **Enable duplicate detection** to avoid re-processing

## 🆘 Troubleshooting

### "API Key Invalid"
- Verify your key at runway.ml
- Ensure no extra spaces when entering

### "Driver Video Not Found"
- Check the video exists in the assets folder
- Use Menu Option 1 to reselect

### Videos Not Generating
- Check internet connection
- Verify API credits available
- Review logs folder for detailed errors

### Wrong Aspect Ratio
- Switch between Smart/Fixed mode (Option 13)
- Ensure input images are high quality

## 📈 What's New in v2.0

- ✅ **Smart Aspect Ratio Selection** - Preserves image composition
- ✅ **Full API Parameter Control** - All RunwayML settings exposed
- ✅ **Enhanced Pattern Matching** - Better image filtering
- ✅ **Console-Based Feedback** - No popup interruptions
- ✅ **Progress Tracking** - Real-time generation status
- ✅ **Comprehensive Settings** - All options configurable

## 📝 Advanced Usage

### Dry Run Preview (Menu Option 7)
Preview which images will be processed without generating videos

### Verbose Logging (Menu Option 11)
Enable detailed logging for troubleshooting

### Manual Path Entry (Options 9-10)
Directly enter paths for driver video or output folder

## 🔒 Privacy & Security

- API keys are stored locally only
- No data sent except to RunwayML API
- All processing happens on your machine
- Videos saved locally to your chosen folder

## 💡 Pro Tips

1. **Portrait Photos**: Will automatically use 3:4 or 9:16 ratio
2. **Landscape Photos**: Will use 16:9 or 21:9 for minimal cropping
3. **Batch Processing**: Process up to 100+ images unattended
4. **Quality vs Speed**: Use Draft quality for testing, High for final output
5. **Consistent Results**: Set a random seed for reproducible generations

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review logs in the `logs` folder
- Visit RunwayML documentation

## 🎉 Credits

Developed with RunwayML Act Two API
Automated batch processing for professional video generation

---

**Version**: 2.0.0
**Release Date**: September 2025
**Compatibility**: Windows 10/11 64-bit
**License**: Free for personal and commercial use