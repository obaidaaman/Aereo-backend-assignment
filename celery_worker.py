import os
from celery import Celery
from database.models import Job, Certificate
from database.db import SessionLocal
from celery import chord
from dotenv import load_dotenv
from utils import upload_certificate_to_cloud
load_dotenv()

from utils import robust_draw_certificate



REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
if "rediss://" in REDIS_URL and "?" not in REDIS_URL:
    REDIS_URL += "?ssl_cert_reqs=CERT_NONE"
celery_app = Celery(
    'certificate_tasks',
    broker=REDIS_URL,
    backend=REDIS_URL
)

@celery_app.task(bind=True, max_retries=3)
def celery_generate_single_certificate(self, job_id: str, event_name: str, date: str, recipient_dict: dict):
    db = SessionLocal()
    os.makedirs("certificates", exist_ok=True)
    try:
        cert_record = Certificate(
            job_id=job_id,
            recipient_name=recipient_dict['name'],
            recipient_email=recipient_dict['email'],
            status="PROCESSING"
        )
        db.add(cert_record)
        db.commit()
        file_name = f"certificates/cert_{cert_record.id}.png"
        robust_draw_certificate(
            name=recipient_dict['name'],
            achievement=event_name,
            date=date, 
            certificate_id=str(cert_record.id),
            output_path=file_name
        )
        
        
        final_file_url = upload_certificate_to_cloud(file_name, f"cert_{cert_record.id}.png")
        
        cert_record.status = "SUCCESS"
        cert_record.file_url = final_file_url
        db.commit()
        return {
            "name" : recipient_dict['name'],
            "email" : recipient_dict['email'],
            "status" : "SUCCESS"
        }
    except Exception as e:
        cert_record.status = "FAILED"
        cert_record.error_message = str(e)
        db.commit()
        return {
            "name" : recipient_dict['name'],
            "email" : recipient_dict['email'],
            "status" : "FAILED"
        }
    finally:
        db.close()

@celery_app.task
def finalize_job(results, job_id: str):

    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if job:
        if "FAILED" in results:
            job.status = "PARTIALLY_FAILED"
        else:
            job.status = "COMPLETED"
        db.commit()
    db.close()




@celery_app.task
def master_certificate_generator(data_dict: dict, job_id: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    if job:
        job.status = "PROCESSING"
        db.commit()
    db.close()
    

    tasks_to_run = []
    for recipient in data_dict['recipients']:

        task_signature = celery_generate_single_certificate.s(
            job_id=job_id,
            event_name=data_dict['event_name'],
            date=data_dict['date'],
            recipient_dict=recipient
        )
        tasks_to_run.append(task_signature)
    

    chord(tasks_to_run)(finalize_job.s(job_id=job_id))



# @celery_app.task(bind=True, max_retries=3)
# def celery_generate_certificate(self, data_dict: dict, job_id: str):
#     os.makedirs("certificates", exist_ok=True)
#     db = SessionLocal()
    

#     data = CertificateModel(**data_dict)
    
#     try:
#         print(f" Started processing job {job_id}")
        
#         job = db.query(Job).filter(Job.id == job_id).first()
#         if job:
#             job.status = "PROCESSING"
#             db.commit()

#         for i, recipient in enumerate(data.recipients):
#             print(f"[CELERY] Processing recipient {i+1}: {recipient.name}")
            
#             cert_record = Certificate(
#                 job_id=job_id,
#                 recipient_name=recipient.name,
#                 recipient_email=recipient.email,
#                 status="PROCESSING"
#             )
#             db.add(cert_record)
#             db.commit() 

#             try:
#                 file_name = f"certificates/cert_{cert_record.id}.png"
                
#                 robust_draw_certificate(
#                     name=recipient.name,
#                     achievement=data.event_name,
#                     date=data.date, 
#                     certificate_id=cert_record.id,
#                     output_path=file_name
#                 )
                
#                 cert_record.status = "SUCCESS"
#                 cert_record.file_url = file_name 
                
#             except Exception as e:
#                 cert_record.status = "FAILED"
#                 cert_record.error_message = str(e)
            
#             db.commit()


#         if job:
#             failed_count = db.query(Certificate).filter(Certificate.job_id == job_id, Certificate.status == "FAILED").count()
            
#             if failed_count > 0:
#                 job.status = "PARTIALLY_FAILED"
#             else:
#                 job.status = "COMPLETED"
                
#             db.commit()

#         print(f"Job {job_id} successfully processed!")

#     except Exception as e:
#         print(f"[CELERY] Error processing job {job_id}: {str(e)}")
#         # self.retry() for timeout
        
#     finally:
#         db.close()
