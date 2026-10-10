# Backend Assignment: Distributed Certificate Generation

This repository contains a backend service designed to handle bulk certificate generation asynchronously. 

**🟢 LIVE DEMO:** The application is live and can be fully tested via the interactive Swagger API documentation here:  
👉 **[https://aereo-backend-assignment.onrender.com/docs](https://aereo-backend-assignment.onrender.com/docs)**

*(Note: The application is deployed on a Free Tier Render instance. It may take 30-50 seconds to wake up from a cold start upon your first request.)*

## How to set up the project

### Prerequisites
- Python 3.11 or higher
- `uv` package manager (or standard `pip`)
- Redis instance (Local or Cloud via Upstash)
- PostgreSQL database (Local or Cloud via Supabase)
- Docker & Docker Compose (Optional but recommended)

### Installation
1. Clone the repository:
```bash
git clone https://github.com/obaidaaman/Aereo-backend-assignment.git
cd Aereo-backend-assignment
```

2. Install the required dependencies (If running without Docker):
```bash
uv sync 
```

3. Create a `.env` file in the root directory and add your connection strings:
```env
POSTGRESQL_URL="postgresql://user:password@host:port/dbname"
REDIS_URL="redis://localhost:6379/0" 
# Cloud Storage variables (Optional, defaults to local OS directory if omitted)
SUPABASE_S3_ENDPOINT_URL="https://<project-ref>.supabase.co/storage/v1/s3"
SUPABASE_S3_ACCESS_KEY="<your-access-key>"
SUPABASE_S3_SECRET_KEY="<your-secret-key>"
SUPABASE_S3_BUCKET_NAME="certificates"
```

> [!NOTE]
> **Zero Configuration Local Mode:** If no `.env` file is present, the application will automatically fall back to running entirely locally. It will create a local SQLite database (`aereo_local.db`), connect to a local Redis server (`localhost:6379`), and save the generated certificates to the local `certificates/` folder on your disk. Furthermore, even if you do not have Redis installed or a Celery worker running, the API will not crash! It will gracefully degrade and process everything using FastAPI's built-in `background_tasks`.


## How to run the application

The system is built as a Monorepo, meaning the API server and the background task workers share the same codebase. 

### Local Development (Manual)
Run the processes in separate terminals:

**1. Start the Redis Server (If running locally):**
```bash
redis-server
```

**2. Start the Web Server:**
```bash
uvicorn main:app --reload
```

**3. Start the Celery Worker:**
```bash
celery -A celery_worker worker --pool=threads --concurrency=10 --loglevel=info
```
*(Note: `--pool=threads` is used locally on macOS to prevent multiprocessing bugs).*

### Local Development (Docker Compose)
To spin up both the API and the Worker seamlessly:
```bash
docker-compose up --build
```

### Production Deployment (e.g., Render Free Tier)
To fit within strict free-tier memory constraints (512MB RAM), the `Dockerfile` is configured to run both the Celery worker (limited to a single process) and the FastAPI server simultaneously in the same container using a shell operator:
```bash
CMD celery -A celery_worker worker --pool=solo --loglevel=info & uvicorn main:app --host 0.0.0.0 --port $PORT
```
This allows the complete distributed architecture to run on a single $0 cloud instance.

## Graceful Degradation: Celery vs Background Tasks

The system features an intelligent fallback mechanism to ensure high availability:

- **When Redis is UP (Primary Flow):** The application relies on **Celery**. The API Controller verifies the Redis connection via a `ping()`. If successful, the JSON payload is dispatched to the Celery Message Queue, leveraging the highly scalable Fan-out architecture for distributed generation.
- **When Redis is DOWN (Fallback Flow):** If the Redis ping fails or connection times out, the application does not crash. Instead, it gracefully degrades to using FastAPI's native `background_tasks`. To ensure generation speed remains fast without Celery, the fallback function utilizes `concurrent.futures.ThreadPoolExecutor` to process certificates in parallel threads before syncing the results to the database sequentially.

## How to run tests

You can verify that the API is communicating properly using manual cURL requests or API clients like Postman. 

To test if the application is running and the database connection is active:
```bash
curl -X GET http://127.0.0.1:8000/
```

## How to submit a certificate generation request

You can submit a batch of recipients using the `POST /api/job/certificate` endpoint. 

**Request:**
```bash
curl -X POST "https://aereo-backend-assignment.onrender.com/api/job/certificate" \
     -H "Content-Type: application/json" \
     -d '{
           "event_name": "Backend Architecture Masterclass",
           "date": "10 October 2026",
           "recipients": [
             {"name": "Aman Obaid", "email": "aman@example.com"},
             {"name": "Sarah Connor", "email": "sarah@example.com"},
             {"name": "John Doe", "email": "john@example.com"},
             {"name": "Bruce Wayne", "email": "bruce@example.com"},
             {"name": "Clark Kent", "email": "clark@example.com"},
             {"name": "Diana Prince", "email": "diana@example.com"},
             {"name": "Barry Allen", "email": "barry@example.com"},
             {"name": "Arthur Curry", "email": "arthur@example.com"},
             {"name": "Victor Stone", "email": "victor@example.com"},
             {"name": "Hal Jordan", "email": "hal@example.com"},
             {"name": "Oliver Queen", "email": "oliver@example.com"},
             {"name": "Tony Stark", "email": "tony@example.com"},
             {"name": "Steve Rogers", "email": "steve@example.com"},
             {"name": "Natasha Romanoff", "email": "natasha@example.com"},
             {"name": "Bruce Banner", "email": "banner@example.com"},
             {"name": "Thor Odinson", "email": "thor@example.com"},
             {"name": "Clint Barton", "email": "clint@example.com"},
             {"name": "Peter Parker", "email": "peter@example.com"},
             {"name": "Stephen Strange", "email": "strange@example.com"},
             {"name": "Wanda Maximoff", "email": "wanda@example.com"},
             {"name": "Vision", "email": "vision@example.com"},
             {"name": "Sam Wilson", "email": "sam@example.com"},
             {"name": "Bucky Barnes", "email": "bucky@example.com"},
             {"name": "Scott Lang", "email": "scott@example.com"},
             {"name": "Hope van Dyne", "email": "hope@example.com"},
             {"name": "TChalla", "email": "tchalla@example.com"},
             {"name": "Carol Danvers", "email": "carol@example.com"},
             {"name": "Nick Fury", "email": "fury@example.com"},
             {"name": "Maria Hill", "email": "maria@example.com"},
             {"name": "Phil Coulson", "email": "phil@example.com"},
             {"name": "Matt Murdock", "email": "matt@example.com"},
             {"name": "Jessica Jones", "email": "jessica@example.com"},
             {"name": "Luke Cage", "email": "luke@example.com"},
             {"name": "Danny Rand", "email": "danny@example.com"},
             {"name": "Frank Castle", "email": "frank@example.com"},
             {"name": "Marc Spector", "email": "marc@example.com"},
             {"name": "Kamala Khan", "email": "kamala@example.com"},
             {"name": "Miles Morales", "email": "miles@example.com"},
             {"name": "Gwen Stacy", "email": "gwen@example.com"},
             {"name": "Eddie Brock", "email": "eddie@example.com"},
             {"name": "Reed Richards", "email": "reed@example.com"},
             {"name": "Sue Storm", "email": "sue@example.com"},
             {"name": "Johnny Storm", "email": "johnny@example.com"},
             {"name": "Ben Grimm", "email": "ben@example.com"},
             {"name": "Charles Xavier", "email": "charles@example.com"},
             {"name": "Logan", "email": "logan@example.com"},
             {"name": "Ororo Munroe", "email": "ororo@example.com"},
             {"name": "Jean Grey", "email": "jean@example.com"},
             {"name": "Scott Summers", "email": "summers@example.com"},
             {"name": "Hank McCoy", "email": "hank@example.com"}
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

5. **Cloud Object Storage Strategy:** 
   Ephemeral deployments (like Render) do not share disk volumes between web servers and background workers. To prevent "File Not Found" errors in production, the application dynamically uploads generated certificates to **Supabase S3 Storage**. The API intercepts `s3://` URLs and generates secure presigned URLs on the fly via `boto3`, gracefully redirecting the user to download the file directly from the cloud. In local development (if env vars are omitted), it safely defaults to the local OS directory.
