import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from src.api import app
from src.recommender import MatrixFactorizationRecommender

def run_batch_job():
    """The Cold Path: Runs the heavy math engine without blocking the API."""
    print("\n[BATCH JOB] Waking up background worker...")
    try:
        # Using 100 epochs for optimal convergence based, scales with data volume
        recommender = MatrixFactorizationRecommender(num_factors=10, lr=0.01, reg=0.05, epochs=100)
        recommender.fit()
        recommender.save_recommendations(top_n=5)
        print("[BATCH JOB] Successfully updated all user recommendations.\n")
    except Exception as e:
        print(f"[BATCH JOB ERROR] {e}")

if __name__ == "__main__":
    # 1. Initialize and start the background scheduler
    scheduler = BackgroundScheduler()

    # Run this every 2 minutes for testing.
    # Would use: trigger='cron', hour=2 (to run at 2:00 AM) in production
    scheduler.add_job(run_batch_job, 'interval', minutes=2)
    scheduler.start()

    print("[INFO] Master Orchestrator started. Background scheduler active.")

    # 2. Launch the Hot Path API Server on the main thread
    uvicorn.run(app, host="0.0.0.0", port=8000)
