"""
Archive Old MLflow Experiments
Archive completed experiments older than retention period
"""

import mlflow
from datetime import datetime, timedelta
import os

def archive_old_experiments():
    """Archive experiments older than retention period"""
    
    experiment_name = "/Shared/water_quality_exp"
    retention_days = 90  # Archive experiments older than 90 days
    
    try:
        # Set MLflow configuration
        mlflow.set_registry_uri("databricks-uc")
        
        client = mlflow.tracking.MlflowClient()
        
        # Get experiment
        experiment = client.get_experiment_by_name(experiment_name)
        if not experiment:
            print(f"❌ Experiment {experiment_name} not found")
            return
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        cutoff_timestamp = int(cutoff_date.timestamp() * 1000)  # MLflow uses milliseconds
        
        # Get all runs from experiment
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string="",
            max_results=10000
        )
        
        print(f"📊 Found {len(runs)} runs in experiment")
        
        # Filter runs older than cutoff
        old_runs = [run for run in runs if run.info.start_time < cutoff_timestamp]
        
        if old_runs:
            print(f"📦 Archiving {len(old_runs)} runs older than {retention_days} days")
            
            archived_count = 0
            for run in old_runs:
                try:
                    # Delete the run (archives it)
                    client.delete_run(run.info.run_id)
                    archived_count += 1
                    
                    if archived_count % 10 == 0:
                        print(f"   Archived {archived_count}/{len(old_runs)} runs...")
                        
                except Exception as e:
                    print(f"   ⚠️ Failed to archive run {run.info.run_id}: {str(e)}")
            
            print(f"✅ Successfully archived {archived_count}/{len(old_runs)} runs")
            
        else:
            print("✅ No old runs to archive")
            
    except Exception as e:
        print(f"❌ Archive failed: {str(e)}")
        raise

if __name__ == "__main__":
    archive_old_experiments()