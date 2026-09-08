# Meter Vision

A Python-based desktop application for reading numerical values from electrical meter images using Optical Character Recognition (OCR).

## Overview

Meter Vision is an OCR-based application developed to assist the process of reading and recording electrical meter values from images. The application combines OpenCV for image processing and PaddleOCR for text recognition.

The system allows users to process multiple meter images, manually select the meter reading area, perform image preprocessing, recognize numerical values, validate OCR results, and manually correct incorrect readings when necessary.

## Features

- Multiple image selection and batch processing
- Manual Region of Interest (ROI) cropping
- Image preprocessing using OpenCV
- Grayscale conversion
- Median filtering for noise reduction
- Image resizing
- Optical Character Recognition using PaddleOCR
- OCR result parsing and validation
- Manual correction of OCR results
- Room and LCD type identification
- Editable text report generation
- Offline desktop application

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language and application logic |
| Tkinter | Graphical User Interface (GUI) |
| OpenCV | Image processing and preprocessing |
| PaddleOCR | Optical Character Recognition |
| PaddlePaddle | OCR framework/backend |
| Pytest | Automated testing |

## System Workflow

```text
Meter Image
    ↓
Manual ROI Cropping
    ↓
Image Preprocessing
    ↓
Grayscale
    ↓
Median Filter
    ↓
Resize
    ↓
PaddleOCR
    ↓
Result Parsing
    ↓
Validation
    ↓
Manual Correction
    ↓
Text Report
Application Flow
Enter the user name.
The application records the current date and time.
Select one or multiple meter images.
Enter the room and LCD type for each image.
Select the meter reading area manually.
The selected area is processed using OpenCV.
PaddleOCR performs text recognition.
The OCR result is parsed and validated.
Incorrect results can be corrected manually.
The application generates a text report.
The report can be edited and copied.
Project Structure
meter-vision/
├── app/
│   ├── config.py
│   ├── cropper.py
│   ├── denoise.py
│   ├── grayscale.py
│   ├── image_loader.py
│   ├── image_processor.py
│   ├── models.py
│   ├── ocr_engine.py
│   ├── parser.py
│   ├── preprocessing.py
│   ├── resize.py
│   └── report/
│       └── text_report.py
├── scripts/
├── tests/
├── output/
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
Installation
Clone the repository
git clone https://github.com/marsmafhikrypradipaa/meter-vision.git
cd meter-vision
Create virtual environment
python3 -m venv .venv
Activate virtual environment
source .venv/bin/activate
Install dependencies
pip install -r requirements.txt
Running the Application
python main.py
Testing

Run the automated tests with:

python -m pytest
Image Processing Pipeline

The application processes meter images through several stages:

ROI Cropping — manually selects the area containing the meter reading.
Grayscale Conversion — converts the image to grayscale.
Median Filtering — reduces image noise.
Resizing — adjusts the image size for OCR processing.
OCR Recognition — PaddleOCR recognizes the numerical reading.
Parsing and Validation — processes and checks the OCR result.
Manual Correction — allows the user to correct inaccurate results.
Output

The generated text report contains information such as:

User name
Date and time
Room
LCD type
Image information
OCR reading
Confidence information
Corrected value when required
Development

This project was developed as part of an internship project at PT Telkom Infrastructure. It focuses on applying OCR and image-processing techniques to assist electrical meter-reading activities.

License

This project is currently provided for educational and development purposes.
