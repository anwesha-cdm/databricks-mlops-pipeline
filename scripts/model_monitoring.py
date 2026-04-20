"""
Automated Model Monitoring Script
Runs data drift detection and model performance monitoring
"""

import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from scipy import stats
import os
import sys
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ModelMonitor:
    def __init__(self):
        self.model_name = "dev_digital_engineering_services.default.water_quality_model"
        self.experiment_name = "/Shared/water_quality_exp"
        self.drift_threshold = 0.05
        self.performance_threshold = 0.80
        
        # Set MLflow configuration
        mlflow.set_registry_uri("databricks-uc")
        mlflow.set_experiment(self.experiment_name)
        
    def load_latest_model(self):
        """Load the latest model version"""
        try:
            client = mlflow.tracking.MlflowClient()
            latest_version = client.get_latest_versions(self.model_name, stages=["None"])[0]
            
            model_uri = f"models:/{self.model_name}/{latest_version.version}"
            model = mlflow.sklearn.load_model(model_uri)
            
            print(f"✅ Loaded model version {latest_version.version}")
            return model, latest_version.version
            
        except Exception as e:
            print(f"❌ Failed to load model: {str(e)}")
            raise
    
    def get_reference_data(self):
        """Get reference data for drift comparison"""
        try:
            # In production, this would query your data warehouse
            # For demo, we'll simulate reference data statistics
            
            reference_stats = {
                'ph': {'mean': 7.08, 'std': 1.59},
                'Hardness': {'mean': 196.37, 'std': 32.42},
                'Solids': {'mean': 22014.09, 'std': 8768.57},
                'Chloramines': {'mean': 7.12, 'std': 1.58},
                'Sulfate': {'mean': 333.78, 'std': 41.42},
                'Conductivity': {'mean': 426.20, 'std': 80.82},
                'Organic_carbon': {'mean': 14.28, 'std': 3.31},
                'Trihalomethanes': {'mean': 66.40, 'std': 16.18},
                'Turbidity': {'mean': 3.97, 'std': 0.78}
            }
            
            print("✅ Reference data statistics loaded")
            return reference_stats
            
        except Exception as e:
            print(f"❌ Failed to load reference data: {str(e)}")
            raise
    
    def get_current_data(self):
        """Get current/recent data for monitoring"""
        try:
            # In production, this would query recent data from your data pipeline
            # For demo, we'll simulate current data with slight drift
            
            np.random.seed(42)
            n_samples = 1000
            
            # Simulate data with potential drift
            current_data = {
                'ph': np.random.normal(7.2, 1.6, n_samples),  # Slight mean shift
                'Hardness': np.random.normal(200, 35, n_samples),  # Increased variance
                'Solids': np.random.normal(22000, 9000, n_samples),
                'Chloramines': np.random.normal(7.0, 1.5, n_samples),
                'Sulfate': np.random.normal(330, 42, n_samples),
                'Conductivity': np.random.normal(430, 85, n_samples),
                'Organic_carbon': np.random.normal(14.5, 3.5, n_samples),
                'Trihalomethanes': np.random.normal(67, 17, n_samples),
                'Turbidity': np.random.normal(4.1, 0.8, n_samples)
            }
            
            df = pd.DataFrame(current_data)
            print(f"✅ Current data loaded: {len(df)} samples")
            return df
            
        except Exception as e:
            print(f"❌ Failed to load current data: {str(e)}")
            raise
    
    def detect_data_drift(self, reference_stats, current_data):
        """Detect data drift using statistical tests"""
        
        drift_results = {}
        features_with_drift = []
        
        print("\n🔍 DETECTING DATA DRIFT:")
        print("=" * 50)
        
        for feature in reference_stats.keys():
            if feature in current_data.columns:
                current_values = current_data[feature].dropna()
                
                # Generate reference sample based on stored statistics
                ref_mean = reference_stats[feature]['mean']
                ref_std = reference_stats[feature]['std']
                
                # Statistical tests
                # 1. Mean shift test (t-test)
                t_stat, t_pvalue = stats.ttest_1samp(current_values, ref_mean)
                
                # 2. Variance test (F-test approximation using variance ratio)
                current_var = current_values.var()
                ref_var = ref_std ** 2
                var_ratio = current_var / ref_var
                
                # Simple thresholds for variance drift
                var_drift = var_ratio > 1.5 or var_ratio < 0.67
                
                # Overall drift detection
                mean_drift = t_pvalue < self.drift_threshold
                drift_detected = mean_drift or var_drift
                
                # Calculate percentage changes
                mean_change_pct = abs((current_values.mean() - ref_mean) / ref_mean * 100)
                var_change_pct = abs((current_var - ref_var) / ref_var * 100)
                
                drift_results[feature] = {
                    'mean_drift': mean_drift,
                    'variance_drift': var_drift,
                    'overall_drift': drift_detected,
                    't_statistic': t_stat,
                    't_pvalue': t_pvalue,
                    'variance_ratio': var_ratio,
                    'mean_change_pct': mean_change_pct,
                    'variance_change_pct': var_change_pct,
                    'reference_mean': ref_mean,
                    'current_mean': current_values.mean(),
                    'reference_std': ref_std,
                    'current_std': current_values.std()
                }
                
                # Print results
                status = "🚨 DRIFT" if drift_detected else "✅ OK"
                print(f"{feature:15} | {status:8} | Mean Δ: {mean_change_pct:5.1f}% | Var Δ: {var_change_pct:5.1f}%")
                
                if drift_detected:
                    features_with_drift.append(feature)
        
        print("=" * 50)
        
        if features_with_drift:
            print(f"⚠️  DRIFT DETECTED in {len(features_with_drift)} features: {features_with_drift}")
        else:
            print("✅ No significant data drift detected")
            
        return drift_results, features_with_drift
    
    def evaluate_model_performance(self, model, current_data):
        """Evaluate model performance on current data"""
        
        try:
            # Feature engineering (same as training pipeline)
            current_data['ph_normalized'] = current_data['ph'] / 14
            current_data['hardness_ratio'] = current_data['Hardness'] / (current_data['Solids'] + 1)
            current_data['organic_load'] = current_data['Organic_carbon'] * current_data['Chloramines']
            
            # Simulate ground truth labels (in production, get from labeled data)
            # For demo, create synthetic labels based on feature thresholds
            labels = ((current_data['ph'] > 6.5) & 
                     (current_data['ph'] < 8.5) & 
                     (current_data['Turbidity'] < 4) &
                     (current_data['Chloramines'] < 8)).astype(int)
            
            # Prepare features
            feature_cols = ['ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
                           'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity',
                           'ph_normalized', 'hardness_ratio', 'organic_load']
            
            X = current_data[feature_cols]
            y_true = labels
            
            # Make predictions
            y_pred = model.predict(X)
            y_prob = model.predict_proba(X)
            
            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
                'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
                'f1_score': f1_score(y_true, y_pred, average='weighted', zero_division=0)
            }
            
            print(f"\n📊 MODEL PERFORMANCE METRICS:")
            print("=" * 40)
            for metric, value in metrics.items():
                status = "✅" if value >= self.performance_threshold else "⚠️ "
                print(f"{status} {metric.capitalize()}: {value:.4f}")
            
            print("=" * 40)
            
            return metrics
            
        except Exception as e:
            print(f"❌ Performance evaluation failed: {str(e)}")
            return {}
    
    def log_monitoring_results(self, drift_results, performance_metrics, model_version):
        """Log monitoring results to MLflow"""
        
        try:
            with mlflow.start_run(run_name=f"monitoring_{datetime.now().strftime('%Y%m%d_%H%M')}"):
                
                # Log drift metrics
                drift_count = sum(1 for f in drift_results.values() if f['overall_drift'])
                mlflow.log_metric("features_with_drift", drift_count)
                mlflow.log_metric("total_features_monitored", len(drift_results))
                
                for feature, results in drift_results.items():
                    mlflow.log_metric(f"drift_{feature}_mean_change_pct", results['mean_change_pct'])
                    mlflow.log_metric(f"drift_{feature}_var_change_pct", results['variance_change_pct'])
                    mlflow.log_metric(f"drift_{feature}_detected", int(results['overall_drift']))
                
                # Log performance metrics
                for metric, value in performance_metrics.items():
                    mlflow.log_metric(f"performance_{metric}", value)
                
                # Log metadata
                mlflow.log_param("model_version", model_version)
                mlflow.log_param("monitoring_timestamp", datetime.now().isoformat())
                mlflow.log_param("drift_threshold", self.drift_threshold)
                mlflow.log_param("performance_threshold", self.performance_threshold)
                
                # Create summary report
                summary = {
                    "timestamp": datetime.now().isoformat(),
                    "model_version": model_version,
                    "drift_summary": {
                        "features_with_drift": drift_count,
                        "total_features": len(drift_results),
                        "drift_detected": drift_count > 0
                    },
                    "performance_summary": performance_metrics,
                    "alerts": []
                }
                
                # Generate alerts
                if drift_count > 0:
                    summary["alerts"].append(f"Data drift detected in {drift_count} features")
                
                if performance_metrics.get('accuracy', 1.0) < self.performance_threshold:
                    summary["alerts"].append(f"Model accuracy below threshold: {performance_metrics['accuracy']:.3f}")
                
                # Log summary as artifact
                with open("monitoring_summary.json", "w") as f:
                    json.dump(summary, f, indent=2)
                mlflow.log_artifact("monitoring_summary.json")
                
                print("✅ Monitoring results logged to MLflow")
                return summary
                
        except Exception as e:
            print(f"❌ Failed to log monitoring results: {str(e)}")
            return None
    
    def run_monitoring(self):
        """Main monitoring workflow"""
        
        print("🚀 STARTING AUTOMATED MODEL MONITORING")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Model: {self.model_name}")
        print("=" * 60)
        
        try:
            # Load model and data
            model, model_version = self.load_latest_model()
            reference_stats = self.get_reference_data()
            current_data = self.get_current_data()
            
            # Detect drift
            drift_results, drift_features = self.detect_data_drift(reference_stats, current_data)
            
            # Evaluate performance
            performance_metrics = self.evaluate_model_performance(model, current_data)
            
            # Log results
            summary = self.log_monitoring_results(drift_results, performance_metrics, model_version)
            
            # Determine overall status
            critical_issues = len(drift_features) > 2 or performance_metrics.get('accuracy', 1.0) < self.performance_threshold
            
            print(f"\n🎯 MONITORING SUMMARY:")
            print("=" * 30)
            print(f"Model Version: {model_version}")
            print(f"Features with Drift: {len(drift_features)}")
            print(f"Model Accuracy: {performance_metrics.get('accuracy', 'N/A')}")
            print(f"Status: {'🚨 ATTENTION NEEDED' if critical_issues else '✅ HEALTHY'}")
            print("=" * 30)
            
            # Exit with appropriate code for CI/CD
            if critical_issues:
                print("❌ Critical issues detected - failing monitoring job")
                sys.exit(1)
            else:
                print("✅ Monitoring completed successfully")
                sys.exit(0)
                
        except Exception as e:
            print(f"❌ Monitoring failed: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    monitor = ModelMonitor()
    monitor.run_monitoring()