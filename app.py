import os
import zipfile
import tempfile
import shutil
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from werkzeug.utils import secure_filename
import pydicom
from PIL import Image
import numpy as np
import io
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dicom-viewer-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def is_dicom_file(filepath):
    """Check if a file is a DICOM file."""
    try:
        pydicom.dcmread(filepath, stop_before_pixels=True)
        return True
    except:
        return False

def dicom_to_image(dicom_path):
    """Convert DICOM file to PIL Image."""
    try:
        ds = pydicom.dcmread(dicom_path)
        
        # Get pixel array
        if hasattr(ds, 'pixel_array'):
            pixel_array = ds.pixel_array
            
            # Normalize pixel values to 0-255 range
            if pixel_array.dtype != np.uint8:
                # Scale to 0-255
                pixel_min = pixel_array.min()
                pixel_max = pixel_array.max()
                if pixel_max > pixel_min:
                    pixel_array = ((pixel_array - pixel_min) / (pixel_max - pixel_min) * 255).astype(np.uint8)
                else:
                    pixel_array = np.zeros_like(pixel_array, dtype=np.uint8)
            
            # Convert to PIL Image
            if len(pixel_array.shape) == 2:  # Grayscale
                image = Image.fromarray(pixel_array, mode='L')
            elif len(pixel_array.shape) == 3:  # RGB
                image = Image.fromarray(pixel_array, mode='RGB')
            else:
                return None
                
            return image
    except Exception as e:
        print(f"Error converting DICOM to image: {e}")
        return None
    
    return None

def image_to_base64(image):
    """Convert PIL Image to base64 string for web display."""
    if image is None:
        return None
    
    # Create thumbnail for web display
    image.thumbnail((800, 600), Image.Resampling.LANCZOS)
    
    # Convert to base64
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_data = base64.b64encode(img_buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_data}"

def extract_dicom_info(dicom_path):
    """Extract metadata from DICOM file."""
    try:
        ds = pydicom.dcmread(dicom_path)
        info = {
            'patient_name': str(getattr(ds, 'PatientName', 'Unknown')),
            'patient_id': str(getattr(ds, 'PatientID', 'Unknown')),
            'study_date': str(getattr(ds, 'StudyDate', 'Unknown')),
            'modality': str(getattr(ds, 'Modality', 'Unknown')),
            'series_description': str(getattr(ds, 'SeriesDescription', 'Unknown')),
            'institution_name': str(getattr(ds, 'InstitutionName', 'Unknown')),
        }
        
        if hasattr(ds, 'pixel_array'):
            info['image_size'] = f"{ds.pixel_array.shape[1]}x{ds.pixel_array.shape[0]}"
        
        return info
    except Exception as e:
        print(f"Error extracting DICOM info: {e}")
        return {}

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file upload."""
    if 'files' not in request.files:
        flash('No files selected')
        return redirect(url_for('index'))
    
    files = request.files.getlist('files')
    
    if not files or all(f.filename == '' for f in files):
        flash('No files selected')
        return redirect(url_for('index'))
    
    # Create a temporary directory for this upload session
    session_dir = tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER'])
    
    dicom_files = []
    
    for file in files:
        if file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(session_dir, filename)
            file.save(filepath)
            
            # Check if it's a DICOM file
            if is_dicom_file(filepath):
                dicom_files.append(filepath)
            else:
                # If it's a zip file, try to extract it
                if filename.lower().endswith('.zip'):
                    try:
                        with zipfile.ZipFile(filepath, 'r') as zip_ref:
                            zip_ref.extractall(session_dir)
                        
                        # Search for DICOM files in extracted content
                        for root, dirs, files in os.walk(session_dir):
                            for fname in files:
                                fpath = os.path.join(root, fname)
                                if is_dicom_file(fpath):
                                    dicom_files.append(fpath)
                    except Exception as e:
                        print(f"Error extracting zip file: {e}")
    
    if not dicom_files:
        flash('No DICOM files found in uploaded files')
        shutil.rmtree(session_dir)
        return redirect(url_for('index'))
    
    session_id = os.path.basename(session_dir)
    return redirect(url_for('gallery', session_id=session_id))

@app.route('/gallery/<session_id>')
def gallery(session_id):
    """Display DICOM images in a gallery."""
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    
    if not os.path.exists(session_dir):
        flash('Session not found')
        return redirect(url_for('index'))
    
    # Find all DICOM files in the session directory
    dicom_files = []
    for root, dirs, files in os.walk(session_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            if is_dicom_file(fpath):
                dicom_files.append(fpath)
    
    # Process DICOM files for display
    images_data = []
    for dicom_path in dicom_files:
        # Convert DICOM to image
        image = dicom_to_image(dicom_path)
        if image:
            # Convert to base64 for web display
            image_b64 = image_to_base64(image)
            
            # Extract metadata
            info = extract_dicom_info(dicom_path)
            
            images_data.append({
                'filename': os.path.basename(dicom_path),
                'image_data': image_b64,
                'info': info
            })
    
    return render_template('gallery.html', images=images_data, session_id=session_id)

@app.route('/cleanup/<session_id>', methods=['POST'])
def cleanup_session(session_id):
    """Clean up uploaded files for a session."""
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    
    if os.path.exists(session_dir):
        shutil.rmtree(session_dir)
        flash('Files cleaned up successfully')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)