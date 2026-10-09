# Backend Assignment: Distributed Certificate Generation

This repository contains a backend service designed to handle bulk certificate generation asynchronously. 

## How to set up the project

### Prerequisites
- Python 3.11 or higher
- `uv` package manager (or standard `pip`)
- Redis instance (Local or Cloud via Upstash)
- PostgreSQL database (Local or Cloud via Supabase)

### Installation
1. Clone the repository:
```bash
git clone https://github.com/obaidaaman/Aereo-backend-assignment.git
cd Aereo-backend-assignment
```

2. Install the required dependencies:
```bash
uv sync 
```

3. Create a `.env` file in the root directory and add your connection strings:
```env
POSTGRESQL_URL="postgresql://user:password@host:port/dbname"
REDIS_URL="redis://localhost:6379/0" 
```

## How to run the application

The system is built as a Monorepo, meaning the API server and the background task workers share the same codebase but must be run as two separate processes.

**1. Start the Web Server:**
```bash
uvicorn main:app --reload
```
For production (e.g., Render/AWS), use: `uvicorn main:app --host 0.0.0.0 --port 8000`

**2. Start the Celery Worker:**
Open a second terminal and run:
```bash
celery -A celery_worker worker --pool=threads --concurrency=10 --loglevel=info
```
*(Note: `--pool=threads` is used to prevent macOS multiprocessing issues. On Linux, this flag can be omitted to use the default prefork pool).*

## How to run tests

You can verify that the API and background workers are communicating properly using manual cURL requests or API clients like Postman. 

To test if the application is running and the database connection is active:
```bash
curl -X GET http://127.0.0.1:8000/
```

## How to submit a certificate generation request

You can submit a batch of recipients using the `POST /api/job/certificate` endpoint. 

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/job/certificate" \
     -H "Content-Type: application/json" \
     -d '{
           "event_name": "Backend Architecture Masterclass",
           "date": "10 October 2026",
           "recipients": [
             {"name": "Aman Obaid", "email": "aman@example.com"},
             {"name": "John Doe", "email": "john@example.com"}
           ]
         }'
```

**Response:**
The API will return a `job_id` immediately while the certificates generate in the background.
```json
{
  "message": "Certificate generation job accepted.",
  "job_id": "d2bc13f3-9c44-405d-a41e-203faea8db86",
  "status": "processing"
}
```

## How to retrieve generated certificates

Retrieval is a two-step process because the certificates are generated asynchronously. 

**1. Check the Job Status:**
Use the `GET /api/job/{job_id}` endpoint to track the background progress.
```bash
curl -X GET "http://127.0.0.1:8000/api/job/d2bc13f3-9c44-405d-a41e-203faea8db86"
```

**2. Download a specific certificate:**
Once the status of a specific recipient within the job shows as `SUCCESS`, you can download their certificate file using their unique certificate `id`.
```bash
curl -O -J "http://127.0.0.1:8000/api/job/download/{cert_id}"
```

## Important implementation/design decisions

1. **Fan-out Architecture (Celery Chords):** 
   Instead of iterating over the bulk JSON array in a single blocking task, the master task spawns individual atomic tasks for every recipient. This increases Redis message volume but provides strict fault tolerance. If one certificate fails to draw, it does not crash the entire batch.

2. **Monorepo Approach:** 
   FastAPI and Celery share the exact same models and utilities. This makes local development seamless while still allowing the web and worker tiers to scale independently in production.

3. **Database Migration (SQLite to PostgreSQL):** 
   The project initially used SQLite. However, distributed background workers require concurrent database access, which SQLite handles poorly due to file locks. We migrated to PostgreSQL (Supabase) and specifically disabled prepared statements in SQLAlchemy (`prepare_threshold: None`) to ensure compatibility with Supabase's Transaction Pooler (PgBouncer).

4. **Robust Retries:** 
   File I/O and image generation can face temporary glitches. The core `robust_draw_certificate` function is wrapped with the `tenacity` library, automatically retrying up to 3 times before committing a failure status to the database.
