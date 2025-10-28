class WasteAnalyzer {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000/api';
        this.initializeEventListeners();
        this.loadHistory();
    }

    initializeEventListeners() {
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        const cameraBtn = document.getElementById('cameraBtn');
        const captureBtn = document.getElementById('captureBtn');
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');

        // File upload handling
        fileInput.addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files[0]);
        });

        // Drag and drop functionality
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#764ba2';
            uploadArea.style.background = '#f0f4ff';
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.borderColor = '#667eea';
            uploadArea.style.background = '';
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#667eea';
            uploadArea.style.background = '';
            
            if (e.dataTransfer.files.length) {
                this.handleFileUpload(e.dataTransfer.files[0]);
            }
        });

        // Camera functionality
        cameraBtn.addEventListener('click', () => this.startCamera());
        captureBtn.addEventListener('click', () => this.captureImage());
    }

    async handleFileUpload(file) {
        if (!file) return;

        // Validate file type
        const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
        if (!validTypes.includes(file.type)) {
            alert('Please upload a valid image file (JPEG, PNG, GIF)');
            return;
        }

        // Validate file size (16MB)
        if (file.size > 16 * 1024 * 1024) {
            alert('File size must be less than 16MB');
            return;
        }

        await this.analyzeImage(file);
    }

    async startCamera() {
        try {
            const video = document.getElementById('video');
            const cameraPreview = document.getElementById('cameraPreview');
            
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'environment' } 
            });
            
            video.srcObject = stream;
            cameraPreview.classList.remove('hidden');
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            alert('Unable to access camera. Please check permissions.');
        }
    }

    captureImage() {
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const context = canvas.getContext('2d');

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);

        canvas.toBlob((blob) => {
            const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
            this.analyzeImage(file);
            
            // Stop camera
            video.srcObject.getTracks().forEach(track => track.stop());
            document.getElementById('cameraPreview').classList.add('hidden');
        }, 'image/jpeg');
    }

    async analyzeImage(file) {
        this.showLoading(true);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${this.apiBaseUrl}/analyze`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Analysis failed');
            }

            const result = await response.json();
            this.displayResult(result);
            this.loadHistory(); // Refresh history

        } catch (error) {
            console.error('Error:', error);
            alert('Error analyzing image. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }

    displayResult(result) {
        const resultSection = document.getElementById('resultSection');
        const wasteTypeElement = document.getElementById('wasteType');
        const confidenceElement = document.getElementById('confidence');
        const categoryBadge = document.getElementById('categoryBadge');
        const disposalGuide = document.getElementById('disposalGuide');
        const safetyInfo = document.getElementById('safetyInfo');
        const predictionBars = document.getElementById('predictionBars');

        // Update main result
        wasteTypeElement.textContent = this.formatWasteType(result.waste_type);
        confidenceElement.textContent = `${Math.round(result.confidence * 100)}%`;
        categoryBadge.textContent = result.category;
        disposalGuide.textContent = result.disposal_guide;

        // Update styling based on waste category
        const resultCard = document.querySelector('.result-card');
        resultCard.className = 'result-card';
        if (result.category === 'Medical Waste') {
            resultCard.classList.add('medical-waste');
            safetyInfo.classList.remove('hidden');
        } else if (result.category === 'Hazardous Waste') {
            resultCard.classList.add('hazardous-waste');
            safetyInfo.classList.remove('hidden');
        } else {
            safetyInfo.classList.add('hidden');
        }

        // Update prediction bars
        predictionBars.innerHTML = '';
        if (result.all_predictions) {
            Object.entries(result.all_predictions)
                .sort(([,a], [,b]) => b - a)
                .forEach(([type, confidence]) => {
                    const barElement = this.createPredictionBar(type, confidence);
                    predictionBars.appendChild(barElement);
                });
        }

        resultSection.classList.remove('hidden');
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    createPredictionBar(type, confidence) {
        const barDiv = document.createElement('div');
        barDiv.className = 'prediction-bar';

        const labelDiv = document.createElement('div');
        labelDiv.className = 'bar-label';
        labelDiv.innerHTML = `
            <span>${this.formatWasteType(type)}</span>
            <span>${Math.round(confidence * 100)}%</span>
        `;

        const containerDiv = document.createElement('div');
        containerDiv.className = 'bar-container';

        const fillDiv = document.createElement('div');
        fillDiv.className = 'bar-fill';
        fillDiv.style.width = `${confidence * 100}%`;

        containerDiv.appendChild(fillDiv);
        barDiv.appendChild(labelDiv);
        barDiv.appendChild(containerDiv);

        return barDiv;
    }

    formatWasteType(type) {
        return type.split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    async loadHistory() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/history`);
            const history = await response.json();

            const historyList = document.getElementById('historyList');
            historyList.innerHTML = '';

            history.forEach(item => {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                historyItem.innerHTML = `
                    <div>
                        <div class="history-type">${this.formatWasteType(item.waste_type)}</div>
                        <small>${new Date(item.timestamp).toLocaleString()}</small>
                    </div>
                    <div class="history-confidence">${Math.round(item.confidence * 100)}%</div>
                `;
                historyList.appendChild(historyItem);
            });

        } catch (error) {
            console.error('Error loading history:', error);
        }
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        loading.classList.toggle('hidden', !show);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WasteAnalyzer();
});

// Service Worker for PWA functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}