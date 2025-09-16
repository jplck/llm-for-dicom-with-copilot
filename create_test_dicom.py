#!/usr/bin/env python3
"""
Create test DICOM files for testing the stacked viewer functionality.
"""
import os
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import generate_uid
import tempfile

def create_test_dicom_series(output_dir, num_slices=5):
    """Create a series of test DICOM files."""
    
    # Generate UIDs for the series
    study_uid = generate_uid()
    series_uid = generate_uid()
    
    for i in range(num_slices):
        # Create a simple test image (gradient with circle)
        img_size = 256
        x, y = np.meshgrid(np.linspace(-1, 1, img_size), np.linspace(-1, 1, img_size))
        
        # Create a gradient background
        gradient = ((x + y) * 127 + 128).astype(np.uint8)
        
        # Add a circle that moves through slices
        center_z = (i / (num_slices - 1)) * 2 - 1  # -1 to 1
        circle = ((x**2 + (y - center_z*0.5)**2) < 0.3).astype(np.uint8) * 100
        
        pixel_array = gradient + circle
        pixel_array = np.clip(pixel_array, 0, 255).astype(np.uint8)
        
        # Create DICOM dataset
        ds = Dataset()
        
        # Patient information
        ds.PatientName = "Test^Patient"
        ds.PatientID = "12345"
        ds.PatientBirthDate = "19800101"
        ds.PatientSex = "M"
        
        # Study information
        ds.StudyDate = "20240101"
        ds.StudyTime = "120000"
        ds.StudyInstanceUID = study_uid
        ds.StudyDescription = "Test Study"
        
        # Series information
        ds.SeriesDate = "20240101"
        ds.SeriesTime = "120000"
        ds.SeriesInstanceUID = series_uid
        ds.SeriesNumber = 1
        ds.SeriesDescription = "Test Series - Axial"
        ds.Modality = "CT"
        
        # Image information
        ds.InstanceNumber = i + 1
        ds.SOPInstanceUID = generate_uid()
        ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2"  # CT Image Storage
        
        # Image position and orientation
        ds.ImagePositionPatient = [0.0, 0.0, float(i * 5)]  # 5mm slice spacing
        ds.ImageOrientationPatient = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        ds.SliceLocation = float(i * 5)
        ds.SliceThickness = 5.0
        
        # Institution information
        ds.InstitutionName = "Test Hospital"
        
        # Image properties
        ds.Rows = img_size
        ds.Columns = img_size
        ds.PixelSpacing = [1.0, 1.0]
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        
        # Pixel data
        ds.PixelData = pixel_array.tobytes()
        
        # File meta information
        file_meta = FileMetaDataset()
        file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
        file_meta.MediaStorageSOPClassUID = ds.SOPClassUID
        file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
        file_meta.ImplementationClassUID = generate_uid()
        file_meta.FileMetaInformationVersion = b'\x00\x01'
        
        ds.file_meta = file_meta
        ds.is_little_endian = True
        ds.is_implicit_VR = False
        
        # Save the file with proper DICOM format
        filename = f"slice_{i+1:03d}.dcm"
        filepath = os.path.join(output_dir, filename)
        
        # Use write_like_original=False to ensure proper DICOM format
        ds.save_as(filepath, write_like_original=False)
        print(f"Created: {filepath}")

if __name__ == "__main__":
    # Create test directory
    test_dir = os.path.join(os.getcwd(), "test_dicom_series")
    os.makedirs(test_dir, exist_ok=True)
    
    print(f"Creating test DICOM series in: {test_dir}")
    create_test_dicom_series(test_dir, num_slices=10)
    print(f"Test DICOM series created successfully!")
    print(f"You can upload the '{test_dir}' folder to test the stacked viewer.")