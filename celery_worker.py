import os
from celery import Celery
from models.models import CertificateModel
from database.models import Job, Certificate
from database.db import SessionLocal

# Import the robust drawing function
from utils import robust_draw_certificate

celery_app = Celery(
    'certificate_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery_app.task(bind=True, max_retries=3)
def celery_generate_certificate(self, data_dict: dict, job_id: str):
    os.makedirs("certificates", exist_ok=True)
    db = SessionLocal()
    

    data = CertificateModel(**data_dict)
    
    try:
        print(f" Started processing job {job_id}")
        
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "PROCESSING"
            db.commit()

        for i, recipient in enumerate(data.recipients):
            print(f"[CELERY] Processing recipient {i+1}: {recipient.name}")
            
            cert_record = Certificate(
                job_id=job_id,
                recipient_name=recipient.name,
                recipient_email=recipient.email,
                status="PROCESSING"
            )
            db.add(cert_record)
            db.commit() 

            try:
                file_name = f"certificates/cert_{cert_record.id}.png"
                
                robust_draw_certificate(
                    name=recipient.name,
                    achievement=data.event_name,
                    date=data.date, 
                    certificate_id=cert_record.id,
                    output_path=file_name
                )
                
                cert_record.status = "SUCCESS"
                cert_record.file_url = file_name 
                
            except Exception as e:
                cert_record.status = "FAILED"
                cert_record.error_message = str(e)
            
            db.commit()


        if job:
            failed_count = db.query(Certificate).filter(Certificate.job_id == job_id, Certificate.status == "FAILED").count()
            
            if failed_count > 0:
                job.status = "PARTIALLY_FAILED"
            else:
                job.status = "COMPLETED"
                
            db.commit()

        print(f"Job {job_id} successfully processed!")

    except Exception as e:
        print(f"[CELERY] Error processing job {job_id}: {str(e)}")
        # self.retry() for timeout
        
    finally:
        db.close()
