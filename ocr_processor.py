"""
OCR Processing Module
Handles image text extraction using pytesseract
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import logging

logger = logging.getLogger(__name__)

class OCRProcessor:
    """Handles OCR processing of trading signal images"""
    
    def __init__(self):
        # Configure pytesseract
        self.tesseract_config = '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz./$:%-'
    
    def preprocess_image(self, image_path: str) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy
        """
        try:
            # Open image
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Convert to grayscale for better OCR
            image = image.convert('L')
            
            # Apply threshold to create binary image
            image = image.point(lambda x: 0 if x < 140 else 255, '1')
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return Image.open(image_path)
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image using OCR
        """
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            
            # Extract text using pytesseract
            extracted_text = pytesseract.image_to_string(
                processed_image, 
                config=self.tesseract_config
            )
            
            # Clean extracted text
            cleaned_text = self._clean_extracted_text(extracted_text)
            
            logger.info(f"Extracted text: {cleaned_text}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        """
        if not text:
            return ""
        
        # Remove extra whitespaces and normalize
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                lines.append(line)
        
        # Join lines with single newline
        cleaned_text = '\n'.join(lines)
        
        # Replace common OCR errors
        replacements = {
            '0': 'O',  # Sometimes O is read as 0
            'l': 'I',  # Sometimes I is read as l
            '|': 'I',  # Sometimes I is read as |
        }
        
        # Apply replacements selectively (only for known patterns)
        # This is conservative to avoid breaking actual numbers
        
        return cleaned_text
    
    def extract_text_with_confidence(self, image_path: str) -> tuple:
        """
        Extract text with confidence scores
        """
        try:
            processed_image = self.preprocess_image(image_path)
            
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(
                processed_image, 
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Filter high confidence text
            high_confidence_text = []
            for i, conf in enumerate(ocr_data['conf']):
                if int(conf) > 50:  # Only include text with >50% confidence
                    text = ocr_data['text'][i].strip()
                    if text:
                        high_confidence_text.append(text)
            
            return ' '.join(high_confidence_text), ocr_data
            
        except Exception as e:
            logger.error(f"Error extracting text with confidence: {e}")
            return "", {}
