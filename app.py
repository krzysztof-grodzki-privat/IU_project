from flask import Flask, request, jsonify
import joblib
import csv
import os
from datetime import datetime

# Loading model and Scaler
model = joblib.load('model/anomaly_model.pkl')
scaler = joblib.load('model/scaler.pkl')

app = Flask(__name__)

# Log configuration
LOG_FILE = 'log/predictions_log.csv'
os.makedirs('log', exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        csv.writer(f).writerow(['timestamp','air_temp','process_temp','rpm','torque','tool_wear','anomaly','score','status'])
    print("Plik logow utworzony")

#API
@app.route('/predict', methods=['POST'])
def predict():
   #Endpoint to receive sensor data and return anomaly detection results.
    data = request.get_json()
    features = [[data['air_temp'], data['process_temp'], data['rpm'], data['torque'], data['tool_wear']]]
    scaled = scaler.transform(features)
    prediction = model.predict(scaled)[0]
    score = model.decision_function(scaled)[0]
    result = {
        'anomaly': bool(prediction == -1),
        'score': round(float(score), 4),
        'status': 'ANOMALY DETECTED' if prediction == -1 else 'Normal'
    }
    # Log the prediction details to the CSV file
    with open(LOG_FILE, 'a', newline='') as f:
        csv.writer(f).writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data['air_temp'], data['process_temp'], data['rpm'], data['torque'], data['tool_wear'], result['anomaly'], result['score'], result['status']])
    return jsonify(result)

#Check to verify if the API is online.    
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'API is running'})
    
#Endpoint to retrieve summary statistics
@app.route('/logs', methods=['GET'])
def logs():
    if not os.path.exists(LOG_FILE):
        return jsonify({'error': 'Brak logow'})
    with open(LOG_FILE, 'r') as f:
        rows = list(csv.DictReader(f))
    total = len(rows)
    anomalies = sum(1 for r in rows if r['anomaly'] == 'True')
    return jsonify({
        'total_predictions': total,
        'total_anomalies': anomalies,
        'anomaly_rate': f"{round(anomalies/total*100,1)}%" if total > 0 else "0%",
        'last_10': rows[-10:]
    })

#Main
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5000)