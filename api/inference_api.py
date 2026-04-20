"""
Water Quality Prediction API
Real-time inference service for water potability prediction
"""

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class WaterQualityPredictor:
    def __init__(self):
        self.model = None
        self.model_version = None
        self.load_model()
    
    def load_model(self):
        """Load the latest model from MLflow Model Registry"""
        try:
            # Set MLflow registry URI
            mlflow.set_registry_uri("databricks-uc")
            
            # Model name from Unity Catalog
            model_name = "dev_digital_engineering_services.default.water_quality_model"
            
            # Get latest model version
            client = mlflow.tracking.MlflowClient()
            latest_version = client.get_latest_versions(model_name, stages=["None"])[0]
            
            # Load model
            model_uri = f"models:/{model_name}/{latest_version.version}"
            self.model = mlflow.sklearn.load_model(model_uri)
            self.model_version = latest_version.version
            
            logger.info(f"Loaded model version {self.model_version}")
            
        except Exception as e:
            logger.error(f" Failed to load model: {str(e)}")
            raise
    
    def engineer_features(self, data):
        """Apply feature engineering to input data"""
        # Create derived features
        data['ph_normalized'] = data['ph'] / 14
        data['hardness_ratio'] = data['Hardness'] / (data['Solids'] + 1)
        data['organic_load'] = data['Organic_carbon'] * data['Chloramines']
        data['id'] = 0  # Required by model
        
        return data
    
    def predict(self, water_data):
        """Make prediction for water quality"""
        try:
            # Convert to DataFrame
            if isinstance(water_data, dict):
                df = pd.DataFrame([water_data])
            else:
                df = pd.DataFrame(water_data)
            
            # Feature engineering
            df = self.engineer_features(df)
            
            # Prepare features (remove ID for prediction)
            features = df.drop('id', axis=1)
            
            # Make prediction
            prediction = self.model.predict(features)
            probabilities = self.model.predict_proba(features)
            
            # Format results
            results = []
            for i in range(len(prediction)):
                result = {
                    'potability': int(prediction[i]),
                    'potability_label': 'Potable (Safe)' if prediction[i] == 1 else 'Not Potable (Unsafe)',
                    'confidence': float(np.max(probabilities[i])),
                    'probabilities': {
                        'not_potable': float(probabilities[i][0]),
                        'potable': float(probabilities[i][1])
                    },
                    'model_version': self.model_version,
                    'prediction_timestamp': datetime.now().isoformat()
                }
                results.append(result)
            
            return results[0] if len(results) == 1 else results
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {str(e)}")
            raise

# Initialize predictor
predictor = WaterQualityPredictor()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_version': predictor.model_version,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict_single():
    """Single prediction endpoint"""
    try:
        # Validate input
        data = request.get_json()
        
        required_features = [
            'ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
            'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity'
        ]
        
        # Check for missing features
        missing_features = [f for f in required_features if f not in data]
        if missing_features:
            return jsonify({
                'error': f'Missing required features: {missing_features}'
            }), 400
        
        # Make prediction
        result = predictor.predict(data)
        
        return jsonify({
            'success': True,
            'prediction': result
        })
        
    except Exception as e:
        logger.error(f"❌ Prediction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Batch prediction endpoint"""
    try:
        # Validate input
        data = request.get_json()
        
        if 'samples' not in data:
            return jsonify({'error': 'Missing samples array'}), 400
        
        # Make batch predictions
        results = predictor.predict(data['samples'])
        
        return jsonify({
            'success': True,
            'predictions': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"❌ Batch prediction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/model/info', methods=['GET'])
def model_info():
    """Get model information"""
    return jsonify({
        'model_name': 'Water Quality Predictor',
        'model_version': predictor.model_version,
        'features': [
            'ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
            'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity'
        ],
        'target': 'Potability (0=Not Potable, 1=Potable)',
        'description': 'Predicts water potability based on chemical and physical properties'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)