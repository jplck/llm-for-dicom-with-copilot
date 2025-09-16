# DICOM Image Viewer

A Python web application with a modern UI for uploading and viewing DICOM medical image files in an image gallery format.

## Features

- **Web-based DICOM Viewer**: Upload and view DICOM files through a modern web interface
- **Folder Upload Support**: Upload entire folders containing DICOM files
- **ZIP File Support**: Extract and process DICOM files from ZIP archives
- **Image Gallery**: View all DICOM images in a responsive gallery layout
- **DICOM Metadata Display**: View detailed DICOM metadata for each image
- **Responsive Design**: Works on desktop and mobile devices
- **Dev Container Ready**: Complete development environment setup

## Quick Start

### Using Dev Containers (Recommended)

1. Clone this repository
2. Open in VS Code
3. When prompted, click "Reopen in Container" or use the Command Palette: `Dev Containers: Reopen in Container`
4. Once the container is built, run the application:
   ```bash
   python app.py
   ```
5. Open your browser to `http://localhost:5000`

### Manual Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd llm-for-dicom-with-copilot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser to `http://localhost:5000`

## Usage

1. **Upload DICOM Files**: 
   - Click "Select Files" to choose individual DICOM files (.dcm, .dicom)
   - Click "Select Folder" to upload an entire folder containing DICOM files
   - Or drag and drop files/folders directly onto the upload area

2. **View Images**: 
   - After upload, you'll be redirected to the image gallery
   - Click on any image to view it in full size with metadata details
   - Use the navigation buttons to return to upload or clean up files

3. **Supported Formats**:
   - DICOM files (.dcm, .dicom)
   - ZIP archives containing DICOM files

## Technology Stack

- **Backend**: Flask (Python web framework)
- **DICOM Processing**: pydicom library
- **Image Processing**: Pillow (PIL)
- **Frontend**: Bootstrap 5, JavaScript
- **Development**: Dev Containers with VS Code integration

## File Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── index.html        # Upload page
│   └── gallery.html      # Image gallery page
├── .devcontainer/        # Dev container configuration
│   ├── devcontainer.json # VS Code dev container settings
│   └── Dockerfile        # Docker environment setup
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Development

The application includes a complete dev container setup for consistent development environments:

- **Python 3.11** runtime
- **Pre-installed dependencies** from requirements.txt
- **VS Code extensions** for Python development
- **Port forwarding** for the Flask development server
- **Non-root user** setup for security

## Security Notes

- Files are uploaded to temporary directories and can be cleaned up after viewing
- The application includes basic file type validation
- Consider adding authentication for production use
- File size limits are configured (100MB max)

## License

MIT License - see LICENSE file for details