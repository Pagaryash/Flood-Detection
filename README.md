###Flood Detection System
A deep learning-based flood detection system using satellite imagery with automated SMS/WhatsApp alert generation and a scalable pipeline design.

Overview
This project leverages deep learning and satellite imagery to automatically detect flood events in real time. When a flood is detected, the system triggers automated alerts via SMS and WhatsApp, making it suitable for early warning systems and disaster management applications.

Features
Satellite Imagery Analysis — Uses Sentinel Hub imagery and geospatial processing to identify flooded regions
Deep Learning Model — Built with TensorFlow/Keras for accurate flood segmentation and classification
SMS Alerts — Automated SMS notifications via sms_alert.py
WhatsApp Alerts — WhatsApp bot integration for real-time messaging via whatsapp_alert.py and whatsapp_bot.py
Automated Pipeline — End-to-end pipeline execution via run_pipeline.py
Web Interface — Flask-based web app (app.py) for visualization and control
Jupyter Notebooks — Exploratory data analysis and model training notebooks in /notebooks
Project Structure
Flood-Detection/
│
├── notebooks/                # Jupyter notebooks for EDA & model training
├── app.py                    # Flask web application
├── alert_manager.py          # Central alert management logic
├── sms_alert.py              # SMS alert integration (Twilio or similar)
├── whatsapp_alert.py         # WhatsApp alert via API
├── whatsapp_bot.py           # WhatsApp bot handler
├── run_pipeline.py           # End-to-end pipeline runner
├── requirements.txt          # Python dependencies
└── .gitignore

Tech Stack
Category	Tools / Libraries
Deep Learning	TensorFlow 2.15, Keras, scikit-learn
Satellite Data	Sentinel Hub, Rasterio, Pyproj, Shapely
Image Processing	OpenCV, Pillow, Albumentations
Web Framework	Flask
Notifications	SMS & WhatsApp APIs
Data & Visualization	NumPy, Pandas, Matplotlib, Seaborn
Notebooks	JupyterLab

Installation
1. Clone the repository
bash
git clone https://github.com/Pagaryash/Flood-Detection.git
cd Flood-Detection
2. Create a virtual environment (recommended)
bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
3. Install dependencies
bash
pip install -r requirements.txt

Usage
Run the full pipeline
bash
python run_pipeline.py
Launch the Flask web app
bash
python app.py
Then open your browser at http://localhost:5000

Explore notebooks
bash
jupyter lab
Navigate to the notebooks/ folder to explore data analysis and model training steps.

Model Overview
The system uses a convolutional neural network (CNN) trained on labeled satellite imagery to perform binary flood/no-flood classification or pixel-level flood segmentation. Key steps include:

Data Acquisition — Satellite images fetched via Sentinel Hub API
Preprocessing — Normalization, augmentation (via Albumentations), and geospatial alignment
Model Training — TensorFlow/Keras model trained on flood-labeled datasets
Inference — Real-time prediction on incoming satellite tiles
Alert Dispatch — If flood probability exceeds threshold, alerts are sent via SMS/WhatsApp

Alert System
Channel	File	Description
SMS	sms_alert.py	Sends SMS to configured phone numbers
WhatsApp	whatsapp_alert.py	Sends WhatsApp messages via API
WhatsApp Bot	whatsapp_bot.py	Interactive WhatsApp bot for status queries
Manager	alert_manager.py	Orchestrates and routes all alerts

License
This project is open-source. Feel free to use, modify, and distribute with attribution.


If you find this project useful, please consider giving it a star!

