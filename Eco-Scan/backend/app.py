from flask import Flask, request
from flask_cors import CORS
import os, io, base64
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import numpy as np
from datetime import datetime
from keras.applications.mobilenet_v2 import MobileNetV2, decode_predictions, preprocess_input
from keras.preprocessing import image

app = Flask(__name__)
CORS(app)

# Load AI Model
model = MobileNetV2(weights="imagenet")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Temporary in-memory storage
waste_entries = []

# --- Helper: classify image ---
def classify_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    preds = model.predict(img_array)
    decoded = decode_predictions(preds, top=1)[0][0]
    label = decoded[1].lower()
    confidence = float(decoded[2])

    # Waste classification logic
    if any(x in label for x in ["plastic", "bottle", "can", "box", "paper", "carton", "metal"]):
        waste_type = "Recyclable"
        disposal = "Recycle"
        recyclability = 0.9
    elif any(x in label for x in ["banana", "apple", "vegetable", "fruit", "food", "plant"]):
        waste_type = "Organic"
        disposal = "Compost"
        recyclability = 0.8
    elif any(x in label for x in ["battery", "computer", "keyboard", "phone"]):
        waste_type = "E-waste"
        disposal = "E-waste Recycling Facility"
        recyclability = 0.6
    else:
        waste_type = "Non-Recyclable"
        disposal = "Landfill"
        recyclability = 0.2

    return {
        "label": label.title(),
        "waste_type": waste_type,
        "disposal": disposal,
        "confidence": round(confidence * 100, 2),
        "recyclability": int(recyclability * 100),
        "image_path": img_path
    }


@app.route("/", methods=["GET"])
def dashboard():
    # Main dashboard + form UI
    html = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Eco-Scan Waste Analyzer</title>
        <style>
            body {{
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(135deg, #d4fc79, #96e6a1);
                margin: 0;
                padding: 0;
            }}
            header {{
                background-color: #2e7d32;
                color: white;
                text-align: center;
                padding: 20px;
                font-size: 26px;
                font-weight: 600;
            }}
            main {{
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 30px;
            }}
            form {{
                background: white;
                padding: 30px;
                border-radius: 16px;
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
                width: 90%;
                max-width: 800px;
                margin-bottom: 40px;
            }}
            label {{
                display: block;
                font-weight: 600;
                margin-top: 15px;
            }}
            input, select, textarea {{
                width: 100%;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #aaa;
                margin-top: 5px;
            }}
            button {{
                margin-top: 20px;
                background: #43a047;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
            }}
            button:hover {{ background: #2e7d32; }}
            table {{
                border-collapse: collapse;
                width: 90%;
                margin: 0 auto;
                background: white;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background: #43a047;
                color: white;
            }}
            footer {{
                text-align: center;
                background: #2e7d32;
                color: white;
                padding: 10px;
                font-size: 14px;
                margin-top: 40px;
            }}
        </style>
    </head>
    <body>
        <header>♻️ Eco-Scan Smart Waste Analyzer</header>
        <main>
            <form id="wasteForm" enctype="multipart/form-data">
                <h3>Waste Data Entry</h3>
                <label>Waste Type</label><input type="text" name="waste_type" required>
                <label>Subcategory</label><input type="text" name="subcategory">
                <label>Quantity/Weight (kg)</label><input type="number" step="0.01" name="quantity">
                <label>Source/Location</label><input type="text" name="source">
                <label>Collection Date & Time</label><input type="datetime-local" name="datetime">
                <label>Disposal Method</label><input type="text" name="disposal">
                <label>Segregation Status</label>
                <select name="seg_status">
                    <option>Segregated</option>
                    <option>Mixed</option>
                    <option>Unknown</option>
                </select>
                <label>Hazardous/Non-Hazardous</label>
                <select name="hazard_status">
                    <option>Non-Hazardous</option>
                    <option>Hazardous</option>
                </select>
                <label>Bin ID / RFID</label><input type="text" name="bin_id">
                <label>User / Operator ID</label><input type="text" name="user_id">
                <label>Volume (liters)</label><input type="number" step="0.01" name="volume">
                <label>Upload Image (for AI analysis)</label><input type="file" name="file" accept="image/*" required>
                <button type="button" onclick="submitForm()">Analyze & Save</button>
            </form>

            <h3>Waste Entries</h3>
            <table>
                <tr>
                    <th>Type</th><th>Subcategory</th><th>Weight (kg)</th><th>Source</th>
                    <th>Datetime</th><th>Disposal</th><th>Segregation</th><th>Hazard</th>
                    <th>Bin ID</th><th>User ID</th><th>Volume</th><th>AI Label</th>
                    <th>Confidence</th><th>Recyclability</th><th>Carbon Footprint</th>
                </tr>
                {"".join([
                    f"<tr><td>{w['waste_type']}</td><td>{w['subcategory']}</td><td>{w['quantity']}</td>"
                    f"<td>{w['source']}</td><td>{w['datetime']}</td><td>{w['disposal']}</td>"
                    f"<td>{w['seg_status']}</td><td>{w['hazard_status']}</td>"
                    f"<td>{w['bin_id']}</td><td>{w['user_id']}</td><td>{w['volume']}</td>"
                    f"<td>{w['label']}</td><td>{w['confidence']}%</td><td>{w['recyclability']}%</td>"
                    f"<td>{w['carbon']} kg CO₂e</td></tr>"
                    for w in waste_entries
                ])}
            </table>
        </main>
        <footer>© 2025 Eco-Scan | AI Waste Analyzer System</footer>

        <script>
            async function submitForm() {{
                const form = document.getElementById('wasteForm');
                const formData = new FormData(form);

                const res = await fetch('/submit', {{
                    method: 'POST',
                    body: formData
                }});
                const result = await res.text();
                location.reload();
            }}
        </script>
    </body>
    </html>
    """
    return html


@app.route("/submit", methods=["POST"])
def submit():
    """Handle form + image upload."""
    file = request.files["file"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    ai_result = classify_image(path)
    os.remove(path)

    data = {
        "waste_type": request.form.get("waste_type"),
        "subcategory": request.form.get("subcategory"),
        "quantity": request.form.get("quantity"),
        "source": request.form.get("source"),
        "datetime": request.form.get("datetime"),
        "disposal": ai_result["disposal"],
        "seg_status": request.form.get("seg_status"),
        "hazard_status": request.form.get("hazard_status"),
        "bin_id": request.form.get("bin_id"),
        "user_id": request.form.get("user_id"),
        "volume": request.form.get("volume"),
        "label": ai_result["label"],
        "confidence": ai_result["confidence"],
        "recyclability": ai_result["recyclability"],
        "carbon": round(float(request.form.get("quantity") or 0) * 1.2, 2)  # estimated CO₂e
    }

    waste_entries.append(data)
    return "Success"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
