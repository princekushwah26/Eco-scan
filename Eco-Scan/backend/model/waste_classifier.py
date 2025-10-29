import numpy as np
import tensorflow as tf
from PIL import Image
import json
import os # Import os for file path handling

class WasteClassifier:
    def __init__(self):
        # ... (other initializations remain the same)
        self.classes = [
            'organic', 'recyclable_plastic', 'recyclable_paper', 
            'recyclable_glass', 'recyclable_metal', 'general_waste',
            'medical_sharps', 'medical_infectious', 'medical_pharmaceutical',
            'hazardous_chemical', 'e_waste'
        ]
        
        self.categories = {
            'organic': 'Biodegradable',
            'recyclable_plastic': 'Recyclable',
            'recyclable_paper': 'Recyclable',
            'recyclable_glass': 'Recyclable',
            'recyclable_metal': 'Recyclable',
            'general_waste': 'General Waste',
            'medical_sharps': 'Medical Waste',
            'medical_infectious': 'Medical Waste',
            'medical_pharmaceutical': 'Medical Waste',
            'hazardous_chemical': 'Hazardous Waste',
            'e_waste': 'E-Waste'
        }
        
        self.disposal_guides = {
            'organic': 'Compost in organic bin. Do not mix with other waste types.',
            'recyclable_plastic': 'Clean and dry before recycling. Check local recycling guidelines.',
            'recyclable_paper': 'Keep dry and place in paper recycling bin.',
            'recyclable_glass': 'Rinse and separate by color if required.',
            'recyclable_metal': 'Clean and place in metal recycling bin.',
            'general_waste': 'Place in general waste bin. Consider if item can be recycled.',
            'medical_sharps': 'Use designated sharps container. Do not dispose in regular trash.',
            'medical_infectious': 'Follow biohazard protocols. Use red biohazard bags.',
            'medical_pharmaceutical': 'Return to pharmacy or use drug take-back programs.',
            'hazardous_chemical': 'Take to hazardous waste facility. Do not pour down drain.',
            'e_waste': 'Take to e-waste recycling center. Contains valuable materials.'
        }
        
        self.model = None # Initialize model attribute

    def load_model(self, model_path="model/waste_classifier_model.h5"):
        """Loads the pre-trained TensorFlow/Keras model."""
        try:
            # Check if model file exists before attempting to load
            if not os.path.exists(model_path):
                print(f"⚠️ Warning: Model file not found at {model_path}. Running with mock prediction.")
                self.model = None
                return
            
            # Load the actual Keras model
            self.model = tf.keras.models.load_model(model_path)
            print(f"✅ Model loaded successfully from {model_path}")
            
            # Ensure the model's output shape matches the number of classes
            if self.model.output_shape[-1] != len(self.classes):
                print(f"❗ Warning: Model output size ({self.model.output_shape[-1]}) does not match number of classes ({len(self.classes)}).")

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            # More specific warning if file not found
            print(f"⚠️ Warning: Model file not found at {model_path}. Running with mock prediction.")
            self.model = None

    def preprocess_image(self, image_array, target_size=(224, 224)):
        """Preprocesses the image array for model prediction."""
        # Convert NumPy array back to PIL Image (if passed as array from the API)
        image = Image.fromarray(image_array.astype('uint8'), 'RGB')
        
        # Resize image to target size (must match model's expected input)
        image = image.resize(target_size)
        
        # Convert back to NumPy array and normalize
        image_array = np.array(image).astype('float32') / 255.0
        
        # Add a batch dimension: (height, width, channels) -> (1, height, width, channels)
        return np.expand_dims(image_array, axis=0)

    def predict(self, image_array):
        """Makes a prediction using the actual model or falls back to mock."""
        if self.model is None:
            # Fallback to mock prediction if model failed to load
            return self._mock_predict()
        
        # 1. Preprocess the image
        processed_image = self.preprocess_image(image_array)
        
        # 2. Make prediction
        predictions = self.model.predict(processed_image, verbose=0)[0]
        
        # 3. Interpret results
        predicted_idx = np.argmax(predictions)
        confidence = predictions[predicted_idx]
        
        waste_type = self.classes[predicted_idx]
        category = self.categories.get(waste_type, 'Unknown')
        disposal_guide = self.disposal_guides.get(waste_type, 'Consult local guidelines.')
        
        return {
            'waste_type': waste_type,
            'category': category,
            'confidence': round(float(confidence), 4),
            'disposal_guide': disposal_guide,
            'all_predictions': {
                cls: round(float(conf), 4) 
                for cls, conf in zip(self.classes, predictions)
            }
        }

    def _mock_predict(self):
        # Original mock prediction logic (kept for fallback)
        mock_prediction = np.random.dirichlet(np.ones(len(self.classes)), size=1)[0]
        predicted_idx = np.argmax(mock_prediction)
        
        waste_type = self.classes[predicted_idx]
        category = self.categories.get(waste_type, 'Unknown')
        disposal_guide = self.disposal_guides.get(waste_type, 'Consult local guidelines.')
        
        confidence = max(mock_prediction[predicted_idx], 0.7) + np.random.random() * 0.2
        
        return {
            'waste_type': waste_type,
            'category': category,
            'confidence': round(float(confidence), 2),
            'disposal_guide': disposal_guide,
            'all_predictions': {
                cls: round(float(conf), 3) 
                for cls, conf in zip(self.classes, mock_prediction)
            }
        }

if __name__ == "__main__":
    print("--- Starting WasteClassifier script execution ---")
    print(f"TensorFlow version: {tf.__version__}")
    print(f"NumPy version: {np.__version__}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Determine the absolute path to the model file
    # The default path in load_model is "model/waste_classifier_model.h5"
    # This path is relative to the current working directory when the script is run.
    # If you run this script from the 'backend' directory, it expects the model in 'backend/model/waste_classifier_model.h5'.
    # If you run it from the project root, it expects 'Eco-Scan/model/waste_classifier_model.h5'.
    # Adjust the path below if your model file is located elsewhere.
    # For example, if waste_classifier_model.h5 is in the same directory as waste_classifier.py:
    # model_path_for_test = os.path.join(os.path.dirname(os.path.abspath(__file__)), "waste_classifier_model.h5")
    
    print("Attempting to initialize WasteClassifier...")
    classifier = WasteClassifier()
    print("WasteClassifier initialized. Attempting to load model...")
    classifier.load_model() # Uses the default path "model/waste_classifier_model.h5"
    print("Model loading attempt completed (may have used mock if file not found).")
    print("--- WasteClassifier script execution finished ---")