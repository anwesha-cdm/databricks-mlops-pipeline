"""
Cleanup Old Model Versions
Removes old model versions to manage storage and maintain registry hygiene
"""

import mlflow
import mlflow.sklearn
from datetime import datetime, timedelta
import os

def cleanup_old_models():
    """Remove old model versions beyond retention policy"""
    
    model_name = "dev_digital_engineering_services.default.water_quality_model"
    max_versions_to_keep = 5  # Keep latest 5 versions
    
    try:
        # Set MLflow configuration
        mlflow.set_registry_uri("databricks-uc")
        
        client = mlflow.tracking.MlflowClient()
        
        # Get all model versions
        model_versions = client.search_model_versions(f"name='{model_name}'")
        
        # Sort by version number (descending)
        sorted_versions = sorted(model_versions, key=lambda x: int(x.version), reverse=True)
        
        print(f"📦 Found {len(sorted_versions)} model versions")
        
        # Keep only the latest N versions
        versions_to_delete = sorted_versions[max_versions_to_keep:]
        
        if versions_to_delete:
            print(f"🗑️  Deleting {len(versions_to_delete)} old versions:")
            
            for version in versions_to_delete:
                print(f"   - Version {version.version} (Created: {version.creation_timestamp})")
                
                # Delete the model version
                client.delete_model_version(
                    name=model_name,
                    version=version.version
                )
                
            print("✅ Cleanup completed successfully")
        else:
            print("✅ No old versions to clean up")
            
    except Exception as e:
        print(f"❌ Cleanup failed: {str(e)}")
        raise

if __name__ == "__main__":
    cleanup_old_models()