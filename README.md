# RunwayML Batch Automation

A powerful batch processing tool for RunwayML Gen-3 Alpha video generation with advanced automation features.

## Features

- **Batch Video Generation**: Process multiple prompts simultaneously with automated queue management
- **Smart Queue Management**: Intelligent handling of rate limits and generation states
- **Comprehensive Status Tracking**: Real-time monitoring of all generation jobs
- **Asset Management**: Automatic downloading and organization of generated videos
- **Watermark Removal**: Built-in support for video processing and watermark removal
- **Error Recovery**: Robust error handling and automatic retry mechanisms
- **Professional UI**: Clean, user-friendly interface with detailed status information

## Installation

### Prerequisites
- Python 3.8 or higher
- RunwayML account with Gen-3 Alpha access
- API credentials

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/runwayml-batch.git
cd runwayml-batch
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API credentials in `config/config.json`:
```json
{
  "api_key": "your_runwayml_api_key",
  "team_id": "your_team_id"
}
```

## Usage

### Running the Application

1. **Using the batch file (Windows):**
```bash
RunwayML_Batch.bat
```

2. **Direct Python execution:**
```bash
python src/main.py
```

### Menu Options

- **[1] Start New Batch**: Begin processing a new batch of prompts
- **[2] Resume Previous Batch**: Continue processing from a saved state
- **[3] Check Status**: View the current status of all jobs
- **[4] Download Assets**: Download completed videos
- **[5] View History**: Browse generation history
- **[6] Settings**: Configure API and processing settings
- **[7] Exit**: Safely exit the application

## Configuration

### API Settings
- Located in `config/config.json`
- Includes API key, team ID, and endpoint configurations

### Processing Settings
- Batch size limits
- Retry attempts
- Timeout configurations
- Download preferences

## Project Structure

```
RunwayML-batch/
├── src/
│   ├── main.py                 # Main application entry point
│   ├── api_handler.py           # RunwayML API interactions
│   ├── batch_processor.py       # Batch processing logic
│   ├── status_tracker.py        # Job status monitoring
│   ├── asset_downloader.py      # Video download management
│   └── utils/                   # Utility functions
├── config/
│   └── config.json             # Configuration file
├── assets/                     # Downloaded videos
├── logs/                       # Application logs
└── README.md
```

## Features in Detail

### Batch Processing
- Supports multiple prompts in a single batch
- Automatic queue management
- Rate limit handling
- Progress tracking

### Status Monitoring
- Real-time status updates
- Detailed job information
- Error reporting
- Completion notifications

### Asset Management
- Automatic video downloading
- Organized file structure
- Metadata preservation
- Batch download support

## Troubleshooting

### Common Issues

1. **Rate Limiting**: The application automatically handles rate limits with intelligent retry logic
2. **Connection Errors**: Built-in reconnection mechanisms with exponential backoff
3. **Failed Generations**: Automatic retry with configurable attempts

### Logging
- Detailed logs are saved in the `logs/` directory
- Log levels can be configured in the settings

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is not officially affiliated with RunwayML. Use at your own risk and in accordance with RunwayML's terms of service.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.