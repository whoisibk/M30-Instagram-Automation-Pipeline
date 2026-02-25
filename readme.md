## M30 Instagram Post Automation Pipeline

## Overview

This project automates the creation of Instagram posts for the Minerva Class of 2030.

Each student submits:

A baby photo

A recent photo

A caption

via Google Forms. The pipeline retrieves submissions, processes the images into a standardized branded template, and generates ready-to-publish Instagram posts.

The goal was to eliminate repetitive manual editing, ensure visual consistency, and create a scalable workflow for handling multiple student submissions efficiently.

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
project/
│
├── pipeline.py          # Main orchestration logic
├── images.py            # Image processing and formatting
├── sheets_api.py        # Google Sheets data retrieval
├── templates/           # Post templates and assets
├── sample_data/         # Placeholder example data
├── output/              # Generated posts
└── README.md

## Key Features

Aspect-ratio-preserving image resizing

Template-based branding system

Automatic validation for required submissions

Modular and extensible architecture

Organized per-student output storage

Error handling for incomplete submissions

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

Python

Pillow (PIL) for image processing

Google Sheets API

Requests
