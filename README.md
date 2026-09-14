# E-Commerce Recommendation Engine
**Eコマース推薦エンジン (行列分解)**

A dual-path recommendation system built from scratch using pure linear algebra (Stochastic Gradient Descent) to process e-commerce clickstreams, bypassing black-box machine learning libraries.

## 🎯 Project Overview
This project tackles a core backend challenge for large-scale e-commerce platforms: turning billions of sparse, implicit user interactions (views, add-to-carts, purchases) into real-time personalized recommendations.

The system demonstrates a production-grade architecture by explicitly decoupling mathematical matrix computations from high-throughput API serving.

## 🏗️ System Architecture
The engine splits data processing into two isolated paths to ensure the web server is never blocked by heavy numerical calculations:

* **The Hot Path (FastAPI):** High-speed event ingestion (`POST /events`) and low-latency recommendation serving (`GET /recommendations`) via pre-computed lookup tables.
* **The Cold Path (NumPy):** A background worker that extracts interaction logs, constructs a sparse User-Item matrix, and factorizes it via Stochastic Gradient Descent (SGD) to discover latent user preferences.

## 🛠️ Tech Stack
* **Language:** Python 3.12+ (NumPy for pure matrix factorization)
* **Database:** SQLite (Relational schema for event logging and materialized serving)
* **API Layer:** FastAPI, Pydantic
* **Infrastructure:** Docker (Planned)
