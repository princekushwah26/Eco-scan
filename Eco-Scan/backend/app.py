from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from model.waste_classifier import WasteClassifier
from utils.image_processor import ImageProcessor
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize components
classifier = WasteClassifier()
image_processor = ImageProcessor()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_database():
    conn = sqlite3.connect('waste_analysis.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            waste_type TEXT,
            category TEXT,
            confidence REAL,
            disposal_guide TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/analyze', methods=['POST'])
def analyze_waste():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process image and classify
            processed_image = image_processor.preprocess_image(filepath)
            result = classifier.predict(processed_image)
            
            # Save to database
            save_analysis_result(filename, result)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify(result)
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def save_analysis_result(filename, result):
    conn = sqlite3.connect('waste_analysis.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO analyses (filename, waste_type, category, confidence, disposal_guide)
        VALUES (?, ?, ?, ?, ?)
    ''', (filename, result['waste_type'], result['category'], 
          result['confidence'], result['disposal_guide']))
    conn.commit()
    conn.close()

@app.route('/api/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('waste_analysis.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM analyses ORDER BY timestamp DESC LIMIT 10
    ''')
    history = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': row[0],
        'filename': row[1],
        'waste_type': row[2],
        'category': row[3],
        'confidence': row[4],
        'disposal_guide': row[5],
        'timestamp': row[6]
    } for row in history])

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Create upload directory
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Initialize database
    init_database()
    
    app.run(debug=True, host='0.0.0.0', port=5000)