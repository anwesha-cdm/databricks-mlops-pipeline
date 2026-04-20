"""
Water Quality API Usage Examples
How to use the inference API for predictions
"""

import requests
import json

# API Base URL (update with your deployment URL)
API_URL = "http://localhost:5000"

def test_api_health():
    """Test if the API is running"""
    response = requests.get(f"{API_URL}/health")
    print("🏥 Health Check:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_single_prediction():
    """Test single water sample prediction"""
    
    # Example water sample data
    water_sample = {
        "ph": 7.2,
        "Hardness": 180.5,
        "Solids": 15000,
        "Chloramines": 8.2,
        "Sulfate": 350.0,
        "Conductivity": 400.0,
        "Organic_carbon": 12.0,
        "Trihalomethanes": 70.0,
        "Turbidity": 3.5
    }
    
    response = requests.post(f"{API_URL}/predict", json=water_sample)
    result = response.json()
    
    print("🚰 Single Prediction Result:")
    if result['success']:
        pred = result['prediction']
        print(f"   Water Quality: {pred['potability_label']}")
        print(f"   Confidence: {pred['confidence']:.3f}")
        print(f"   Model Version: {pred['model_version']}")
        print(f"   Probabilities: Not Potable={pred['probabilities']['not_potable']:.3f}, Potable={pred['probabilities']['potable']:.3f}")
    else:
        print(f"   Error: {result['error']}")
    print()

def test_batch_prediction():
    """Test batch prediction with multiple samples"""
    
    batch_data = {
        "samples": [
            {
                "ph": 7.2, "Hardness": 180.5, "Solids": 15000, "Chloramines": 8.2,
                "Sulfate": 350.0, "Conductivity": 400.0, "Organic_carbon": 12.0,
                "Trihalomethanes": 70.0, "Turbidity": 3.5
            },
            {
                "ph": 6.8, "Hardness": 220.0, "Solids": 18000, "Chloramines": 9.1,
                "Sulfate": 400.0, "Conductivity": 450.0, "Organic_carbon": 15.0,
                "Trihalomethanes": 85.0, "Turbidity": 4.2
            },
            {
                "ph": 8.1, "Hardness": 150.0, "Solids": 12000, "Chloramines": 7.5,
                "Sulfate": 300.0, "Conductivity": 350.0, "Organic_carbon": 10.0,
                "Trihalomethanes": 60.0, "Turbidity": 2.8
            }
        ]
    }
    
    response = requests.post(f"{API_URL}/predict/batch", json=batch_data)
    result = response.json()
    
    print("Batch Prediction Results:")
    if result['success']:
        print(f"   Processed {result['count']} samples:")
        for i, pred in enumerate(result['predictions'], 1):
            print(f"   Sample {i}: {pred['potability_label']} (Confidence: {pred['confidence']:.3f})")
    else:
        print(f"   Error: {result['error']}")
    print()

def test_model_info():
    """Get model information"""
    response = requests.get(f"{API_URL}/model/info")
    print(" Model Information:")
    print(json.dumps(response.json(), indent=2))
    print()

if __name__ == "__main__":
    print("🧪 Testing Water Quality Prediction API")
    print("=" * 50)
    
    try:
        # Test all endpoints
        test_api_health()
        test_model_info()
        test_single_prediction()
        test_batch_prediction()
        
        print("✅ All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on http://localhost:5000")
        print("\nTo start the API server, run:")
        print("   python api/inference_api.py")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

# Example CURL commands
print("\n🔧 Example CURL Commands:")
print("=" * 30)
print("# Health Check")
print('curl -X GET "http://localhost:5000/health"')
print()
print("# Single Prediction")
print('''curl -X POST "http://localhost:5000/predict" \\
  -H "Content-Type: application/json" \\
  -d '{
    "ph": 7.2,
    "Hardness": 180.5,
    "Solids": 15000,
    "Chloramines": 8.2,
    "Sulfate": 350.0,
    "Conductivity": 400.0,
    "Organic_carbon": 12.0,
    "Trihalomethanes": 70.0,
    "Turbidity": 3.5
  }' ''')
print()
print("# Model Info")
print('curl -X GET "http://localhost:5000/model/info"')