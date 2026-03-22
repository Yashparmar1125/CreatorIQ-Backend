# CreatorIQ Backend (v1.0)

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.12+
- PostgreSQL 16 (on RDS or local)
- Redis 7
- Kafka (MSK or local)

### 2. Installation
```bash
# Clone the repository
git clone <repo-url>
cd CreatorIQ_Backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory based on `src/core/config.py`:
```env
ENVIRONMENT=development
LOG_LEVEL=DEBUG
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=localhost
POSTGRES_DB=creatoriq
REDIS_URL=redis://localhost:6379/0
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### 4. Running the Application
```bash
uvicorn src.main:app --reload
```
The API documentation will be available at `http://localhost:8000/docs`.

## 🏗️ Architecture
- **API Framework**: FastAPI
- **Database**: SQLAlchemy 2.0 (Async) + Alembic
- **ML Services**: TorchServe
- **Logging**: Structured JSON
- **Middleware**: JWT Auth, Rate Limiting, Request Tracking

## 📁 Project Structure
- `src/api`: Domain-specific API routers
- `src/core`: Configuration, Database, Logging, Security
- `src/models`: SQLAlchemy and Pydantic models/schemas
- `src/services`: Business logic
- `src/repositories`: Data access layer
- `src/middleware`: FastAPI middlewares
- `src/ml`: ML pipelines
- `src/integrations`: External API clients (YouTube, Anthropic, SerpAPI)
