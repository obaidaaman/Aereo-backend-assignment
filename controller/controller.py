import os
import uuid
import redis
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from models.models import CertificateModel, Recipient
from database.models import Job, Certificate
from database.db import SessionLocal
from celery_worker import master_certificate_generator
from utils import robust_draw_certificate
from fastapi.responses import FileResponse
from fastapi.responses import FileResponse
from dotenv import load_dotenv
load_dotenv()

def generate_certificate_controller(data: CertificateModel, background_tasks: BackgroundTasks, db: Session):
    job_id = str(uuid.uuid4())

    try:
        new_job = Job(
            id=job_id, 
            event_name=data.event_name, 
            total_recipients=len(data.recipients)
        )
        db.add(new_job)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job in database: {str(e)}"
        )
        
    
    #  "redis://localhost:6379/0"

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
   
    if "rediss://" in redis_url:
        redis_client = redis.from_url(redis_url, ssl_cert_reqs="none", socket_connect_timeout=2)
    else:
        redis_client = redis.from_url(redis_url, socket_connect_timeout=2)
    try:
        redis_client.ping()
        print("REDIS is UP!")
        
        master_certificate_generator.delay(data.model_dump(), job_id)

    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
        print("Redis is DOWN!")
        background_tasks.add_task(generate_certificate, data, job_id)

    return {
        "message": "Certificate generation job accepted.",
        "job_id": job_id,
        "status": "processing"
    }


import concurrent.futures

def generate_certificate(data: CertificateModel, job_id: str):
    os.makedirs("certificates", exist_ok=True)
    db = SessionLocal()
    
    try:
        print(f"Background Processing started for job {job_id}")
        
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "PROCESSING"
            db.commit()

        recipients: list[Recipient] = data.recipients
        cert_records_data = []

        # Step 1: Pre-create all certificates in DB synchronously
        for recipient in recipients:
            cert_record = Certificate(
                job_id=job_id,
                recipient_name=recipient.name,
                recipient_email=recipient.email,
                status="PROCESSING"
            )
            db.add(cert_record)
            db.commit()
            db.refresh(cert_record)
            cert_records_data.append((recipient, str(cert_record.id)))

        # Call Function for for thread
        def draw_cert(recipient, cert_id):
            file_name = f"certificates/cert_{cert_id}.png"
            try:
                robust_draw_certificate(
                    name=recipient.name,
                    achievement=data.event_name,
                    date=data.date, 
                    certificate_id=cert_id,
                    output_path=file_name
                )
                return cert_id, "SUCCESS", file_name, None
            except Exception as e:
                return cert_id, "FAILED", None, str(e)

        
        print(f"Starting parallel generation for {len(cert_records_data)} certificates...")
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            
            futures = [executor.submit(draw_cert, rec, cid) for rec, cid in cert_records_data]
            
           
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())

       
        for cert_id, status, file_name, error_message in results:
            cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
            if cert:
                cert.status = status
                if status == "SUCCESS":
                    cert.file_url = file_name
                else:
                    cert.error_message = error_message
        db.commit()

      
        if job:
            failed_count = db.query(Certificate).filter(Certificate.job_id == job_id, Certificate.status == "FAILED").count()
            if failed_count > 0:
                job.status = "PARTIALLY_FAILED"
            else:
                job.status = "COMPLETED"
            db.commit()

        print(f"Processing completed for job {job_id}")

    finally:
        db.close()


def get_job_controller(job_id : str, db: Session):
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code = 400, detail = "Job not found")

        certificates = db.query(Certificate).filter(Certificate.job_id == job_id).all()

        cert_list = [
            {
                "cert_id" : cert.id,
                "name" : cert.recipient_name,
                "status" : cert.status,
                "download_url" : f"/api/job/download/{cert.id}" if cert.status == "SUCCESS" else None
            }

            for cert in certificates
        ]
        return {
            "job_id": job.id,
            "status": job.status,
            "total_recipients": job.total_recipients,
            "certificates": cert_list
        }
        
       

    except Exception as e:
        return {
            "message": "Error fetching job",
            "job_id": job_id,
            "status": "ERROR"
        }


def downlaod_certificate_controller(cert_id : str, db :Session):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code = 400, detail = "Certificate not found")
    if cert.status != "SUCCESS":
        raise HTTPException(status_code = 400, detail = "Certificate is not ready yet")
    
    file_path = cert.file_url
    if not os.path.exists(file_path):
        raise HTTPException(status_code = 404, detail = "Certificate file not found")
    

    return FileResponse(path=file_path, filename=f"{cert.recipient_name}_certificate.png", media_type="image/png")
    
