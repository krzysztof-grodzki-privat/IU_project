# IoT Anomaly Detection System

> Real-time machine failure detection for industrial IoT environments — built as part of **DLBDSMTP01: Project From Model to Production** at IU International University of Applied Sciences.

---

## About This Project

This system monitors factory sensor data in real time and automatically flags potential machine failures before they happen. A Python stream simulator feeds sensor readings row-by-row into a Flask REST API, which runs each reading through a trained **Isolation Forest** model and returns an anomaly score within milliseconds.


##  System Architecture

```
Factory Sensors / Kaggle Dataset
         │
         ▼
  Stream Simulator          ← simulator.py (reads CSV row-by-row)
         │
         ▼  HTTP POST /predict
  Flask REST API            ← app.py (port 5000)
         │
         ├──► Isolation Forest Model   ← model/anomaly_model.pkl
         │           │
         │           └──► Anomaly Score + Status
         │
         ├──► Prediction Log           ← log/predictions_log.csv
         │
         └──► ngrok Public URL         ← https://xxxx.ngrok-free.app
```

---

##  Tech Stack

| Component | Tool |
|---|---|
| Language | Python 3.12 |
| ML Model | scikit-learn — Isolation Forest |
| API Server | Flask |
| Data Handling | pandas |
| Model Persistence | joblib |
| Stream Simulation | Python (CSV iterator) |
| Dataset | AI4I 2020 Predictive Maintenance (Kaggle) |

---

## Project Structure

```
iot_project/
├── data/
│   ├── predictive_maintenance.csv   # Training data (10,000 rows)
│   └── stream_data.csv              # Synthetic stream data (3,000 rows)
├── model/
│   ├── anomaly_model.pkl            # Trained Isolation Forest
│   └── scaler.pkl                   # Fitted StandardScaler
├── log/
│   └── predictions_log.csv          # Live prediction audit trail
├── app.py                           # Flask REST API server
├── simulator.py                     # Stream data simulator
├── notebook.ipynb                   # Model training notebook
└── README.md
```

## How the Model Works

The **Isolation Forest** algorithm detects anomalies without needing labeled failure examples (unsupervised learning). It builds 100 random decision trees and measures how many splits are needed to isolate each data point:

- **Few splits needed → short path → anomaly** (unusual combination of sensor values)
- **Many splits needed → long path → normal** (typical factory reading)

### Features used

| Feature | Unit | What it detects |
|---|---|---|
| Air temperature | Kelvin [K] | Machine overheating / stall |
| Process temperature | Kelvin [K] | Thermal runaway / heat dissipation failure |
| Rotational speed | RPM | Bearing failure, belt breakage |
| Torque | Newton-metre [Nm] | Mechanical overload |
| Tool wear | Minutes | End-of-life component failure |

All features are normalised with **StandardScaler** before prediction so that high-magnitude values (like RPM ~1500) do not dominate over smaller ones (like Torque ~40).

**Anomaly score interpretation:**
- Score `> 0` → Normal reading
- Score `< 0` → Anomaly (the more negative, the more unusual)

---

## Dataset

**AI4I 2020 Predictive Maintenance Dataset**

| Property | Value |
|---|---|
| Source | Kaggle / UCI ML Repository |
| Records | 10,000 |
| Features | 5 sensor columns + failure flags |
| Failure rate | 3.39% (339 records) |

---
## Setup & Installation

**Prerequisites**
```bash
Anaconda (recommended) or Python 3.10+
```
1. Clone the repository
2. Install dependencies
Using Anaconda Prompt:
```bash
pip install flask scikit-learn pandas joblib mlflow
```
3. Train the model
Open `model_training.ipynb` in Jupyter Notebook and run all cells. This will:
Load and preprocess the dataset
Train the Isolation Forest model
Save `model/anomaly_model.pkl` and `model/scaler.pkl`
4. Running the System
Step 1 — Start the Flask API
Open a terminal and run:
```bash
python app.py
```
Expected output:
```
* Running on http://127.0.0.1:5000
```
Step 2 — Run the stream simulator
Open `simulator.ipynb` in Jupyter Notebook and run all cells.
Expected output:
```
 Symulator strumienia IoT uruchomiony...
==================================================
 Wiersz     0 | Normal   | score:  0.0821
 Wiersz   143 | ANOMALIA | score: -0.1102 | RPM: 1463 | Torque: 68.3
 Wiersz   200 | Normal   | score:  0.0721
```
log are saved in log/predictions_log.csv

## Key Findings

- Model trained on 10,000 records flagged **500 anomalies (5.0%)** matching the contamination parameter
- Stream simulation on 3,000 synthetic records shows **~16% anomaly rate** demonstrating **data drift**, a realistic production phenomenon where new data diverges from the training distribution
- API response time: **< 200ms** per prediction on local hardware
