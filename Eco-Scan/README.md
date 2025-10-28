# EcoAnalyzer - Smart Waste Classification System

A comprehensive web application that uses AI to classify different types of waste, including medical and hazardous materials, with proper disposal guidance.

## Features

- **Multi-Category Waste Classification**: Organic, Recyclable, General, Medical, Hazardous, E-Waste
- **Medical Waste Detection**: Specialized classification for medical waste types
- **Image Upload & Camera Capture**: Multiple ways to input waste images
- **Real-time Analysis**: Instant classification with confidence scores
- **Disposal Guidance**: Proper disposal instructions for each waste type
- **Safety Warnings**: Special handling instructions for hazardous materials
- **Analysis History**: Track previous classifications
- **Responsive Design**: Works on desktop and mobile devices

## Waste Categories

1. **Biodegradable**: Food waste, garden waste
2. **Recyclable**: Plastic, paper, glass, metal
3. **General Waste**: Non-recyclable materials
4. **Medical Waste**: 
   - Sharps (needles, syringes)
   - Infectious waste
   - Pharmaceutical waste
5. **Hazardous Waste**: Chemicals, batteries
6. **E-Waste**: Electronics, batteries

## Installation

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python database/init_db.py
python app.py