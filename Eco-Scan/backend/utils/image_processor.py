from PIL import Image
import numpy as np

class ImageProcessor:
    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size

    def preprocess_image(self, image_path):
        """Preprocess image for model prediction"""
        try:
            # Open and convert image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image
            image = image.resize(self.target_size)
            
            # Convert to numpy array and normalize
            image_array = np.array(image) / 255.0
            
            # Add batch dimension
            image_array = np.expand_dims(image_array, axis=0)
            
            return image_array
            
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

    def validate_image(self, image_path):
        """Validate image before processing"""
        try:
            with Image.open(image_path) as img:
                # Check image size
                if img.size[0] < 50 or img.size[1] < 50:
                    return False, "Image too small"
                
                # Check file size (rough estimate)
                file_size = len(open(image_path, 'rb').read())
                if file_size > 16 * 1024 * 1024:  # 16MB
                    return False, "Image too large"
                
                return True, "Valid"
                
        except Exception as e:
            return False, str(e)