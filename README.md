# E-Commerce Recommendation Engine
**Eコマース推薦エンジン (行列分解)**

A dual-path recommendation system built from scratch using pure linear algebra (Stochastic Gradient Descent) to process e-commerce clickstreams, bypassing black-box machine learning libraries.

## 🎯 Project Overview | プロジェクト概要
This project tackles a core backend challenge for large-scale e-commerce platforms: turning billions of sparse, implicit user interactions (views, add-to-carts, purchases) into real-time personalized recommendations.

The system demonstrates a production-grade architecture by explicitly decoupling mathematical matrix computations from high-throughput API serving.

## 🏗️ System Architecture | システムアーキテクチャ
The engine splits data processing into two isolated paths to ensure the web server is never blocked by heavy numerical calculations:

* **The Hot Path (FastAPI):** High-speed event ingestion (`POST /events`) and low-latency recommendation serving (`GET /recommendations`) via pre-computed lookup tables.
* **The Cold Path (NumPy):** A background worker (APScheduler) that extracts interaction logs, constructs a sparse User-Item matrix, and factorizes it via Stochastic Gradient Descent (SGD) to discover latent user preferences.

## 🛠️ Tech Stack | 技術スタック
* **Language:** Python 3.12+ (NumPy for pure matrix factorization)
* **Database:** SQLite (Relational schema with strict Foreign Key enforcement)
* **API Layer:** FastAPI, Pydantic (Two-Layer Data Validation)
* **Infrastructure:** Docker & Docker Compose (Persistent Data Volumes)

## 🚀 Quick Start | 使い方

**1. Clone and Boot the Container**
```bash
docker compose up --build
```

**2. Access the Interactive API Docs**
Navigate to http://localhost:8000/docs to view the Swagger UI.

**3. Test the Endpoints**
- POST /api/v1/events: Submit a user click (view, cart, buy).
- GET /api/v1/recommendations/{user_id}: Instantly retrieve the top 5 predicted items for a user.

## 🧠 Lessons Learned & Engineering Defenses
- Algorithm Translation: Successfully translated theoretical Stochastic Gradient Descent mathematics into a stable, iterative Python loop.
- Two-Layer Validation: Implemented Pydantic boundary checks (Layer 1) and SQLite Foreign Key enforcement (Layer 2) to completely block "phantom" relational data from corrupting the math engine.
- Lambda Architecture: Mastered running asynchronous web servers alongside synchronous background batch jobs using APScheduler without freezing the event loop.
