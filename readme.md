# M30 Instagram Post Automation Pipeline

## Quick Start

### With Docker (Recommended)
```bash
docker-compose up
```

### With Python (Local Development)
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows bash
pip install -r requirements.txt
python -m src.main
```

## Overview

This project automates the creation of Instagram posts for the Minerva Class of 2030.

Each student submits:

A baby photo

A recent photo

A caption

via Google Forms. The pipeline retrieves submissions, processes the images into a standardized branded template, and generates ready-to-publish Instagram posts.

The goal was to eliminate repetitive manual editing, ensure visual consistency, and create a scalable workflow for handling multiple student submissions efficiently.

## Examples

### Image Processing Pipeline

The pipeline transforms raw student photos into branded Instagram posts with consistent formatting:

<table>
<tr>
<td align="center"><b>Original Image</b></td>
<td align="center"><b>Processed Result</b></td>
</tr>
<tr>
<td><img src="images/Leonardo/raw/1WKho9PCTLPEZuNLVvjR0cZ34P2hlaH1F.jpg" width="300"/></td>
<td><img src="images/Leonardo/edited/baby_edited.jpg" width="300"/></td>
</tr>
</table>

**Processing steps:**
- Downloads images from Google Forms submissions
- Resizes while preserving aspect ratio (no distortion)
- Applies branded template with consistent layout
- Centers images and maintains quality
- Outputs Instagram-ready posts

### See It Live

Check out the final posts on Instagram: [**@minervauni2030**](https://www.instagram.com/minervauni2030/?hl=en)

## Problem Statement

The Minerva Class of 2030 needed a structured and consistent way to generate Instagram posts for their cohort. Manually editing and formatting each post would have been time-consuming and error-prone.

## Key challenges:

Collecting exactly two photos per student

Maintaining consistent layout and branding

Avoiding image distortion during resizing

Reducing manual editing workload

Organizing outputs cleanly per student

This pipeline solves those challenges through automation and modular design.

## Architecture Overview

1. Data Collection

Students submit responses through Google Forms

Responses are automatically stored in Google Sheets

2. Data Retrieval

The system fetches submission data using the Google Sheets API

Validates that each student uploaded exactly two images

Extracts image URLs and captions

3. Image Processing

Downloads images from provided URLs

Resizes while preserving aspect ratio

Prevents distortion or unnecessary upscaling

Inserts images into a predefined branded template

Centers and formats images automatically

4. Output Generation

Generates final Instagram-ready images

Organizes outputs by student

Prepares captions for publishing

Project Structure
```
project/
├── Dockerfile          # Container configuration
├── docker-compose.yml  # Docker Compose setup
├── requirements.txt    # Python dependencies
├── pytest.ini          # pytest configuration
├── .gitignore          # Git ignore rules
│
├── src/
│   ├── main.py         # Entry point
│   ├── insta.py        # Instagram posting logic
│   ├── images.py       # Image processing
│   └── sheets.py       # Google Sheets integration
│
├── tests/
│   └── test_insta.py   # Test suite
│
├── utils/
│   ├── credentials.json  # (excluded from git) API credentials
│   ├── session.json      # (excluded from git) Instagram session
│   ├── state.json        # (excluded from git) Script state
│   └── fonts/            # Font files for image processing
│
├── [Student Folders]/    # Per-student organized outputs
│   ├── Ayaan/
│   ├── Leonardo/
│   └── ...
│
└── README.md
```

## Key Features

Aspect-ratio-preserving image resizing

Template-based branding system

Automatic validation for required submissions

Modular and extensible architecture

Organized per-student output storage

Error handling for incomplete submissions

---

## Setup & Installation

### Prerequisites
- **Docker approach**: Docker and Docker Compose
- **Local approach**: Python 3.11+, pip

### Environment Variables
Create a `.env` file in the project root:
```
IG_USERNAME=your_instagram_username
IG_PASSWORD=your_instagram_password
GOOGLE_FORMS_SHEET_ID=your_sheet_id
SESSION_FILE=/app/utils/session.json
STATE_PATH=/app/utils/state.json
```

### Installation

**Option 1: Docker (Recommended)**
```bash
docker-compose up
```
- No Python installation needed
- Automatic dependency installation
- Runs in isolated container
- See [DOCKER.md](DOCKER.md) for detailed instructions

**Option 2: Local Python Setup**
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows bash / Git Bash)
source .venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python -m src.main
```

---

## Testing

Run the test suite:
```bash
# From project root with venv activated
pytest tests/test_insta.py -v
```

**Current Status**: All 8 tests passing ✅
- Tests for Instagram post uploading with tags and location
- Tests for image album posting
- Geolocation validation tests

---


Anyone cloning this repo will need to:
1. Create their own `.env` file with credentials
2. Run `docker-compose up` or local installation
3. All data stays private on their machine

---

## Performance & Impact

Significantly reduced manual editing time

Standardized visual identity across all posts

Automated repetitive formatting tasks

Created a scalable content production workflow

Future iterations may include concrete metrics such as:

Average processing time per student

Total posts generated

Percentage reduction in manual workload


## Privacy Considerations

This repository does not include real student images, personal data, or API credentials.

Sample data and placeholder images are provided for demonstration.

Production credentials and private assets are excluded.

All personal content used in deployment remains private.


Tech Stack

**Runtime**
- Python 3.11
- Docker & Docker Compose (containerization)

**Image Processing**
- Pillow (PIL) - Image manipulation
- MoviePy - Video processing
- OpenCV - Computer vision
- ImageIO - Image I/O

**API & Web**
- Instagrapi - Instagram API wrapper
- Google Sheets API - Data retrieval
- Requests - HTTP client
- python-dotenv - Environment variable management

**Geolocation**
- geopy - Geographic coordinate lookup (Nominatim)

**Testing & Quality**
- pytest - Test framework
- pytest-mock - Mocking for tests

**Utilities**
- tqdm - Progress bars
- Pydantic - Data validation
