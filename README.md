# 🚀 CreatorIQ Backend: AI-Driven YouTube Intelligence

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python 3.13](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql)](https://www.postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

CreatorIQ is a high-performance, modular backend designed for YouTube content creators. It leverages AI/ML (PyTorch, Transformers), time-series analytics (TimescaleDB), and low-latency asynchronous processing to provide real-time trending insights, content strategy generation, and performance tracking.

---

## 🏗️ System Architecture

The project follows a **Modular Monolith** pattern, ensuring clean domain boundaries while maintaining deployment simplicity.

```mermaid
graph TD
    User([User]) -->|HTTPS| API[FastAPI Gateway]
    API -->|Auth| JWT[JWT/OAuth 2.0]
    API -->|Async Ops| Redis[(Redis)]
    API -->|Streams| Kafka[Kafka Cluster]
    
    subgraph Core Domain
        D_Auth[Auth Service]
        D_Analytics[Analytics Service]
        D_ML[Trend Prediction ML]
    end
    
    API --> Core Domain
    D_Auth --> DB[(PostgreSQL/TimescaleDB)]
    D_Analytics --> DB
    D_ML --> Influx[(InfluxDB/ML Metrics)]
```

## 🛠️ Tech Stack & Implementation

- **Core**: Python 3.13 (AsyncIO), FastAPI
- **Database**: PostgreSQL 16 + TimescaleDB (Time-series)
- **ORM**: SQLAlchemy 2.0 (Asynchronous) + Alembic
- **Caching/State**: Redis 7
- **Event Streaming**: Kafka / Confluent
- **AI/ML**: PyTorch, HuggingFace Transformers, scikit-learn
- **Observability**: Structured JSON Logging, OpenTelemetry (Planned)
- **Infrastructure**: AWS ECS, Terraform, GitHub Actions

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.13.7**
- **Docker** (Optional, recommended for DB/Redis/Kafka)

### 2. Environment Setup
```powershell
# Clone the repository
git clone https://github.com/Yashparmar1125/CreatorIQ-Backend.git
cd CreatorIQ-Backend

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies (Python 3.13 optimized)
pip install -r requirements.txt
```

### 3. Configuration
Configure your `.env` file from the provided defaults:
```env
APP_NAME="CreatorIQ Backend"
LOG_LEVEL=DEBUG
ENVIRONMENT=development

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=creatoriq

# Redis & Kafka
REDIS_URL=redis://localhost:6379/0
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Security
SECRET_KEY=generate_a_secure_key_here
```

### 4. Launching the API
```powershell
uvicorn src.main:app --reload
```
- **Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Redoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📁 Repository Structure

```text
CreatorIQ_Backend/
├── src/
│   ├── api/            # Domain-specific REST Controllers
│   ├── core/           # Universal config, DB, & logging
│   ├── middleware/     # Auth, Tracking, & Monitoring
│   ├── models/         # SQLAlchemy ORM & Pydantic Schemas
│   ├── services/       # Core Business Logic Layer
│   ├── repositories/   # Data Access Layer (Abstracted)
│   ├── ml/             # Inference & Prediction Pipelines
│   └── integrations/   # YouTube, Anthropic, & External Clients
├── migrations/         # Alembic DB Migration Scripts
├── tests/              # Pytest Suite (Unit/Integration)
└── infra/              # Terraform & Docker configuration
```

---

## 🛡️ Security & Performance

- **Authentication**: JWT (RS256) with Refresh Token rotation.
- **Data Protection**: AES-256 for sensitive channel tokens at rest.
- **Integrity**: Strict Pydantic v2 validation for all API boundaries.
- **Performance**: Asynchronous non-blocking I/O across the entire stack.

---

## 📜 License
Published under the **MIT License**. See [LICENSE](LICENSE) for details. (Initial scaffolding v1.0)
