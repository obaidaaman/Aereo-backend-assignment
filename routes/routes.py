from controller.controller import get_job_controller, downlaod_certificate_controller
from fastapi import APIRouter, status, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from models.models import CertificateModel
from database.db import get_db
from controller.controller import generate_certificate_controller

route = APIRouter(
    prefix="/api/job"
)

@route.post("/certificate", status_code=status.HTTP_202_ACCEPTED)
def certificate(data: CertificateModel, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
   
    return generate_certificate_controller(data, background_tasks, db)

@route.get("/{job_id}")
def get_job(job_id : str, db: Session = Depends(get_db)):
    return get_job_controller(job_id, db)


@route.get("/download/{cert_id}")
def download_certificate(cert_id: str, db  : Session = Depends(get_db)):
    return downlaod_certificate_controller(cert_id, db)
