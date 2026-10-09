from pydantic import BaseModel, Field
from typing import List


class Recipient(BaseModel):
    name: str = Field(description="Name of the recipient")
    email: str = Field(description="Email of the recipient")


class CertificateModel(BaseModel):
    event_name: str = Field(description="Name of the certificate")
    date: str = Field(description="Date of the event")
    recipients: List[Recipient] = Field(description="List of recipients")
